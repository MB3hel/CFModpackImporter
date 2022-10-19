
from typing import Dict, List
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtCore import QUrl, Signal, QObject
import time
import os
from bs4 import BeautifulSoup


## Wraps QT Web View to download mods from CurseForge
class Downloader(QObject):
    error = Signal()
    done = Signal()

    ## Create a new Downloader and start downloading mods
    #  @param idmap Dict of project ids mapped to fileids idmap[projid] = fileid
    #  @param urls List of urls for mods
    def __init__(self, idmap: Dict[int, int], urls: List[str], destfolder: str):
        super().__init__(None)
        self.__idmap = idmap
        self.__urls = urls
        self.__destfoler = destfolder
        self.__curr_idx = 0
        self.__attempts = 0
        self.__web = QWebEngineView()
        self.__web.show()
        self.__start_next()
    
    def __on_error(self):
        self.__web.close()
        self.error.emit()
    
    def __on_done(self):
        self.__web.close()
        self.done.emit()

    def __start_next(self):
        if(self.__attempts > 3):
            self.__on_error()
            return
        if(self.__curr_idx == len(self.__urls)):
            self.__on_done()
            return
        
        # Connect loadFinished signal and load next url
        self.__web.loadFinished.connect(self.__page_loaded)
        url = QUrl(self.__urls[self.__curr_idx])
        self.__attempts += 1
        self.__web.load(url)
        

    def __page_loaded(self, ok: bool):
        self.__web.loadFinished.disconnect(self.__page_loaded)
        if ok:
            # Run javascript to load page source
            self.__web.page().runJavaScript("document.documentElement.outerHTML", self.__source_read)
        else:
            # Retry loading the page in 2 seconds
            time.sleep(2)
            self.__start_next()

    def __source_read(self, html: str):
        # Connect download request signal
        self.__web.page().profile().downloadRequested.connect(self.__download_handler)
        
        # Parse webpage to get project ID
        fileid = -1
        try:
            soup = BeautifulSoup(html, "lxml")
            label_tag = soup.find("span", text="Project ID")
            id_tag = label_tag.find_next_sibling("span")
            projid = int(id_tag.text)
            fileid = self.__idmap[projid]
        except:
            print("Failed to obtain Project ID for {0}".format(self.__web.url().toString()))
            self.__on_error()
            return
        
        # Construct and navigate to download url
        # This url will start a file download after a number of seconds
        # Thus, don't need a load finished slot, but a download requested slot
        dlurl = self.__web.url().toString()
        if dlurl.endswith("/"):
            dlurl = dlurl[:-1]
        dlurl = "{0}/{1}".format(dlurl, fileid)
        self.__web.load(QUrl(dlurl))

    def __download_handler(self, download: QWebEngineDownloadRequest):
        # Disconnect webview download signal
        self.__web.page().profile().downloadRequested.disconnect(self.__download_handler)
        
        # Connect download state changed signal
        download.stateChanged.connect(self.__download_state_changed)

        # Set download folder and start download
        download.setDownloadDirectory(self.__destfoler)
        download.accept()

    def __download_state_changed(self, state: QWebEngineDownloadRequest.DownloadState):
        if(state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted):
            # Download done. Start the next one.
            self.__curr_idx += 1
            self.__attempts = 0
            self.__start_next()
        elif(state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled or \
                state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted):
            # Download failed. Retry in 2 seconds.
            time.sleep(2)
            self.__start_next()


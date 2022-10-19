
from typing import Dict, List
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtCore import QUrl, Signal, QObject
from PySide6.QtGui import QCloseEvent
import time
import os
from bs4 import BeautifulSoup


class MyWebEngineView(QWebEngineView):
    closed = Signal()

    def closeEvent(self, arg__1: QCloseEvent):
        self.closed.emit()
        return super().closeEvent(arg__1)


## Wraps QT Web View to download mods from CurseForge
class Downloader(QObject):

    # Signal to start next download
    next = Signal()

    ## Create a new Downloader and start downloading mods
    #  @param idmap Dict of project ids mapped to fileids idmap[projid] = fileid
    #  @param urls List of urls for mods
    def __init__(self, parent):
        super().__init__(parent)
        self.__idmap = {}
        self.__urls = []
        self.__destfoler = ""
        self.__web = MyWebEngineView()
        self.__web.resize(640, 480)
        self.__web.closed.connect(self.__on_error)
        self.__web.loadFinished.connect(self.__page_loaded)
        self.__web.loadProgress.connect(self.__page_progress)
        self.next.connect(self.__start_next)
        
    def start(self, idmap: Dict[int, int], urls: List[str], destfolder: str):
        self.__idmap = idmap
        self.__urls = urls
        self.__destfoler = destfolder
        self.__done = False
        self.__error = False
        self.__curr_idx = 0
        self.__attempts = 0
        self.next.emit()
    
    @property
    def done(self) -> bool:
        return self.__done
    
    @property
    def error(self) -> bool:
        return self.__error

    def __on_error(self):
        self.__web.close()
        self.__error = True
        self.__done = True
    
    def __on_done(self):
        self.__web.close()
        self.__error = False
        self.__done = True

    def __start_next(self):
        if(self.__curr_idx == 0):
            self.__web.show()

        if(self.__attempts > 3):
            self.__on_error()
            return
        if(self.__curr_idx == len(self.__urls)):
            self.__on_done()
            return

        if self.__attempts != 0:
            print("(Retry {})".format(self.__attempts), end="")
        print("Downloading mod {0} of {1}...".format(self.__curr_idx, len(self.__urls)))
                
        # Load next url
        self.__web.stop()
        self.__ignore_loads = False
        url = QUrl(self.__urls[self.__curr_idx])
        self.__attempts += 1
        self.__web.load(url)
        
    def __page_progress(self, progress: int):
        if self.__ignore_loads:
            return
        # Run javascript to read page source
        print("Progress {}".format(progress))
        self.__web.page().runJavaScript("document.documentElement.outerHTML", 0, self.__source_read)

    def __page_loaded(self, ok: bool):
        if self.__ignore_loads:
            return
        if not ok:
            # Retry download of this mod 2 seconds
            print("Loading page failed.")
            time.sleep(2)
            self.next.emit()

    def __source_read(self, html: str):
        if html.find("Project ID") == -1:
            # page is not loaded enough yet
            print("Not enough")
            return
        print("Loaded")
        
        # Page is as loaded as it needs to be

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
        self.__ignore_loads = True
        dlurl = self.__web.url().toString()
        if dlurl.endswith("/"):
            dlurl = dlurl[:-1]
        dlurl = "{0}/download/{1}".format(dlurl, fileid)
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
            self.next.emit()
        elif(state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled or \
                state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted):
            # Download failed. Retry in 2 seconds.
            print("Download interrupted.")
            time.sleep(2)
            self.next.emit()



from typing import Dict, List
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from PySide6.QtCore import QUrl
import time


## Wraps QT Web View to download mods from CurseForge
class Downloader:
    ## Create a new Downloader and start downloading mods
    #  @param idmap Dict of project ids mapped to fileids idmap[projid] = fileid
    #  @param urls List of urls for mods
    def __init__(self, idmap: Dict[int, int], urls: List[str]):
        self.__idmap = idmap
        self.__urls = urls
        self.__curr_idx = 0
        self.__attempts = 0
        self.__web = QWebEngineView()
        self.__web.show()
        self.__start_next()
    
    def __start_next(self):
        if(self.__attempts > 3):
            # TODO: Emit error signal
            return
        if(self.__curr_idx == len(self.__urls)):
            # TODO: Emit done signal
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
        # TODO: Parse page and construct download url
        # TODO: Navigate to download url

    def __download_handler(self, download: QWebEngineDownloadRequest):
        # TODO: Disconnect webview download signal
        # TODO: Set download path and start download (connect state change sig)
        pass

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


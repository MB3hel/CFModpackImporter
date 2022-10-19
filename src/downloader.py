
from PySide6.QtCore import QObject, Signal, QUrl, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from enum import Enum, auto
from typing import List, Dict
from bs4 import BeautifulSoup
import time

# TODO: Add page load timeout with increased delay before retry

class MyWebEngineView(QWebEngineView):
    closed = Signal()
    def closeEvent(self, arg__1: QCloseEvent):
        self.closed.emit()
        return super().closeEvent(arg__1)


class Downloader(QObject):

    error_sig = Signal()
    next_timer_sig = Signal()

    class State(Enum):
        LoadParsePage = auto()
        LoadDownloadPage = auto()
        WaitForDownload = auto()

    def __init__(self, parent, id: int):
        super().__init__(parent)

        # Information provided in start() function
        self.__idmap = {}
        self.__urls = []
        self.__destfoler = ""
        self.__id = id

        # State machine
        self.__curr_idx = 0
        self.__attempts = 0
        self.__state = None
        self.__done = False
        self.__error = False

        # Webview
        self.__web = MyWebEngineView()
        self.__web.resize(640, 480)
        self.__web.closed.connect(self.__on_error)
        self.__web.loadFinished.connect(self.__page_loaded)
        self.__web.loadProgress.connect(self.__page_progress)
        self.__web.page().profile().downloadRequested.connect(self.__download_handler)

        # Delay timer
        self.__next_timer = QTimer(self)
        self.__next_timer.setSingleShot(True)
        self.__next_timer.timeout.connect(self.__start_next)

        # Other signals
        self.next_timer_sig.connect(self.__next_timer.start)
        self.error_sig.connect(self.__on_error)
    
    @property
    def done(self) -> bool:
        return self.__done
    
    @property
    def error(self) -> bool:
        return self.__error

    def start(self, idmap: Dict[int, int], urls: List[str], destfolder: str, show_webview: bool):
        self.__idmap = idmap
        self.__urls = urls
        self.__destfoler = destfolder
        self.__done = False
        self.__error = False
        self.__curr_idx = 0
        self.__attempts = 0
        self.__state = None
        self.__show_webview = show_webview
        self.__next_timer.setInterval(1)
        self.next_timer_sig.emit()
    
    def stop(self):
        self.__state = None
        self.error_sig.emit()

    def __start_next(self):
        if(self.__curr_idx == 0 and self.__show_webview):
            # Show view on first download started
            self.__web.show()

        if(self.__attempts > 3):
            # Too many attempts = error
            self.__on_error()
            return
        
        if(self.__curr_idx == len(self.__urls)):
            # All urls handled = modpack downloaded fully
            self.__on_done()
            return

        # Show what is being downloaded in the log
        if self.__attempts != 0:
            print("(Retry {}) ".format(self.__attempts), end="")
        print("Downloader {0}: Mod {1} of {2}...".format(self.__id, self.__curr_idx+1, len(self.__urls)))
                
        # Load next url
        self.__web.stop()
        self.__state = Downloader.State.LoadParsePage
        url = QUrl(self.__urls[self.__curr_idx])
        self.__attempts += 1
        self.__web.load(url)

    def __on_error(self):
        self.__web.close()
        self.__error = True
        self.__done = True
    
    def __on_done(self):
        self.__web.close()
        self.__error = False
        self.__done = True

    def __page_loaded(self, ok: bool):
        if self.__state == Downloader.State.LoadParsePage:
            if ok:
                # Get page source to see if page is loaded enough to get required information
                self.__web.page().runJavaScript("document.documentElement.outerHTML", 0, self.__source_read)
            else:
                # Error loading page. Retry same mod.
                self.__next_timer.setInterval(2000)
                self.next_timer_sig.emit()

    def __page_progress(self, progress: int):
        if self.__state == Downloader.State.LoadParsePage:
            # Get page source to see if page is loaded enough to get required information
            self.__web.page().runJavaScript("document.documentElement.outerHTML", 0, self.__source_read)
    
    def __source_read(self, html: str):
        if self.__state == Downloader.State.LoadParsePage:
            if html.find("Project ID") == -1:
                # Not loaded enough
                return
            
            # Page is loaded enough. Find project id and use it to get file id
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
            self.__state = Downloader.State.LoadDownloadPage
            dlurl = self.__web.url().toString()
            if dlurl.endswith("/"):
                dlurl = dlurl[:-1]
            dlurl = "{0}/download/{1}".format(dlurl, fileid)
            self.__web.load(QUrl(dlurl))
    
    def __download_handler(self, download: QWebEngineDownloadRequest):
        if self.__state == Downloader.State.LoadDownloadPage:
            # Connect download state changed signal
            download.stateChanged.connect(self.__download_state_changed)

            # Set download folder and start download
            self.__state = Downloader.State.WaitForDownload
            download.setDownloadDirectory(self.__destfoler)
            download.accept()

    def __download_state_changed(self, state: QWebEngineDownloadRequest.DownloadState):
        if self.__state == Downloader.State.WaitForDownload:
            if(state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted):
                # Download done. Start the next one.
                self.__next_timer.setInterval(2000)
                self.next_timer_sig.emit()
            elif(state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled or \
                    state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted):
                # Download failed. Retry same mode.
                self.__next_timer.setInterval(2000)
                self.next_timer_sig.emit()

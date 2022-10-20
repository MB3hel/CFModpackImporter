
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
    __error_sig = Signal()
    __next_start = Signal()

    def __init__(self, parent, id: int):
        super().__init__(parent)

        # Information provided in start() function
        self.__idmap = {}
        self.__urls = []
        self.__destfoler = ""
        self.__id = id

        # Status info
        self.__curr_idx = 0
        self.__attempts = 0
        self.__done = False
        self.__error = False

        # Webview
        self.__web = MyWebEngineView()
        self.__web.resize(640, 480)
        self.__web.closed.connect(self.__on_error)

        # Delayed start next timer
        self.__delayed_next = QTimer()
        self.__delayed_next.setSingleShot(True)
        self.__delayed_next.timeout.connect(self.__start_next)

        # Other signals
        self.__error_sig.connect(self.__on_error)
        self.__next_start.connect(self.__delayed_next.start)
    
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
        self.__show_webview = show_webview

        # This function may not be called from main thread
        self.__delayed_next.setInterval(1)
        self.__next_start.emit()
    
    def stop(self):
        # This function may not be called from main thread
        self.__error_sig.emit()

    def __start_next(self):
        if self.__done:
            return

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
                
        # Load next url to parse mod id
        self.__web.stop()
        url = QUrl(self.__urls[self.__curr_idx])
        self.__attempts += 1
        self.__web.loadProgress.connect(self.__parse_page_progress)
        self.__web.load(url)

    def __on_error(self):
        self.__error = True
        self.__done = True
        self.__web.stop()
        self.__web.close()
    
    def __on_done(self):
        self.__web.close()
        self.__error = False
        self.__done = True

    # TODO: Handle errors loading pages

    def __parse_page_progress(self, progress: int):
        if self.__done:
            return
        
        # Once loaded "enough", stop loading and read page source to parse ID
        # No need to wait for all ads to load
        # "enough" = 75% is based on experimental data
        if progress > 75:
            self.__web.loadProgress.disconnect(self.__parse_page_progress)
            self.__web.stop()
            self.__web.page().runJavaScript("document.documentElement.outerHTML", 0, self.__parse_page_source)
    
    def __parse_page_source(self, html: str):
        if self.__done:
            return
        
        if html.find("Project ID") == -1:
            # Parse failed. Retry same mod.
            print("Downloader {0}: Parse failed.".format(self.__id))
            self.__delayed_next.setInterval(2000)
            self.__delayed_next.start()
            return

        # Parse project id and use it to get the file id
        fileid = -1
        try:
            soup = BeautifulSoup(html, "lxml")
            label_tag = soup.find("span", text="Project ID")
            id_tag = label_tag.find_next_sibling("span")
            projid = int(id_tag.text)
            fileid = self.__idmap[projid]
        except:
            # Parse failed. Retry same mod.
            print("Downloader {0}: Parse failed.".format(self.__id))
            self.__delayed_next.setInterval(2000)
            self.__delayed_next.start()
            self.__on_error()
            return
        
        # Use file id to construct download url
        dlurl = self.__web.url().toString()
        if dlurl.endswith("/"):
            dlurl = dlurl[:-1]
        dlurl = "{0}/download/{1}".format(dlurl, fileid)

        # Navigate to download url (without file suffix)
        self.__web.loadProgress.connect(self.__download_page_progress)
        self.__web.load(dlurl)

    def __download_page_progress(self, progress: int):
        if self.__done:
            return
        
        # Once loaded "enough", stop loading and navigate to direct download link
        # No need to wait for 5 seconds
        # "enough" = 75% is based on experimental data
        if progress > 75:
            self.__web.loadProgress.disconnect(self.__download_page_progress)
            self.__web.stop()
            direct_url = self.__web.url().toString()
            if direct_url.endswith("/"):
                direct_url = direct_url[:-1]
            direct_url = "{0}/file".format(direct_url)
            self.__web.page().profile().downloadRequested.connect(self.__download_handler)
            self.__web.load(QUrl(direct_url))

    def __download_handler(self, download: QWebEngineDownloadRequest):
        if self.__done:
            return
        
        # Won't need to accept more downloads
        self.__web.page().profile().downloadRequested.disconnect(self.__download_handler)
        
        # Connect download state changed signal (used to detect done and error)
        download.stateChanged.connect(self.__download_state_changed)

        # Set download folder and start download
        download.setDownloadDirectory(self.__destfoler)
        download.accept()

    def __download_state_changed(self, state: QWebEngineDownloadRequest.DownloadState):
        if self.__done:
            return
        
        if(state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted):
            # Download done. Start the next one.
            self.__curr_idx += 1
            self.__attempts = 0
            self.__delayed_next.setInterval(2000)
            self.__delayed_next.start()
        elif(state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled or \
                state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted):
            # Download failed. Retry same mod.
            print("Downloader {0}: Download failed.".format(self.__id))
            self.__delayed_next.setInterval(2000)
            self.__delayed_next.start()

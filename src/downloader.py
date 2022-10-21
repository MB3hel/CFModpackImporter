
from PySide6.QtCore import QObject, Signal, QUrl, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEnginePage, QWebEngineProfile
from enum import Enum, auto
from typing import Callable, List, Dict, Tuple
from bs4 import BeautifulSoup
import time
import os

# TODO: Add page load timeout with increased delay before retry

class MyWebEngineView(QWebEngineView):
    closed = Signal()
    def closeEvent(self, arg__1: QCloseEvent):
        self.closed.emit()
        return super().closeEvent(arg__1)


class Downloader(QObject):

    # External use
    downloader_error = Signal(QObject)
    downloader_done = Signal(QObject)
    
    # Internal use
    __error_sig = Signal()
    __next_start = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        # Information provided in start() function
        self.__idmap = {}
        self.__url_getter = None
        self.__curr_url = ""
        self.__destfolder = ""
        self.__id = -1

        # Status info
        self.__attempts = 0
        self.__done = False
        self.__error = False
        self.__curr_dl = None

        # Webview
        # Give each web view its own profile to avoid issues with parallel downloads
        self.__web = MyWebEngineView()
        self.__web.setPage(QWebEnginePage(QWebEngineProfile("", parent), parent))
        self.__web.resize(640, 480)
        self.__web.closed.connect(self.__on_error)

        # Delayed start next timer
        self.__delayed_next = QTimer()
        self.__delayed_next.setSingleShot(True)
        self.__delayed_next.timeout.connect(self.__start_next)

        # Timeout for getting to the download starting
        # Used to detect when pages are not loading and need a reload to work (CurseForge / Cloudflare issue)
        self.__get_to_dl_timer = QTimer()
        self.__get_to_dl_timer.setSingleShot(True)
        self.__get_to_dl_timer.timeout.connect(self.__stop_and_reload)

        # Download stall detection
        # If not bytes received for a certain time, assume the download has failed and needs to be retried
        self.__dl_stall_timer = QTimer()
        self.__dl_stall_timer.setSingleShot(True)
        self.__dl_stall_timer.timeout.connect(self.__cancel_download)

        # Other signals
        self.__error_sig.connect(self.__on_error)
        self.__next_start.connect(self.__delayed_next.start)
    
    @property
    def done(self) -> bool:
        return self.__done
    
    @property
    def error(self) -> bool:
        return self.__error

    def start(self, idmap: Dict[int, int], url_getter: Callable[[], Tuple[int, str]], destfolder: str, show_webview: bool):
        self.__idmap = idmap
        self.__destfolder = destfolder
        self.__url_getter = url_getter
        self.__id, self.__curr_url = self.__url_getter()
        self.__done = False
        self.__error = False
        self.__attempts = 0

        if show_webview:
            self.__web.show()

        # This function may not be called from main thread
        self.__delayed_next.setInterval(1)
        self.__next_start.emit()
    
    def stop(self):
        # This function may not be called from main thread
        self.__error_sig.emit()

    def __stop_and_reload(self):
        # Disconnect any signals that may be connected
        try:
            self.__web.loadProgress.disconnect(self.__parse_page_progress)
        except:
            pass
        try:
            self.__web.loadProgress.disconnect(self.__download_page_progress)
        except:
            pass
        try:
            self.__web.loadProgress.disconnect(self.__download_page_progress)
        except:
            pass
        
        print("Downloader {0}: Timed out getting to download.".format(self.__id))

        # Stop loading the page
        self.__web.stop()

        # Retry the same mod (after a delay to ensure the page should actually load this time)
        self.__delayed_next.setInterval(2000)
        self.__delayed_next.start()

    def __start_next(self):
        if self.__done:
            return

        if(self.__attempts > 5):
            # Too many attempts = error
            self.__on_error()
            return
        
        if(self.__curr_url == "" or self.__curr_url is None):
            # All urls handled = modpack downloaded fully
            self.__on_done()
            return

        # Show what is being downloaded in the log
        if self.__attempts != 0:
            print("(Retry {}) ".format(self.__attempts), end="")
        print("Mod {0}: Starting download...".format(self.__id))
                
        # Load next url to parse mod id
        self.__get_to_dl_timer.setInterval(15000)
        self.__web.stop()
        url = QUrl(self.__curr_url)
        self.__attempts += 1
        self.__web.loadProgress.connect(self.__parse_page_progress)
        self.__web.load(url)

    def __on_error(self):
        if self.__done:
            return
        self.__error = True
        self.__done = True
        self.__web.stop()
        self.__web.hide()
        self.downloader_error.emit(self)
    
    def __on_done(self):
        if self.__done:
            return
        self.__error = False
        self.__done = True
        self.__web.stop()
        self.__web.hide()
        self.downloader_done.emit(self)

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
            print("Mod {0}: Parse failed.".format(self.__id))
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
            print("Mod {0}: Parse failed.".format(self.__id))
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

        self.__curr_dl = download

        # Got to the download phase. Don't use this timeout once download started.
        # This is a timeout for getting to the download stage
        self.__get_to_dl_timer.stop()

        # Won't need to accept more downloads
        self.__web.page().profile().downloadRequested.disconnect(self.__download_handler)
        
        # Connect download state changed signal (used to detect done and error)
        download.stateChanged.connect(self.__download_state_changed)
        download.receivedBytesChanged.connect(self.__download_received_bytes)

        # Start stall timer
        self.__dl_stall_timer.setInterval(10000)
        self.__dl_stall_timer.start()

        # Set download folder and start download
        download.setDownloadDirectory(self.__destfolder)
        download.accept()

    def __download_received_bytes(self):
        # Reset timeout because download is not stalled
        self.__dl_stall_timer.stop()
        self.__dl_stall_timer.setInterval(10000)
        self.__dl_stall_timer.start()

    def __download_state_changed(self, state: QWebEngineDownloadRequest.DownloadState):
        if self.__done:
            return
        
        if(state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted):
            fn = self.__curr_dl.downloadFileName()
            self.__dl_stall_timer.stop()
            self.__curr_dl.deleteLater()
            self.__curr_dl = None

            # Download done. Start the next one.
            print("Mod {0}: Download successful.".format(self.__id))
            self.__id, self.__curr_url = self.__url_getter()
            self.__attempts = 0
            self.__delayed_next.setInterval(2000)
            self.__delayed_next.start()
        elif(state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted):
            self.__dl_stall_timer.stop()
            self.__curr_dl.deleteLater()
            self.__curr_dl = None

            # Download failed. Retry same mod.
            print("Mod {0}: Download failed.".format(self.__id))
            self.__delayed_next.setInterval(2000)
            self.__delayed_next.start()
    
    def __cancel_download(self):
        # Download failed. Retry same mod.
        print("Mod {0}: Download has stalled.")
        self.__curr_dl.cancel()
        self.__curr_dl.deleteLater()
        self.__curr_dl = None
        self.__delayed_next.setInterval(2000)
        self.__delayed_next.start()

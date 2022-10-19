#
# Copyright 2022 Marcus Behel
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors 
# may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.
#


from ast import List
import json
from logging import root
import os
import shutil
import tempfile
import sys
import threading
import time
import traceback
import platform
from typing import Optional, Callable, List, Dict
import zipfile
from PySide6.QtCore import QDir, Signal, QRunnable, QObject, QThreadPool, Qt, QFile, QThread
from PySide6.QtWidgets import QMainWindow, QWidget, QFileDialog, QMessageBox, QProgressDialog, QLineEdit
from PySide6.QtGui import QCloseEvent, QIntValidator
from downloader import Downloader
from instructionsdialog import InstructionsDialog
from logwindow import LogWindow
from ui_importer import Ui_Importer
from aboutdialog import AboutDialog
import subprocess
from bs4 import BeautifulSoup


class MyProgressDialog(QProgressDialog):
    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent=parent)
        self.setCancelButton(None)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()


class Task(QRunnable, QObject):
    task_complete = Signal(object)
    task_exception = Signal(Exception)
    def __init__(self, parent, target: Callable, *args, **kwargs):
        QRunnable.__init__(self)
        QObject.__init__(self, parent=parent)
        self.__target = target
        self.__args = args
        self.__kwargs = kwargs

        self.setAutoDelete(True)
    
    def run(self):
        try:
            res = self.__target(*self.__args, **self.__kwargs)
            self.task_complete.emit(res)
        except Exception as e:
            try:
                self.task_exception.emit(e)
            except:
                pass


class ImporterWindow(QMainWindow):
    update_progress = Signal(str)

    def __init__(self, logwindow: LogWindow, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Non-UI variables
        self.logwindow = logwindow
        self.manifest_json = None
        self.tasks = []

        # Setup UI
        self.ui = Ui_Importer()
        self.ui.setupUi(self)
        self.pdialog = MyProgressDialog(self)
        self.pdialog.cancel()
        self.pdialog.hide()

        # Holds currently used download instances
        self.downloaders: List[Downloader] = []

        # Only allow integers
        self.ui.txt_parallel_down.setValidator(QIntValidator(1, 999))

        # Add version to title
        version_file = QFile(":/version.txt")
        if version_file.open(QFile.ReadOnly):
            version = bytes(version_file.readLine()).decode().strip()
            print("v{0}".format(version))
            self.setWindowTitle("{0} - v{1}".format(self.windowTitle(), version))

        # Signal / slot setup
        self.ui.act_instructions.triggered.connect(self.open_instructions)
        self.ui.act_about.triggered.connect(self.open_about)
        self.ui.btn_browse_modpack.clicked.connect(self.browse)
        self.ui.btn_generate.clicked.connect(self.generate)
        self.update_progress.connect(self.do_update_progress)

    def start_task(self, task: Task):
        self.tasks.append(task)
        QThreadPool.globalInstance().start(task)

    def closeEvent(self, event: QCloseEvent):
        self.logwindow.manualClose()
        return super().closeEvent(event)

    def browser_changed(self, text: str):
        self.ui.chk_headless.setEnabled(text == "firefox")
        if not self.ui.chk_headless.isEnabled():
            self.ui.chk_headless.setChecked(False)

    def browse(self):
        filename = QFileDialog.getOpenFileName(self, self.tr("Select Modpack Zip"), QDir.homePath(), self.tr("Zip Files (*.zip)"))[0]
        
        if filename == "":
            return
        
        # Extract to temp directory and read info from manifest (also makes sure valid zip file)
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                with zipfile.ZipFile(filename, "r") as zf:
                    zf.extract('manifest.json', tempdir)
                with open(os.path.join(tempdir, "manifest.json"), "r") as manifest_file:
                    self.manifest_json = json.load(manifest_file)
                self.ui.txt_modpack_zip.setText(filename)
                self.ui.txt_mc_version.setText(self.manifest_json["minecraft"]["version"])
                self.ui.txt_modloader.setText(self.manifest_json["minecraft"]["modLoaders"][0]["id"])
                self.ui.txt_modpack_name.setText(self.manifest_json["name"])
                self.ui.txt_nummods.setText("{}".format(len(self.manifest_json["files"])))
                self.ui.btn_generate.setEnabled(True)
        except Exception as e:
            self.ui.txt_modpack_zip.setText("")
            self.ui.txt_mc_version.setText("")
            self.ui.txt_modloader.setText("")
            self.ui.txt_modpack_name.setText("")
            self.ui.txt_nummods.setText("")
            self.ui.btn_generate.setEnabled(False)

            dialog = QMessageBox(parent=self)
            dialog.setWindowModality(Qt.WindowModal)
            dialog.setIcon(QMessageBox.Warning)
            dialog.setText("{0}: {1}".format(type(e).__name__, str(e)))
            dialog.setWindowTitle(self.tr("Error Opening Modpack Zip"))
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec()
            return

    def open_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def open_instructions(self):
        dialog = InstructionsDialog(self)
        dialog.exec()
    
    def show_progress(self, label: str):
        self.pdialog.hide()
        self.pdialog.setWindowTitle("Working")
        self.pdialog.setLabelText(label)
        self.pdialog.setWindowModality(Qt.WindowModal)
        self.pdialog.setModal(True)
        self.pdialog.setMinimum(0)
        self.pdialog.setMaximum(0)
        self.pdialog.setValue(0)
        self.pdialog.show()
    
    def do_update_progress(self, label: str):
        self.pdialog.setLabelText(label)

    def generate(self):
        filename = QFileDialog.getSaveFileName(self, "Generated File Name", "modpack_add_to_instance.zip", ".zip")[0]
        if filename == "":
            return

        # Setup downloaders before starting do_generate
        parallel = int(self.ui.txt_parallel_down.text())
        if len(self.downloaders) != parallel:
            self.downloaders = []
            for i in range(parallel):
                self.downloaders.append(Downloader(self, i+1))

        task = Task(self, self.do_generate, filename, parallel)
        task.task_complete.connect(self.generate_done)
        task.task_exception.connect(self.generate_exec)
        self.start_task(task)
        self.show_progress("Generating...")
        

    def generate_done(self, res):
        print("Modpack zip generated successfully at '{0}'".format(res))
        self.pdialog.hide()
        dialog = QMessageBox(parent=self)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setIcon(QMessageBox.Information)
        dialog.setText(self.tr("Modpack zip file generated successfully. Extract the contents of this zip file to the minecraft folder of a modded instance in the launcher of your choice. {0}").format(res))
        dialog.setWindowTitle(self.tr("Successfully Generated Zip"))
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()

    def generate_exec(self, e):
        traceback.print_tb(e.__traceback__)
        dialog = QMessageBox(parent=self)
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setText("{0}: {1}".format(type(e).__name__, str(e)))
        dialog.setWindowTitle(self.tr("Error Generating Zip"))
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()
        self.pdialog.hide()

    def split_list(self, l: List, n: int) -> List[List]:
        # Split l into n "equally" sized sublists
        sublists: List[List] = []
        for i in range(n):
            sublists.append([])
        l_pos = 0
        curr_subl = 0
        while l_pos < len(l):
            sublists[curr_subl].append(l[l_pos])
            l_pos += 1
            curr_subl = (curr_subl + 1) % n
        return sublists

    def do_generate(self, filename: str, parallel: int):
        with tempfile.TemporaryDirectory() as tempdir:
            print("Working generation directory: {0}".format(tempdir))

            # Copy modpack zip to tempdir
            self.update_progress.emit("Copying modpack zip...")
            mpfile = os.path.join(tempdir, "modpack.zip")
            shutil.copy(self.ui.txt_modpack_zip.text(), mpfile)

            # Extract manifest.json and modlist.html
            self.update_progress.emit("Extracting files from modpack zip...")
            try:
                with zipfile.ZipFile(mpfile) as zf:
                    zf.extract('manifest.json', tempdir)
                    zf.extract('modlist.html', tempdir)
            except:
                traceback.print_exc()
                raise Exception("Failed to extract manifest.json and / or modlist.html")

            # Extract modpack overrides
            self.update_progress.emit("Extracting modpack overrides...")
            with zipfile.ZipFile(mpfile, "r") as zf:
                zf.extractall(os.path.join(tempdir, "modpack_extracted"))
            shutil.move(os.path.join(tempdir, "modpack_extracted", "overrides"), os.path.join(tempdir, "overrides"))
            shutil.rmtree(os.path.join(tempdir, "modpack_extracted"))

            # Read manifest to get Dict[projid] -> fileid
            # idmap[projid] = fileid
            idmap: Dict[int, int] = {}
            self.update_progress.emit("Parsing manifest.json...")
            try:
                with open(os.path.join(tempdir, "manifest.json"), "r") as manifest_file:
                    filedata = json.load(manifest_file)
                for file in filedata["files"]:
                    projectid = file["projectID"]
                    fileid = file["fileID"]
                    idmap[int(projectid)] = int(fileid)
            except:
                traceback.print_exc()
                raise Exception("Failed to parse manifest.json")

            # Read modlist html to get list of urls
            urls: List[str] = []
            self.update_progress.emit("Parsing modlist.html...")
            try:
                with open(os.path.join(tempdir, "modlist.html"), "rb") as modlist_file:
                    soup = BeautifulSoup(modlist_file.read().decode('utf-8'), "lxml")
                    for a in soup.find_all('a'):
                        urls.append(a.get("href"))
            except:
                traceback.print_exc()
                raise Exception("Failed to parse modlist.html")

            # Download each file into the overrides mods directory
            self.update_progress.emit("Downloading mods...")

            # Prepare mods directory
            modsdir = os.path.join(tempdir, "overrides", "mods")
            if not os.path.exists(modsdir):
                os.mkdir(modsdir)

            # TODO: Instead of splitting url list, just have each downloader remove an item from the shared list when a new one is needed
            # TODO: This is more efficient as it ensures no downloaders are ever sitting idle if one gets delayed
            # Start all downloaders on a subset of urls
            suburls = self.split_list(urls, parallel)
            for i in range(parallel):
                self.downloaders[i].start(idmap, suburls[i], modsdir, self.ui.cbx_show_webview.isChecked())
            
            # Wait for all downloaders to finish. If any have error, stop all
            done = False
            error = False
            while not done:
                done = True
                for i in range(parallel):
                    if not self.downloaders[i].done:
                        done = False
                    elif self.downloaders[i].error:
                        error = True
                        done = True
                        break
                time.sleep(1)
            if error:
                for i in range(parallel):
                    self.downloaders[i].stop()
                raise Exception("Failed to download one or more mods.")

            # Zip contents of overrides folder
            self.update_progress.emit("Zipping generated files...")
            try:
                overrides_dir = os.path.join(tempdir, "overrides")
                archive = shutil.make_archive(os.path.basename(filename)[:-4], format="zip", 
                        root_dir=overrides_dir, base_dir=".")
                shutil.move(archive, filename)
            except Exception as e:
                traceback.print_exc()
                raise e
        return filename

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
import requests
import platform
from typing import Optional, Callable, List
import zipfile
from PySide6.QtCore import QDir, Signal, QRunnable, QObject, QThreadPool, Qt, QFile
from PySide6.QtWidgets import QMainWindow, QWidget, QFileDialog, QMessageBox, QProgressDialog, QLineEdit
from PySide6.QtGui import QCloseEvent, QIntValidator
from instructionsdialog import InstructionsDialog
from logwindow import LogWindow
from ui_importer import Ui_Importer
from aboutdialog import AboutDialog
import subprocess


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

        # Only allow integers in concurrent tabs fields
        self.ui.txt_cfmparse_tabs.setValidator(QIntValidator(1, 999))
        self.ui.txt_cfmdown_tabs.setValidator(QIntValidator(1, 999))

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
        self.ui.cbo_browser.currentTextChanged.connect(self.browser_changed)

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

        task = Task(self, self.do_generate, filename)
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

    def do_generate(self, filename: str):
        with tempfile.TemporaryDirectory() as tempdir:
            print("Working generation directory: {0}".format(tempdir))
            # Download required tools
            self.update_progress.emit("Downloading CFModDownloader...")
            if platform.system() == "Windows":
                cfmdown_file = "win64.zip"
            elif platform.system() == "Darwin":
                cfmdown_file = "macos64.zip"
            elif platform.system() == "Linux":
                cfmdown_file = "linux64.zip"
            else:
                raise Exception(self.tr("No build of CFModDownloader available for this OS."))
            res = requests.get("https://github.com/MB3hel/CFModDownloader/releases/latest/download/{0}".format(cfmdown_file))
            if res.status_code != 200:
                print(res.status_code)
                raise Exception(self.tr("Failed to download CFModDownloader."))
            with open(os.path.join(tempdir, "cfmdown.zip"), "wb") as f:
                f.write(res.content)
            with zipfile.ZipFile(os.path.join(tempdir, "cfmdown.zip"), "r") as zf:
                zf.extractall(tempdir)

            # Remove quarentine (allow running) on macOS
            print("Allowing execution of downloaded files...")
            if platform.system() == "Darwin":
                self.run_cmd(["xattr", "-d", "com.apple.quarantine"], tempdir)
            
            # Allow execution of the downloaded files
            print("Making downloaded files executable")
            if platform.system() != "Windows":
                self.run_cmd(["chmod", "+x", "./cfmdown"], tempdir)
                self.run_cmd(["chmod", "+x", "./cfmparse"], tempdir)

            # Copy modpack zip to tempdir
            self.update_progress.emit("Copying modpack zip...")
            mpfile = os.path.join(tempdir, "modpack.zip")
            shutil.copy(self.ui.txt_modpack_zip.text(), mpfile)
            browser = self.ui.cbo_browser.currentText()
            headless = self.ui.chk_headless.isChecked()

            # Run cfmparse
            parse_tabs = 4
            try:
                parse_tabs = int(self.ui.txt_cfmparse_tabs.text())
            except:
                print("Invalid number of tabs for cfmparse. Using default of {0}".format(parse_tabs))
            self.update_progress.emit("Running cfmparse...")
            args = [os.path.join(tempdir, "cfmparse"), "-b", browser, "-t", str(parse_tabs), mpfile]
            if headless:
                args.append("-n")
            self.run_cmd(args, tempdir)

            # Run cfmdown
            down_tabs = 4
            try:
                down_tabs = int(self.ui.txt_cfmdown_tabs.text())
            except:
                print("Invalid number of tabs for cfmdown. Using default of {0}".format(down_tabs))
            self.update_progress.emit("Running cfmdown...")
            args = [os.path.join(tempdir, "cfmdown"), "-b", browser, "-f", "modfile_modpack.txt", "-d", "mods", "-t", str(down_tabs)]
            if headless:
                args.append("-n")
            self.run_cmd(args, tempdir)

            # Extract modpack overrides
            self.update_progress.emit("Extracting modpack overrides...")
            with zipfile.ZipFile(mpfile, "r") as zf:
                zf.extractall(os.path.join(tempdir, "modpack_extracted"))
            shutil.move(os.path.join(tempdir, "modpack_extracted", "overrides"), os.path.join(tempdir, "overrides"))
            shutil.rmtree(os.path.join(tempdir, "modpack_extracted"))

            # Copy mods to overrides
            self.update_progress.emit("Adding downloaded mods...")
            if not os.path.exists(os.path.join(tempdir, "overrides", "mods")):
                os.mkdir(os.path.join(tempdir, "overrides", "mods"))
            for file in os.listdir(os.path.join(tempdir, "mods")):
                shutil.move(os.path.join(tempdir, "mods", file), os.path.join(tempdir, "overrides", "mods"))
            print(os.listdir(tempdir))

            # Zip contents of overrides folder
            self.update_progress.emit("Zipping generated files...")
            try:
                overrides_dir = os.path.join(tempdir, "overrides")
                archive = shutil.make_archive(os.path.basename(filename)[:-4], format="zip", 
                        root_dir=overrides_dir, base_dir=".")
                shutil.move(archive, filename)
            except Exception as e:
                raise e
        return filename
    
    def run_cmd(self, cmd_list: List[str], working_dir: str):
        # Don't show console window on windows
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        else:
            startupinfo = None
        cmd = None
        try:
            cmd = subprocess.Popen(cmd_list,
                    cwd=working_dir,
                    startupinfo=startupinfo,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
            while True:
                out = cmd.stdout.readline()
                if out == b'' and cmd.poll() is not None:
                    break
                if out != b'':
                    print(out.replace(b'\r', b'').replace(b'\n', b'').decode())
            if cmd.poll() != 0:
                raise Exception("Failed to execute command '{0}'. Process exited with code {1}.".format(" ".join(cmd_list), cmd.returncode))
        except Exception as e:
            if cmd is not None:
                cmd.kill()
            raise e

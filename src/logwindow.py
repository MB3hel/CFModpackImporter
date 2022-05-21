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

import io
from typing import Optional
from PySide6.QtGui import QFontDatabase, QCloseEvent, QTextCursor
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QWidget
from ui_logwindow import Ui_LogWindow


class LogWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.stdout = io.StringIO()

        self.allow_close = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_log)
        self.timer.start(15)

        self.ui = Ui_LogWindow()
        self.ui.setupUi(self)

        self.ui.txt_log.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
    
    def update_log(self):
        txt = self.stdout.getvalue()
        oldtxt = self.ui.txt_log.toPlainText()
        if txt != oldtxt:
            self.ui.txt_log.setPlainText(txt)
            self.ui.txt_log.textCursor().movePosition(QTextCursor.End)
    
    def manualClose(self):
        self.allow_close = True
        self.close()

    def closeEvent(self, event: QCloseEvent):
        if not self.allow_close:
            event.ignore()
            return
        return super().closeEvent(event)

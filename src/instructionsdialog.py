
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QDialog
from ui_instructions import Ui_InstructionsDialog


class InstructionsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_InstructionsDialog()
        self.ui.setupUi(self)

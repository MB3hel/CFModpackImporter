# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'instructions.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget)
import resources_rc

class Ui_InstructionsDialog(object):
    def setupUi(self, InstructionsDialog):
        if not InstructionsDialog.objectName():
            InstructionsDialog.setObjectName(u"InstructionsDialog")
        InstructionsDialog.resize(568, 354)
        icon = QIcon()
        icon.addFile(u":/icon.png", QSize(), QIcon.Normal, QIcon.Off)
        InstructionsDialog.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(InstructionsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.textEdit = QTextEdit(InstructionsDialog)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setReadOnly(True)

        self.verticalLayout.addWidget(self.textEdit)

        self.buttonBox = QDialogButtonBox(InstructionsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(InstructionsDialog)
        self.buttonBox.accepted.connect(InstructionsDialog.accept)
        self.buttonBox.rejected.connect(InstructionsDialog.reject)

        QMetaObject.connectSlotsByName(InstructionsDialog)
    # setupUi

    def retranslateUi(self, InstructionsDialog):
        InstructionsDialog.setWindowTitle(QCoreApplication.translate("InstructionsDialog", u"CFModpackImporter Instructions", None))
        self.textEdit.setHtml(QCoreApplication.translate("InstructionsDialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">CFModpackImporter Usage Instructions</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic;\">Note: you must either install chrome or firefox before using this tool.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">1. Download the modpack zip file from CurseFo"
                        "rge's website. This can be done by finding the modpack's page and selecting a speicifc version / file under the &quot;Files&quot; tab.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">2. Select the downloaded zip in this tool. Also select which browser you want to use to download files. Firefox is recommended as it has been faster during testing.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">3. Create an instance in the launcher of your choice using the version of minecraft and modloader indicated for the selected pack (this info is indicated in this tool after selecting the downloaded modpack).</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">4. Click the Downalod &amp; Generate button. You will then be asked where to save a generated zip file. Choose somewhere on "
                        "your computer. This will then open firefox or chrome (must be installed on your computer) to download all of the mods in the modpack using CurseForge's website. You do not need to interact with the browser. It will close automatically when complete. The browser may close and reopen a few times. This program will prompt you when it is complete.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">5. Extract the contents of this zip file and add it to the instance you created in the launcher earlier. If you are upating the modpack, replace any folders with the same names in the instance folder.</p></body></html>", None))
    # retranslateUi


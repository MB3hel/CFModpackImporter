# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'importer.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)
import resources_rc

class Ui_Importer(object):
    def setupUi(self, Importer):
        if not Importer.objectName():
            Importer.setObjectName(u"Importer")
        Importer.resize(600, 365)
        icon = QIcon()
        icon.addFile(u":/icon.png", QSize(), QIcon.Normal, QIcon.Off)
        Importer.setWindowIcon(icon)
        self.act_about = QAction(Importer)
        self.act_about.setObjectName(u"act_about")
        self.act_instructions = QAction(Importer)
        self.act_instructions.setObjectName(u"act_instructions")
        self.centralwidget = QWidget(Importer)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_5 = QLabel(self.centralwidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 11, 0, 1, 1)

        self.btn_browse_modpack = QPushButton(self.centralwidget)
        self.btn_browse_modpack.setObjectName(u"btn_browse_modpack")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_browse_modpack.sizePolicy().hasHeightForWidth())
        self.btn_browse_modpack.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.btn_browse_modpack, 2, 3, 1, 1)

        self.txt_modpack_name = QLineEdit(self.centralwidget)
        self.txt_modpack_name.setObjectName(u"txt_modpack_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.txt_modpack_name.sizePolicy().hasHeightForWidth())
        self.txt_modpack_name.setSizePolicy(sizePolicy1)
        self.txt_modpack_name.setReadOnly(True)

        self.gridLayout.addWidget(self.txt_modpack_name, 7, 1, 1, 3)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 10, 0, 1, 1)

        self.label_7 = QLabel(self.centralwidget)
        self.label_7.setObjectName(u"label_7")
        font = QFont()
        font.setBold(True)
        self.label_7.setFont(font)

        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 3)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.label_3, 7, 0, 1, 1)

        self.txt_nummods = QLineEdit(self.centralwidget)
        self.txt_nummods.setObjectName(u"txt_nummods")
        self.txt_nummods.setReadOnly(True)

        self.gridLayout.addWidget(self.txt_nummods, 11, 1, 1, 3)

        self.btn_generate = QPushButton(self.centralwidget)
        self.btn_generate.setObjectName(u"btn_generate")
        self.btn_generate.setEnabled(False)

        self.gridLayout.addWidget(self.btn_generate, 15, 0, 1, 4)

        self.label_6 = QLabel(self.centralwidget)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 8, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 12, 1, 1, 2)

        self.txt_modloader = QLineEdit(self.centralwidget)
        self.txt_modloader.setObjectName(u"txt_modloader")
        self.txt_modloader.setReadOnly(True)

        self.gridLayout.addWidget(self.txt_modloader, 10, 1, 1, 3)

        self.txt_mc_version = QLineEdit(self.centralwidget)
        self.txt_mc_version.setObjectName(u"txt_mc_version")
        self.txt_mc_version.setReadOnly(True)

        self.gridLayout.addWidget(self.txt_mc_version, 8, 1, 1, 3)

        self.label_8 = QLabel(self.centralwidget)
        self.label_8.setObjectName(u"label_8")
        font1 = QFont()
        font1.setBold(False)
        self.label_8.setFont(font1)

        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        font2 = QFont()
        font2.setItalic(True)
        self.label_4.setFont(font2)
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_4.setWordWrap(True)

        self.gridLayout.addWidget(self.label_4, 13, 0, 1, 4)

        self.txt_modpack_zip = QLineEdit(self.centralwidget)
        self.txt_modpack_zip.setObjectName(u"txt_modpack_zip")
        self.txt_modpack_zip.setReadOnly(True)

        self.gridLayout.addWidget(self.txt_modpack_zip, 2, 0, 1, 3)

        self.cbox_browser = QComboBox(self.centralwidget)
        self.cbox_browser.addItem("")
        self.cbox_browser.addItem("")
        self.cbox_browser.setObjectName(u"cbox_browser")

        self.gridLayout.addWidget(self.cbox_browser, 3, 1, 1, 3)

        self.label_9 = QLabel(self.centralwidget)
        self.label_9.setObjectName(u"label_9")
        font3 = QFont()
        font3.setBold(True)
        font3.setItalic(True)
        self.label_9.setFont(font3)
        self.label_9.setAlignment(Qt.AlignCenter)
        self.label_9.setWordWrap(True)

        self.gridLayout.addWidget(self.label_9, 14, 0, 1, 4)

        Importer.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Importer)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 600, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        Importer.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.act_instructions)
        self.menuFile.addAction(self.act_about)

        self.retranslateUi(Importer)

        QMetaObject.connectSlotsByName(Importer)
    # setupUi

    def retranslateUi(self, Importer):
        Importer.setWindowTitle(QCoreApplication.translate("Importer", u"CFModpackImporter", None))
        self.act_about.setText(QCoreApplication.translate("Importer", u"About", None))
        self.act_instructions.setText(QCoreApplication.translate("Importer", u"Instructions", None))
        self.label_5.setText(QCoreApplication.translate("Importer", u"Number Mods", None))
        self.btn_browse_modpack.setText(QCoreApplication.translate("Importer", u"Browse", None))
        self.label_2.setText(QCoreApplication.translate("Importer", u"Modloader", None))
        self.label_7.setText(QCoreApplication.translate("Importer", u"Modpack Information", None))
        self.label.setText(QCoreApplication.translate("Importer", u"Modpack Zip (Download form CurseForge)", None))
        self.label_3.setText(QCoreApplication.translate("Importer", u"Modpack Name", None))
        self.btn_generate.setText(QCoreApplication.translate("Importer", u"Download Mods and Generate Zip", None))
        self.label_6.setText(QCoreApplication.translate("Importer", u"Minecraft Version", None))
        self.label_8.setText(QCoreApplication.translate("Importer", u"Download Using", None))
        self.label_4.setText(QCoreApplication.translate("Importer", u"This tool will use Firefox or Chrome to automate downloading of the modpack mods. You will see many tabs opened and downloads happening automatically. Do not close the browser or this tool will fail.", None))
        self.cbox_browser.setItemText(0, QCoreApplication.translate("Importer", u"chrome", None))
        self.cbox_browser.setItemText(1, QCoreApplication.translate("Importer", u"firefox", None))

        self.label_9.setText(QCoreApplication.translate("Importer", u"WARNING: Tabs may open and change rapidly causing significant flashing. Those sensative to such things may wish to avoid this tool.", None))
        self.menuFile.setTitle(QCoreApplication.translate("Importer", u"File", None))
    # retranslateUi


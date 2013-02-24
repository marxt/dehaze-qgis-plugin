# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/var/vhosts/pyqgis/builder/build/dehazeimage/Ui_DeHazeImage.ui'
#
# Created: Thu Sep 10 07:50:43 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DeHazeImage(object):
    def setupUi(self, DeHazeImage):
        DeHazeImage.setObjectName("DeHazeImage")
        DeHazeImage.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(DeHazeImage)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(DeHazeImage)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), DeHazeImage.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), DeHazeImage.reject)
        QtCore.QMetaObject.connectSlotsByName(DeHazeImage)

    def retranslateUi(self, DeHazeImage):
        DeHazeImage.setWindowTitle(QtGui.QApplication.translate("DeHazeImage", "DeHazeImage", None, QtGui.QApplication.UnicodeUTF8))


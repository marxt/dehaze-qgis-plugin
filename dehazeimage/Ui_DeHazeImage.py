# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_DeHazeImage.ui'
#
# Created: Sun Mar 15 23:06:23 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DeHazeImage(object):
    def setupUi(self, DeHazeImage):
        DeHazeImage.setObjectName(_fromUtf8("DeHazeImage"))
        DeHazeImage.resize(226, 162)
        self.widget = QtGui.QWidget(DeHazeImage)
        self.widget.setGeometry(QtCore.QRect(20, 10, 191, 141))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.layerLabel = QtGui.QLabel(self.widget)
        self.layerLabel.setObjectName(_fromUtf8("layerLabel"))
        self.verticalLayout_3.addWidget(self.layerLabel)
        self.layerComboBox = QtGui.QComboBox(self.widget)
        self.layerComboBox.setObjectName(_fromUtf8("layerComboBox"))
        self.verticalLayout_3.addWidget(self.layerComboBox)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelBlueBand = QtGui.QLabel(self.widget)
        self.labelBlueBand.setObjectName(_fromUtf8("labelBlueBand"))
        self.verticalLayout.addWidget(self.labelBlueBand)
        self.blueComboBox = QtGui.QComboBox(self.widget)
        self.blueComboBox.setObjectName(_fromUtf8("blueComboBox"))
        self.verticalLayout.addWidget(self.blueComboBox)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.labelRedBand = QtGui.QLabel(self.widget)
        self.labelRedBand.setObjectName(_fromUtf8("labelRedBand"))
        self.verticalLayout_2.addWidget(self.labelRedBand)
        self.redComboBox = QtGui.QComboBox(self.widget)
        self.redComboBox.setObjectName(_fromUtf8("redComboBox"))
        self.verticalLayout_2.addWidget(self.redComboBox)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_4.addWidget(self.buttonBox)

        self.retranslateUi(DeHazeImage)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DeHazeImage.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DeHazeImage.reject)
        QtCore.QMetaObject.connectSlotsByName(DeHazeImage)

    def retranslateUi(self, DeHazeImage):
        DeHazeImage.setWindowTitle(_translate("DeHazeImage", "DeHazeImage", None))
        self.layerLabel.setText(_translate("DeHazeImage", "Select Input Layer", None))
        self.labelBlueBand.setText(_translate("DeHazeImage", "blue band", None))
        self.labelRedBand.setText(_translate("DeHazeImage", "red band", None))


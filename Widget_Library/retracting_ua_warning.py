# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'retracting_ua_warning.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_retracting_ua_warn(object):
    def setupUi(self, retracting_ua_warn):
        retracting_ua_warn.setObjectName("retracting_ua_warn")
        retracting_ua_warn.resize(515, 133)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            retracting_ua_warn.sizePolicy().hasHeightForWidth()
        )
        retracting_ua_warn.setSizePolicy(sizePolicy)
        retracting_ua_warn.setMinimumSize(QtCore.QSize(515, 133))
        retracting_ua_warn.setMaximumSize(QtCore.QSize(515, 133))
        self.label = QtWidgets.QLabel(retracting_ua_warn)
        self.label.setGeometry(QtCore.QRect(10, 20, 491, 18))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.widget = QtWidgets.QWidget(retracting_ua_warn)
        self.widget.setGeometry(QtCore.QRect(150, 80, 211, 32))
        self.widget.setObjectName("widget")
        self.cont_cancel_horz = QtWidgets.QHBoxLayout(self.widget)
        self.cont_cancel_horz.setContentsMargins(0, 0, 0, 0)
        self.cont_cancel_horz.setSpacing(24)
        self.cont_cancel_horz.setObjectName("cont_cancel_horz")
        self.continue_button = QtWidgets.QPushButton(self.widget)
        self.continue_button.setMinimumSize(QtCore.QSize(70, 30))
        self.continue_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.continue_button.setObjectName("continue_button")
        self.cont_cancel_horz.addWidget(self.continue_button)
        self.cancel_button = QtWidgets.QPushButton(self.widget)
        self.cancel_button.setMinimumSize(QtCore.QSize(70, 30))
        self.cancel_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.cancel_button.setObjectName("cancel_button")
        self.cont_cancel_horz.addWidget(self.cancel_button)

        self.retranslateUi(retracting_ua_warn)
        QtCore.QMetaObject.connectSlotsByName(retracting_ua_warn)

    def retranslateUi(self, retracting_ua_warn):
        _translate = QtCore.QCoreApplication.translate
        retracting_ua_warn.setWindowTitle(_translate("retracting_ua_warn", "Dialog"))
        self.label.setText(
            _translate(
                "retracting_ua_warn",
                "Warning - Retracting UA from tank. Check water level is below UA seal level",
            )
        )
        self.continue_button.setText(_translate("retracting_ua_warn", "Continue"))
        self.cancel_button.setText(_translate("retracting_ua_warn", "Cancel"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    retracting_ua_warn = QtWidgets.QDialog()
    ui = Ui_retracting_ua_warn()
    ui.setupUi(retracting_ua_warn)
    retracting_ua_warn.show()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_select_ua_channel.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_select_ua_channel(object):
    def setupUi(self, select_ua_channel):
        select_ua_channel.setObjectName("select_ua_channel")
        select_ua_channel.resize(267, 206)
        self.layoutWidget = QtWidgets.QWidget(select_ua_channel)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 121, 41))
        self.layoutWidget.setObjectName("layoutWidget")
        self.sel_ua_channel_vert = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.sel_ua_channel_vert.setContentsMargins(0, 0, 0, 0)
        self.sel_ua_channel_vert.setObjectName("sel_ua_channel_vert")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.sel_ua_channel_vert.addWidget(self.label)
        self.sel_ua_channel_spin = QtWidgets.QSpinBox(self.layoutWidget)
        self.sel_ua_channel_spin.setMaximum(10)
        self.sel_ua_channel_spin.setObjectName("sel_ua_channel_spin")
        self.sel_ua_channel_vert.addWidget(self.sel_ua_channel_spin)

        self.retranslateUi(select_ua_channel)
        QtCore.QMetaObject.connectSlotsByName(select_ua_channel)

    def retranslateUi(self, select_ua_channel):
        _translate = QtCore.QCoreApplication.translate
        select_ua_channel.setWindowTitle(_translate("select_ua_channel", "Form"))
        self.label.setText(_translate("select_ua_channel", "Channel (0=All off)"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    select_ua_channel = QtWidgets.QWidget()
    ui = Ui_select_ua_channel()
    ui.setupUi(select_ua_channel)
    select_ua_channel.show()
    sys.exit(app.exec_())

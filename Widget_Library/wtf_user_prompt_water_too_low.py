# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wtf_user_prompt_water_too_low.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wtf_user_prompt_water_too_low(object):
    def setupUi(self, wtf_user_prompt_water_too_low):
        wtf_user_prompt_water_too_low.setObjectName("wtf_user_prompt_water_too_low")
        wtf_user_prompt_water_too_low.resize(400, 157)
        wtf_user_prompt_water_too_low.setMinimumSize(QtCore.QSize(400, 157))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        wtf_user_prompt_water_too_low.setFont(font)
        self.layoutWidget = QtWidgets.QWidget(wtf_user_prompt_water_too_low)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 100, 371, 51))
        self.layoutWidget.setObjectName("layoutWidget")
        self.cont_abort_horz = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.cont_abort_horz.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.cont_abort_horz.setContentsMargins(0, 0, 0, 0)
        self.cont_abort_horz.setSpacing(13)
        self.cont_abort_horz.setObjectName("cont_abort_horz")
        self.fill_tank_button = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fill_tank_button.sizePolicy().hasHeightForWidth())
        self.fill_tank_button.setSizePolicy(sizePolicy)
        self.fill_tank_button.setMinimumSize(QtCore.QSize(200, 0))
        self.fill_tank_button.setMaximumSize(QtCore.QSize(70, 30))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.fill_tank_button.setFont(font)
        self.fill_tank_button.setObjectName("fill_tank_button")
        self.cont_abort_horz.addWidget(self.fill_tank_button)
        self.user_prompt_output = QtWidgets.QTextBrowser(wtf_user_prompt_water_too_low)
        self.user_prompt_output.setGeometry(QtCore.QRect(10, 10, 381, 71))
        self.user_prompt_output.setFrameShape(QtWidgets.QFrame.Panel)
        self.user_prompt_output.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.user_prompt_output.setLineWidth(2)
        self.user_prompt_output.setObjectName("user_prompt_output")

        self.retranslateUi(wtf_user_prompt_water_too_low)
        QtCore.QMetaObject.connectSlotsByName(wtf_user_prompt_water_too_low)

    def retranslateUi(self, wtf_user_prompt_water_too_low):
        _translate = QtCore.QCoreApplication.translate
        wtf_user_prompt_water_too_low.setWindowTitle(_translate("wtf_user_prompt_water_too_low", "Dialog"))
        self.fill_tank_button.setText(_translate("wtf_user_prompt_water_too_low", "FILL TANK"))
        self.user_prompt_output.setHtml(_translate("wtf_user_prompt_water_too_low",
                                                   "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                   "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                                   "p, li { white-space: pre-wrap; }\n"
                                                   "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600; font-style:normal;\">\n"
                                                   "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:400;\">Measurement tank water too low.</span></p>\n"
                                                   "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:400;\"><br /></p>\n"
                                                   "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:400;\">Please fill the measurement tank and click to continue.</span></p></body></html>"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    wtf_user_prompt_water_too_low = QtWidgets.QDialog()
    ui = Ui_wtf_user_prompt_water_too_low()
    ui.setupUi(wtf_user_prompt_water_too_low)
    wtf_user_prompt_water_too_low.show()
    sys.exit(app.exec_())

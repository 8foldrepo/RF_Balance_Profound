# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'user_info_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_user_info_dialog(object):
    def setupUi(self, user_info_dialog):
        user_info_dialog.setObjectName("user_info_dialog")
        user_info_dialog.resize(499, 280)
        self.user_prompt_output = QtWidgets.QTextBrowser(user_info_dialog)
        self.user_prompt_output.setGeometry(QtCore.QRect(10, 10, 481, 191))
        self.user_prompt_output.setFrameShape(QtWidgets.QFrame.Panel)
        self.user_prompt_output.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.user_prompt_output.setLineWidth(2)
        self.user_prompt_output.setObjectName("user_prompt_output")
        self.layoutWidget = QtWidgets.QWidget(user_info_dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(210, 220, 81, 41))
        self.layoutWidget.setObjectName("layoutWidget")
        self.buttons_horz = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.buttons_horz.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.buttons_horz.setContentsMargins(0, 0, 0, 0)
        self.buttons_horz.setSpacing(13)
        self.buttons_horz.setObjectName("buttons_horz")
        self.continue_button = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.continue_button.sizePolicy().hasHeightForWidth())
        self.continue_button.setSizePolicy(sizePolicy)
        self.continue_button.setMinimumSize(QtCore.QSize(70, 30))
        self.continue_button.setMaximumSize(QtCore.QSize(70, 30))
        self.continue_button.setObjectName("continue_button")
        self.buttons_horz.addWidget(self.continue_button)

        self.retranslateUi(user_info_dialog)
        QtCore.QMetaObject.connectSlotsByName(user_info_dialog)

    def retranslateUi(self, user_info_dialog):
        _translate = QtCore.QCoreApplication.translate
        user_info_dialog.setWindowTitle(_translate("user_info_dialog", "User Info Dialog"))
        self.continue_button.setText(_translate("user_info_dialog", "Continue"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    user_info_dialog = QtWidgets.QDialog()
    ui = Ui_user_info_dialog()
    ui.setupUi(user_info_dialog)
    user_info_dialog.show()
    sys.exit(app.exec_())
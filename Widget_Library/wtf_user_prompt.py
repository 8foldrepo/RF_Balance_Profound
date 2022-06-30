# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wtf_user_prompt.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_wtf_user_prompt(object):
    def setupUi(self, wtf_user_prompt):
        wtf_user_prompt.setObjectName("wtf_user_prompt")
        wtf_user_prompt.resize(501, 283)
        self.gridLayout = QtWidgets.QGridLayout(wtf_user_prompt)
        self.gridLayout.setObjectName("gridLayout")
        self.user_prompt_output = QtWidgets.QTextBrowser(wtf_user_prompt)
        self.user_prompt_output.setFrameShape(QtWidgets.QFrame.Panel)
        self.user_prompt_output.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.user_prompt_output.setLineWidth(2)
        self.user_prompt_output.setObjectName("user_prompt_output")
        self.gridLayout.addWidget(self.user_prompt_output, 0, 0, 1, 1)
        self.buttons_horz = QtWidgets.QHBoxLayout()
        self.buttons_horz.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.buttons_horz.setSpacing(13)
        self.buttons_horz.setObjectName("buttons_horz")
        self.widget = QtWidgets.QWidget(wtf_user_prompt)
        self.widget.setObjectName("widget")
        self.buttons_horz.addWidget(self.widget)
        self.abort_button = QtWidgets.QPushButton(wtf_user_prompt)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.abort_button.sizePolicy().hasHeightForWidth())
        self.abort_button.setSizePolicy(sizePolicy)
        self.abort_button.setMinimumSize(QtCore.QSize(70, 30))
        self.abort_button.setMaximumSize(QtCore.QSize(70, 30))
        self.abort_button.setAutoDefault(False)
        self.abort_button.setObjectName("abort_button")
        self.buttons_horz.addWidget(self.abort_button)
        self.retry_button = QtWidgets.QPushButton(wtf_user_prompt)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.retry_button.sizePolicy().hasHeightForWidth())
        self.retry_button.setSizePolicy(sizePolicy)
        self.retry_button.setMaximumSize(QtCore.QSize(70, 30))
        self.retry_button.setAutoDefault(False)
        self.retry_button.setObjectName("retry_button")
        self.buttons_horz.addWidget(self.retry_button)
        self.continue_button = QtWidgets.QPushButton(wtf_user_prompt)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.continue_button.sizePolicy().hasHeightForWidth())
        self.continue_button.setSizePolicy(sizePolicy)
        self.continue_button.setMinimumSize(QtCore.QSize(70, 30))
        self.continue_button.setMaximumSize(QtCore.QSize(70, 30))
        self.continue_button.setDefault(True)
        self.continue_button.setObjectName("continue_button")
        self.buttons_horz.addWidget(self.continue_button)
        self.gridLayout.addLayout(self.buttons_horz, 1, 0, 1, 1)

        self.retranslateUi(wtf_user_prompt)
        QtCore.QMetaObject.connectSlotsByName(wtf_user_prompt)

    def retranslateUi(self, wtf_user_prompt):
        _translate = QtCore.QCoreApplication.translate
        wtf_user_prompt.setWindowTitle(_translate("wtf_user_prompt", "WTF user prompt"))
        self.abort_button.setText(_translate("wtf_user_prompt", "Abort"))
        self.retry_button.setText(_translate("wtf_user_prompt", "Retry"))
        self.continue_button.setText(_translate("wtf_user_prompt", "Continue"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    wtf_user_prompt = QtWidgets.QDialog()
    ui = Ui_wtf_user_prompt()
    ui.setupUi(wtf_user_prompt)
    wtf_user_prompt.show()
    sys.exit(app.exec_())

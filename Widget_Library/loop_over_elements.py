# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loop_over_elements.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(440, 530)
        Form.setMinimumSize(QtCore.QSize(440, 530))
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 10, 431, 511))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.textEdit = QtWidgets.QTextEdit(self.frame)
        self.textEdit.setEnabled(False)
        self.textEdit.setGeometry(QtCore.QRect(200, 70, 221, 341))
        self.textEdit.setFrameShape(QtWidgets.QFrame.Box)
        self.textEdit.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textEdit.setLineWidth(2)
        self.textEdit.setObjectName("textEdit")
        self.layoutWidget = QtWidgets.QWidget(self.frame)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 151, 491))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.element_checkbox_1 = QtWidgets.QCheckBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.element_checkbox_1.sizePolicy().hasHeightForWidth())
        self.element_checkbox_1.setSizePolicy(sizePolicy)
        self.element_checkbox_1.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_1.setFont(font)
        self.element_checkbox_1.setChecked(False)
        self.element_checkbox_1.setObjectName("element_checkbox_1")
        self.verticalLayout.addWidget(self.element_checkbox_1)
        self.element_checkbox_2 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_2.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_2.setFont(font)
        self.element_checkbox_2.setObjectName("element_checkbox_2")
        self.verticalLayout.addWidget(self.element_checkbox_2)
        self.element_checkbox_3 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_3.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_3.setFont(font)
        self.element_checkbox_3.setObjectName("element_checkbox_3")
        self.verticalLayout.addWidget(self.element_checkbox_3)
        self.element_checkbox_4 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_4.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_4.setFont(font)
        self.element_checkbox_4.setObjectName("element_checkbox_4")
        self.verticalLayout.addWidget(self.element_checkbox_4)
        self.element_checkbox_5 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_5.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_5.setFont(font)
        self.element_checkbox_5.setObjectName("element_checkbox_5")
        self.verticalLayout.addWidget(self.element_checkbox_5)
        self.element_checkbox_6 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_6.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_6.setFont(font)
        self.element_checkbox_6.setObjectName("element_checkbox_6")
        self.verticalLayout.addWidget(self.element_checkbox_6)
        self.element_checkbox_7 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_7.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_7.setFont(font)
        self.element_checkbox_7.setObjectName("element_checkbox_7")
        self.verticalLayout.addWidget(self.element_checkbox_7)
        self.element_checkbox_8 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_8.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_8.setFont(font)
        self.element_checkbox_8.setObjectName("element_checkbox_8")
        self.verticalLayout.addWidget(self.element_checkbox_8)
        self.element_checkbox_9 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_9.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_9.setFont(font)
        self.element_checkbox_9.setObjectName("element_checkbox_9")
        self.verticalLayout.addWidget(self.element_checkbox_9)
        self.element_checkbox_10 = QtWidgets.QCheckBox(self.layoutWidget)
        self.element_checkbox_10.setSizeIncrement(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.element_checkbox_10.setFont(font)
        self.element_checkbox_10.setObjectName("element_checkbox_10")
        self.verticalLayout.addWidget(self.element_checkbox_10)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Loop over elements"))
        self.textEdit.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; text-decoration: underline;\">Note:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; font-weight:600; text-decoration: underline;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">If element 1 is </span><span style=\" font-size:14pt; font-weight:600; text-decoration: underline;\">NOT</span><span style=\" font-size:14pt;\"> selected, the initial search positions for each selected element will be based upon the default element 1 position. (Typically X = 0)</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">This may mean it takes the system longer to find the optimum position for each selected element.</span></p></body></html>"))
        self.element_checkbox_1.setText(_translate("Form", "Element 1"))
        self.element_checkbox_2.setText(_translate("Form", "Element 2"))
        self.element_checkbox_3.setText(_translate("Form", "Element 3"))
        self.element_checkbox_4.setText(_translate("Form", "Element 4"))
        self.element_checkbox_5.setText(_translate("Form", "Element 5"))
        self.element_checkbox_6.setText(_translate("Form", "Element 6"))
        self.element_checkbox_7.setText(_translate("Form", "Element 7"))
        self.element_checkbox_8.setText(_translate("Form", "Element 8"))
        self.element_checkbox_9.setText(_translate("Form", "Element 9"))
        self.element_checkbox_10.setText(_translate("Form", "Element 10"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
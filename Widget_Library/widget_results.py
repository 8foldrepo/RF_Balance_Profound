# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_results.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1039, 608)
        self.tabWidget_2 = QtWidgets.QTabWidget(Form)
        self.tabWidget_2.setGeometry(QtCore.QRect(10, 10, 1001, 581))
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.scriptlog_tab = QtWidgets.QWidget()
        self.scriptlog_tab.setObjectName("scriptlog_tab")
        self.tableView = QtWidgets.QTableView(self.scriptlog_tab)
        self.tableView.setGeometry(QtCore.QRect(10, 40, 971, 501))
        self.tableView.setObjectName("tableView")
        self.label_131 = QtWidgets.QLabel(self.scriptlog_tab)
        self.label_131.setGeometry(QtCore.QRect(10, 10, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_131.setFont(font)
        self.label_131.setObjectName("label_131")
        self.tabWidget_2.addTab(self.scriptlog_tab, "")
        self.tab_8 = QtWidgets.QWidget()
        self.tab_8.setObjectName("tab_8")
        self.results_table = QtWidgets.QTableView(self.tab_8)
        self.results_table.setGeometry(QtCore.QRect(9, 40, 991, 511))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.results_table.sizePolicy().hasHeightForWidth())
        self.results_table.setSizePolicy(sizePolicy)
        self.results_table.setMaximumSize(QtCore.QSize(1000, 1000))
        self.results_table.setObjectName("results_table")
        self.label_130 = QtWidgets.QLabel(self.tab_8)
        self.label_130.setGeometry(QtCore.QRect(10, 10, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_130.setFont(font)
        self.label_130.setObjectName("label_130")
        self.pushButton_2 = QtWidgets.QPushButton(self.tab_8)
        self.pushButton_2.setGeometry(QtCore.QRect(890, 560, 111, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.tabWidget_2.addTab(self.tab_8, "")

        self.retranslateUi(Form)
        self.tabWidget_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_131.setText(_translate("Form", "UA Script Log"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.scriptlog_tab), _translate("Form", "ScriptLog"))
        self.label_130.setText(_translate("Form", "UA Test Results"))
        self.pushButton_2.setText(_translate("Form", "Save Report"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_8), _translate("Form", "UA Results"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
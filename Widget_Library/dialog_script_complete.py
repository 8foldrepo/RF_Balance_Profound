# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_script_complete.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(700, 470)
        Dialog.setMinimumSize(QtCore.QSize(700, 470))
        Dialog.setMaximumSize(QtCore.QSize(700, 470))
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(30, 50, 631, 351))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(12)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.verticalHeader().setDefaultSectionSize(27)
        self.tableWidget.verticalHeader().setMinimumSectionSize(22)
        self.tableWidget.verticalHeader().setStretchLastSection(False)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 22, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.ok_button = QtWidgets.QPushButton(Dialog)
        self.ok_button.setGeometry(QtCore.QRect(540, 430, 75, 23))
        self.ok_button.setObjectName("ok_button")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(410, 30, 243, 13))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("Dialog", "Element 1"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("Dialog", "Element 2"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("Dialog", "Element 3"))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("Dialog", "Element 4"))
        item = self.tableWidget.verticalHeaderItem(4)
        item.setText(_translate("Dialog", "Element 5"))
        item = self.tableWidget.verticalHeaderItem(5)
        item.setText(_translate("Dialog", "Element 6"))
        item = self.tableWidget.verticalHeaderItem(6)
        item.setText(_translate("Dialog", "Element 7"))
        item = self.tableWidget.verticalHeaderItem(7)
        item.setText(_translate("Dialog", "Element 8"))
        item = self.tableWidget.verticalHeaderItem(8)
        item.setText(_translate("Dialog", "Element 9"))
        item = self.tableWidget.verticalHeaderItem(9)
        item.setText(_translate("Dialog", "Element 10"))
        item = self.tableWidget.verticalHeaderItem(11)
        item.setText(_translate("Dialog", "UA Write"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Result"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Description"))
        self.label.setText(_translate("Dialog", "Pass/Fail Summary"))
        self.ok_button.setText(_translate("Dialog", "OK"))
        self.label_2.setText(_translate("Dialog", "Check RFB, position, and results tab for more data"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

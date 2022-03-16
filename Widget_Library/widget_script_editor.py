# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_script_editor.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(792, 613)
        self.tabWidget_5 = QtWidgets.QTabWidget(Form)
        self.tabWidget_5.setGeometry(QtCore.QRect(110, 90, 661, 461))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tabWidget_5.setFont(font)
        self.tabWidget_5.setObjectName("tabWidget_5")
        self.tab_13 = QtWidgets.QWidget()
        self.tab_13.setObjectName("tab_13")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.tab_13)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.treeWidget = QtWidgets.QTreeWidget(self.tab_13)
        self.treeWidget.setObjectName("treeWidget")
        self.gridLayout_8.addWidget(self.treeWidget, 0, 0, 1, 1)
        self.tabWidget_5.addTab(self.tab_13, "")
        self.script_cmd_dropdown = QtWidgets.QComboBox(Form)
        self.script_cmd_dropdown.setGeometry(QtCore.QRect(20, 50, 221, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.script_cmd_dropdown.setFont(font)
        self.script_cmd_dropdown.setObjectName("script_cmd_dropdown")
        self.script_cmd_dropdown.addItem("")
        self.script_cmd_dropdown.addItem("")
        self.script_cmd_dropdown.addItem("")
        self.script_cmd_dropdown.addItem("")
        self.add_cmd_to_script_button = QtWidgets.QPushButton(Form)
        self.add_cmd_to_script_button.setGeometry(QtCore.QRect(250, 50, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.add_cmd_to_script_button.setFont(font)
        self.add_cmd_to_script_button.setObjectName("add_cmd_to_script_button")
        self.script_command_buttons = QtWidgets.QGroupBox(Form)
        self.script_command_buttons.setGeometry(QtCore.QRect(10, 150, 91, 351))
        self.script_command_buttons.setTitle("")
        self.script_command_buttons.setObjectName("script_command_buttons")
        self.delete_all_button = QtWidgets.QPushButton(self.script_command_buttons)
        self.delete_all_button.setGeometry(QtCore.QRect(10, 290, 75, 51))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.delete_all_button.setFont(font)
        self.delete_all_button.setObjectName("delete_all_button")
        self.move_cmd_up_button = QtWidgets.QPushButton(self.script_command_buttons)
        self.move_cmd_up_button.setGeometry(QtCore.QRect(10, 10, 75, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.move_cmd_up_button.setFont(font)
        self.move_cmd_up_button.setObjectName("move_cmd_up_button")
        self.delete_step_button = QtWidgets.QPushButton(self.script_command_buttons)
        self.delete_step_button.setGeometry(QtCore.QRect(10, 220, 75, 51))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.delete_step_button.setFont(font)
        self.delete_step_button.setObjectName("delete_step_button")
        self.collapse_btn = QtWidgets.QPushButton(self.script_command_buttons)
        self.collapse_btn.setGeometry(QtCore.QRect(10, 80, 75, 51))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.collapse_btn.setFont(font)
        self.collapse_btn.setObjectName("collapse_btn")
        self.move_cmd_down_button = QtWidgets.QPushButton(self.script_command_buttons)
        self.move_cmd_down_button.setGeometry(QtCore.QRect(10, 150, 75, 51))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.move_cmd_down_button.setFont(font)
        self.move_cmd_down_button.setObjectName("move_cmd_down_button")
        self.label_132 = QtWidgets.QLabel(Form)
        self.label_132.setGeometry(QtCore.QRect(20, 20, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_132.setFont(font)
        self.label_132.setObjectName("label_132")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(280, 560, 271, 61))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.update_tree_button = QtWidgets.QPushButton(self.groupBox)
        self.update_tree_button.setMinimumSize(QtCore.QSize(0, 40))
        self.update_tree_button.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.update_tree_button.setFont(font)
        self.update_tree_button.setObjectName("update_tree_button")
        self.horizontalLayout.addWidget(self.update_tree_button)
        self.save_script_button = QtWidgets.QPushButton(self.groupBox)
        self.save_script_button.setMinimumSize(QtCore.QSize(0, 40))
        self.save_script_button.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.save_script_button.setFont(font)
        self.save_script_button.setObjectName("save_script_button")
        self.horizontalLayout.addWidget(self.save_script_button)

        self.retranslateUi(Form)
        self.tabWidget_5.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.tabWidget_5.setTabText(self.tabWidget_5.indexOf(self.tab_13), _translate("Form", "Tab 1"))
        self.script_cmd_dropdown.setCurrentText(_translate("Form", "Measure element efficiency (RFB)"))
        self.script_cmd_dropdown.setItemText(0, _translate("Form", "Measure element efficiency (RFB)"))
        self.script_cmd_dropdown.setItemText(1, _translate("Form", "Pre-test initialisation"))
        self.script_cmd_dropdown.setItemText(2, _translate("Form", "Find element n"))
        self.script_cmd_dropdown.setItemText(3, _translate("Form", "Loop over elements"))
        self.add_cmd_to_script_button.setText(_translate("Form", "Add to Script"))
        self.delete_all_button.setText(_translate("Form", "Delete All"))
        self.move_cmd_up_button.setText(_translate("Form", "⬆️"))
        self.delete_step_button.setText(_translate("Form", "Delete Step"))
        self.collapse_btn.setText(_translate("Form", "Collapse"))
        self.move_cmd_down_button.setText(_translate("Form", "⬇️"))
        self.label_132.setText(_translate("Form", "Script Action"))
        self.update_tree_button.setText(_translate("Form", "UPDATE TREE"))
        self.save_script_button.setText(_translate("Form", "SAVE SCRIPT"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

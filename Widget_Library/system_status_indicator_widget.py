# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'system_status_indicator_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 551)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 40, 19, 13))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 130, 31, 13))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(10, 220, 29, 13))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(10, 310, 20, 13))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(10, 400, 28, 13))
        self.label_5.setObjectName("label_5")
        self.label_10 = QtWidgets.QLabel(Form)
        self.label_10.setGeometry(QtCore.QRect(530, 270, 117, 13))
        self.label_10.setObjectName("label_10")
        self.sounder_output_function_frame = QtWidgets.QFrame(Form)
        self.sounder_output_function_frame.setGeometry(QtCore.QRect(530, 290, 136, 142))
        self.sounder_output_function_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sounder_output_function_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.sounder_output_function_frame.setObjectName("sounder_output_function_frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.sounder_output_function_frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.ok_radio = QtWidgets.QRadioButton(self.sounder_output_function_frame)
        self.ok_radio.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.ok_radio.setObjectName("ok_radio")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.ok_radio)
        self.idle_warning_radio = QtWidgets.QRadioButton(self.sounder_output_function_frame)
        self.idle_warning_radio.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.idle_warning_radio.setObjectName("idle_warning_radio")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.idle_warning_radio)
        self.critical_radio = QtWidgets.QRadioButton(self.sounder_output_function_frame)
        self.critical_radio.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.critical_radio.setObjectName("critical_radio")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.critical_radio)
        self.verticalLayout_3.addLayout(self.formLayout)
        self.label_14 = QtWidgets.QLabel(self.sounder_output_function_frame)
        self.label_14.setObjectName("label_14")
        self.verticalLayout_3.addWidget(self.label_14)
        self.attention_required_only_radio = QtWidgets.QRadioButton(self.sounder_output_function_frame)
        self.attention_required_only_radio.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.attention_required_only_radio.setObjectName("attention_required_only_radio")
        self.verticalLayout_3.addWidget(self.attention_required_only_radio)
        self.gridLayout_2.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setGeometry(QtCore.QRect(20, 60, 441, 64))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_16 = QtWidgets.QLabel(self.frame_2)
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 0, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.frame_2)
        self.label_17.setObjectName("label_17")
        self.gridLayout.addWidget(self.label_17, 0, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.frame_2)
        self.pushButton.setStyleSheet("background:red")
        self.pushButton.setText("")
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_2.setStyleSheet("background:darkred")
        self.pushButton_2.setText("")
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_15 = QtWidgets.QLabel(self.frame_2)
        self.label_15.setObjectName("label_15")
        self.verticalLayout_9.addWidget(self.label_15)
        self.red_function = QtWidgets.QComboBox(self.frame_2)
        self.red_function.setObjectName("red_function")
        self.red_function.addItem("")
        self.red_function.addItem("")
        self.red_function.addItem("")
        self.red_function.addItem("")
        self.verticalLayout_9.addWidget(self.red_function)
        self.horizontalLayout.addLayout(self.verticalLayout_9)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.label_13 = QtWidgets.QLabel(self.frame_2)
        self.label_13.setObjectName("label_13")
        self.verticalLayout_10.addWidget(self.label_13)
        self.red_enable = QtWidgets.QCheckBox(self.frame_2)
        self.red_enable.setText("")
        self.red_enable.setObjectName("red_enable")
        self.verticalLayout_10.addWidget(self.red_enable)
        self.horizontalLayout.addLayout(self.verticalLayout_10)
        self.frame_3 = QtWidgets.QFrame(Form)
        self.frame_3.setGeometry(QtCore.QRect(20, 240, 441, 64))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_18 = QtWidgets.QLabel(self.frame_3)
        self.label_18.setObjectName("label_18")
        self.gridLayout_3.addWidget(self.label_18, 0, 0, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.frame_3)
        self.label_19.setObjectName("label_19")
        self.gridLayout_3.addWidget(self.label_19, 0, 1, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.frame_3)
        self.pushButton_3.setStyleSheet("background:lightgreen")
        self.pushButton_3.setText("")
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_3.addWidget(self.pushButton_3, 1, 0, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_3)
        self.pushButton_4.setStyleSheet("background:darkgreen")
        self.pushButton_4.setText("")
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_3.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout_3)
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_20 = QtWidgets.QLabel(self.frame_3)
        self.label_20.setObjectName("label_20")
        self.verticalLayout_11.addWidget(self.label_20)
        self.green_function = QtWidgets.QComboBox(self.frame_3)
        self.green_function.setObjectName("green_function")
        self.green_function.addItem("")
        self.green_function.addItem("")
        self.green_function.addItem("")
        self.green_function.addItem("")
        self.verticalLayout_11.addWidget(self.green_function)
        self.horizontalLayout_2.addLayout(self.verticalLayout_11)
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_21 = QtWidgets.QLabel(self.frame_3)
        self.label_21.setObjectName("label_21")
        self.verticalLayout_12.addWidget(self.label_21)
        self.green_enable = QtWidgets.QCheckBox(self.frame_3)
        self.green_enable.setText("")
        self.green_enable.setObjectName("green_enable")
        self.verticalLayout_12.addWidget(self.green_enable)
        self.horizontalLayout_2.addLayout(self.verticalLayout_12)
        self.frame_4 = QtWidgets.QFrame(Form)
        self.frame_4.setGeometry(QtCore.QRect(20, 330, 441, 64))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_22 = QtWidgets.QLabel(self.frame_4)
        self.label_22.setObjectName("label_22")
        self.gridLayout_4.addWidget(self.label_22, 0, 0, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.frame_4)
        self.label_23.setObjectName("label_23")
        self.gridLayout_4.addWidget(self.label_23, 0, 1, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_5.setStyleSheet("background:lightblue")
        self.pushButton_5.setText("")
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_4.addWidget(self.pushButton_5, 1, 0, 1, 1)
        self.pushButton_6 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_6.setStyleSheet("background:darkblue")
        self.pushButton_6.setText("")
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout_4.addWidget(self.pushButton_6, 1, 1, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_4)
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_24 = QtWidgets.QLabel(self.frame_4)
        self.label_24.setObjectName("label_24")
        self.verticalLayout_13.addWidget(self.label_24)
        self.blue_function = QtWidgets.QComboBox(self.frame_4)
        self.blue_function.setObjectName("blue_function")
        self.blue_function.addItem("")
        self.blue_function.addItem("")
        self.blue_function.addItem("")
        self.blue_function.addItem("")
        self.verticalLayout_13.addWidget(self.blue_function)
        self.horizontalLayout_3.addLayout(self.verticalLayout_13)
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_25 = QtWidgets.QLabel(self.frame_4)
        self.label_25.setObjectName("label_25")
        self.verticalLayout_14.addWidget(self.label_25)
        self.blue_enable = QtWidgets.QCheckBox(self.frame_4)
        self.blue_enable.setText("")
        self.blue_enable.setObjectName("blue_enable")
        self.verticalLayout_14.addWidget(self.blue_enable)
        self.horizontalLayout_3.addLayout(self.verticalLayout_14)
        self.frame_5 = QtWidgets.QFrame(Form)
        self.frame_5.setGeometry(QtCore.QRect(20, 420, 441, 64))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_26 = QtWidgets.QLabel(self.frame_5)
        self.label_26.setObjectName("label_26")
        self.gridLayout_5.addWidget(self.label_26, 0, 0, 1, 1)
        self.label_27 = QtWidgets.QLabel(self.frame_5)
        self.label_27.setObjectName("label_27")
        self.gridLayout_5.addWidget(self.label_27, 0, 1, 1, 1)
        self.pushButton_7 = QtWidgets.QPushButton(self.frame_5)
        self.pushButton_7.setStyleSheet("background:white")
        self.pushButton_7.setText("")
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout_5.addWidget(self.pushButton_7, 1, 0, 1, 1)
        self.pushButton_8 = QtWidgets.QPushButton(self.frame_5)
        self.pushButton_8.setStyleSheet("background:black")
        self.pushButton_8.setText("")
        self.pushButton_8.setObjectName("pushButton_8")
        self.gridLayout_5.addWidget(self.pushButton_8, 1, 1, 1, 1)
        self.horizontalLayout_4.addLayout(self.gridLayout_5)
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.label_28 = QtWidgets.QLabel(self.frame_5)
        self.label_28.setObjectName("label_28")
        self.verticalLayout_15.addWidget(self.label_28)
        self.white_function = QtWidgets.QComboBox(self.frame_5)
        self.white_function.setObjectName("white_function")
        self.white_function.addItem("")
        self.white_function.addItem("")
        self.white_function.addItem("")
        self.white_function.addItem("")
        self.verticalLayout_15.addWidget(self.white_function)
        self.horizontalLayout_4.addLayout(self.verticalLayout_15)
        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.label_29 = QtWidgets.QLabel(self.frame_5)
        self.label_29.setObjectName("label_29")
        self.verticalLayout_16.addWidget(self.label_29)
        self.white_enable = QtWidgets.QCheckBox(self.frame_5)
        self.white_enable.setText("")
        self.white_enable.setObjectName("white_enable")
        self.verticalLayout_16.addWidget(self.white_enable)
        self.horizontalLayout_4.addLayout(self.verticalLayout_16)
        self.frame_6 = QtWidgets.QFrame(Form)
        self.frame_6.setGeometry(QtCore.QRect(20, 150, 441, 64))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_30 = QtWidgets.QLabel(self.frame_6)
        self.label_30.setObjectName("label_30")
        self.gridLayout_6.addWidget(self.label_30, 0, 0, 1, 1)
        self.label_31 = QtWidgets.QLabel(self.frame_6)
        self.label_31.setObjectName("label_31")
        self.gridLayout_6.addWidget(self.label_31, 0, 1, 1, 1)
        self.pushButton_9 = QtWidgets.QPushButton(self.frame_6)
        self.pushButton_9.setStyleSheet("background:orange")
        self.pushButton_9.setText("")
        self.pushButton_9.setObjectName("pushButton_9")
        self.gridLayout_6.addWidget(self.pushButton_9, 1, 0, 1, 1)
        self.pushButton_10 = QtWidgets.QPushButton(self.frame_6)
        self.pushButton_10.setStyleSheet("background:rgb(91, 45, 0)")
        self.pushButton_10.setText("")
        self.pushButton_10.setObjectName("pushButton_10")
        self.gridLayout_6.addWidget(self.pushButton_10, 1, 1, 1, 1)
        self.horizontalLayout_5.addLayout(self.gridLayout_6)
        self.verticalLayout_18 = QtWidgets.QVBoxLayout()
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.label_32 = QtWidgets.QLabel(self.frame_6)
        self.label_32.setObjectName("label_32")
        self.verticalLayout_18.addWidget(self.label_32)
        self.amber_function = QtWidgets.QComboBox(self.frame_6)
        self.amber_function.setObjectName("amber_function")
        self.amber_function.addItem("")
        self.amber_function.addItem("")
        self.amber_function.addItem("")
        self.amber_function.addItem("")
        self.verticalLayout_18.addWidget(self.amber_function)
        self.horizontalLayout_5.addLayout(self.verticalLayout_18)
        self.verticalLayout_19 = QtWidgets.QVBoxLayout()
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.label_33 = QtWidgets.QLabel(self.frame_6)
        self.label_33.setObjectName("label_33")
        self.verticalLayout_19.addWidget(self.label_33)
        self.amber_enable = QtWidgets.QCheckBox(self.frame_6)
        self.amber_enable.setText("")
        self.amber_enable.setObjectName("amber_enable")
        self.verticalLayout_19.addWidget(self.amber_enable)
        self.horizontalLayout_5.addLayout(self.verticalLayout_19)
        self.label_34 = QtWidgets.QLabel(Form)
        self.label_34.setGeometry(QtCore.QRect(10, 10, 781, 20))
        self.label_34.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_34.setStyleSheet("background:rgb(0, 121, 214)")
        self.label_34.setObjectName("label_34")
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(530, 60, 151, 197))
        self.widget.setObjectName("widget")
        self.LIP_flash_func_sounder_plug_frame = QtWidgets.QVBoxLayout(self.widget)
        self.LIP_flash_func_sounder_plug_frame.setContentsMargins(0, 0, 0, 0)
        self.LIP_flash_func_sounder_plug_frame.setSpacing(22)
        self.LIP_flash_func_sounder_plug_frame.setObjectName("LIP_flash_func_sounder_plug_frame")
        self.light_hardware_plugin_vert = QtWidgets.QVBoxLayout()
        self.light_hardware_plugin_vert.setObjectName("light_hardware_plugin_vert")
        self.label_7 = QtWidgets.QLabel(self.widget)
        self.label_7.setMaximumSize(QtCore.QSize(16777215, 13))
        self.label_7.setObjectName("label_7")
        self.light_hardware_plugin_vert.addWidget(self.label_7)
        self.light_hardware_plugin_combo = QtWidgets.QComboBox(self.widget)
        self.light_hardware_plugin_combo.setObjectName("light_hardware_plugin_combo")
        self.light_hardware_plugin_combo.addItem("")
        self.light_hardware_plugin_vert.addWidget(self.light_hardware_plugin_combo)
        self.LIP_flash_func_sounder_plug_frame.addLayout(self.light_hardware_plugin_vert)
        self.flash_func_vert = QtWidgets.QVBoxLayout()
        self.flash_func_vert.setObjectName("flash_func_vert")
        self.label_8 = QtWidgets.QLabel(self.widget)
        self.label_8.setMaximumSize(QtCore.QSize(16777215, 13))
        self.label_8.setObjectName("label_8")
        self.flash_func_vert.addWidget(self.label_8)
        self.flashing_function_combo = QtWidgets.QComboBox(self.widget)
        self.flashing_function_combo.setObjectName("flashing_function_combo")
        self.flashing_function_combo.addItem("")
        self.flash_func_vert.addWidget(self.flashing_function_combo)
        self.LIP_flash_func_sounder_plug_frame.addLayout(self.flash_func_vert)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_9 = QtWidgets.QLabel(self.widget)
        self.label_9.setMaximumSize(QtCore.QSize(16777215, 13))
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.label_9)
        self.sounder_plugin_combo = QtWidgets.QComboBox(self.widget)
        self.sounder_plugin_combo.setObjectName("sounder_plugin_combo")
        self.sounder_plugin_combo.addItem("")
        self.verticalLayout.addWidget(self.sounder_plugin_combo)
        self.LIP_flash_func_sounder_plug_frame.addLayout(self.verticalLayout)
        self.widget1 = QtWidgets.QWidget(Form)
        self.widget1.setGeometry(QtCore.QRect(690, 60, 96, 114))
        self.widget1.setObjectName("widget1")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setSpacing(36)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_12 = QtWidgets.QLabel(self.widget1)
        self.label_12.setMaximumSize(QtCore.QSize(16777215, 13))
        self.label_12.setObjectName("label_12")
        self.verticalLayout_6.addWidget(self.label_12)
        self.show_ui_by_default_box = QtWidgets.QCheckBox(self.widget1)
        self.show_ui_by_default_box.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.show_ui_by_default_box.setText("")
        self.show_ui_by_default_box.setObjectName("show_ui_by_default_box")
        self.verticalLayout_6.addWidget(self.show_ui_by_default_box)
        self.verticalLayout_8.addLayout(self.verticalLayout_6)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_11 = QtWidgets.QLabel(self.widget1)
        self.label_11.setMaximumSize(QtCore.QSize(16777215, 13))
        self.label_11.setObjectName("label_11")
        self.verticalLayout_7.addWidget(self.label_11)
        self.flash_period_spin = QtWidgets.QSpinBox(self.widget1)
        self.flash_period_spin.setObjectName("flash_period_spin")
        self.verticalLayout_7.addWidget(self.flash_period_spin)
        self.verticalLayout_8.addLayout(self.verticalLayout_7)
        self.widget2 = QtWidgets.QWidget(Form)
        self.widget2.setGeometry(QtCore.QRect(10, 500, 231, 41))
        self.widget2.setObjectName("widget2")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(self.widget2)
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.label_6 = QtWidgets.QLabel(self.widget2)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_17.addWidget(self.label_6)
        self.action_combo = QtWidgets.QComboBox(self.widget2)
        self.action_combo.setObjectName("action_combo")
        self.action_combo.addItem("")
        self.verticalLayout_17.addWidget(self.action_combo)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Red"))
        self.label_2.setText(_translate("Form", "Amber"))
        self.label_3.setText(_translate("Form", "Green"))
        self.label_4.setText(_translate("Form", "Blue"))
        self.label_5.setText(_translate("Form", "White"))
        self.label_10.setText(_translate("Form", "Sounder output function"))
        self.ok_radio.setText(_translate("Form", "OK                       "))
        self.idle_warning_radio.setText(_translate("Form", "Idle/Warning       "))
        self.critical_radio.setText(_translate("Form", "Critical                 "))
        self.label_14.setText(_translate("Form", "         --- AND ---"))
        self.attention_required_only_radio.setText(_translate("Form", "Attention required\n"
"only"))
        self.label_16.setText(_translate("Form", "On color"))
        self.label_17.setText(_translate("Form", "Off color"))
        self.label_15.setText(_translate("Form", "Function"))
        self.red_function.setItemText(0, _translate("Form", "Critical issue"))
        self.red_function.setItemText(1, _translate("Form", "Idle/Warning"))
        self.red_function.setItemText(2, _translate("Form", "OK"))
        self.red_function.setItemText(3, _translate("Form", "S/W only"))
        self.label_13.setText(_translate("Form", "Enabled"))
        self.label_18.setText(_translate("Form", "On color"))
        self.label_19.setText(_translate("Form", "Off color"))
        self.label_20.setText(_translate("Form", "Function"))
        self.green_function.setItemText(0, _translate("Form", "Critical issue"))
        self.green_function.setItemText(1, _translate("Form", "Idle/Warning"))
        self.green_function.setItemText(2, _translate("Form", "OK"))
        self.green_function.setItemText(3, _translate("Form", "S/W only"))
        self.label_21.setText(_translate("Form", "Enabled"))
        self.label_22.setText(_translate("Form", "On color"))
        self.label_23.setText(_translate("Form", "Off color"))
        self.label_24.setText(_translate("Form", "Function"))
        self.blue_function.setItemText(0, _translate("Form", "Critical issue"))
        self.blue_function.setItemText(1, _translate("Form", "Idle/Warning"))
        self.blue_function.setItemText(2, _translate("Form", "OK"))
        self.blue_function.setItemText(3, _translate("Form", "S/W only"))
        self.label_25.setText(_translate("Form", "Enabled"))
        self.label_26.setText(_translate("Form", "On color"))
        self.label_27.setText(_translate("Form", "Off color"))
        self.label_28.setText(_translate("Form", "Function"))
        self.white_function.setItemText(0, _translate("Form", "Critical issue"))
        self.white_function.setItemText(1, _translate("Form", "Idle/Warning"))
        self.white_function.setItemText(2, _translate("Form", "OK"))
        self.white_function.setItemText(3, _translate("Form", "S/W only"))
        self.label_29.setText(_translate("Form", "Enabled"))
        self.label_30.setText(_translate("Form", "On color"))
        self.label_31.setText(_translate("Form", "Off color"))
        self.label_32.setText(_translate("Form", "Function"))
        self.amber_function.setItemText(0, _translate("Form", "Critical issue"))
        self.amber_function.setItemText(1, _translate("Form", "Idle/Warning"))
        self.amber_function.setItemText(2, _translate("Form", "OK"))
        self.amber_function.setItemText(3, _translate("Form", "S/W only"))
        self.label_33.setText(_translate("Form", "Enabled"))
        self.label_34.setText(_translate("Form", "<html><head/><body><p align=\"center\"><span style=\" font-size:11pt; font-weight:600; color:#ffffff;\">System status indicator</span></p></body></html>"))
        self.label_7.setText(_translate("Form", "Light hardware plugin"))
        self.light_hardware_plugin_combo.setItemText(0, _translate("Form", "Patlite"))
        self.label_8.setText(_translate("Form", "Flashing function"))
        self.flashing_function_combo.setItemText(0, _translate("Form", "Attention required"))
        self.label_9.setText(_translate("Form", "Sounder plugin"))
        self.sounder_plugin_combo.setItemText(0, _translate("Form", "Patlite"))
        self.label_12.setText(_translate("Form", "Show UI by default"))
        self.label_11.setText(_translate("Form", "Flash period (s)"))
        self.label_6.setText(_translate("Form", "Action (unconfigured)"))
        self.action_combo.setItemText(0, _translate("Form", "Ignore"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
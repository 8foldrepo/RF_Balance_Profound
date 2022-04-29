# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_system_config.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(650, 649)
        self.save_config_button = QtWidgets.QPushButton(Form)
        self.save_config_button.setGeometry(QtCore.QRect(260, 570, 201, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.save_config_button.setFont(font)
        self.save_config_button.setObjectName("save_config_button")
        self.gridFrame_8 = QtWidgets.QFrame(Form)
        self.gridFrame_8.setGeometry(QtCore.QRect(230, 10, 391, 91))
        self.gridFrame_8.setObjectName("gridFrame_8")
        self.gridLayout_20 = QtWidgets.QGridLayout(self.gridFrame_8)
        self.gridLayout_20.setObjectName("gridLayout_20")
        self.label_94 = QtWidgets.QLabel(self.gridFrame_8)
        self.label_94.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.label_94.setFont(font)
        self.label_94.setObjectName("label_94")
        self.gridLayout_20.addWidget(self.label_94, 0, 0, 1, 2)
        self.label_97 = QtWidgets.QLabel(self.gridFrame_8)
        self.label_97.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.label_97.setFont(font)
        self.label_97.setObjectName("label_97")
        self.gridLayout_20.addWidget(self.label_97, 2, 0, 1, 1)
        self.ua_results_directory = QtWidgets.QLineEdit(self.gridFrame_8)
        self.ua_results_directory.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.ua_results_directory.setFont(font)
        self.ua_results_directory.setObjectName("ua_results_directory")
        self.gridLayout_20.addWidget(self.ua_results_directory, 1, 0, 1, 1)
        self.ua_serial_numbers_path = QtWidgets.QLineEdit(self.gridFrame_8)
        self.ua_serial_numbers_path.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.ua_serial_numbers_path.setFont(font)
        self.ua_serial_numbers_path.setObjectName("ua_serial_numbers_path")
        self.gridLayout_20.addWidget(self.ua_serial_numbers_path, 3, 0, 1, 1)
        self.gridFrame_10 = QtWidgets.QFrame(Form)
        self.gridFrame_10.setGeometry(QtCore.QRect(220, 120, 211, 125))
        self.gridFrame_10.setObjectName("gridFrame_10")
        self.gridLayout_22 = QtWidgets.QGridLayout(self.gridFrame_10)
        self.gridLayout_22.setObjectName("gridLayout_22")
        self.interrupt_action = QtWidgets.QComboBox(self.gridFrame_10)
        self.interrupt_action.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.interrupt_action.setFont(font)
        self.interrupt_action.setObjectName("interrupt_action")
        self.interrupt_action.addItem("")
        self.interrupt_action.addItem("")
        self.gridLayout_22.addWidget(self.interrupt_action, 4, 1, 1, 1)
        self.label_99 = QtWidgets.QLabel(self.gridFrame_10)
        self.label_99.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_99.setFont(font)
        self.label_99.setObjectName("label_99")
        self.gridLayout_22.addWidget(self.label_99, 1, 0, 1, 1)
        self.label_101 = QtWidgets.QLabel(self.gridFrame_10)
        self.label_101.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_101.setFont(font)
        self.label_101.setObjectName("label_101")
        self.gridLayout_22.addWidget(self.label_101, 0, 0, 1, 2)
        self.label_100 = QtWidgets.QLabel(self.gridFrame_10)
        self.label_100.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_100.setFont(font)
        self.label_100.setObjectName("label_100")
        self.gridLayout_22.addWidget(self.label_100, 2, 0, 1, 1)
        self.retries = QtWidgets.QSpinBox(self.gridFrame_10)
        self.retries.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.retries.setFont(font)
        self.retries.setMinimum(-999999999)
        self.retries.setMaximum(999999999)
        self.retries.setProperty("value", 0)
        self.retries.setObjectName("retries")
        self.gridLayout_22.addWidget(self.retries, 1, 1, 1, 1)
        self.label_102 = QtWidgets.QLabel(self.gridFrame_10)
        self.label_102.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_102.setFont(font)
        self.label_102.setObjectName("label_102")
        self.gridLayout_22.addWidget(self.label_102, 4, 0, 1, 1)
        self.pass_fail_action = QtWidgets.QComboBox(self.gridFrame_10)
        self.pass_fail_action.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.pass_fail_action.setFont(font)
        self.pass_fail_action.setObjectName("pass_fail_action")
        self.pass_fail_action.addItem("")
        self.pass_fail_action.addItem("")
        self.gridLayout_22.addWidget(self.pass_fail_action, 2, 1, 1, 1)
        self.dialog_timeout = QtWidgets.QSpinBox(self.gridFrame_10)
        self.dialog_timeout.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.dialog_timeout.setFont(font)
        self.dialog_timeout.setMinimum(-999999999)
        self.dialog_timeout.setMaximum(999999999)
        self.dialog_timeout.setObjectName("dialog_timeout")
        self.gridLayout_22.addWidget(self.dialog_timeout, 5, 1, 1, 1)
        self.label_92 = QtWidgets.QLabel(self.gridFrame_10)
        self.label_92.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_92.setFont(font)
        self.label_92.setObjectName("label_92")
        self.gridLayout_22.addWidget(self.label_92, 5, 0, 1, 1)
        self.show_config_button = QtWidgets.QPushButton(Form)
        self.show_config_button.setGeometry(QtCore.QRect(10, 570, 201, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.show_config_button.setFont(font)
        self.show_config_button.setObjectName("show_config_button")
        self.gridFrame_6 = QtWidgets.QFrame(Form)
        self.gridFrame_6.setGeometry(QtCore.QRect(10, 160, 201, 122))
        self.gridFrame_6.setObjectName("gridFrame_6")
        self.gridLayout_18 = QtWidgets.QGridLayout(self.gridFrame_6)
        self.gridLayout_18.setObjectName("gridLayout_18")
        self.fill_mode = QtWidgets.QComboBox(self.gridFrame_6)
        self.fill_mode.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.fill_mode.setFont(font)
        self.fill_mode.setObjectName("fill_mode")
        self.fill_mode.addItem("")
        self.gridLayout_18.addWidget(self.fill_mode, 7, 1, 1, 1)
        self.label_78 = QtWidgets.QLabel(self.gridFrame_6)
        self.label_78.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_78.setFont(font)
        self.label_78.setObjectName("label_78")
        self.gridLayout_18.addWidget(self.label_78, 7, 0, 1, 1)
        self.label_81 = QtWidgets.QLabel(self.gridFrame_6)
        self.label_81.setText("")
        self.label_81.setObjectName("label_81")
        self.gridLayout_18.addWidget(self.label_81, 1, 0, 1, 1)
        self.water_timeout = QtWidgets.QSpinBox(self.gridFrame_6)
        self.water_timeout.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.water_timeout.setFont(font)
        self.water_timeout.setMinimum(-999999999)
        self.water_timeout.setMaximum(999999999)
        self.water_timeout.setProperty("value", 230)
        self.water_timeout.setObjectName("water_timeout")
        self.gridLayout_18.addWidget(self.water_timeout, 4, 1, 1, 1)
        self.daq_devicename = QtWidgets.QLineEdit(self.gridFrame_6)
        self.daq_devicename.setEnabled(True)
        self.daq_devicename.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.daq_devicename.setFont(font)
        self.daq_devicename.setObjectName("daq_devicename")
        self.gridLayout_18.addWidget(self.daq_devicename, 2, 1, 1, 1)
        self.label_76 = QtWidgets.QLabel(self.gridFrame_6)
        self.label_76.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_76.setFont(font)
        self.label_76.setObjectName("label_76")
        self.gridLayout_18.addWidget(self.label_76, 0, 0, 1, 2)
        self.label_75 = QtWidgets.QLabel(self.gridFrame_6)
        self.label_75.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_75.setFont(font)
        self.label_75.setObjectName("label_75")
        self.gridLayout_18.addWidget(self.label_75, 4, 0, 1, 1)
        self.label_77 = QtWidgets.QLabel(self.gridFrame_6)
        self.label_77.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_77.setFont(font)
        self.label_77.setObjectName("label_77")
        self.gridLayout_18.addWidget(self.label_77, 2, 0, 1, 1)
        self.gridFrame_9 = QtWidgets.QFrame(Form)
        self.gridFrame_9.setGeometry(QtCore.QRect(440, 120, 181, 91))
        self.gridFrame_9.setObjectName("gridFrame_9")
        self.gridLayout_21 = QtWidgets.QGridLayout(self.gridFrame_9)
        self.gridLayout_21.setObjectName("gridLayout_21")
        self.label_93 = QtWidgets.QLabel(self.gridFrame_9)
        self.label_93.setText("")
        self.label_93.setObjectName("label_93")
        self.gridLayout_21.addWidget(self.label_93, 1, 0, 1, 1)
        self.label_98 = QtWidgets.QLabel(self.gridFrame_9)
        self.label_98.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_98.setFont(font)
        self.label_98.setObjectName("label_98")
        self.gridLayout_21.addWidget(self.label_98, 2, 0, 1, 1)
        self.label_95 = QtWidgets.QLabel(self.gridFrame_9)
        self.label_95.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_95.setFont(font)
        self.label_95.setObjectName("label_95")
        self.gridLayout_21.addWidget(self.label_95, 0, 0, 1, 2)
        self.label_96 = QtWidgets.QLabel(self.gridFrame_9)
        self.label_96.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_96.setFont(font)
        self.label_96.setObjectName("label_96")
        self.gridLayout_21.addWidget(self.label_96, 4, 0, 1, 1)
        self.max_time_of_flight = QtWidgets.QDoubleSpinBox(self.gridFrame_9)
        self.max_time_of_flight.setMinimumSize(QtCore.QSize(0, 20))
        self.max_time_of_flight.setMaximumSize(QtCore.QSize(50, 40))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.max_time_of_flight.setFont(font)
        self.max_time_of_flight.setMinimum(-99999999999999.0)
        self.max_time_of_flight.setMaximum(9999999999999.0)
        self.max_time_of_flight.setObjectName("max_time_of_flight")
        self.gridLayout_21.addWidget(self.max_time_of_flight, 4, 1, 1, 1)
        self.min_time_of_flight = QtWidgets.QDoubleSpinBox(self.gridFrame_9)
        self.min_time_of_flight.setMinimumSize(QtCore.QSize(0, 20))
        self.min_time_of_flight.setMaximumSize(QtCore.QSize(50, 40))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.min_time_of_flight.setFont(font)
        self.min_time_of_flight.setMinimum(-99999999999999.0)
        self.min_time_of_flight.setMaximum(9999999999999.0)
        self.min_time_of_flight.setObjectName("min_time_of_flight")
        self.gridLayout_21.addWidget(self.min_time_of_flight, 2, 1, 1, 1)
        self.gridFrame_4 = QtWidgets.QFrame(Form)
        self.gridFrame_4.setGeometry(QtCore.QRect(10, 10, 201, 141))
        self.gridFrame_4.setObjectName("gridFrame_4")
        self.gridLayout_16 = QtWidgets.QGridLayout(self.gridFrame_4)
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.label_56 = QtWidgets.QLabel(self.gridFrame_4)
        self.label_56.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_56.setFont(font)
        self.label_56.setObjectName("label_56")
        self.gridLayout_16.addWidget(self.label_56, 3, 0, 1, 1)
        self.label_63 = QtWidgets.QLabel(self.gridFrame_4)
        self.label_63.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_63.setFont(font)
        self.label_63.setObjectName("label_63")
        self.gridLayout_16.addWidget(self.label_63, 0, 0, 1, 2)
        self.admin_pass_field = QtWidgets.QLineEdit(self.gridFrame_4)
        self.admin_pass_field.setEnabled(True)
        self.admin_pass_field.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.admin_pass_field.setFont(font)
        self.admin_pass_field.setObjectName("admin_pass_field")
        self.gridLayout_16.addWidget(self.admin_pass_field, 5, 1, 1, 1)
        self.label_57 = QtWidgets.QLabel(self.gridFrame_4)
        self.label_57.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_57.setFont(font)
        self.label_57.setObjectName("label_57")
        self.gridLayout_16.addWidget(self.label_57, 2, 0, 1, 1)
        self.label_60 = QtWidgets.QLabel(self.gridFrame_4)
        self.label_60.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_60.setFont(font)
        self.label_60.setObjectName("label_60")
        self.gridLayout_16.addWidget(self.label_60, 4, 0, 1, 1)
        self.label_61 = QtWidgets.QLabel(self.gridFrame_4)
        self.label_61.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_61.setFont(font)
        self.label_61.setObjectName("label_61")
        self.gridLayout_16.addWidget(self.label_61, 5, 0, 1, 1)
        self.label_62 = QtWidgets.QLabel(self.gridFrame_4)
        self.label_62.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_62.setFont(font)
        self.label_62.setObjectName("label_62")
        self.gridLayout_16.addWidget(self.label_62, 2, 1, 1, 1)
        self.engineer_pass_field = QtWidgets.QLineEdit(self.gridFrame_4)
        self.engineer_pass_field.setEnabled(True)
        self.engineer_pass_field.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.engineer_pass_field.setFont(font)
        self.engineer_pass_field.setObjectName("engineer_pass_field")
        self.gridLayout_16.addWidget(self.engineer_pass_field, 4, 1, 1, 1)
        self.operator_pass_field = QtWidgets.QLineEdit(self.gridFrame_4)
        self.operator_pass_field.setEnabled(True)
        self.operator_pass_field.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.operator_pass_field.setFont(font)
        self.operator_pass_field.setObjectName("operator_pass_field")
        self.gridLayout_16.addWidget(self.operator_pass_field, 3, 1, 1, 1)
        self.label_64 = QtWidgets.QLabel(self.gridFrame_4)
        self.label_64.setText("")
        self.label_64.setObjectName("label_64")
        self.gridLayout_16.addWidget(self.label_64, 1, 0, 1, 1)
        self.gridFrame_5 = QtWidgets.QFrame(Form)
        self.gridFrame_5.setGeometry(QtCore.QRect(10, 310, 201, 238))
        self.gridFrame_5.setObjectName("gridFrame_5")
        self.gridLayout_17 = QtWidgets.QGridLayout(self.gridFrame_5)
        self.gridLayout_17.setObjectName("gridLayout_17")
        self.label_65 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_65.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_65.setFont(font)
        self.label_65.setObjectName("label_65")
        self.gridLayout_17.addWidget(self.label_65, 5, 0, 1, 1)
        self.label_69 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_69.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_69.setFont(font)
        self.label_69.setObjectName("label_69")
        self.gridLayout_17.addWidget(self.label_69, 9, 0, 1, 1)
        self.label_68 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_68.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_68.setFont(font)
        self.label_68.setObjectName("label_68")
        self.gridLayout_17.addWidget(self.label_68, 7, 0, 1, 1)
        self.label_71 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_71.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_71.setText("")
        self.label_71.setObjectName("label_71")
        self.gridLayout_17.addWidget(self.label_71, 1, 0, 1, 1)
        self.label_70 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_70.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_70.setFont(font)
        self.label_70.setObjectName("label_70")
        self.gridLayout_17.addWidget(self.label_70, 10, 0, 1, 1)
        self.x_elementpitch = QtWidgets.QSpinBox(self.gridFrame_5)
        self.x_elementpitch.setMinimumSize(QtCore.QSize(0, 20))
        self.x_elementpitch.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.x_elementpitch.setFont(font)
        self.x_elementpitch.setMinimum(-999999999)
        self.x_elementpitch.setMaximum(999999999)
        self.x_elementpitch.setProperty("value", 5)
        self.x_elementpitch.setObjectName("x_elementpitch")
        self.gridLayout_17.addWidget(self.x_elementpitch, 10, 1, 1, 1)
        self.theta_prehomemove = QtWidgets.QSpinBox(self.gridFrame_5)
        self.theta_prehomemove.setMinimumSize(QtCore.QSize(0, 20))
        self.theta_prehomemove.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.theta_prehomemove.setFont(font)
        self.theta_prehomemove.setMinimum(-999999999)
        self.theta_prehomemove.setMaximum(999999999)
        self.theta_prehomemove.setProperty("value", 2)
        self.theta_prehomemove.setObjectName("theta_prehomemove")
        self.gridLayout_17.addWidget(self.theta_prehomemove, 11, 1, 1, 1)
        self.x_element1 = QtWidgets.QSpinBox(self.gridFrame_5)
        self.x_element1.setMinimumSize(QtCore.QSize(0, 20))
        self.x_element1.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.x_element1.setFont(font)
        self.x_element1.setMinimum(-999999999)
        self.x_element1.setMaximum(999999999)
        self.x_element1.setObjectName("x_element1")
        self.gridLayout_17.addWidget(self.x_element1, 9, 1, 1, 1)
        self.label_72 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_72.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_72.setFont(font)
        self.label_72.setObjectName("label_72")
        self.gridLayout_17.addWidget(self.label_72, 11, 0, 1, 1)
        self.label_67 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_67.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_67.setFont(font)
        self.label_67.setObjectName("label_67")
        self.gridLayout_17.addWidget(self.label_67, 3, 0, 1, 1)
        self.x_homecoord = QtWidgets.QSpinBox(self.gridFrame_5)
        self.x_homecoord.setMinimumSize(QtCore.QSize(0, 20))
        self.x_homecoord.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.x_homecoord.setFont(font)
        self.x_homecoord.setMinimum(-999999999)
        self.x_homecoord.setMaximum(999999999)
        self.x_homecoord.setProperty("value", 263)
        self.x_homecoord.setObjectName("x_homecoord")
        self.gridLayout_17.addWidget(self.x_homecoord, 3, 1, 1, 1)
        self.x_insertionpoint = QtWidgets.QSpinBox(self.gridFrame_5)
        self.x_insertionpoint.setMinimumSize(QtCore.QSize(0, 20))
        self.x_insertionpoint.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.x_insertionpoint.setFont(font)
        self.x_insertionpoint.setMinimum(-999999999)
        self.x_insertionpoint.setMaximum(999999999)
        self.x_insertionpoint.setProperty("value", 108)
        self.x_insertionpoint.setObjectName("x_insertionpoint")
        self.gridLayout_17.addWidget(self.x_insertionpoint, 7, 1, 1, 1)
        self.theta_homecoord = QtWidgets.QSpinBox(self.gridFrame_5)
        self.theta_homecoord.setMinimumSize(QtCore.QSize(0, 20))
        self.theta_homecoord.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.theta_homecoord.setFont(font)
        self.theta_homecoord.setMinimum(-999999999)
        self.theta_homecoord.setMaximum(999999999)
        self.theta_homecoord.setProperty("value", -90)
        self.theta_homecoord.setObjectName("theta_homecoord")
        self.gridLayout_17.addWidget(self.theta_homecoord, 5, 1, 1, 1)
        self.thetaloadenc = QtWidgets.QCheckBox(self.gridFrame_5)
        self.thetaloadenc.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.thetaloadenc.setFont(font)
        self.thetaloadenc.setText("")
        self.thetaloadenc.setObjectName("thetaloadenc")
        self.gridLayout_17.addWidget(self.thetaloadenc, 12, 1, 1, 1)
        self.label_66 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_66.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_66.setFont(font)
        self.label_66.setObjectName("label_66")
        self.gridLayout_17.addWidget(self.label_66, 0, 0, 1, 2)
        self.label_73 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_73.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_73.setFont(font)
        self.label_73.setObjectName("label_73")
        self.gridLayout_17.addWidget(self.label_73, 12, 0, 1, 1)
        self.label_74 = QtWidgets.QLabel(self.gridFrame_5)
        self.label_74.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_74.setFont(font)
        self.label_74.setObjectName("label_74")
        self.gridLayout_17.addWidget(self.label_74, 13, 0, 1, 1)
        self.centerhometheta = QtWidgets.QCheckBox(self.gridFrame_5)
        self.centerhometheta.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.centerhometheta.setFont(font)
        self.centerhometheta.setText("")
        self.centerhometheta.setChecked(True)
        self.centerhometheta.setObjectName("centerhometheta")
        self.gridLayout_17.addWidget(self.centerhometheta, 13, 1, 1, 1)
        self.gridFrame_7 = QtWidgets.QFrame(Form)
        self.gridFrame_7.setGeometry(QtCore.QRect(220, 260, 201, 301))
        self.gridFrame_7.setObjectName("gridFrame_7")
        self.gridLayout_19 = QtWidgets.QGridLayout(self.gridFrame_7)
        self.gridLayout_19.setObjectName("gridLayout_19")
        self.label_85 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_85.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_85.setFont(font)
        self.label_85.setObjectName("label_85")
        self.gridLayout_19.addWidget(self.label_85, 11, 0, 1, 1)
        self.lf_burstcount = QtWidgets.QSpinBox(self.gridFrame_7)
        self.lf_burstcount.setMinimumSize(QtCore.QSize(0, 20))
        self.lf_burstcount.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.lf_burstcount.setFont(font)
        self.lf_burstcount.setMinimum(-999999999)
        self.lf_burstcount.setMaximum(999999999)
        self.lf_burstcount.setObjectName("lf_burstcount")
        self.gridLayout_19.addWidget(self.lf_burstcount, 9, 1, 1, 1)
        self.label_86 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_86.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_86.setFont(font)
        self.label_86.setObjectName("label_86")
        self.gridLayout_19.addWidget(self.label_86, 3, 0, 1, 1)
        self.label_87 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_87.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_87.setFont(font)
        self.label_87.setObjectName("label_87")
        self.gridLayout_19.addWidget(self.label_87, 0, 0, 1, 2)
        self.label_89 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_89.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_89.setFont(font)
        self.label_89.setObjectName("label_89")
        self.gridLayout_19.addWidget(self.label_89, 13, 0, 1, 1)
        self.label_88 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_88.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_88.setFont(font)
        self.label_88.setObjectName("label_88")
        self.gridLayout_19.addWidget(self.label_88, 12, 0, 1, 1)
        self.label_91 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_91.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_91.setFont(font)
        self.label_91.setObjectName("label_91")
        self.gridLayout_19.addWidget(self.label_91, 16, 0, 1, 1)
        self.hf_burstcount = QtWidgets.QSpinBox(self.gridFrame_7)
        self.hf_burstcount.setMinimumSize(QtCore.QSize(0, 20))
        self.hf_burstcount.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.hf_burstcount.setFont(font)
        self.hf_burstcount.setMinimum(-999999999)
        self.hf_burstcount.setMaximum(999999999)
        self.hf_burstcount.setProperty("value", 2)
        self.hf_burstcount.setObjectName("hf_burstcount")
        self.gridLayout_19.addWidget(self.hf_burstcount, 14, 1, 1, 1)
        self.label_90 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_90.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_90.setFont(font)
        self.label_90.setObjectName("label_90")
        self.gridLayout_19.addWidget(self.label_90, 14, 0, 1, 1)
        self.label_79 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_79.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_79.setFont(font)
        self.label_79.setObjectName("label_79")
        self.gridLayout_19.addWidget(self.label_79, 5, 0, 1, 1)
        self.label_83 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_83.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_83.setText("")
        self.label_83.setObjectName("label_83")
        self.gridLayout_19.addWidget(self.label_83, 1, 0, 1, 1)
        self.label_82 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_82.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_82.setFont(font)
        self.label_82.setObjectName("label_82")
        self.gridLayout_19.addWidget(self.label_82, 7, 0, 1, 1)
        self.label_80 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_80.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_80.setFont(font)
        self.label_80.setObjectName("label_80")
        self.gridLayout_19.addWidget(self.label_80, 9, 0, 1, 1)
        self.label_84 = QtWidgets.QLabel(self.gridFrame_7)
        self.label_84.setMinimumSize(QtCore.QSize(0, 15))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label_84.setFont(font)
        self.label_84.setObjectName("label_84")
        self.gridLayout_19.addWidget(self.label_84, 15, 0, 1, 1)
        self.search_coarseincr = QtWidgets.QDoubleSpinBox(self.gridFrame_7)
        self.search_coarseincr.setMinimumSize(QtCore.QSize(0, 20))
        self.search_coarseincr.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.search_coarseincr.setFont(font)
        self.search_coarseincr.setSingleStep(0.1)
        self.search_coarseincr.setObjectName("search_coarseincr")
        self.gridLayout_19.addWidget(self.search_coarseincr, 15, 1, 1, 1)
        self.search_fineincr = QtWidgets.QDoubleSpinBox(self.gridFrame_7)
        self.search_fineincr.setMinimumSize(QtCore.QSize(0, 20))
        self.search_fineincr.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.search_fineincr.setFont(font)
        self.search_fineincr.setSingleStep(0.01)
        self.search_fineincr.setObjectName("search_fineincr")
        self.gridLayout_19.addWidget(self.search_fineincr, 16, 1, 1, 1)
        self.hf_highlimit = QtWidgets.QDoubleSpinBox(self.gridFrame_7)
        self.hf_highlimit.setMinimumSize(QtCore.QSize(0, 20))
        self.hf_highlimit.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.hf_highlimit.setFont(font)
        self.hf_highlimit.setMinimum(-9999999999.0)
        self.hf_highlimit.setMaximum(999999999.0)
        self.hf_highlimit.setObjectName("hf_highlimit")
        self.gridLayout_19.addWidget(self.hf_highlimit, 12, 1, 1, 1)
        self.hf_lowlimit = QtWidgets.QDoubleSpinBox(self.gridFrame_7)
        self.hf_lowlimit.setMinimumSize(QtCore.QSize(0, 20))
        self.hf_lowlimit.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.hf_lowlimit.setFont(font)
        self.hf_lowlimit.setMinimum(-9999999999.0)
        self.hf_lowlimit.setMaximum(999999999.0)
        self.hf_lowlimit.setObjectName("hf_lowlimit")
        self.gridLayout_19.addWidget(self.hf_lowlimit, 11, 1, 1, 1)
        self.hf_amplitude = QtWidgets.QDoubleSpinBox(self.gridFrame_7)
        self.hf_amplitude.setMinimumSize(QtCore.QSize(0, 20))
        self.hf_amplitude.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.hf_amplitude.setFont(font)
        self.hf_amplitude.setMinimum(-9999999999.0)
        self.hf_amplitude.setMaximum(999999999.0)
        self.hf_amplitude.setObjectName("hf_amplitude")
        self.gridLayout_19.addWidget(self.hf_amplitude, 13, 1, 1, 1)
        self.lf_lowlimit = QtWidgets.QDoubleSpinBox(self.gridFrame_7)
        self.lf_lowlimit.setMinimumSize(QtCore.QSize(0, 20))
        self.lf_lowlimit.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.lf_lowlimit.setFont(font)
        self.lf_lowlimit.setMinimum(-9999999999.0)
        self.lf_lowlimit.setMaximum(999999999.0)
        self.lf_lowlimit.setObjectName("lf_lowlimit")
        self.gridLayout_19.addWidget(self.lf_lowlimit, 3, 1, 1, 1)
        self.lf_highlimit = QtWidgets.QDoubleSpinBox(self.gridFrame_7)
        self.lf_highlimit.setMinimumSize(QtCore.QSize(0, 20))
        self.lf_highlimit.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.lf_highlimit.setFont(font)
        self.lf_highlimit.setMinimum(-9999999999.0)
        self.lf_highlimit.setMaximum(999999999.0)
        self.lf_highlimit.setObjectName("lf_highlimit")
        self.gridLayout_19.addWidget(self.lf_highlimit, 5, 1, 1, 1)
        self.lf_amplitude = QtWidgets.QDoubleSpinBox(self.gridFrame_7)
        self.lf_amplitude.setMinimumSize(QtCore.QSize(0, 20))
        self.lf_amplitude.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.lf_amplitude.setFont(font)
        self.lf_amplitude.setMinimum(-9999999999.0)
        self.lf_amplitude.setMaximum(999999999.0)
        self.lf_amplitude.setObjectName("lf_amplitude")
        self.gridLayout_19.addWidget(self.lf_amplitude, 7, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.save_config_button.setText(_translate("Form", "Save"))
        self.label_94.setText(_translate("Form", "UA results root directory"))
        self.label_97.setText(_translate("Form", "UA Serial numbers file"))
        self.ua_results_directory.setText(_translate("Form", "C:\\Users\\Isaiah\\OneDrive\\Documents\\UA results"))
        self.ua_serial_numbers_path.setText(
            _translate("Form", "C:\\Users\\Isaiah\\OneDrive\\Documents\\UA Serial Numbers\\Serial numbers.txt"))
        self.interrupt_action.setItemText(0, _translate("Form", "No dialog (abort)"))
        self.interrupt_action.setItemText(1, _translate("Form", "User prompt"))
        self.label_99.setText(_translate("Form", "Retries"))
        self.label_101.setText(_translate("Form", "Sequence Pass/fail"))
        self.label_100.setText(_translate("Form", "Pass fail action"))
        self.label_102.setText(_translate("Form", "Interrupt action"))
        self.pass_fail_action.setItemText(0, _translate("Form", "No dialog (abort)"))
        self.pass_fail_action.setItemText(1, _translate("Form", "User prompt"))
        self.label_92.setText(_translate("Form", "Dialog Timeout (s)"))
        self.show_config_button.setText(_translate("Form", "Show Configuration"))
        self.fill_mode.setItemText(0, _translate("Form", "Automatic"))
        self.label_78.setText(_translate("Form", "Fill/drain mode"))
        self.daq_devicename.setText(_translate("Form", "WTF3"))
        self.label_76.setText(_translate("Form", "WTF_DIO config"))
        self.label_75.setText(_translate("Form", "Water level timeout (s)"))
        self.label_77.setText(_translate("Form", "DAQ Device Name"))
        self.label_98.setText(_translate("Form", "Min time of flight (us)"))
        self.label_95.setText(_translate("Form", "Autoset timebase"))
        self.label_96.setText(_translate("Form", "Max time of flight (us)"))
        self.label_56.setText(_translate("Form", "Operator"))
        self.label_63.setText(_translate("Form", "User Accounts"))
        self.admin_pass_field.setText(_translate("Form", "PMI_Admin"))
        self.label_57.setText(_translate("Form", "Account"))
        self.label_60.setText(_translate("Form", "Engineer"))
        self.label_61.setText(_translate("Form", "Administrator"))
        self.label_62.setText(_translate("Form", "Password"))
        self.engineer_pass_field.setText(_translate("Form", "Engineer"))
        self.operator_pass_field.setText(_translate("Form", "Operator"))
        self.label_65.setText(_translate("Form", "Theta_HomeCoord"))
        self.label_69.setText(_translate("Form", "X-Element1"))
        self.label_68.setText(_translate("Form", "X-TankInsertionPoint"))
        self.label_70.setText(_translate("Form", "X-Element pitch (mm)"))
        self.label_72.setText(_translate("Form", "ThetaPreHomeMove"))
        self.label_67.setText(_translate("Form", "XHomeCoord"))
        self.label_66.setText(_translate("Form", "WTF_PositionParameters"))
        self.label_73.setText(_translate("Form", "ThetaLoadEnc?"))
        self.label_74.setText(_translate("Form", "CentreHomeTheta?"))
        self.label_85.setText(_translate("Form", "HF.LowFreqLimit(MHz)"))
        self.label_86.setText(_translate("Form", "LF.LowFreqLimit(MHz)"))
        self.label_87.setText(_translate("Form", "FrequencyParameters"))
        self.label_89.setText(_translate("Form", "HF.Amplitude(mVpp)"))
        self.label_88.setText(_translate("Form", "HF.HighFreqLimit(MHz)"))
        self.label_91.setText(_translate("Form", "Search.FineIncr(MHz)"))
        self.label_90.setText(_translate("Form", "HF.BurstCount"))
        self.label_79.setText(_translate("Form", "LF.HighFreqLimit(MHz)"))
        self.label_82.setText(_translate("Form", "LF.Amplitude(mVpp)"))
        self.label_80.setText(_translate("Form", "LF.BurstCount"))
        self.label_84.setText(_translate("Form", "Search.CoarseIncr"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

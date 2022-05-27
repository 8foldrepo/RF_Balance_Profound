# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_position.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(834, 626)
        self.tabWidget_3 = QtWidgets.QTabWidget(Form)
        self.tabWidget_3.setGeometry(QtCore.QRect(4, 4, 821, 621))
        self.tabWidget_3.setToolTip("")
        self.tabWidget_3.setObjectName("tabWidget_3")
        self.config_tab = QtWidgets.QWidget()
        self.config_tab.setToolTip("")
        self.config_tab.setObjectName("config_tab")
        self.label_31 = QtWidgets.QLabel(self.config_tab)
        self.label_31.setGeometry(QtCore.QRect(0, 0, 820, 20))
        self.label_31.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_31.setObjectName("label_31")
        self.set_button = QtWidgets.QPushButton(self.config_tab)
        self.set_button.setEnabled(False)
        self.set_button.setGeometry(QtCore.QRect(10, 390, 75, 40))
        self.set_button.setMinimumSize(QtCore.QSize(0, 40))
        self.set_button.setMaximumSize(QtCore.QSize(150, 16777215))
        self.set_button.setObjectName("set_button")
        self.widget_3 = QtWidgets.QWidget(self.config_tab)
        self.widget_3.setGeometry(QtCore.QRect(9, 29, 481, 351))
        self.widget_3.setStyleSheet("background-color: rgb(220, 242, 255)")
        self.widget_3.setObjectName("widget_3")
        self.gridLayoutWidget = QtWidgets.QWidget(self.widget_3)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 171, 41))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_11.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.label_32 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_32.setObjectName("label_32")
        self.gridLayout_11.addWidget(self.label_32, 0, 0, 1, 1)
        self.visa_resource_field = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.visa_resource_field.setEnabled(False)
        self.visa_resource_field.setObjectName("visa_resource_field")
        self.gridLayout_11.addWidget(self.visa_resource_field, 1, 0, 1, 1)
        self.gridFrame_2 = QtWidgets.QFrame(self.widget_3)
        self.gridFrame_2.setEnabled(False)
        self.gridFrame_2.setGeometry(QtCore.QRect(10, 95, 281, 231))
        self.gridFrame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.gridFrame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.gridFrame_2.setObjectName("gridFrame_2")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.gridFrame_2)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.label_35 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_35.setObjectName("label_35")
        self.gridLayout_12.addWidget(self.label_35, 2, 0, 1, 1)
        self.label_36 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_36.setObjectName("label_36")
        self.gridLayout_12.addWidget(self.label_36, 3, 0, 1, 1)
        self.theta_rotation_indicator = Switch(self.gridFrame_2)
        self.theta_rotation_indicator.setEnabled(False)
        self.theta_rotation_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.theta_rotation_indicator.setStyleSheet("background-color: white")
        self.theta_rotation_indicator.setObjectName("theta_rotation_indicator")
        self.gridLayout_12.addWidget(self.theta_rotation_indicator, 3, 1, 1, 1)
        self.trans_2_indicator = Switch(self.gridFrame_2)
        self.trans_2_indicator.setEnabled(False)
        self.trans_2_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.trans_2_indicator.setStyleSheet("background-color: white")
        self.trans_2_indicator.setObjectName("trans_2_indicator")
        self.gridLayout_12.addWidget(self.trans_2_indicator, 4, 1, 1, 1)
        self.vert_2_indicator = Switch(self.gridFrame_2)
        self.vert_2_indicator.setEnabled(False)
        self.vert_2_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.vert_2_indicator.setStyleSheet("background-color: white")
        self.vert_2_indicator.setObjectName("vert_2_indicator")
        self.gridLayout_12.addWidget(self.vert_2_indicator, 5, 1, 1, 1)
        self.long_1_indicator = Switch(self.gridFrame_2)
        self.long_1_indicator.setEnabled(False)
        self.long_1_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.long_1_indicator.setStyleSheet("background-color: white")
        self.long_1_indicator.setObjectName("long_1_indicator")
        self.gridLayout_12.addWidget(self.long_1_indicator, 2, 1, 1, 1)
        self.label_33 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_33.setObjectName("label_33")
        self.gridLayout_12.addWidget(self.label_33, 1, 0, 1, 1)
        self.label_34 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_34.setObjectName("label_34")
        self.gridLayout_12.addWidget(self.label_34, 0, 0, 1, 1)
        self.long_2_indicator = Switch(self.gridFrame_2)
        self.long_2_indicator.setEnabled(False)
        self.long_2_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.long_2_indicator.setStyleSheet("background-color: white")
        self.long_2_indicator.setObjectName("long_2_indicator")
        self.gridLayout_12.addWidget(self.long_2_indicator, 6, 1, 1, 1)
        self.vert_1_indicator = Switch(self.gridFrame_2)
        self.vert_1_indicator.setEnabled(False)
        self.vert_1_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.vert_1_indicator.setStyleSheet("background-color: white")
        self.vert_1_indicator.setObjectName("vert_1_indicator")
        self.gridLayout_12.addWidget(self.vert_1_indicator, 1, 1, 1, 1)
        self.trans_1_indicator = Switch(self.gridFrame_2)
        self.trans_1_indicator.setEnabled(False)
        self.trans_1_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.trans_1_indicator.setStyleSheet("background-color: white")
        self.trans_1_indicator.setObjectName("trans_1_indicator")
        self.gridLayout_12.addWidget(self.trans_1_indicator, 0, 1, 1, 1)
        self.theta_2_indicator = Switch(self.gridFrame_2)
        self.theta_2_indicator.setEnabled(False)
        self.theta_2_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.theta_2_indicator.setStyleSheet("background-color: white")
        self.theta_2_indicator.setObjectName("theta_2_indicator")
        self.gridLayout_12.addWidget(self.theta_2_indicator, 7, 1, 1, 1)
        self.label_37 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_37.setObjectName("label_37")
        self.gridLayout_12.addWidget(self.label_37, 4, 0, 1, 1)
        self.label_38 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_38.setObjectName("label_38")
        self.gridLayout_12.addWidget(self.label_38, 7, 0, 1, 1)
        self.label_39 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_39.setObjectName("label_39")
        self.gridLayout_12.addWidget(self.label_39, 5, 0, 1, 1)
        self.label_40 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_40.setObjectName("label_40")
        self.gridLayout_12.addWidget(self.label_40, 6, 0, 1, 1)
        self.checkBox_4 = QtWidgets.QCheckBox(self.gridFrame_2)
        self.checkBox_4.setEnabled(False)
        self.checkBox_4.setMaximumSize(QtCore.QSize(20, 20))
        self.checkBox_4.setText("")
        self.checkBox_4.setObjectName("checkBox_4")
        self.gridLayout_12.addWidget(self.checkBox_4, 4, 3, 1, 1)
        self.checkBox_5 = QtWidgets.QCheckBox(self.gridFrame_2)
        self.checkBox_5.setEnabled(False)
        self.checkBox_5.setMaximumSize(QtCore.QSize(20, 20))
        self.checkBox_5.setText("")
        self.checkBox_5.setObjectName("checkBox_5")
        self.gridLayout_12.addWidget(self.checkBox_5, 5, 3, 1, 1)
        self.checkBox_6 = QtWidgets.QCheckBox(self.gridFrame_2)
        self.checkBox_6.setEnabled(False)
        self.checkBox_6.setMaximumSize(QtCore.QSize(20, 20))
        self.checkBox_6.setText("")
        self.checkBox_6.setObjectName("checkBox_6")
        self.gridLayout_12.addWidget(self.checkBox_6, 6, 3, 1, 1)
        self.checkBox_7 = QtWidgets.QCheckBox(self.gridFrame_2)
        self.checkBox_7.setEnabled(False)
        self.checkBox_7.setMaximumSize(QtCore.QSize(20, 20))
        self.checkBox_7.setText("")
        self.checkBox_7.setObjectName("checkBox_7")
        self.gridLayout_12.addWidget(self.checkBox_7, 7, 3, 1, 1)
        self.checkBox_9 = QtWidgets.QCheckBox(self.gridFrame_2)
        self.checkBox_9.setEnabled(False)
        self.checkBox_9.setMaximumSize(QtCore.QSize(20, 20))
        self.checkBox_9.setText("")
        self.checkBox_9.setObjectName("checkBox_9")
        self.gridLayout_12.addWidget(self.checkBox_9, 2, 3, 1, 1)
        self.z_vert_indicator = Switch(self.gridFrame_2)
        self.z_vert_indicator.setEnabled(False)
        self.z_vert_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.z_vert_indicator.setStyleSheet("background-color: white")
        self.z_vert_indicator.setObjectName("z_vert_indicator")
        self.gridLayout_12.addWidget(self.z_vert_indicator, 1, 2, 1, 1)
        self.label_41 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_41.setObjectName("label_41")
        self.gridLayout_12.addWidget(self.label_41, 0, 2, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.gridFrame_2)
        self.checkBox.setEnabled(False)
        self.checkBox.setMaximumSize(QtCore.QSize(20, 20))
        self.checkBox.setText("")
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_12.addWidget(self.checkBox, 0, 3, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.gridFrame_2)
        self.checkBox_2.setEnabled(False)
        self.checkBox_2.setMaximumSize(QtCore.QSize(20, 20))
        self.checkBox_2.setText("")
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout_12.addWidget(self.checkBox_2, 1, 3, 1, 1)
        self.checkBox_3 = QtWidgets.QCheckBox(self.gridFrame_2)
        self.checkBox_3.setEnabled(False)
        self.checkBox_3.setMaximumSize(QtCore.QSize(20, 20))
        self.checkBox_3.setText("")
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout_12.addWidget(self.checkBox_3, 3, 3, 1, 1)
        self.label_42 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_42.setObjectName("label_42")
        self.gridLayout_12.addWidget(self.label_42, 7, 4, 1, 1)
        self.axis_spinbox = QtWidgets.QSpinBox(self.widget_3)
        self.axis_spinbox.setGeometry(QtCore.QRect(260, 30, 42, 22))
        self.axis_spinbox.setStyleSheet("background-color: white")
        self.axis_spinbox.setMinimum(1)
        self.axis_spinbox.setMaximum(2)
        self.axis_spinbox.setObjectName("axis_spinbox")
        self.label_43 = QtWidgets.QLabel(self.widget_3)
        self.label_43.setGeometry(QtCore.QRect(260, 10, 111, 20))
        self.label_43.setObjectName("label_43")
        self.frame = QtWidgets.QFrame(self.widget_3)
        self.frame.setGeometry(QtCore.QRect(300, 30, 161, 291))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.formLayout_2 = QtWidgets.QFormLayout(self.frame)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_46 = QtWidgets.QLabel(self.frame)
        self.label_46.setObjectName("label_46")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_46)
        self.label_47 = QtWidgets.QLabel(self.frame)
        self.label_47.setObjectName("label_47")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_47)
        self.label_48 = QtWidgets.QLabel(self.frame)
        self.label_48.setObjectName("label_48")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_48)
        self.label_49 = QtWidgets.QLabel(self.frame)
        self.label_49.setObjectName("label_49")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_49)
        self.encoded_indicator = Switch(self.frame)
        self.encoded_indicator.setEnabled(False)
        self.encoded_indicator.setMaximumSize(QtCore.QSize(40, 15))
        self.encoded_indicator.setStyleSheet("background-color: white")
        self.encoded_indicator.setObjectName("encoded_indicator")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.encoded_indicator)
        self.type_combobox = QtWidgets.QComboBox(self.frame)
        self.type_combobox.setStyleSheet("background-color: white")
        self.type_combobox.setObjectName("type_combobox")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.type_combobox)
        self.gearing_double_spinbox = QtWidgets.QDoubleSpinBox(self.frame)
        self.gearing_double_spinbox.setObjectName("gearing_double_spinbox")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.gearing_double_spinbox)
        self.steps_mm_doublespinbox = QtWidgets.QDoubleSpinBox(self.frame)
        self.steps_mm_doublespinbox.setObjectName("steps_mm_doublespinbox")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.steps_mm_doublespinbox)
        self.label_44 = QtWidgets.QLabel(self.widget_3)
        self.label_44.setGeometry(QtCore.QRect(10, 70, 111, 20))
        self.label_44.setObjectName("label_44")
        self.label_45 = QtWidgets.QLabel(self.widget_3)
        self.label_45.setGeometry(QtCore.QRect(180, 70, 81, 20))
        self.label_45.setObjectName("label_45")
        self.tabWidget_3.addTab(self.config_tab, "")
        self.tab_11 = QtWidgets.QWidget()
        self.tab_11.setObjectName("tab_11")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.tab_11)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 300, 426, 161))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_14.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.x_pos_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.x_pos_button.setObjectName("x_pos_button")
        self.gridLayout_14.addWidget(self.x_pos_button, 0, 1, 1, 1)
        self.x_neg_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.x_neg_button.setObjectName("x_neg_button")
        self.gridLayout_14.addWidget(self.x_neg_button, 0, 0, 1, 1)
        self.go_element_combo = QtWidgets.QComboBox(self.gridLayoutWidget_3)
        self.go_element_combo.setObjectName("go_element_combo")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.go_element_combo.addItem("")
        self.gridLayout_14.addWidget(self.go_element_combo, 3, 3, 1, 1)
        self.insert_ua_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.insert_ua_button.setObjectName("insert_ua_button")
        self.gridLayout_14.addWidget(self.insert_ua_button, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_14.addItem(spacerItem, 0, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_14.addItem(spacerItem1, 2, 0, 1, 1)
        self.theta_neg_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.theta_neg_button.setObjectName("theta_neg_button")
        self.gridLayout_14.addWidget(self.theta_neg_button, 1, 0, 1, 1)
        self.retract_ua_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.retract_ua_button.setObjectName("retract_ua_button")
        self.gridLayout_14.addWidget(self.retract_ua_button, 3, 1, 1, 1)
        self.go_x_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.go_x_button.setObjectName("go_x_button")
        self.gridLayout_14.addWidget(self.go_x_button, 0, 4, 1, 1)
        self.theta_pos_lineedit = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.theta_pos_lineedit.setEnabled(False)
        self.theta_pos_lineedit.setMaximumSize(QtCore.QSize(60, 16777215))
        self.theta_pos_lineedit.setObjectName("theta_pos_lineedit")
        self.gridLayout_14.addWidget(self.theta_pos_lineedit, 1, 3, 1, 1)
        self.x_pos_lineedit = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.x_pos_lineedit.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.x_pos_lineedit.sizePolicy().hasHeightForWidth())
        self.x_pos_lineedit.setSizePolicy(sizePolicy)
        self.x_pos_lineedit.setMaximumSize(QtCore.QSize(60, 16777215))
        self.x_pos_lineedit.setObjectName("x_pos_lineedit")
        self.gridLayout_14.addWidget(self.x_pos_lineedit, 0, 3, 1, 1)
        self.theta_pos_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.theta_pos_button.setObjectName("theta_pos_button")
        self.gridLayout_14.addWidget(self.theta_pos_button, 1, 1, 1, 1)
        self.go_theta_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.go_theta_button.sizePolicy().hasHeightForWidth())
        self.go_theta_button.setSizePolicy(sizePolicy)
        self.go_theta_button.setMinimumSize(QtCore.QSize(80, 0))
        self.go_theta_button.setObjectName("go_theta_button")
        self.gridLayout_14.addWidget(self.go_theta_button, 1, 4, 1, 1)
        self.go_element_button = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.go_element_button.setObjectName("go_element_button")
        self.gridLayout_14.addWidget(self.go_element_button, 3, 4, 1, 1)
        self.go_x_sb = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.go_x_sb.setMinimum(-999999999.0)
        self.go_x_sb.setMaximum(9999999999.0)
        self.go_x_sb.setObjectName("go_x_sb")
        self.gridLayout_14.addWidget(self.go_x_sb, 0, 5, 1, 1)
        self.go_theta_sb = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget_3)
        self.go_theta_sb.setMinimum(-999999999.0)
        self.go_theta_sb.setMaximum(9999999999.0)
        self.go_theta_sb.setObjectName("go_theta_sb")
        self.gridLayout_14.addWidget(self.go_theta_sb, 1, 5, 1, 1)
        self.reset_zero_button = QtWidgets.QPushButton(self.tab_11)
        self.reset_zero_button.setGeometry(QtCore.QRect(10, 510, 101, 41))
        self.reset_zero_button.setObjectName("reset_zero_button")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.tab_11)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(480, 320, 81, 129))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_53 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_53.setObjectName("label_53")
        self.verticalLayout_5.addWidget(self.label_53)
        self.frame_2 = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.frame_2.setStyleSheet("background-color: rgb(220, 242, 255)")
        self.frame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.formLayout_3 = QtWidgets.QFormLayout(self.frame_2)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_52 = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_52.sizePolicy().hasHeightForWidth())
        self.label_52.setSizePolicy(sizePolicy)
        self.label_52.setMaximumSize(QtCore.QSize(110231, 16777215))
        self.label_52.setObjectName("label_52")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_52)
        self.label_58 = QtWidgets.QLabel(self.frame_2)
        self.label_58.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_58.setObjectName("label_58")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_58)
        self.label_59 = QtWidgets.QLabel(self.frame_2)
        self.label_59.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_59.setObjectName("label_59")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_59)
        self.x_home_radio = QtWidgets.QRadioButton(self.frame_2)
        self.x_home_radio.setMaximumSize(QtCore.QSize(20, 20))
        self.x_home_radio.setText("")
        self.x_home_radio.setObjectName("x_home_radio")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.x_home_radio)
        self.all_axes_radio = QtWidgets.QRadioButton(self.frame_2)
        self.all_axes_radio.setMaximumSize(QtCore.QSize(20, 20))
        self.all_axes_radio.setText("")
        self.all_axes_radio.setChecked(True)
        self.all_axes_radio.setObjectName("all_axes_radio")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.all_axes_radio)
        self.theta_home_radio = QtWidgets.QRadioButton(self.frame_2)
        self.theta_home_radio.setMaximumSize(QtCore.QSize(20, 20))
        self.theta_home_radio.setText("")
        self.theta_home_radio.setObjectName("theta_home_radio")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.theta_home_radio)
        self.verticalLayout_5.addWidget(self.frame_2)
        self.manual_home_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.manual_home_button.setObjectName("manual_home_button")
        self.verticalLayout_5.addWidget(self.manual_home_button)
        self.stop_button = QtWidgets.QPushButton(self.tab_11)
        self.stop_button.setGeometry(QtCore.QRect(660, 390, 101, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.stop_button.setFont(font)
        self.stop_button.setStyleSheet("background-color: red")
        self.stop_button.setObjectName("stop_button")
        self.formFrame = QtWidgets.QFrame(self.tab_11)
        self.formFrame.setGeometry(QtCore.QRect(10, 50, 561, 231))
        self.formFrame.setObjectName("formFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.formFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.ang_inc_double_sb = QtWidgets.QSpinBox(self.formFrame)
        self.ang_inc_double_sb.setMinimum(-2147483647)
        self.ang_inc_double_sb.setMaximum(1231231231)
        self.ang_inc_double_sb.setProperty("value", 99)
        self.ang_inc_double_sb.setObjectName("ang_inc_double_sb")
        self.gridLayout.addWidget(self.ang_inc_double_sb, 2, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.formFrame)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.save_settings_button = QtWidgets.QPushButton(self.formFrame)
        self.save_settings_button.setObjectName("save_settings_button")
        self.gridLayout.addWidget(self.save_settings_button, 7, 0, 1, 4)
        self.steps_per_degree_sb = QtWidgets.QDoubleSpinBox(self.formFrame)
        self.steps_per_degree_sb.setMaximum(10000000000.0)
        self.steps_per_degree_sb.setObjectName("steps_per_degree_sb")
        self.gridLayout.addWidget(self.steps_per_degree_sb, 1, 3, 1, 1)
        self.steps_per_mm_sb = QtWidgets.QDoubleSpinBox(self.formFrame)
        self.steps_per_mm_sb.setMaximum(10000000000.0)
        self.steps_per_mm_sb.setObjectName("steps_per_mm_sb")
        self.gridLayout.addWidget(self.steps_per_mm_sb, 1, 1, 1, 1)
        self.label_50 = QtWidgets.QLabel(self.formFrame)
        self.label_50.setObjectName("label_50")
        self.gridLayout.addWidget(self.label_50, 2, 0, 1, 1)
        self.label_51 = QtWidgets.QLabel(self.formFrame)
        self.label_51.setObjectName("label_51")
        self.gridLayout.addWidget(self.label_51, 2, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.formFrame)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 2, 1, 1)
        self.setup_button = QtWidgets.QPushButton(self.formFrame)
        self.setup_button.setObjectName("setup_button")
        self.gridLayout.addWidget(self.setup_button, 6, 0, 1, 4)
        self.lin_incr_double_sb = QtWidgets.QSpinBox(self.formFrame)
        self.lin_incr_double_sb.setMinimum(-2147483647)
        self.lin_incr_double_sb.setMaximum(1231231231)
        self.lin_incr_double_sb.setProperty("value", 99)
        self.lin_incr_double_sb.setObjectName("lin_incr_double_sb")
        self.gridLayout.addWidget(self.lin_incr_double_sb, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.formFrame)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.formFrame)
        self.label_7.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 2)
        self.label = QtWidgets.QLabel(self.formFrame)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 2, 1, 1)
        self.linear_speed_mm_s_sb = QtWidgets.QDoubleSpinBox(self.formFrame)
        self.linear_speed_mm_s_sb.setObjectName("linear_speed_mm_s_sb")
        self.gridLayout.addWidget(self.linear_speed_mm_s_sb, 4, 1, 1, 1)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.formFrame)
        self.doubleSpinBox.setMinimum(0.01)
        self.doubleSpinBox.setMaximum(3.0)
        self.doubleSpinBox.setSingleStep(0.1)
        self.doubleSpinBox.setProperty("value", 1.9)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout.addWidget(self.doubleSpinBox, 5, 3, 1, 1)
        self.rotational_speed_deg_s_sb = QtWidgets.QDoubleSpinBox(self.formFrame)
        self.rotational_speed_deg_s_sb.setObjectName("rotational_speed_deg_s_sb")
        self.gridLayout.addWidget(self.rotational_speed_deg_s_sb, 4, 3, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.formFrame)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 0, 2, 1, 2)
        self.label_6 = QtWidgets.QLabel(self.formFrame)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 2, 1, 1)
        self.move_tooltip = QtWidgets.QWidget(self.tab_11)
        self.move_tooltip.setGeometry(QtCore.QRect(0, 0, 820, 50))
        self.move_tooltip.setObjectName("move_tooltip")
        self.tabWidget_3.addTab(self.tab_11, "")

        self.retranslateUi(Form)
        self.tabWidget_3.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_31.setToolTip(_translate("Form",
                                            "Here you may set specific configuration parameters for the drivers/software that moves the motors."))
        self.label_31.setText(_translate("Form", "Stepper system"))
        self.set_button.setText(_translate("Form", "Set"))
        self.label_32.setText(_translate("Form", "VISA Resource Name"))
        self.label_35.setText(_translate("Form", "Longitudinal 1"))
        self.label_36.setText(_translate("Form", "Theta Rotation"))
        self.theta_rotation_indicator.setText(_translate("Form", "PushButton"))
        self.trans_2_indicator.setText(_translate("Form", "PushButton"))
        self.vert_2_indicator.setText(_translate("Form", "PushButton"))
        self.long_1_indicator.setText(_translate("Form", "PushButton"))
        self.label_33.setText(_translate("Form", "Vertical 1"))
        self.label_34.setText(_translate("Form", "Transverse 1"))
        self.long_2_indicator.setText(_translate("Form", "PushButton"))
        self.vert_1_indicator.setText(_translate("Form", "PushButton"))
        self.trans_1_indicator.setText(_translate("Form", "PushButton"))
        self.theta_2_indicator.setText(_translate("Form", "PushButton"))
        self.label_37.setText(_translate("Form", "Transverse 2"))
        self.label_38.setText(_translate("Form", "Theta 2"))
        self.label_39.setText(_translate("Form", "Vertical 2"))
        self.label_40.setText(_translate("Form", "Longitudinal 2"))
        self.z_vert_indicator.setText(_translate("Form", "PushButton"))
        self.label_41.setText(_translate("Form", "Z vertical"))
        self.label_42.setText(_translate("Form", "Th2 Sim if absent"))
        self.label_43.setText(_translate("Form", "Physical Parameters"))
        self.label_46.setText(_translate("Form", "Steps/mm"))
        self.label_47.setText(_translate("Form", "Gearing"))
        self.label_48.setText(_translate("Form", "Type"))
        self.label_49.setText(_translate("Form", "Encoded"))
        self.encoded_indicator.setText(_translate("Form", "PushButton"))
        self.label_44.setText(_translate("Form", "Axes present"))
        self.label_45.setText(_translate("Form", "Sim if absent"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.config_tab), _translate("Form", "Config"))
        self.x_pos_button.setText(_translate("Form", "+X"))
        self.x_neg_button.setText(_translate("Form", "-X"))
        self.go_element_combo.setItemText(0, _translate("Form", "Current"))
        self.go_element_combo.setItemText(1, _translate("Form", "1"))
        self.go_element_combo.setItemText(2, _translate("Form", "2"))
        self.go_element_combo.setItemText(3, _translate("Form", "3"))
        self.go_element_combo.setItemText(4, _translate("Form", "4"))
        self.go_element_combo.setItemText(5, _translate("Form", "5"))
        self.go_element_combo.setItemText(6, _translate("Form", "6"))
        self.go_element_combo.setItemText(7, _translate("Form", "7"))
        self.go_element_combo.setItemText(8, _translate("Form", "8"))
        self.go_element_combo.setItemText(9, _translate("Form", "9"))
        self.go_element_combo.setItemText(10, _translate("Form", "10"))
        self.insert_ua_button.setText(_translate("Form", "Insert UA"))
        self.theta_neg_button.setText(_translate("Form", "-Theta"))
        self.retract_ua_button.setText(_translate("Form", "Retract UA"))
        self.go_x_button.setText(_translate("Form", "Go to X"))
        self.theta_pos_lineedit.setText(_translate("Form", "0"))
        self.x_pos_lineedit.setText(_translate("Form", "0"))
        self.theta_pos_button.setText(_translate("Form", "+Theta"))
        self.go_theta_button.setText(_translate("Form", "Go to Theta"))
        self.go_element_button.setText(_translate("Form", "Go to element"))
        self.reset_zero_button.setText(_translate("Form", "Reset Zero"))
        self.label_53.setText(_translate("Form", "Manual home"))
        self.label_52.setText(_translate("Form", "All Axes"))
        self.label_58.setText(_translate("Form", "X"))
        self.label_59.setText(_translate("Form", "Theta"))
        self.manual_home_button.setText(_translate("Form", "Home Axis"))
        self.stop_button.setText(_translate("Form", "STOP"))
        self.label_4.setText(_translate("Form", "Steps per mm"))
        self.save_settings_button.setText(_translate("Form", "Save settings as default"))
        self.label_50.setText(_translate("Form", "Linear Increment (mm)"))
        self.label_51.setText(_translate("Form", "Angular Increment (deg)"))
        self.label_5.setText(_translate("Form", "Steps per degree"))
        self.setup_button.setText(_translate("Form", "Setup"))
        self.label_2.setText(_translate("Form", "Linear speed (mm/s)"))
        self.label_7.setText(_translate("Form", "X"))
        self.label.setText(_translate("Form", "Rotational speed (deg/s)"))
        self.label_8.setText(_translate("Form", "Theta"))
        self.label_6.setText(_translate("Form", "Gearing"))
        self.move_tooltip.setToolTip(_translate("Form",
                                                "Here you may manually home either the X or Theta position of the ultrasound actuator using the motors, with addtional options in a user friendly GUI"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_11), _translate("Form", "Move"))


from ui_elements.switch import Switch

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

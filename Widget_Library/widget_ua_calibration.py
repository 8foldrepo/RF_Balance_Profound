# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_ua_calibration.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(524, 448)
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(20, 60, 461, 341))
        self.frame.setStyleSheet("background:white")
        self.frame.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.label_32 = QtWidgets.QLabel(self.frame)
        self.label_32.setGeometry(QtCore.QRect(365, 10, 62, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_32.setFont(font)
        self.label_32.setObjectName("label_32")
        self.label_31 = QtWidgets.QLabel(self.frame)
        self.label_31.setGeometry(QtCore.QRect(130, 10, 95, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_31.setFont(font)
        self.label_31.setObjectName("label_31")
        self.label_33 = QtWidgets.QLabel(self.frame)
        self.label_33.setGeometry(QtCore.QRect(265, 10, 59, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_33.setFont(font)
        self.label_33.setObjectName("label_33")
        self.layoutWidget = QtWidgets.QWidget(self.frame)
        self.layoutWidget.setGeometry(QtCore.QRect(5, 30, 231, 301))
        self.layoutWidget.setObjectName("layoutWidget")
        self.labels_values_horz_3 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.labels_values_horz_3.setContentsMargins(0, 0, 0, 0)
        self.labels_values_horz_3.setObjectName("labels_values_horz_3")
        self.data_labels_vert_3 = QtWidgets.QVBoxLayout()
        self.data_labels_vert_3.setSpacing(0)
        self.data_labels_vert_3.setObjectName("data_labels_vert_3")
        self.label_21 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.data_labels_vert_3.addWidget(self.label_21)
        self.label_22 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        self.data_labels_vert_3.addWidget(self.label_22)
        self.label_23 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_23.setFont(font)
        self.label_23.setObjectName("label_23")
        self.data_labels_vert_3.addWidget(self.label_23)
        self.label_24 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_24.setFont(font)
        self.label_24.setObjectName("label_24")
        self.data_labels_vert_3.addWidget(self.label_24)
        self.label_25 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_25.setFont(font)
        self.label_25.setObjectName("label_25")
        self.data_labels_vert_3.addWidget(self.label_25)
        self.label_26 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_26.setFont(font)
        self.label_26.setObjectName("label_26")
        self.data_labels_vert_3.addWidget(self.label_26)
        self.label_27 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_27.setFont(font)
        self.label_27.setObjectName("label_27")
        self.data_labels_vert_3.addWidget(self.label_27)
        self.label_28 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_28.setFont(font)
        self.label_28.setObjectName("label_28")
        self.data_labels_vert_3.addWidget(self.label_28)
        self.label_29 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_29.setFont(font)
        self.label_29.setObjectName("label_29")
        self.data_labels_vert_3.addWidget(self.label_29)
        self.label_30 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_30.setFont(font)
        self.label_30.setObjectName("label_30")
        self.data_labels_vert_3.addWidget(self.label_30)
        self.labels_values_horz_3.addLayout(self.data_labels_vert_3)
        self.cal_data_array_group_3 = QtWidgets.QVBoxLayout()
        self.cal_data_array_group_3.setObjectName("cal_data_array_group_3")
        self.schema_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.schema_3.setStyleSheet("background-color:lightgrey")
        self.schema_3.setObjectName("schema_3")
        self.cal_data_array_group_3.addWidget(self.schema_3)
        self.serial_no_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.serial_no_3.setStyleSheet("background-color:lightgrey")
        self.serial_no_3.setObjectName("serial_no_3")
        self.cal_data_array_group_3.addWidget(self.serial_no_3)
        self.prod_date_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.prod_date_3.setStyleSheet("background-color:lightgrey")
        self.prod_date_3.setObjectName("prod_date_3")
        self.cal_data_array_group_3.addWidget(self.prod_date_3)
        self.hardware_code_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.hardware_code_3.setStyleSheet("background-color:lightgrey")
        self.hardware_code_3.setObjectName("hardware_code_3")
        self.cal_data_array_group_3.addWidget(self.hardware_code_3)
        self.common_lo_freq_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.common_lo_freq_3.setStyleSheet("background-color:lightgrey")
        self.common_lo_freq_3.setObjectName("common_lo_freq_3")
        self.cal_data_array_group_3.addWidget(self.common_lo_freq_3)
        self.common_hi_freq_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.common_hi_freq_3.setStyleSheet("background-color:lightgrey")
        self.common_hi_freq_3.setObjectName("common_hi_freq_3")
        self.cal_data_array_group_3.addWidget(self.common_hi_freq_3)
        self.beam_align_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.beam_align_3.setStyleSheet("background-color:lightgrey")
        self.beam_align_3.setObjectName("beam_align_3")
        self.cal_data_array_group_3.addWidget(self.beam_align_3)
        self.command_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.command_3.setStyleSheet("background-color:lightgrey")
        self.command_3.setObjectName("command_3")
        self.cal_data_array_group_3.addWidget(self.command_3)
        self.status_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.status_3.setStyleSheet("background-color:lightgrey")
        self.status_3.setObjectName("status_3")
        self.cal_data_array_group_3.addWidget(self.status_3)
        self.fw_version_3 = QtWidgets.QTextBrowser(self.layoutWidget)
        self.fw_version_3.setStyleSheet("background-color:lightgrey")
        self.fw_version_3.setObjectName("fw_version_3")
        self.cal_data_array_group_3.addWidget(self.fw_version_3)
        self.labels_values_horz_3.addLayout(self.cal_data_array_group_3)
        self.layoutWidget_2 = QtWidgets.QWidget(self.frame)
        self.layoutWidget_2.setGeometry(QtCore.QRect(265, 30, 86, 301))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.low_freq_group_3 = QtWidgets.QVBoxLayout(self.layoutWidget_2)
        self.low_freq_group_3.setContentsMargins(0, 0, 0, 0)
        self.low_freq_group_3.setObjectName("low_freq_group_3")
        self.schema_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.schema_lo_3.setStyleSheet("background-color:lightgrey")
        self.schema_lo_3.setObjectName("schema_lo_3")
        self.low_freq_group_3.addWidget(self.schema_lo_3)
        self.serial_no_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.serial_no_lo_3.setStyleSheet("background-color:lightgrey")
        self.serial_no_lo_3.setObjectName("serial_no_lo_3")
        self.low_freq_group_3.addWidget(self.serial_no_lo_3)
        self.prod_date_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.prod_date_lo_3.setStyleSheet("background-color:lightgrey")
        self.prod_date_lo_3.setObjectName("prod_date_lo_3")
        self.low_freq_group_3.addWidget(self.prod_date_lo_3)
        self.hardware_code_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.hardware_code_lo_3.setStyleSheet("background-color:lightgrey")
        self.hardware_code_lo_3.setObjectName("hardware_code_lo_3")
        self.low_freq_group_3.addWidget(self.hardware_code_lo_3)
        self.common_lo_freq_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.common_lo_freq_lo_3.setStyleSheet("background-color:lightgrey")
        self.common_lo_freq_lo_3.setObjectName("common_lo_freq_lo_3")
        self.low_freq_group_3.addWidget(self.common_lo_freq_lo_3)
        self.common_hi_freq_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.common_hi_freq_lo_3.setStyleSheet("background-color:lightgrey")
        self.common_hi_freq_lo_3.setObjectName("common_hi_freq_lo_3")
        self.low_freq_group_3.addWidget(self.common_hi_freq_lo_3)
        self.beam_align_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.beam_align_lo_3.setStyleSheet("background-color:lightgrey")
        self.beam_align_lo_3.setObjectName("beam_align_lo_3")
        self.low_freq_group_3.addWidget(self.beam_align_lo_3)
        self.command_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.command_lo_3.setStyleSheet("background-color:lightgrey")
        self.command_lo_3.setObjectName("command_lo_3")
        self.low_freq_group_3.addWidget(self.command_lo_3)
        self.status_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.status_lo_3.setStyleSheet("background-color:lightgrey")
        self.status_lo_3.setObjectName("status_lo_3")
        self.low_freq_group_3.addWidget(self.status_lo_3)
        self.fw_version_lo_3 = QtWidgets.QTextBrowser(self.layoutWidget_2)
        self.fw_version_lo_3.setStyleSheet("background-color:lightgrey")
        self.fw_version_lo_3.setObjectName("fw_version_lo_3")
        self.low_freq_group_3.addWidget(self.fw_version_lo_3)
        self.layoutWidget_3 = QtWidgets.QWidget(self.frame)
        self.layoutWidget_3.setGeometry(QtCore.QRect(365, 30, 86, 301))
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.high_freq_group_3 = QtWidgets.QVBoxLayout(self.layoutWidget_3)
        self.high_freq_group_3.setContentsMargins(0, 0, 0, 0)
        self.high_freq_group_3.setObjectName("high_freq_group_3")
        self.schema_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.schema_hi_3.setStyleSheet("background-color:lightgrey")
        self.schema_hi_3.setObjectName("schema_hi_3")
        self.high_freq_group_3.addWidget(self.schema_hi_3)
        self.serial_no_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.serial_no_hi_3.setStyleSheet("background-color:lightgrey")
        self.serial_no_hi_3.setObjectName("serial_no_hi_3")
        self.high_freq_group_3.addWidget(self.serial_no_hi_3)
        self.prod_date_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.prod_date_hi_3.setStyleSheet("background-color:lightgrey")
        self.prod_date_hi_3.setObjectName("prod_date_hi_3")
        self.high_freq_group_3.addWidget(self.prod_date_hi_3)
        self.hardware_code_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.hardware_code_hi_3.setStyleSheet("background-color:lightgrey")
        self.hardware_code_hi_3.setObjectName("hardware_code_hi_3")
        self.high_freq_group_3.addWidget(self.hardware_code_hi_3)
        self.common_lo_freq_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.common_lo_freq_hi_3.setStyleSheet("background-color:lightgrey")
        self.common_lo_freq_hi_3.setObjectName("common_lo_freq_hi_3")
        self.high_freq_group_3.addWidget(self.common_lo_freq_hi_3)
        self.common_hi_freq_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.common_hi_freq_hi_3.setStyleSheet("background-color:lightgrey")
        self.common_hi_freq_hi_3.setObjectName("common_hi_freq_hi_3")
        self.high_freq_group_3.addWidget(self.common_hi_freq_hi_3)
        self.beam_align_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.beam_align_hi_3.setStyleSheet("background-color:lightgrey")
        self.beam_align_hi_3.setObjectName("beam_align_hi_3")
        self.high_freq_group_3.addWidget(self.beam_align_hi_3)
        self.command_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.command_hi_3.setStyleSheet("background-color:lightgrey")
        self.command_hi_3.setObjectName("command_hi_3")
        self.high_freq_group_3.addWidget(self.command_hi_3)
        self.status_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.status_hi_3.setStyleSheet("background-color:lightgrey")
        self.status_hi_3.setObjectName("status_hi_3")
        self.high_freq_group_3.addWidget(self.status_hi_3)
        self.fw_version_hi_3 = QtWidgets.QTextBrowser(self.layoutWidget_3)
        self.fw_version_hi_3.setStyleSheet("background-color:lightgrey")
        self.fw_version_hi_3.setObjectName("fw_version_hi_3")
        self.high_freq_group_3.addWidget(self.fw_version_hi_3)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(380, 410, 111, 31))
        self.pushButton.setObjectName("pushButton")
        self.label_34 = QtWidgets.QLabel(Form)
        self.label_34.setGeometry(QtCore.QRect(20, 40, 41, 13))
        self.label_34.setObjectName("label_34")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_32.setText(_translate("Form", "High Freq"))
        self.label_31.setText(_translate("Form", "Cal Data Array"))
        self.label_33.setText(_translate("Form", "Low Freq"))
        self.label_21.setText(_translate("Form", "Schema"))
        self.label_22.setText(_translate("Form", "SerialNumber"))
        self.label_23.setText(_translate("Form", "ProductionDate"))
        self.label_24.setText(_translate("Form", "HardwareCode"))
        self.label_25.setText(_translate("Form", "CommonLowFreq"))
        self.label_26.setText(_translate("Form", "CommonHighFreq"))
        self.label_27.setText(_translate("Form", "BeamAlign"))
        self.label_28.setText(_translate("Form", "Command"))
        self.label_29.setText(_translate("Form", "Status"))
        self.label_30.setText(_translate("Form", "FWVersion"))
        self.pushButton.setText(_translate("Form", "Read from UA"))
        self.label_34.setText(_translate("Form", "Cal Data"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'write_cal_data_to_ua.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_write_cal_data_to_ua(object):
    def setupUi(self, write_cal_data_to_ua):
        write_cal_data_to_ua.setObjectName("write_cal_data_to_ua")
        write_cal_data_to_ua.resize(459, 400)
        write_cal_data_to_ua.setMinimumSize(QtCore.QSize(459, 370))
        write_cal_data_to_ua.setMaximumSize(QtCore.QSize(459, 400))
        self.label_11 = QtWidgets.QLabel(write_cal_data_to_ua)
        self.label_11.setGeometry(QtCore.QRect(125, 0, 95, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(write_cal_data_to_ua)
        self.label_12.setGeometry(QtCore.QRect(260, 0, 59, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(write_cal_data_to_ua)
        self.label_13.setGeometry(QtCore.QRect(360, 0, 62, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(write_cal_data_to_ua)
        self.label_14.setGeometry(QtCore.QRect(55, 320, 346, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.layoutWidget = QtWidgets.QWidget(write_cal_data_to_ua)
        self.layoutWidget.setGeometry(QtCore.QRect(270, 360, 181, 32))
        self.layoutWidget.setObjectName("layoutWidget")
        self.buttons_horz = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.buttons_horz.setContentsMargins(0, 0, 0, 0)
        self.buttons_horz.setSpacing(13)
        self.buttons_horz.setObjectName("buttons_horz")
        self.cancel_button = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.cancel_button.sizePolicy().hasHeightForWidth()
        )
        self.cancel_button.setSizePolicy(sizePolicy)
        self.cancel_button.setMinimumSize(QtCore.QSize(70, 30))
        self.cancel_button.setObjectName("cancel_button")
        self.buttons_horz.addWidget(self.cancel_button)
        self.write_ua_button = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.write_ua_button.sizePolicy().hasHeightForWidth()
        )
        self.write_ua_button.setSizePolicy(sizePolicy)
        self.write_ua_button.setObjectName("write_ua_button")
        self.buttons_horz.addWidget(self.write_ua_button)
        self.layoutWidget1 = QtWidgets.QWidget(write_cal_data_to_ua)
        self.layoutWidget1.setGeometry(QtCore.QRect(0, 20, 231, 291))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.labels_values_horz = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.labels_values_horz.setContentsMargins(0, 0, 0, 0)
        self.labels_values_horz.setObjectName("labels_values_horz")
        self.data_labels_vert = QtWidgets.QVBoxLayout()
        self.data_labels_vert.setSpacing(0)
        self.data_labels_vert.setObjectName("data_labels_vert")
        self.label = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.data_labels_vert.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.data_labels_vert.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.data_labels_vert.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.data_labels_vert.addWidget(self.label_4)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.data_labels_vert.addWidget(self.label_5)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.data_labels_vert.addWidget(self.label_7)
        self.label_6 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.data_labels_vert.addWidget(self.label_6)
        self.label_8 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.data_labels_vert.addWidget(self.label_8)
        self.label_10 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.data_labels_vert.addWidget(self.label_10)
        self.label_9 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.data_labels_vert.addWidget(self.label_9)
        self.labels_values_horz.addLayout(self.data_labels_vert)
        self.cal_data_array_group = QtWidgets.QVBoxLayout()
        self.cal_data_array_group.setObjectName("cal_data_array_group")
        self.schema = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.schema.setStyleSheet("background-color:lightgrey")
        self.schema.setObjectName("schema")
        self.cal_data_array_group.addWidget(self.schema)
        self.serial_no = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.serial_no.setStyleSheet("background-color:lightgrey")
        self.serial_no.setObjectName("serial_no")
        self.cal_data_array_group.addWidget(self.serial_no)
        self.prod_date = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.prod_date.setStyleSheet("background-color:lightgrey")
        self.prod_date.setObjectName("prod_date")
        self.cal_data_array_group.addWidget(self.prod_date)
        self.hardware_code = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.hardware_code.setStyleSheet("background-color:lightgrey")
        self.hardware_code.setObjectName("hardware_code")
        self.cal_data_array_group.addWidget(self.hardware_code)
        self.common_lo_freq = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.common_lo_freq.setStyleSheet("background-color:lightgrey")
        self.common_lo_freq.setObjectName("common_lo_freq")
        self.cal_data_array_group.addWidget(self.common_lo_freq)
        self.common_hi_freq = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.common_hi_freq.setStyleSheet("background-color:lightgrey")
        self.common_hi_freq.setObjectName("common_hi_freq")
        self.cal_data_array_group.addWidget(self.common_hi_freq)
        self.beam_align = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.beam_align.setStyleSheet("background-color:lightgrey")
        self.beam_align.setObjectName("beam_align")
        self.cal_data_array_group.addWidget(self.beam_align)
        self.command = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.command.setStyleSheet("background-color:lightgrey")
        self.command.setObjectName("command")
        self.cal_data_array_group.addWidget(self.command)
        self.status = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.status.setStyleSheet("background-color:lightgrey")
        self.status.setObjectName("status")
        self.cal_data_array_group.addWidget(self.status)
        self.fw_version = QtWidgets.QTextBrowser(self.layoutWidget1)
        self.fw_version.setStyleSheet("background-color:lightgrey")
        self.fw_version.setObjectName("fw_version")
        self.cal_data_array_group.addWidget(self.fw_version)
        self.labels_values_horz.addLayout(self.cal_data_array_group)
        self.layoutWidget2 = QtWidgets.QWidget(write_cal_data_to_ua)
        self.layoutWidget2.setGeometry(QtCore.QRect(360, 20, 86, 291))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.high_freq_group = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.high_freq_group.setContentsMargins(0, 0, 0, 0)
        self.high_freq_group.setObjectName("high_freq_group")
        self.schema_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.schema_hi.setStyleSheet("background-color:lightgrey")
        self.schema_hi.setObjectName("schema_hi")
        self.high_freq_group.addWidget(self.schema_hi)
        self.serial_no_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.serial_no_hi.setStyleSheet("background-color:lightgrey")
        self.serial_no_hi.setObjectName("serial_no_hi")
        self.high_freq_group.addWidget(self.serial_no_hi)
        self.prod_date_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.prod_date_hi.setStyleSheet("background-color:lightgrey")
        self.prod_date_hi.setObjectName("prod_date_hi")
        self.high_freq_group.addWidget(self.prod_date_hi)
        self.hardware_code_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.hardware_code_hi.setStyleSheet("background-color:lightgrey")
        self.hardware_code_hi.setObjectName("hardware_code_hi")
        self.high_freq_group.addWidget(self.hardware_code_hi)
        self.common_lo_freq_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.common_lo_freq_hi.setStyleSheet("background-color:lightgrey")
        self.common_lo_freq_hi.setObjectName("common_lo_freq_hi")
        self.high_freq_group.addWidget(self.common_lo_freq_hi)
        self.common_hi_freq_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.common_hi_freq_hi.setStyleSheet("background-color:lightgrey")
        self.common_hi_freq_hi.setObjectName("common_hi_freq_hi")
        self.high_freq_group.addWidget(self.common_hi_freq_hi)
        self.beam_align_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.beam_align_hi.setStyleSheet("background-color:lightgrey")
        self.beam_align_hi.setObjectName("beam_align_hi")
        self.high_freq_group.addWidget(self.beam_align_hi)
        self.command_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.command_hi.setStyleSheet("background-color:lightgrey")
        self.command_hi.setObjectName("command_hi")
        self.high_freq_group.addWidget(self.command_hi)
        self.status_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.status_hi.setStyleSheet("background-color:lightgrey")
        self.status_hi.setObjectName("status_hi")
        self.high_freq_group.addWidget(self.status_hi)
        self.fw_version_hi = QtWidgets.QTextBrowser(self.layoutWidget2)
        self.fw_version_hi.setStyleSheet("background-color:lightgrey")
        self.fw_version_hi.setObjectName("fw_version_hi")
        self.high_freq_group.addWidget(self.fw_version_hi)
        self.layoutWidget3 = QtWidgets.QWidget(write_cal_data_to_ua)
        self.layoutWidget3.setGeometry(QtCore.QRect(260, 20, 86, 291))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.low_freq_group = QtWidgets.QVBoxLayout(self.layoutWidget3)
        self.low_freq_group.setContentsMargins(0, 0, 0, 0)
        self.low_freq_group.setObjectName("low_freq_group")
        self.schema_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.schema_lo.setStyleSheet("background-color:lightgrey")
        self.schema_lo.setObjectName("schema_lo")
        self.low_freq_group.addWidget(self.schema_lo)
        self.serial_no_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.serial_no_lo.setStyleSheet("background-color:lightgrey")
        self.serial_no_lo.setObjectName("serial_no_lo")
        self.low_freq_group.addWidget(self.serial_no_lo)
        self.prod_date_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.prod_date_lo.setStyleSheet("background-color:lightgrey")
        self.prod_date_lo.setObjectName("prod_date_lo")
        self.low_freq_group.addWidget(self.prod_date_lo)
        self.hardware_code_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.hardware_code_lo.setStyleSheet("background-color:lightgrey")
        self.hardware_code_lo.setObjectName("hardware_code_lo")
        self.low_freq_group.addWidget(self.hardware_code_lo)
        self.common_lo_freq_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.common_lo_freq_lo.setStyleSheet("background-color:lightgrey")
        self.common_lo_freq_lo.setObjectName("common_lo_freq_lo")
        self.low_freq_group.addWidget(self.common_lo_freq_lo)
        self.common_hi_freq_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.common_hi_freq_lo.setStyleSheet("background-color:lightgrey")
        self.common_hi_freq_lo.setObjectName("common_hi_freq_lo")
        self.low_freq_group.addWidget(self.common_hi_freq_lo)
        self.beam_align_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.beam_align_lo.setStyleSheet("background-color:lightgrey")
        self.beam_align_lo.setObjectName("beam_align_lo")
        self.low_freq_group.addWidget(self.beam_align_lo)
        self.command_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.command_lo.setStyleSheet("background-color:lightgrey")
        self.command_lo.setObjectName("command_lo")
        self.low_freq_group.addWidget(self.command_lo)
        self.status_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.status_lo.setStyleSheet("background-color:lightgrey")
        self.status_lo.setObjectName("status_lo")
        self.low_freq_group.addWidget(self.status_lo)
        self.fw_version_lo = QtWidgets.QTextBrowser(self.layoutWidget3)
        self.fw_version_lo.setStyleSheet("background-color:lightgrey")
        self.fw_version_lo.setObjectName("fw_version_lo")
        self.low_freq_group.addWidget(self.fw_version_lo)

        self.retranslateUi(write_cal_data_to_ua)
        QtCore.QMetaObject.connectSlotsByName(write_cal_data_to_ua)

    def retranslateUi(self, write_cal_data_to_ua):
        _translate = QtCore.QCoreApplication.translate
        write_cal_data_to_ua.setWindowTitle(
            _translate("write_cal_data_to_ua", "Dialog")
        )
        self.label_11.setText(_translate("write_cal_data_to_ua", "Cal Data Array"))
        self.label_12.setText(_translate("write_cal_data_to_ua", "Low Freq"))
        self.label_13.setText(_translate("write_cal_data_to_ua", "High Freq"))
        self.label_14.setText(
            _translate(
                "write_cal_data_to_ua",
                "The above results are ready to be written to the UA.",
            )
        )
        self.cancel_button.setText(_translate("write_cal_data_to_ua", "Cancel"))
        self.write_ua_button.setText(_translate("write_cal_data_to_ua", "Write UA"))
        self.label.setText(_translate("write_cal_data_to_ua", "Schema"))
        self.label_2.setText(_translate("write_cal_data_to_ua", "SerialNumber"))
        self.label_3.setText(_translate("write_cal_data_to_ua", "ProductionDate"))
        self.label_4.setText(_translate("write_cal_data_to_ua", "HardwareCode"))
        self.label_5.setText(_translate("write_cal_data_to_ua", "CommonLowFreq"))
        self.label_7.setText(_translate("write_cal_data_to_ua", "CommonHighFreq"))
        self.label_6.setText(_translate("write_cal_data_to_ua", "BeamAlign"))
        self.label_8.setText(_translate("write_cal_data_to_ua", "Command"))
        self.label_10.setText(_translate("write_cal_data_to_ua", "Status"))
        self.label_9.setText(_translate("write_cal_data_to_ua", "FWVersion"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    write_cal_data_to_ua = QtWidgets.QDialog()
    ui = Ui_write_cal_data_to_ua()
    ui.setupUi(write_cal_data_to_ua)
    write_cal_data_to_ua.show()
    sys.exit(app.exec_())

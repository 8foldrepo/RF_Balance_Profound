# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_results_saving.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_configure_results_saving(object):
    def setupUi(self, configure_results_saving):
        configure_results_saving.setObjectName("configure_results_saving")
        configure_results_saving.resize(541, 373)
        self.config_res_sav_frame = QtWidgets.QFrame(configure_results_saving)
        self.config_res_sav_frame.setGeometry(QtCore.QRect(20, 20, 251, 72))
        self.config_res_sav_frame.setStyleSheet("background:rgb(220, 242, 255)")
        self.config_res_sav_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.config_res_sav_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.config_res_sav_frame.setObjectName("config_res_sav_frame")
        self.write_ua_subframe = QtWidgets.QFrame(self.config_res_sav_frame)
        self.write_ua_subframe.setGeometry(QtCore.QRect(-1, 30, 251, 41))
        self.write_ua_subframe.setFrameShape(QtWidgets.QFrame.Box)
        self.write_ua_subframe.setFrameShadow(QtWidgets.QFrame.Raised)
        self.write_ua_subframe.setObjectName("write_ua_subframe")
        self.layoutWidget = QtWidgets.QWidget(self.write_ua_subframe)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 231, 19))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horz_lyout_write_ua = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horz_lyout_write_ua.setContentsMargins(0, 0, 0, 0)
        self.horz_lyout_write_ua.setObjectName("horz_lyout_write_ua")
        self.write_ua_calibration_checkbox = QtWidgets.QCheckBox(self.layoutWidget)
        self.write_ua_calibration_checkbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.write_ua_calibration_checkbox.setObjectName("write_ua_calibration_checkbox")
        self.horz_lyout_write_ua.addWidget(self.write_ua_calibration_checkbox)
        self.with_prompt_checkbox = QtWidgets.QCheckBox(self.layoutWidget)
        self.with_prompt_checkbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.with_prompt_checkbox.setObjectName("with_prompt_checkbox")
        self.horz_lyout_write_ua.addWidget(self.with_prompt_checkbox)
        self.sav_sum_file_chkbx = QtWidgets.QCheckBox(self.config_res_sav_frame)
        self.sav_sum_file_chkbx.setGeometry(QtCore.QRect(7, 10, 121, 20))
        self.sav_sum_file_chkbx.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.sav_sum_file_chkbx.setObjectName("sav_sum_file_chkbx")

        self.retranslateUi(configure_results_saving)
        QtCore.QMetaObject.connectSlotsByName(configure_results_saving)

    def retranslateUi(self, configure_results_saving):
        _translate = QtCore.QCoreApplication.translate
        configure_results_saving.setWindowTitle(_translate("configure_results_saving", "Form"))
        self.write_ua_calibration_checkbox.setText(_translate("configure_results_saving", "Write UA Calibration"))
        self.with_prompt_checkbox.setText(_translate("configure_results_saving", "With prompt"))
        self.sav_sum_file_chkbx.setText(_translate("configure_results_saving", "Save summary file   "))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    configure_results_saving = QtWidgets.QWidget()
    ui = Ui_configure_results_saving()
    ui.setupUi(configure_results_saving)
    configure_results_saving.show()
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_frequency_sweep.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(537, 480)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 85, 13))
        self.label.setObjectName("label")
        self.freq_sweep_frame = QtWidgets.QFrame(Form)
        self.freq_sweep_frame.setGeometry(QtCore.QRect(10, 30, 331, 421))
        self.freq_sweep_frame.setStyleSheet("background:rgb(220, 242, 255)")
        self.freq_sweep_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.freq_sweep_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.freq_sweep_frame.setObjectName("freq_sweep_frame")
        self.peak_vsi_thresh_frame = QtWidgets.QFrame(self.freq_sweep_frame)
        self.peak_vsi_thresh_frame.setGeometry(QtCore.QRect(10, 350, 225, 51))
        self.peak_vsi_thresh_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.peak_vsi_thresh_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.peak_vsi_thresh_frame.setObjectName("peak_vsi_thresh_frame")
        self.layoutWidget = QtWidgets.QWidget(self.peak_vsi_thresh_frame)
        self.layoutWidget.setGeometry(QtCore.QRect(6, 7, 210, 41))
        self.layoutWidget.setObjectName("layoutWidget")
        self.peak_vsi_test_horz = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.peak_vsi_test_horz.setContentsMargins(0, 0, 0, 0)
        self.peak_vsi_test_horz.setSpacing(48)
        self.peak_vsi_test_horz.setObjectName("peak_vsi_test_horz")
        self.peak_vsi_horz_2 = QtWidgets.QVBoxLayout()
        self.peak_vsi_horz_2.setObjectName("peak_vsi_horz_2")
        self.label_15 = QtWidgets.QLabel(self.layoutWidget)
        self.label_15.setObjectName("label_15")
        self.peak_vsi_horz_2.addWidget(self.label_15)
        self.peak_vsi_spinbox = QtWidgets.QSpinBox(self.layoutWidget)
        self.peak_vsi_spinbox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.peak_vsi_spinbox.setStyleSheet("background:white")
        self.peak_vsi_spinbox.setObjectName("peak_vsi_spinbox")
        self.peak_vsi_horz_2.addWidget(self.peak_vsi_spinbox)
        self.peak_vsi_test_horz.addLayout(self.peak_vsi_horz_2)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_16 = QtWidgets.QLabel(self.layoutWidget)
        self.label_16.setObjectName("label_16")
        self.verticalLayout_2.addWidget(self.label_16)
        self.incl_test_check = QtWidgets.QCheckBox(self.layoutWidget)
        self.incl_test_check.setText("")
        self.incl_test_check.setObjectName("incl_test_check")
        self.verticalLayout_2.addWidget(self.incl_test_check)
        self.peak_vsi_test_horz.addLayout(self.verticalLayout_2)
        self.data_direc_button = QtWidgets.QPushButton(self.freq_sweep_frame)
        self.data_direc_button.setGeometry(QtCore.QRect(280, 320, 30, 21))
        self.data_direc_button.setStyleSheet("background:white")
        self.data_direc_button.setObjectName("data_direc_button")
        self.layoutWidget1 = QtWidgets.QWidget(self.freq_sweep_frame)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 20, 251, 164))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.freq_incr_subframe = QtWidgets.QFormLayout(self.layoutWidget1)
        self.freq_incr_subframe.setContentsMargins(0, 0, 0, 0)
        self.freq_incr_subframe.setObjectName("freq_incr_subframe")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_2.setObjectName("label_2")
        self.freq_incr_subframe.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.freq_range_combo = QtWidgets.QComboBox(self.layoutWidget1)
        self.freq_range_combo.setStyleSheet("background:white")
        self.freq_range_combo.setObjectName("freq_range_combo")
        self.freq_range_combo.addItem("")
        self.freq_range_combo.addItem("")
        self.freq_incr_subframe.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.freq_range_combo)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_3.setObjectName("label_3")
        self.freq_incr_subframe.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.start_freq_spin = QtWidgets.QSpinBox(self.layoutWidget1)
        self.start_freq_spin.setMaximumSize(QtCore.QSize(60, 16777215))
        self.start_freq_spin.setStyleSheet("background:white")
        self.start_freq_spin.setObjectName("start_freq_spin")
        self.freq_incr_subframe.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.start_freq_spin)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_4.setObjectName("label_4")
        self.freq_incr_subframe.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.end_freq_doublespin = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.end_freq_doublespin.setMaximumSize(QtCore.QSize(60, 16777215))
        self.end_freq_doublespin.setStyleSheet("background:white")
        self.end_freq_doublespin.setDecimals(1)
        self.end_freq_doublespin.setObjectName("end_freq_doublespin")
        self.freq_incr_subframe.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.end_freq_doublespin)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_5.setObjectName("label_5")
        self.freq_incr_subframe.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.coarse_inc_doublespin = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.coarse_inc_doublespin.setMaximumSize(QtCore.QSize(60, 16777215))
        self.coarse_inc_doublespin.setStyleSheet("background:white")
        self.coarse_inc_doublespin.setDecimals(1)
        self.coarse_inc_doublespin.setObjectName("coarse_inc_doublespin")
        self.freq_incr_subframe.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.coarse_inc_doublespin)
        self.label_6 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_6.setObjectName("label_6")
        self.freq_incr_subframe.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.fine_incr_doublespin = QtWidgets.QDoubleSpinBox(self.layoutWidget1)
        self.fine_incr_doublespin.setMaximumSize(QtCore.QSize(60, 16777215))
        self.fine_incr_doublespin.setStyleSheet("background:white")
        self.fine_incr_doublespin.setObjectName("fine_incr_doublespin")
        self.freq_incr_subframe.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.fine_incr_doublespin)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_7.setObjectName("label_7")
        self.freq_incr_subframe.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.burst_count_spin = QtWidgets.QSpinBox(self.layoutWidget1)
        self.burst_count_spin.setMaximumSize(QtCore.QSize(60, 16777215))
        self.burst_count_spin.setStyleSheet("background:white")
        self.burst_count_spin.setObjectName("burst_count_spin")
        self.freq_incr_subframe.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.burst_count_spin)
        self.label_8 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_8.setObjectName("label_8")
        self.freq_incr_subframe.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.amplitude_spin = QtWidgets.QSpinBox(self.layoutWidget1)
        self.amplitude_spin.setMaximumSize(QtCore.QSize(60, 16777215))
        self.amplitude_spin.setStyleSheet("background:white")
        self.amplitude_spin.setObjectName("amplitude_spin")
        self.freq_incr_subframe.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.amplitude_spin)
        self.layoutWidget2 = QtWidgets.QWidget(self.freq_sweep_frame)
        self.layoutWidget2.setGeometry(QtCore.QRect(10, 190, 291, 51))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.scope_acq_arg_grid = QtWidgets.QGridLayout(self.layoutWidget2)
        self.scope_acq_arg_grid.setContentsMargins(0, 0, 0, 0)
        self.scope_acq_arg_grid.setVerticalSpacing(6)
        self.scope_acq_arg_grid.setObjectName("scope_acq_arg_grid")
        self.label_9 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_9.setMinimumSize(QtCore.QSize(0, 13))
        self.label_9.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label_9.setObjectName("label_9")
        self.scope_acq_arg_grid.addWidget(self.label_9, 0, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_10.setMinimumSize(QtCore.QSize(0, 13))
        self.label_10.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label_10.setObjectName("label_10")
        self.scope_acq_arg_grid.addWidget(self.label_10, 0, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_11.setMinimumSize(QtCore.QSize(0, 13))
        self.label_11.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label_11.setObjectName("label_11")
        self.scope_acq_arg_grid.addWidget(self.label_11, 0, 2, 1, 1)
        self.scope_channel_combo = QtWidgets.QComboBox(self.layoutWidget2)
        self.scope_channel_combo.setMinimumSize(QtCore.QSize(0, 20))
        self.scope_channel_combo.setStyleSheet("background:white")
        self.scope_channel_combo.setObjectName("scope_channel_combo")
        self.scope_channel_combo.addItem("")
        self.scope_channel_combo.addItem("")
        self.scope_acq_arg_grid.addWidget(self.scope_channel_combo, 1, 0, 1, 1)
        self.acq_type_combo = QtWidgets.QComboBox(self.layoutWidget2)
        self.acq_type_combo.setMinimumSize(QtCore.QSize(0, 20))
        self.acq_type_combo.setStyleSheet("background:white")
        self.acq_type_combo.setObjectName("acq_type_combo")
        self.acq_type_combo.addItem("")
        self.scope_acq_arg_grid.addWidget(self.acq_type_combo, 1, 1, 1, 1)
        self.averages_spinbox = QtWidgets.QSpinBox(self.layoutWidget2)
        self.averages_spinbox.setMinimumSize(QtCore.QSize(0, 20))
        self.averages_spinbox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.averages_spinbox.setStyleSheet("background:white")
        self.averages_spinbox.setObjectName("averages_spinbox")
        self.scope_acq_arg_grid.addWidget(self.averages_spinbox, 1, 2, 1, 1)
        self.layoutWidget3 = QtWidgets.QWidget(self.freq_sweep_frame)
        self.layoutWidget3.setGeometry(QtCore.QRect(10, 300, 261, 41))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.data_direc_vert_layout = QtWidgets.QVBoxLayout(self.layoutWidget3)
        self.data_direc_vert_layout.setContentsMargins(0, 0, 0, 0)
        self.data_direc_vert_layout.setObjectName("data_direc_vert_layout")
        self.label_14 = QtWidgets.QLabel(self.layoutWidget3)
        self.label_14.setObjectName("label_14")
        self.data_direc_vert_layout.addWidget(self.label_14)
        self.data_direc_input = QtWidgets.QLineEdit(self.layoutWidget3)
        self.data_direc_input.setStyleSheet("background-color: white")
        self.data_direc_input.setObjectName("data_direc_input")
        self.data_direc_vert_layout.addWidget(self.data_direc_input)
        self.layoutWidget4 = QtWidgets.QWidget(self.freq_sweep_frame)
        self.layoutWidget4.setGeometry(QtCore.QRect(12, 252, 281, 39))
        self.layoutWidget4.setObjectName("layoutWidget4")
        self.storage_grid = QtWidgets.QGridLayout(self.layoutWidget4)
        self.storage_grid.setContentsMargins(0, 0, 0, 0)
        self.storage_grid.setObjectName("storage_grid")
        self.label_12 = QtWidgets.QLabel(self.layoutWidget4)
        self.label_12.setObjectName("label_12")
        self.storage_grid.addWidget(self.label_12, 0, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.layoutWidget4)
        self.label_13.setObjectName("label_13")
        self.storage_grid.addWidget(self.label_13, 0, 1, 1, 1)
        self.data_storage_combo = QtWidgets.QComboBox(self.layoutWidget4)
        self.data_storage_combo.setStyleSheet("background:white")
        self.data_storage_combo.setObjectName("data_storage_combo")
        self.data_storage_combo.addItem("")
        self.storage_grid.addWidget(self.data_storage_combo, 1, 0, 1, 1)
        self.storage_loc_combo = QtWidgets.QComboBox(self.layoutWidget4)
        self.storage_loc_combo.setStyleSheet("background:white")
        self.storage_loc_combo.setObjectName("storage_loc_combo")
        self.storage_loc_combo.addItem("")
        self.storage_grid.addWidget(self.storage_loc_combo, 1, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Frequency sweep"))
        self.label_15.setText(_translate("Form", "Peak VSI threshold"))
        self.label_16.setText(_translate("Form", "Include test"))
        self.data_direc_button.setText(_translate("Form", "📁"))
        self.label_2.setText(_translate("Form", "Frequency range"))
        self.freq_range_combo.setItemText(0, _translate("Form", "Low frequency"))
        self.freq_range_combo.setItemText(1, _translate("Form", "High frequency"))
        self.label_3.setText(_translate("Form", "Start frequency (MHz)"))
        self.label_4.setText(_translate("Form", "End frequency (MHz)"))
        self.label_5.setText(_translate("Form", "Coarse increment (MHz)"))
        self.label_6.setText(_translate("Form", "Fine increment (MHz)"))
        self.label_7.setText(_translate("Form", "Burst count"))
        self.label_8.setText(_translate("Form", "Amplitude (mVpp)"))
        self.label_9.setText(_translate("Form", "Scope channel"))
        self.label_10.setText(_translate("Form", "Acquisition type"))
        self.label_11.setText(_translate("Form", "Averages"))
        self.scope_channel_combo.setItemText(0, _translate("Form", "Channel 1"))
        self.scope_channel_combo.setItemText(1, _translate("Form", "Channel 2"))
        self.acq_type_combo.setItemText(0, _translate("Form", "Single Waveform"))
        self.label_14.setText(_translate("Form", "Data directory"))
        self.label_12.setText(_translate("Form", "Data storage"))
        self.label_13.setText(_translate("Form", "Storage location"))
        self.data_storage_combo.setItemText(0, _translate("Form", "Do not store"))
        self.storage_loc_combo.setItemText(0, _translate("Form", "UA results directory"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

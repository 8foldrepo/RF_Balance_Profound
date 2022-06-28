# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_scan.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_scan_tab_widget(object):
    def setupUi(self, scan_tab_widget):
        scan_tab_widget.setObjectName("scan_tab_widget")
        scan_tab_widget.resize(1000, 700)
        scan_tab_widget.setMinimumSize(QtCore.QSize(1000, 700))
        scan_tab_widget.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.scan_tabs = QtWidgets.QTabWidget(scan_tab_widget)
        self.scan_tabs.setGeometry(QtCore.QRect(10, 5, 980, 680))
        self.scan_tabs.setMinimumSize(QtCore.QSize(980, 680))
        self.scan_tabs.setMaximumSize(QtCore.QSize(980, 680))
        self.scan_tabs.setToolTipDuration(0)
        self.scan_tabs.setObjectName("scan_tabs")
        self.one_dimension_scan_tab = QtWidgets.QWidget()
        self.one_dimension_scan_tab.setToolTip("")
        self.one_dimension_scan_tab.setObjectName("one_dimension_scan_tab")
        self.last_acquired_waveform_plot_label = QtWidgets.QLabel(self.one_dimension_scan_tab)
        self.last_acquired_waveform_plot_label.setGeometry(QtCore.QRect(9, 0, 1000, 20))
        self.last_acquired_waveform_plot_label.setMaximumSize(QtCore.QSize(16777215, 20))
        self.last_acquired_waveform_plot_label.setObjectName("last_acquired_waveform_plot_label")
        self.waveform_plot = Plot(self.one_dimension_scan_tab)
        self.waveform_plot.setGeometry(QtCore.QRect(9, 35, 1002, 285))
        self.waveform_plot.setMinimumSize(QtCore.QSize(0, 100))
        self.waveform_plot.setToolTip("")
        self.waveform_plot.setObjectName("waveform_plot")
        self.label_55 = QtWidgets.QLabel(self.one_dimension_scan_tab)
        self.label_55.setGeometry(QtCore.QRect(9, 326, 30, 16))
        self.label_55.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_55.setObjectName("label_55")
        self.profile_plot = Plot(self.one_dimension_scan_tab)
        self.profile_plot.setGeometry(QtCore.QRect(9, 352, 1002, 285))
        self.profile_plot.setMinimumSize(QtCore.QSize(0, 100))
        self.profile_plot.setObjectName("profile_plot")
        self.scan_tabs.addTab(self.one_dimension_scan_tab, "")
        self.acquire_waveform_tab = QtWidgets.QWidget()
        self.acquire_waveform_tab.setToolTip("")
        self.acquire_waveform_tab.setObjectName("acquire_waveform_tab")
        self.voltage_time_plot = Plot(self.acquire_waveform_tab)
        self.voltage_time_plot.setGeometry(QtCore.QRect(60, 30, 911, 341))
        self.voltage_time_plot.setObjectName("voltage_time_plot")
        self.label_31 = QtWidgets.QLabel(self.acquire_waveform_tab)
        self.label_31.setGeometry(QtCore.QRect(0, 0, 1020, 30))
        self.label_31.setObjectName("label_31")
        self.acquisition_arg_frame = QtWidgets.QFrame(self.acquire_waveform_tab)
        self.acquisition_arg_frame.setGeometry(QtCore.QRect(60, 400, 181, 181))
        self.acquisition_arg_frame.setStyleSheet("background:lightblue")
        self.acquisition_arg_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.acquisition_arg_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.acquisition_arg_frame.setObjectName("acquisition_arg_frame")
        self.layoutWidget = QtWidgets.QWidget(self.acquisition_arg_frame)
        self.layoutWidget.setGeometry(QtCore.QRect(11, 11, 161, 141))
        self.layoutWidget.setObjectName("layoutWidget")
        self.acquisition_arg_vert = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.acquisition_arg_vert.setContentsMargins(0, 0, 0, 0)
        self.acquisition_arg_vert.setSpacing(0)
        self.acquisition_arg_vert.setObjectName("acquisition_arg_vert")
        self.label_34 = QtWidgets.QLabel(self.layoutWidget)
        self.label_34.setObjectName("label_34")
        self.acquisition_arg_vert.addWidget(self.label_34)
        self.acquisition_type_combo_box = QtWidgets.QComboBox(self.layoutWidget)
        self.acquisition_type_combo_box.setStyleSheet("background-color:white;\n"
"                                            selection-color:rgb(255, 255, 255);\n"
"                                            selection-background-color:rgb(85, 170, 255);\n"
"                                        ")
        self.acquisition_type_combo_box.setObjectName("acquisition_type_combo_box")
        self.acquisition_type_combo_box.addItem("")
        self.acquisition_type_combo_box.addItem("")
        self.acquisition_arg_vert.addWidget(self.acquisition_type_combo_box)
        self.label_35 = QtWidgets.QLabel(self.layoutWidget)
        self.label_35.setObjectName("label_35")
        self.acquisition_arg_vert.addWidget(self.label_35)
        self.source_channel_combo_box = QtWidgets.QComboBox(self.layoutWidget)
        self.source_channel_combo_box.setStyleSheet("background-color:white;\n"
"                                            selection-color:rgb(255, 255, 255);\n"
"                                            selection-background-color:rgb(85, 170, 255);\n"
"                                        ")
        self.source_channel_combo_box.setObjectName("source_channel_combo_box")
        self.source_channel_combo_box.addItem("")
        self.source_channel_combo_box.addItem("")
        self.acquisition_arg_vert.addWidget(self.source_channel_combo_box)
        self.label_37 = QtWidgets.QLabel(self.layoutWidget)
        self.label_37.setObjectName("label_37")
        self.acquisition_arg_vert.addWidget(self.label_37)
        self.averages_spin_box = QtWidgets.QSpinBox(self.layoutWidget)
        self.averages_spin_box.setStyleSheet("background:white")
        self.averages_spin_box.setMinimum(1)
        self.averages_spin_box.setObjectName("averages_spin_box")
        self.acquisition_arg_vert.addWidget(self.averages_spin_box)
        self.waveform_data_out_frame = QtWidgets.QFrame(self.acquire_waveform_tab)
        self.waveform_data_out_frame.setGeometry(QtCore.QRect(260, 400, 441, 181))
        self.waveform_data_out_frame.setMinimumSize(QtCore.QSize(55, 0))
        self.waveform_data_out_frame.setStyleSheet("background:lightblue")
        self.waveform_data_out_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.waveform_data_out_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.waveform_data_out_frame.setObjectName("waveform_data_out_frame")
        self.label_39 = QtWidgets.QLabel(self.waveform_data_out_frame)
        self.label_39.setGeometry(QtCore.QRect(12, 61, 59, 16))
        self.label_39.setObjectName("label_39")
        self.label_40 = QtWidgets.QLabel(self.waveform_data_out_frame)
        self.label_40.setGeometry(QtCore.QRect(230, 61, 59, 16))
        self.label_40.setObjectName("label_40")
        self.x_data_type_view = QtWidgets.QTextBrowser(self.waveform_data_out_frame)
        self.x_data_type_view.setGeometry(QtCore.QRect(12, 80, 199, 21))
        self.x_data_type_view.setStyleSheet("background:lightgrey")
        self.x_data_type_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.x_data_type_view.setObjectName("x_data_type_view")
        self.y_data_type_view = QtWidgets.QTextBrowser(self.waveform_data_out_frame)
        self.y_data_type_view.setGeometry(QtCore.QRect(230, 80, 200, 21))
        self.y_data_type_view.setStyleSheet("background:lightgrey")
        self.y_data_type_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.y_data_type_view.setObjectName("y_data_type_view")
        self.layoutWidget_2 = QtWidgets.QWidget(self.waveform_data_out_frame)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 10, 135, 41))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.label_vert = QtWidgets.QVBoxLayout(self.layoutWidget_2)
        self.label_vert.setContentsMargins(0, 0, 0, 0)
        self.label_vert.setObjectName("label_vert")
        self.label_38 = QtWidgets.QLabel(self.layoutWidget_2)
        self.label_38.setObjectName("label_38")
        self.label_vert.addWidget(self.label_38)
        self.label_line_edit = QtWidgets.QLineEdit(self.layoutWidget_2)
        self.label_line_edit.setEnabled(False)
        self.label_line_edit.setStyleSheet("background:lightgrey")
        self.label_line_edit.setObjectName("label_line_edit")
        self.label_vert.addWidget(self.label_line_edit)
        self.layoutWidget1 = QtWidgets.QWidget(self.waveform_data_out_frame)
        self.layoutWidget1.setGeometry(QtCore.QRect(50, 120, 341, 41))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.x_data_grid = QtWidgets.QGridLayout(self.layoutWidget1)
        self.x_data_grid.setContentsMargins(0, 0, 0, 0)
        self.x_data_grid.setObjectName("x_data_grid")
        self.y_data_view = QtWidgets.QLineEdit(self.layoutWidget1)
        self.y_data_view.setEnabled(False)
        self.y_data_view.setStyleSheet("background:lightgrey")
        self.y_data_view.setText("")
        self.y_data_view.setObjectName("y_data_view")
        self.x_data_grid.addWidget(self.y_data_view, 1, 2, 1, 1)
        self.label_41 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_41.setObjectName("label_41")
        self.x_data_grid.addWidget(self.label_41, 0, 1, 1, 1)
        self.label_42 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_42.setObjectName("label_42")
        self.x_data_grid.addWidget(self.label_42, 0, 2, 1, 1)
        self.x_data_view = QtWidgets.QLineEdit(self.layoutWidget1)
        self.x_data_view.setEnabled(False)
        self.x_data_view.setStyleSheet("background:lightgrey")
        self.x_data_view.setText("")
        self.x_data_view.setObjectName("x_data_view")
        self.x_data_grid.addWidget(self.x_data_view, 1, 1, 1, 1)
        self.index_spinbox = QtWidgets.QSpinBox(self.layoutWidget1)
        self.index_spinbox.setMinimumSize(QtCore.QSize(70, 0))
        self.index_spinbox.setStyleSheet("background:white")
        self.index_spinbox.setMaximum(1000000000)
        self.index_spinbox.setObjectName("index_spinbox")
        self.x_data_grid.addWidget(self.index_spinbox, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        self.x_data_grid.addWidget(self.label, 0, 0, 1, 1)
        self.label_32 = QtWidgets.QLabel(self.acquire_waveform_tab)
        self.label_32.setGeometry(QtCore.QRect(260, 380, 201, 16))
        self.label_32.setObjectName("label_32")
        self.label_33 = QtWidgets.QLabel(self.acquire_waveform_tab)
        self.label_33.setGeometry(QtCore.QRect(60, 380, 75, 13))
        self.label_33.setObjectName("label_33")
        self.acquire_scope_trace_button = QtWidgets.QPushButton(self.acquire_waveform_tab)
        self.acquire_scope_trace_button.setGeometry(QtCore.QRect(710, 540, 171, 41))
        self.acquire_scope_trace_button.setStyleSheet("background:lightgrey")
        self.acquire_scope_trace_button.setObjectName("acquire_scope_trace_button")
        self.scan_tabs.addTab(self.acquire_waveform_tab, "")
        self.scan_setup_tab = QtWidgets.QWidget()
        self.scan_setup_tab.setObjectName("scan_setup_tab")
        self.label_44 = QtWidgets.QLabel(self.scan_setup_tab)
        self.label_44.setGeometry(QtCore.QRect(320, 150, 57, 13))
        self.label_44.setObjectName("label_44")
        self.scan_details_frame = QtWidgets.QFrame(self.scan_setup_tab)
        self.scan_details_frame.setGeometry(QtCore.QRect(320, 169, 241, 421))
        self.scan_details_frame.setStyleSheet("background:lightblue")
        self.scan_details_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.scan_details_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scan_details_frame.setObjectName("scan_details_frame")
        self.axis_pts_inc_frame = QtWidgets.QFrame(self.scan_details_frame)
        self.axis_pts_inc_frame.setGeometry(QtCore.QRect(0, 0, 241, 131))
        self.axis_pts_inc_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.axis_pts_inc_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.axis_pts_inc_frame.setLineWidth(1)
        self.axis_pts_inc_frame.setObjectName("axis_pts_inc_frame")
        self.layoutWidget_4 = QtWidgets.QWidget(self.axis_pts_inc_frame)
        self.layoutWidget_4.setGeometry(QtCore.QRect(10, 10, 224, 111))
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.axis_pts_inc_form = QtWidgets.QFormLayout(self.layoutWidget_4)
        self.axis_pts_inc_form.setContentsMargins(0, 0, 0, 0)
        self.axis_pts_inc_form.setHorizontalSpacing(29)
        self.axis_pts_inc_form.setVerticalSpacing(10)
        self.axis_pts_inc_form.setObjectName("axis_pts_inc_form")
        self.label_46 = QtWidgets.QLabel(self.layoutWidget_4)
        self.label_46.setObjectName("label_46")
        self.axis_pts_inc_form.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_46)
        self.axis_combo = QtWidgets.QComboBox(self.layoutWidget_4)
        self.axis_combo.setStyleSheet("background-color:white;\n"
"                                                selection-color:rgb(255, 255, 255);\n"
"                                                selection-background-color:rgb(85, 170, 255);\n"
"                                            ")
        self.axis_combo.setObjectName("axis_combo")
        self.axis_combo.addItem("")
        self.axis_combo.addItem("")
        self.axis_pts_inc_form.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.axis_combo)
        self.label_47 = QtWidgets.QLabel(self.layoutWidget_4)
        self.label_47.setObjectName("label_47")
        self.axis_pts_inc_form.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_47)
        self.pts_spin = QtWidgets.QSpinBox(self.layoutWidget_4)
        self.pts_spin.setStyleSheet("background:white")
        self.pts_spin.setMinimum(1)
        self.pts_spin.setMaximum(500000)
        self.pts_spin.setProperty("value", 40)
        self.pts_spin.setObjectName("pts_spin")
        self.axis_pts_inc_form.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.pts_spin)
        self.label_48 = QtWidgets.QLabel(self.layoutWidget_4)
        self.label_48.setObjectName("label_48")
        self.axis_pts_inc_form.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_48)
        self.increment_spin = QtWidgets.QDoubleSpinBox(self.layoutWidget_4)
        self.increment_spin.setStyleSheet("background:white")
        self.increment_spin.setDecimals(2)
        self.increment_spin.setMinimum(-99999.0)
        self.increment_spin.setMaximum(99999.0)
        self.increment_spin.setProperty("value", 0.4)
        self.increment_spin.setObjectName("increment_spin")
        self.axis_pts_inc_form.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.increment_spin)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget_4)
        self.label_2.setObjectName("label_2")
        self.axis_pts_inc_form.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.element_spinbox = QtWidgets.QSpinBox(self.layoutWidget_4)
        self.element_spinbox.setStyleSheet("background:white")
        self.element_spinbox.setMinimum(1)
        self.element_spinbox.setMaximum(10)
        self.element_spinbox.setObjectName("element_spinbox")
        self.axis_pts_inc_form.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.element_spinbox)
        self.label_53 = QtWidgets.QLabel(self.scan_details_frame)
        self.label_53.setGeometry(QtCore.QRect(12, 370, 69, 13))
        self.label_53.setObjectName("label_53")
        self.file_browser_button = QtWidgets.QPushButton(self.scan_details_frame)
        self.file_browser_button.setGeometry(QtCore.QRect(190, 370, 31, 20))
        self.file_browser_button.setStyleSheet("background:white")
        self.file_browser_button.setObjectName("file_browser_button")
        self.data_directory_input = QtWidgets.QLineEdit(self.scan_details_frame)
        self.data_directory_input.setEnabled(False)
        self.data_directory_input.setGeometry(QtCore.QRect(12, 390, 211, 20))
        self.data_directory_input.setStyleSheet("background:white")
        self.data_directory_input.setObjectName("data_directory_input")
        self.layoutWidget_5 = QtWidgets.QWidget(self.scan_details_frame)
        self.layoutWidget_5.setGeometry(QtCore.QRect(10, 140, 189, 39))
        self.layoutWidget_5.setObjectName("layoutWidget_5")
        self.ref_end_pos_grid = QtWidgets.QGridLayout(self.layoutWidget_5)
        self.ref_end_pos_grid.setContentsMargins(0, 0, 0, 0)
        self.ref_end_pos_grid.setObjectName("ref_end_pos_grid")
        self.label_49 = QtWidgets.QLabel(self.layoutWidget_5)
        self.label_49.setObjectName("label_49")
        self.ref_end_pos_grid.addWidget(self.label_49, 0, 0, 1, 1)
        self.label_50 = QtWidgets.QLabel(self.layoutWidget_5)
        self.label_50.setObjectName("label_50")
        self.ref_end_pos_grid.addWidget(self.label_50, 0, 1, 1, 1)
        self.ref_pos_combo = QtWidgets.QComboBox(self.layoutWidget_5)
        self.ref_pos_combo.setStyleSheet("background-color:white;\n"
"                                            selection-color:rgb(255, 255, 255);\n"
"                                            selection-background-color:rgb(85, 170, 255);\n"
"                                        ")
        self.ref_pos_combo.setObjectName("ref_pos_combo")
        self.ref_pos_combo.addItem("")
        self.ref_pos_combo.addItem("")
        self.ref_pos_combo.addItem("")
        self.ref_end_pos_grid.addWidget(self.ref_pos_combo, 1, 0, 1, 1)
        self.end_pos_combo = QtWidgets.QComboBox(self.layoutWidget_5)
        self.end_pos_combo.setStyleSheet("background-color:white;\n"
"                                            selection-color:rgb(255, 255, 255);\n"
"                                            selection-background-color:rgb(85, 170, 255);\n"
"                                        ")
        self.end_pos_combo.setObjectName("end_pos_combo")
        self.end_pos_combo.addItem("")
        self.end_pos_combo.addItem("")
        self.ref_end_pos_grid.addWidget(self.end_pos_combo, 1, 1, 1, 1)
        self.layoutWidget_6 = QtWidgets.QWidget(self.scan_details_frame)
        self.layoutWidget_6.setGeometry(QtCore.QRect(10, 180, 211, 41))
        self.layoutWidget_6.setObjectName("layoutWidget_6")
        self.comments_vert = QtWidgets.QVBoxLayout(self.layoutWidget_6)
        self.comments_vert.setContentsMargins(0, 0, 0, 0)
        self.comments_vert.setObjectName("comments_vert")
        self.label_51 = QtWidgets.QLabel(self.layoutWidget_6)
        self.label_51.setObjectName("label_51")
        self.comments_vert.addWidget(self.label_51)
        self.comments_input = QtWidgets.QLineEdit(self.layoutWidget_6)
        self.comments_input.setStyleSheet("background:white")
        self.comments_input.setObjectName("comments_input")
        self.comments_vert.addWidget(self.comments_input)
        self.layoutWidget_7 = QtWidgets.QWidget(self.scan_details_frame)
        self.layoutWidget_7.setGeometry(QtCore.QRect(10, 230, 131, 41))
        self.layoutWidget_7.setObjectName("layoutWidget_7")
        self.filename_stub_vert = QtWidgets.QVBoxLayout(self.layoutWidget_7)
        self.filename_stub_vert.setContentsMargins(0, 0, 0, 0)
        self.filename_stub_vert.setObjectName("filename_stub_vert")
        self.label_52 = QtWidgets.QLabel(self.layoutWidget_7)
        self.label_52.setObjectName("label_52")
        self.filename_stub_vert.addWidget(self.label_52)
        self.filename_stub_input = QtWidgets.QLineEdit(self.layoutWidget_7)
        self.filename_stub_input.setStyleSheet("background:white")
        self.filename_stub_input.setObjectName("filename_stub_input")
        self.filename_stub_vert.addWidget(self.filename_stub_input)
        self.store_state_combo = QtWidgets.QComboBox(self.scan_details_frame)
        self.store_state_combo.setGeometry(QtCore.QRect(12, 343, 141, 18))
        self.store_state_combo.setStyleSheet("background-color:white;\n"
"                                selection-color:rgb(255, 255, 255);\n"
"                                selection-background-color:rgb(85, 170, 255);\n"
"                            ")
        self.store_state_combo.setObjectName("store_state_combo")
        self.store_state_combo.addItem("")
        self.store_state_combo.addItem("")
        self.store_state_combo.addItem("")
        self.label_59 = QtWidgets.QLabel(self.scan_details_frame)
        self.label_59.setGeometry(QtCore.QRect(12, 330, 129, 13))
        self.label_59.setObjectName("label_59")
        self.layoutWidget_9 = QtWidgets.QWidget(self.scan_details_frame)
        self.layoutWidget_9.setGeometry(QtCore.QRect(10, 280, 211, 41))
        self.layoutWidget_9.setObjectName("layoutWidget_9")
        self.comments_vert_2 = QtWidgets.QVBoxLayout(self.layoutWidget_9)
        self.comments_vert_2.setContentsMargins(0, 0, 0, 0)
        self.comments_vert_2.setObjectName("comments_vert_2")
        self.label_61 = QtWidgets.QLabel(self.layoutWidget_9)
        self.label_61.setObjectName("label_61")
        self.comments_vert_2.addWidget(self.label_61)
        self.serial_input = QtWidgets.QLineEdit(self.layoutWidget_9)
        self.serial_input.setStyleSheet("background:white")
        self.serial_input.setObjectName("serial_input")
        self.comments_vert_2.addWidget(self.serial_input)
        self.start_scan_button = QtWidgets.QPushButton(self.scan_setup_tab)
        self.start_scan_button.setGeometry(QtCore.QRect(610, 380, 111, 31))
        self.start_scan_button.setStyleSheet("background:lightgrey")
        self.start_scan_button.setObjectName("start_scan_button")
        self.layoutWidget_8 = QtWidgets.QWidget(self.scan_setup_tab)
        self.layoutWidget_8.setGeometry(QtCore.QRect(610, 170, 162, 207))
        self.layoutWidget_8.setObjectName("layoutWidget_8")
        self.acquisition_settings_vert = QtWidgets.QVBoxLayout(self.layoutWidget_8)
        self.acquisition_settings_vert.setContentsMargins(0, 0, 0, 0)
        self.acquisition_settings_vert.setObjectName("acquisition_settings_vert")
        self.label_45 = QtWidgets.QLabel(self.layoutWidget_8)
        self.label_45.setObjectName("label_45")
        self.acquisition_settings_vert.addWidget(self.label_45)
        self.acquisition_settings_frame = QtWidgets.QFrame(self.layoutWidget_8)
        self.acquisition_settings_frame.setStyleSheet("background:lightblue")
        self.acquisition_settings_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.acquisition_settings_frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.acquisition_settings_frame.setObjectName("acquisition_settings_frame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.acquisition_settings_frame)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_54 = QtWidgets.QLabel(self.acquisition_settings_frame)
        self.label_54.setObjectName("label_54")
        self.verticalLayout_5.addWidget(self.label_54)
        self.acquisition_type_combo = QtWidgets.QComboBox(self.acquisition_settings_frame)
        self.acquisition_type_combo.setStyleSheet("background-color:white;\n"
"                                                    selection-color:rgb(255, 255, 255);\n"
"                                                    selection-background-color:rgb(85, 170, 255);\n"
"                                                ")
        self.acquisition_type_combo.setObjectName("acquisition_type_combo")
        self.acquisition_type_combo.addItem("")
        self.acquisition_type_combo.addItem("")
        self.verticalLayout_5.addWidget(self.acquisition_type_combo)
        self.label_56 = QtWidgets.QLabel(self.acquisition_settings_frame)
        self.label_56.setObjectName("label_56")
        self.verticalLayout_5.addWidget(self.label_56)
        self.source_channel_combo = QtWidgets.QComboBox(self.acquisition_settings_frame)
        self.source_channel_combo.setStyleSheet("background-color:white;\n"
"                                                    selection-color:rgb(255, 255, 255);\n"
"                                                    selection-background-color:rgb(85, 170, 255);\n"
"                                                ")
        self.source_channel_combo.setObjectName("source_channel_combo")
        self.source_channel_combo.addItem("")
        self.source_channel_combo.addItem("")
        self.verticalLayout_5.addWidget(self.source_channel_combo)
        self.label_57 = QtWidgets.QLabel(self.acquisition_settings_frame)
        self.label_57.setObjectName("label_57")
        self.verticalLayout_5.addWidget(self.label_57)
        self.window_combo_box_2 = QtWidgets.QComboBox(self.acquisition_settings_frame)
        self.window_combo_box_2.setEnabled(False)
        self.window_combo_box_2.setStyleSheet("background-color:white;\n"
"                                                    selection-color:rgb(255, 255, 255);\n"
"                                                    selection-background-color:rgb(85, 170, 255);\n"
"                                                ")
        self.window_combo_box_2.setObjectName("window_combo_box_2")
        self.window_combo_box_2.addItem("")
        self.verticalLayout_5.addWidget(self.window_combo_box_2)
        self.label_58 = QtWidgets.QLabel(self.acquisition_settings_frame)
        self.label_58.setObjectName("label_58")
        self.verticalLayout_5.addWidget(self.label_58)
        self.averages_spin_box_2 = QtWidgets.QSpinBox(self.acquisition_settings_frame)
        self.averages_spin_box_2.setStyleSheet("background:white")
        self.averages_spin_box_2.setObjectName("averages_spin_box_2")
        self.verticalLayout_5.addWidget(self.averages_spin_box_2)
        self.acquisition_settings_vert.addWidget(self.acquisition_settings_frame)
        self.tooltip_scan_setup = QtWidgets.QWidget(self.scan_setup_tab)
        self.tooltip_scan_setup.setGeometry(QtCore.QRect(0, 0, 1020, 130))
        self.tooltip_scan_setup.setObjectName("tooltip_scan_setup")
        self.scan_tabs.addTab(self.scan_setup_tab, "")

        self.retranslateUi(scan_tab_widget)
        self.scan_tabs.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(scan_tab_widget)

    def retranslateUi(self, scan_tab_widget):
        _translate = QtCore.QCoreApplication.translate
        scan_tab_widget.setWindowTitle(_translate("scan_tab_widget", "Form"))
        self.last_acquired_waveform_plot_label.setToolTip(_translate("scan_tab_widget", "The 1D Scan tab shows the last acquired waveform with voltage over time, and profile\n"
"                            graph\n"
"                            that shows the voltage squared interval over time. Both these are supplied by the\n"
"                            oscilloscope.\n"
"                        "))
        self.last_acquired_waveform_plot_label.setText(_translate("scan_tab_widget", "Last Aquired Waveform"))
        self.label_55.setText(_translate("scan_tab_widget", "Profile"))
        self.scan_tabs.setTabText(self.scan_tabs.indexOf(self.one_dimension_scan_tab), _translate("scan_tab_widget", "1D Scan"))
        self.label_31.setToolTip(_translate("scan_tab_widget", "The acquire waveform tab allows for more control over capturing the voltage waveform,\n"
"                            such as specifying the acquisition type, source channel, averages, etc. A script isn\'t\n"
"                            needed as you request a trace via button.\n"
"                        "))
        self.label_31.setText(_translate("scan_tab_widget", "Acquired waveform"))
        self.label_34.setText(_translate("scan_tab_widget", "Acquisition Type"))
        self.acquisition_type_combo_box.setItemText(0, _translate("scan_tab_widget", "Single Waveform"))
        self.acquisition_type_combo_box.setItemText(1, _translate("scan_tab_widget", "N Averaged Waveform"))
        self.label_35.setText(_translate("scan_tab_widget", "Source Channel"))
        self.source_channel_combo_box.setItemText(0, _translate("scan_tab_widget", "1"))
        self.source_channel_combo_box.setItemText(1, _translate("scan_tab_widget", "2"))
        self.label_37.setText(_translate("scan_tab_widget", "Averages"))
        self.label_39.setText(_translate("scan_tab_widget", "X Data Type"))
        self.label_40.setText(_translate("scan_tab_widget", "Y Data Type"))
        self.x_data_type_view.setHtml(_translate("scan_tab_widget", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                                </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                                 </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                                 </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Time (s)                             </p></body></html>"))
        self.y_data_type_view.setHtml(_translate("scan_tab_widget", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                                </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                                 </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">                                 </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Voltage (V)                             </p></body></html>"))
        self.label_38.setText(_translate("scan_tab_widget", "Label"))
        self.label_41.setText(_translate("scan_tab_widget", "X Data"))
        self.label_42.setText(_translate("scan_tab_widget", "Y Data"))
        self.label.setText(_translate("scan_tab_widget", "Index"))
        self.label_32.setText(_translate("scan_tab_widget", "Waveform data out"))
        self.label_33.setText(_translate("scan_tab_widget", "Acquisition Arg."))
        self.acquire_scope_trace_button.setText(_translate("scan_tab_widget", "Aqcuire Scope Trace"))
        self.scan_tabs.setTabText(self.scan_tabs.indexOf(self.acquire_waveform_tab), _translate("scan_tab_widget", "Acquire Waveform"))
        self.label_44.setText(_translate("scan_tab_widget", "Scan details"))
        self.label_46.setText(_translate("scan_tab_widget", "Axis"))
        self.axis_combo.setItemText(0, _translate("scan_tab_widget", "X"))
        self.axis_combo.setItemText(1, _translate("scan_tab_widget", "Theta"))
        self.label_47.setText(_translate("scan_tab_widget", "# of Pts."))
        self.label_48.setText(_translate("scan_tab_widget", "Increment (deg or mm)"))
        self.label_2.setText(_translate("scan_tab_widget", "Element"))
        self.label_53.setText(_translate("scan_tab_widget", "Data directory"))
        self.file_browser_button.setText(_translate("scan_tab_widget", "📁"))
        self.data_directory_input.setText(_translate("scan_tab_widget", "UA Results Directory"))
        self.label_49.setText(_translate("scan_tab_widget", "Ref Position"))
        self.label_50.setText(_translate("scan_tab_widget", "End position"))
        self.ref_pos_combo.setItemText(0, _translate("scan_tab_widget", "Hydrophone"))
        self.ref_pos_combo.setItemText(1, _translate("scan_tab_widget", "Down"))
        self.ref_pos_combo.setItemText(2, _translate("scan_tab_widget", "RFB"))
        self.end_pos_combo.setItemText(0, _translate("scan_tab_widget", "Peak (1D)"))
        self.end_pos_combo.setItemText(1, _translate("scan_tab_widget", "End of range"))
        self.label_51.setText(_translate("scan_tab_widget", "Comments"))
        self.label_52.setText(_translate("scan_tab_widget", "Filename stub"))
        self.filename_stub_input.setText(_translate("scan_tab_widget", "FindElement"))
        self.store_state_combo.setItemText(0, _translate("scan_tab_widget", "Store entire waveform"))
        self.store_state_combo.setItemText(1, _translate("scan_tab_widget", "Store profiles only"))
        self.store_state_combo.setItemText(2, _translate("scan_tab_widget", "Do not store"))
        self.label_59.setText(_translate("scan_tab_widget", "Save Type"))
        self.label_61.setText(_translate("scan_tab_widget", "Serial Number"))
        self.start_scan_button.setText(_translate("scan_tab_widget", "Start Scan"))
        self.label_45.setText(_translate("scan_tab_widget", "Acquisition settings"))
        self.label_54.setText(_translate("scan_tab_widget", "Acquisition type"))
        self.acquisition_type_combo.setItemText(0, _translate("scan_tab_widget", "Single Waveform"))
        self.acquisition_type_combo.setItemText(1, _translate("scan_tab_widget", "N Averaged Waveform"))
        self.label_56.setText(_translate("scan_tab_widget", "Source Channel"))
        self.source_channel_combo.setItemText(0, _translate("scan_tab_widget", "Channel 1"))
        self.source_channel_combo.setItemText(1, _translate("scan_tab_widget", "Channel 2"))
        self.label_57.setText(_translate("scan_tab_widget", "Window (FFT only)"))
        self.window_combo_box_2.setToolTip(_translate("scan_tab_widget", "<html><head/><body><p>This feature is\n"
"                                                    built into the graphing library. Right click a graph for window\n"
"                                                    options</p></body></html>\n"
"                                                "))
        self.window_combo_box_2.setItemText(0, _translate("scan_tab_widget", "Blackman-Harris"))
        self.label_58.setText(_translate("scan_tab_widget", "Averages"))
        self.tooltip_scan_setup.setToolTip(_translate("scan_tab_widget", "The scan tab allows you to perform scans on individual elements to your desired\n"
"                            specifications. This tab can be used without a script, as you are trigger this tab manually.\n"
"                        "))
        self.scan_tabs.setTabText(self.scan_tabs.indexOf(self.scan_setup_tab), _translate("scan_tab_widget", "Scan Setup"))

from ui_elements.ui_oscilloscope_plot import Plot

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    scan_tab_widget = QtWidgets.QWidget()
    ui = Ui_scan_tab_widget()
    ui.setupUi(scan_tab_widget)
    scan_tab_widget.show()
    sys.exit(app.exec_())


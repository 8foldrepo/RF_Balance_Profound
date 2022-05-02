# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_find_element.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_FIND_ELEMENT_WIDGET(object):
    def setupUi(self, FIND_ELEMENT_WIDGET):
        FIND_ELEMENT_WIDGET.setObjectName("FIND_ELEMENT_WIDGET")
        FIND_ELEMENT_WIDGET.resize(470, 560)
        FIND_ELEMENT_WIDGET.setMinimumSize(QtCore.QSize(470, 560))
        self.frame = QtWidgets.QFrame(FIND_ELEMENT_WIDGET)
        self.frame.setGeometry(QtCore.QRect(10, 10, 450, 131))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setLineWidth(2)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 130, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 91, 16))
        self.label_2.setObjectName("label_2")
        self.ELEMENT_SELECTION_FIELD = QtWidgets.QComboBox(self.frame)
        self.ELEMENT_SELECTION_FIELD.setGeometry(QtCore.QRect(100, 40, 75, 20))
        self.ELEMENT_SELECTION_FIELD.setObjectName("ELEMENT_SELECTION_FIELD")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.X_INCREMENT_FIELD = QtWidgets.QDoubleSpinBox(self.frame)
        self.X_INCREMENT_FIELD.setGeometry(QtCore.QRect(100, 70, 90, 20))
        self.X_INCREMENT_FIELD.setToolTip("")
        self.X_INCREMENT_FIELD.setStatusTip("")
        self.X_INCREMENT_FIELD.setWhatsThis("")
        self.X_INCREMENT_FIELD.setPrefix("")
        self.X_INCREMENT_FIELD.setDecimals(4)
        self.X_INCREMENT_FIELD.setMinimum(-500.0)
        self.X_INCREMENT_FIELD.setMaximum(500.0)
        self.X_INCREMENT_FIELD.setSingleStep(0.0001)
        self.X_INCREMENT_FIELD.setObjectName("X_INCREMENT_FIELD")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(10, 70, 92, 16))
        self.label_3.setObjectName("label_3")
        self.THETA_INCREMENT_FIELD = QtWidgets.QDoubleSpinBox(self.frame)
        self.THETA_INCREMENT_FIELD.setGeometry(QtCore.QRect(300, 70, 115, 20))
        self.THETA_INCREMENT_FIELD.setToolTip("")
        self.THETA_INCREMENT_FIELD.setStatusTip("")
        self.THETA_INCREMENT_FIELD.setWhatsThis("")
        self.THETA_INCREMENT_FIELD.setPrefix("")
        self.THETA_INCREMENT_FIELD.setDecimals(0)
        self.THETA_INCREMENT_FIELD.setMinimum(-360.0)
        self.THETA_INCREMENT_FIELD.setMaximum(360.0)
        self.THETA_INCREMENT_FIELD.setSingleStep(1.0)
        self.THETA_INCREMENT_FIELD.setObjectName("THETA_INCREMENT_FIELD")
        self.label_22 = QtWidgets.QLabel(self.frame)
        self.label_22.setGeometry(QtCore.QRect(210, 70, 111, 16))
        self.label_22.setObjectName("label_22")
        self.X_PNT_FIELD = QtWidgets.QSpinBox(self.frame)
        self.X_PNT_FIELD.setGeometry(QtCore.QRect(100, 100, 90, 20))
        self.X_PNT_FIELD.setToolTip("")
        self.X_PNT_FIELD.setStatusTip("")
        self.X_PNT_FIELD.setWhatsThis("")
        self.X_PNT_FIELD.setObjectName("X_PNT_FIELD")
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setGeometry(QtCore.QRect(10, 100, 92, 16))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.frame)
        self.label_6.setGeometry(QtCore.QRect(210, 100, 111, 16))
        self.label_6.setObjectName("label_6")
        self.THETA_PNT_FIELD = QtWidgets.QSpinBox(self.frame)
        self.THETA_PNT_FIELD.setGeometry(QtCore.QRect(300, 100, 115, 20))
        self.THETA_PNT_FIELD.setToolTip("")
        self.THETA_PNT_FIELD.setStatusTip("")
        self.THETA_PNT_FIELD.setWhatsThis("")
        self.THETA_PNT_FIELD.setObjectName("THETA_PNT_FIELD")
        self.frame_2 = QtWidgets.QFrame(FIND_ELEMENT_WIDGET)
        self.frame_2.setGeometry(QtCore.QRect(10, 150, 450, 191))
        self.frame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setLineWidth(2)
        self.frame_2.setObjectName("frame_2")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(10, 10, 161, 16))
        self.label_4.setObjectName("label_4")
        self.OSCOPE_CHANNEL_FIELD = QtWidgets.QComboBox(self.frame_2)
        self.OSCOPE_CHANNEL_FIELD.setGeometry(QtCore.QRect(100, 40, 75, 20))
        self.OSCOPE_CHANNEL_FIELD.setObjectName("OSCOPE_CHANNEL_FIELD")
        self.OSCOPE_CHANNEL_FIELD.addItem("")
        self.OSCOPE_CHANNEL_FIELD.addItem("")
        self.OSCOPE_CHANNEL_FIELD.addItem("")
        self.OSCOPE_CHANNEL_FIELD.addItem("")
        self.label_7 = QtWidgets.QLabel(self.frame_2)
        self.label_7.setGeometry(QtCore.QRect(10, 40, 75, 16))
        self.label_7.setObjectName("label_7")
        self.OSCOPE_AQTYPE_FIELD = QtWidgets.QComboBox(self.frame_2)
        self.OSCOPE_AQTYPE_FIELD.setGeometry(QtCore.QRect(100, 70, 81, 20))
        self.OSCOPE_AQTYPE_FIELD.setObjectName("OSCOPE_AQTYPE_FIELD")
        self.OSCOPE_AQTYPE_FIELD.addItem("")
        self.OSCOPE_AQTYPE_FIELD.addItem("")
        self.label_8 = QtWidgets.QLabel(self.frame_2)
        self.label_8.setGeometry(QtCore.QRect(10, 70, 85, 16))
        self.label_8.setObjectName("label_8")
        self.OSCOPE_SAMPLES_FIELD = QtWidgets.QComboBox(self.frame_2)
        self.OSCOPE_SAMPLES_FIELD.setGeometry(QtCore.QRect(310, 70, 90, 20))
        self.OSCOPE_SAMPLES_FIELD.setObjectName("OSCOPE_SAMPLES_FIELD")
        self.OSCOPE_SAMPLES_FIELD.addItem("")
        self.OSCOPE_SAMPLES_FIELD.addItem("")
        self.OSCOPE_SAMPLES_FIELD.addItem("")
        self.OSCOPE_SAMPLES_FIELD.addItem("")
        self.OSCOPE_SAMPLES_FIELD.addItem("")
        self.OSCOPE_SAMPLES_FIELD.addItem("")
        self.OSCOPE_SAMPLES_FIELD.addItem("")
        self.OSCOPE_SAMPLES_FIELD.addItem("")
        self.label_9 = QtWidgets.QLabel(self.frame_2)
        self.label_9.setGeometry(QtCore.QRect(210, 70, 101, 16))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.frame_2)
        self.label_10.setGeometry(QtCore.QRect(10, 100, 80, 16))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.frame_2)
        self.label_11.setGeometry(QtCore.QRect(210, 100, 70, 16))
        self.label_11.setObjectName("label_11")
        self.OSCOPE_CYCLES_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.OSCOPE_CYCLES_FIELD.setGeometry(QtCore.QRect(100, 100, 86, 20))
        self.OSCOPE_CYCLES_FIELD.setToolTip("")
        self.OSCOPE_CYCLES_FIELD.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD.setPrefix("")
        self.OSCOPE_CYCLES_FIELD.setSuffix("")
        self.OSCOPE_CYCLES_FIELD.setDecimals(0)
        self.OSCOPE_CYCLES_FIELD.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD.setMaximum(1000000.0)
        self.OSCOPE_CYCLES_FIELD.setSingleStep(1.0)
        self.OSCOPE_CYCLES_FIELD.setObjectName("OSCOPE_CYCLES_FIELD")
        self.OSCOPE_DELAYCYCLE_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.OSCOPE_DELAYCYCLE_FIELD.setGeometry(QtCore.QRect(310, 100, 71, 20))
        self.OSCOPE_DELAYCYCLE_FIELD.setToolTip("")
        self.OSCOPE_DELAYCYCLE_FIELD.setStatusTip("")
        self.OSCOPE_DELAYCYCLE_FIELD.setWhatsThis("")
        self.OSCOPE_DELAYCYCLE_FIELD.setPrefix("")
        self.OSCOPE_DELAYCYCLE_FIELD.setSuffix("")
        self.OSCOPE_DELAYCYCLE_FIELD.setDecimals(0)
        self.OSCOPE_DELAYCYCLE_FIELD.setMinimum(0.0)
        self.OSCOPE_DELAYCYCLE_FIELD.setMaximum(1000000.0)
        self.OSCOPE_DELAYCYCLE_FIELD.setSingleStep(1.0)
        self.OSCOPE_DELAYCYCLE_FIELD.setObjectName("OSCOPE_DELAYCYCLE_FIELD")
        self.OSCOPE_AUTO_CHECKBOX = QtWidgets.QCheckBox(self.frame_2)
        self.OSCOPE_AUTO_CHECKBOX.setGeometry(QtCore.QRect(210, 40, 91, 17))
        self.OSCOPE_AUTO_CHECKBOX.setObjectName("OSCOPE_AUTO_CHECKBOX")
        self.label_12 = QtWidgets.QLabel(self.frame_2)
        self.label_12.setGeometry(QtCore.QRect(10, 130, 71, 16))
        self.label_12.setObjectName("label_12")
        self.OSCOPE_DATASTORE_FIELD = QtWidgets.QComboBox(self.frame_2)
        self.OSCOPE_DATASTORE_FIELD.setGeometry(QtCore.QRect(100, 130, 81, 20))
        self.OSCOPE_DATASTORE_FIELD.setObjectName("OSCOPE_DATASTORE_FIELD")
        self.OSCOPE_DATASTORE_FIELD.addItem("")
        self.OSCOPE_DATASTORE_FIELD.addItem("")
        self.OSCOPE_DATASTORE_FIELD.addItem("")
        self.label_13 = QtWidgets.QLabel(self.frame_2)
        self.label_13.setGeometry(QtCore.QRect(210, 130, 85, 16))
        self.label_13.setObjectName("label_13")
        self.OSCOPE_DATALOC_FIELD = QtWidgets.QComboBox(self.frame_2)
        self.OSCOPE_DATALOC_FIELD.setGeometry(QtCore.QRect(310, 130, 131, 20))
        self.OSCOPE_DATALOC_FIELD.setObjectName("OSCOPE_DATALOC_FIELD")
        self.OSCOPE_DATALOC_FIELD.addItem("")
        self.OSCOPE_DATALOC_FIELD.addItem("")
        self.label_14 = QtWidgets.QLabel(self.frame_2)
        self.label_14.setGeometry(QtCore.QRect(10, 160, 81, 16))
        self.label_14.setObjectName("label_14")
        self.OSCOPE_DATA_DIRECTORY_FIELD = QtWidgets.QLineEdit(self.frame_2)
        self.OSCOPE_DATA_DIRECTORY_FIELD.setGeometry(QtCore.QRect(100, 160, 200, 20))
        self.OSCOPE_DATA_DIRECTORY_FIELD.setObjectName("OSCOPE_DATA_DIRECTORY_FIELD")
        self.OSCOPE_DATA_DIRECTORY_BUTTON = QtWidgets.QPushButton(self.frame_2)
        self.OSCOPE_DATA_DIRECTORY_BUTTON.setGeometry(QtCore.QRect(310, 160, 75, 20))
        self.OSCOPE_DATA_DIRECTORY_BUTTON.setObjectName("OSCOPE_DATA_DIRECTORY_BUTTON")
        self.frame_3 = QtWidgets.QFrame(FIND_ELEMENT_WIDGET)
        self.frame_3.setGeometry(QtCore.QRect(10, 350, 450, 201))
        self.frame_3.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setLineWidth(2)
        self.frame_3.setObjectName("frame_3")
        self.label_15 = QtWidgets.QLabel(self.frame_3)
        self.label_15.setGeometry(QtCore.QRect(10, 10, 161, 16))
        self.label_15.setObjectName("label_15")
        self.label_16 = QtWidgets.QLabel(self.frame_3)
        self.label_16.setGeometry(QtCore.QRect(10, 30, 91, 16))
        self.label_16.setObjectName("label_16")
        self.FREQANG_PRESET_FIELD = QtWidgets.QComboBox(self.frame_3)
        self.FREQANG_PRESET_FIELD.setGeometry(QtCore.QRect(100, 30, 131, 20))
        self.FREQANG_PRESET_FIELD.setObjectName("FREQANG_PRESET_FIELD")
        self.FREQANG_PRESET_FIELD.addItem("")
        self.FREQANG_PRESET_FIELD.addItem("")
        self.FREQANG_PRESET_FIELD.addItem("")
        self.FREQANG_PRESET_FIELD.addItem("")
        self.FREQANG_PRESET_FIELD.addItem("")
        self.FREQANG_BURST_FIELD = QtWidgets.QDoubleSpinBox(self.frame_3)
        self.FREQANG_BURST_FIELD.setGeometry(QtCore.QRect(310, 60, 131, 20))
        self.FREQANG_BURST_FIELD.setToolTip("")
        self.FREQANG_BURST_FIELD.setStatusTip("")
        self.FREQANG_BURST_FIELD.setWhatsThis("")
        self.FREQANG_BURST_FIELD.setPrefix("")
        self.FREQANG_BURST_FIELD.setDecimals(0)
        self.FREQANG_BURST_FIELD.setMinimum(0.0)
        self.FREQANG_BURST_FIELD.setMaximum(1000000.0)
        self.FREQANG_BURST_FIELD.setSingleStep(1.0)
        self.FREQANG_BURST_FIELD.setObjectName("FREQANG_BURST_FIELD")
        self.label_17 = QtWidgets.QLabel(self.frame_3)
        self.label_17.setGeometry(QtCore.QRect(210, 60, 70, 16))
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(self.frame_3)
        self.label_18.setGeometry(QtCore.QRect(10, 60, 85, 16))
        self.label_18.setObjectName("label_18")
        self.FREQANG_FREQ_FIELD = QtWidgets.QDoubleSpinBox(self.frame_3)
        self.FREQANG_FREQ_FIELD.setGeometry(QtCore.QRect(100, 60, 105, 20))
        self.FREQANG_FREQ_FIELD.setToolTip("")
        self.FREQANG_FREQ_FIELD.setStatusTip("")
        self.FREQANG_FREQ_FIELD.setWhatsThis("")
        self.FREQANG_FREQ_FIELD.setPrefix("")
        self.FREQANG_FREQ_FIELD.setDecimals(4)
        self.FREQANG_FREQ_FIELD.setMinimum(0.0)
        self.FREQANG_FREQ_FIELD.setMaximum(20.0)
        self.FREQANG_FREQ_FIELD.setSingleStep(0.0001)
        self.FREQANG_FREQ_FIELD.setObjectName("FREQANG_FREQ_FIELD")
        self.FREQANG_VOLT_FIELD = QtWidgets.QDoubleSpinBox(self.frame_3)
        self.FREQANG_VOLT_FIELD.setGeometry(QtCore.QRect(100, 90, 105, 20))
        self.FREQANG_VOLT_FIELD.setToolTip("")
        self.FREQANG_VOLT_FIELD.setStatusTip("")
        self.FREQANG_VOLT_FIELD.setWhatsThis("")
        self.FREQANG_VOLT_FIELD.setPrefix("")
        self.FREQANG_VOLT_FIELD.setDecimals(0)
        self.FREQANG_VOLT_FIELD.setMinimum(-10000.0)
        self.FREQANG_VOLT_FIELD.setMaximum(10000.0)
        self.FREQANG_VOLT_FIELD.setSingleStep(1.0)
        self.FREQANG_VOLT_FIELD.setObjectName("FREQANG_VOLT_FIELD")
        self.label_19 = QtWidgets.QLabel(self.frame_3)
        self.label_19.setGeometry(QtCore.QRect(10, 90, 80, 16))
        self.label_19.setObjectName("label_19")
        self.label_20 = QtWidgets.QLabel(self.frame_3)
        self.label_20.setGeometry(QtCore.QRect(10, 140, 131, 16))
        self.label_20.setObjectName("label_20")
        self.FREQANG_ANG_FIELD = QtWidgets.QDoubleSpinBox(self.frame_3)
        self.FREQANG_ANG_FIELD.setGeometry(QtCore.QRect(150, 140, 131, 20))
        self.FREQANG_ANG_FIELD.setToolTip("")
        self.FREQANG_ANG_FIELD.setStatusTip("")
        self.FREQANG_ANG_FIELD.setWhatsThis("")
        self.FREQANG_ANG_FIELD.setPrefix("")
        self.FREQANG_ANG_FIELD.setDecimals(0)
        self.FREQANG_ANG_FIELD.setMinimum(-360.0)
        self.FREQANG_ANG_FIELD.setMaximum(360.0)
        self.FREQANG_ANG_FIELD.setSingleStep(1.0)
        self.FREQANG_ANG_FIELD.setObjectName("FREQANG_ANG_FIELD")
        self.FREQANG_ANG_TEST_CHECKBOX = QtWidgets.QCheckBox(self.frame_3)
        self.FREQANG_ANG_TEST_CHECKBOX.setGeometry(QtCore.QRect(310, 140, 91, 17))
        self.FREQANG_ANG_TEST_CHECKBOX.setObjectName("FREQANG_ANG_TEST_CHECKBOX")
        self.FREQANG_POS_TEST_CHECKBOX = QtWidgets.QCheckBox(self.frame_3)
        self.FREQANG_POS_TEST_CHECKBOX.setGeometry(QtCore.QRect(310, 170, 91, 17))
        self.FREQANG_POS_TEST_CHECKBOX.setObjectName("FREQANG_POS_TEST_CHECKBOX")
        self.FREQANG_POS_FIELD = QtWidgets.QDoubleSpinBox(self.frame_3)
        self.FREQANG_POS_FIELD.setGeometry(QtCore.QRect(150, 170, 131, 20))
        self.FREQANG_POS_FIELD.setToolTip("")
        self.FREQANG_POS_FIELD.setStatusTip("")
        self.FREQANG_POS_FIELD.setWhatsThis("")
        self.FREQANG_POS_FIELD.setPrefix("")
        self.FREQANG_POS_FIELD.setDecimals(3)
        self.FREQANG_POS_FIELD.setMinimum(-100.0)
        self.FREQANG_POS_FIELD.setMaximum(100.0)
        self.FREQANG_POS_FIELD.setSingleStep(0.001)
        self.FREQANG_POS_FIELD.setObjectName("FREQANG_POS_FIELD")
        self.label_21 = QtWidgets.QLabel(self.frame_3)
        self.label_21.setGeometry(QtCore.QRect(10, 170, 131, 16))
        self.label_21.setObjectName("label_21")

        self.retranslateUi(FIND_ELEMENT_WIDGET)
        QtCore.QMetaObject.connectSlotsByName(FIND_ELEMENT_WIDGET)

    def retranslateUi(self, FIND_ELEMENT_WIDGET):
        _translate = QtCore.QCoreApplication.translate
        FIND_ELEMENT_WIDGET.setWindowTitle(_translate("FIND_ELEMENT_WIDGET", "Find Element"))
        self.label.setText(_translate("FIND_ELEMENT_WIDGET",
                                      "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600; text-decoration: underline;\">Element Positioning</span></p></body></html>"))
        self.label_2.setText(_translate("FIND_ELEMENT_WIDGET", "Element Selected:"))
        self.ELEMENT_SELECTION_FIELD.setItemText(0, _translate("FIND_ELEMENT_WIDGET", "Element 1"))
        self.ELEMENT_SELECTION_FIELD.setItemText(1, _translate("FIND_ELEMENT_WIDGET", "Element 2"))
        self.ELEMENT_SELECTION_FIELD.setItemText(2, _translate("FIND_ELEMENT_WIDGET", "Element 3"))
        self.X_INCREMENT_FIELD.setSuffix(_translate("FIND_ELEMENT_WIDGET", " mm"))
        self.label_3.setText(_translate("FIND_ELEMENT_WIDGET", "X-Axis Increment:"))
        self.THETA_INCREMENT_FIELD.setSuffix(_translate("FIND_ELEMENT_WIDGET", " Degrees"))
        self.label_22.setText(
            _translate("FIND_ELEMENT_WIDGET", "<html><head/><body><p>Theta Increment:</p></body></html>"))
        self.label_5.setText(_translate("FIND_ELEMENT_WIDGET", "X-Axis # of Points:"))
        self.label_6.setText(
            _translate("FIND_ELEMENT_WIDGET", "<html><head/><body><p>Theta # of Points:</p></body></html>"))
        self.label_4.setText(_translate("FIND_ELEMENT_WIDGET",
                                        "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600; text-decoration: underline;\">Oscilliscope Parameters</span></p></body></html>"))
        self.OSCOPE_CHANNEL_FIELD.setItemText(0, _translate("FIND_ELEMENT_WIDGET", "Channel 1"))
        self.OSCOPE_CHANNEL_FIELD.setItemText(1, _translate("FIND_ELEMENT_WIDGET", "Channel 2"))
        self.OSCOPE_CHANNEL_FIELD.setItemText(2, _translate("FIND_ELEMENT_WIDGET", "Channel 3"))
        self.OSCOPE_CHANNEL_FIELD.setItemText(3, _translate("FIND_ELEMENT_WIDGET", "Channel 4"))
        self.label_7.setText(_translate("FIND_ELEMENT_WIDGET", "Scope Channel:"))
        self.OSCOPE_AQTYPE_FIELD.setToolTip(_translate("FIND_ELEMENT_WIDGET",
                                                       "<html><head/><body><p><span style=\" font-size:10pt; text-decoration: underline;\">Selections Available:</span></p><p>- Single Waveform </p><p>- N Averaged Waveform</p></body></html>"))
        self.OSCOPE_AQTYPE_FIELD.setItemText(0, _translate("FIND_ELEMENT_WIDGET", "N Averaged Waveform"))
        self.OSCOPE_AQTYPE_FIELD.setItemText(1, _translate("FIND_ELEMENT_WIDGET", "Single Waveform"))
        self.label_8.setText(_translate("FIND_ELEMENT_WIDGET", "Acquisition Type:"))
        self.OSCOPE_SAMPLES_FIELD.setItemText(0, _translate("FIND_ELEMENT_WIDGET", "2 Averages"))
        self.OSCOPE_SAMPLES_FIELD.setItemText(1, _translate("FIND_ELEMENT_WIDGET", "4 Averages"))
        self.OSCOPE_SAMPLES_FIELD.setItemText(2, _translate("FIND_ELEMENT_WIDGET", "8 Averages"))
        self.OSCOPE_SAMPLES_FIELD.setItemText(3, _translate("FIND_ELEMENT_WIDGET", "16 Averages"))
        self.OSCOPE_SAMPLES_FIELD.setItemText(4, _translate("FIND_ELEMENT_WIDGET", "32 Averages"))
        self.OSCOPE_SAMPLES_FIELD.setItemText(5, _translate("FIND_ELEMENT_WIDGET", "64 Averages"))
        self.OSCOPE_SAMPLES_FIELD.setItemText(6, _translate("FIND_ELEMENT_WIDGET", "128 Averages"))
        self.OSCOPE_SAMPLES_FIELD.setItemText(7, _translate("FIND_ELEMENT_WIDGET", "256 Averages"))
        self.label_9.setText(_translate("FIND_ELEMENT_WIDGET", "Number of Samples:"))
        self.label_10.setText(_translate("FIND_ELEMENT_WIDGET", "Capture Cycles:"))
        self.label_11.setText(_translate("FIND_ELEMENT_WIDGET", "Delay Cycles:"))
        self.OSCOPE_AUTO_CHECKBOX.setText(_translate("FIND_ELEMENT_WIDGET", "Auto Timebase"))
        self.label_12.setText(_translate("FIND_ELEMENT_WIDGET", "Data Storage:"))
        self.OSCOPE_DATASTORE_FIELD.setToolTip(_translate("FIND_ELEMENT_WIDGET",
                                                          "<html><head/><body><p><span style=\" font-size:10pt; text-decoration: underline;\">Selections Available:</span></p><p>- Do not store</p><p>- Store profiles only</p><p>- Store entire waveform</p></body></html> "))
        self.OSCOPE_DATASTORE_FIELD.setItemText(0, _translate("FIND_ELEMENT_WIDGET", "Do not store"))
        self.OSCOPE_DATASTORE_FIELD.setItemText(1, _translate("FIND_ELEMENT_WIDGET", "Store profiles only"))
        self.OSCOPE_DATASTORE_FIELD.setItemText(2, _translate("FIND_ELEMENT_WIDGET", "Store entire waveform"))
        self.label_13.setText(_translate("FIND_ELEMENT_WIDGET", "Storage Location:"))
        self.OSCOPE_DATALOC_FIELD.setItemText(0, _translate("FIND_ELEMENT_WIDGET", "UA Results Directory"))
        self.OSCOPE_DATALOC_FIELD.setItemText(1, _translate("FIND_ELEMENT_WIDGET", "Other Directory"))
        self.label_14.setText(_translate("FIND_ELEMENT_WIDGET", "Data Directory:"))
        self.OSCOPE_DATA_DIRECTORY_BUTTON.setText(_translate("FIND_ELEMENT_WIDGET", "Browse"))
        self.label_15.setText(_translate("FIND_ELEMENT_WIDGET",
                                         "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600; text-decoration: underline;\">Frequency &amp; Angle</span></p></body></html>"))
        self.label_16.setText(_translate("FIND_ELEMENT_WIDGET", "Frequency Preset:"))
        self.FREQANG_PRESET_FIELD.setToolTip(_translate("FIND_ELEMENT_WIDGET",
                                                        "<html><head/><body><p><span style=\" font-size:10pt; text-decoration: underline;\">Selections Available:</span></p><p>- From config cluster </p><p>- Element pk low frequency</p><p>- Element pk high frequency</p><p>- Common low frequency</p><p>- Common high frequency</p></body></html>"))
        self.FREQANG_PRESET_FIELD.setItemText(0, _translate("FIND_ELEMENT_WIDGET", "From config cluster"))
        self.FREQANG_PRESET_FIELD.setItemText(1, _translate("FIND_ELEMENT_WIDGET", "Element pk low frequency"))
        self.FREQANG_PRESET_FIELD.setItemText(2, _translate("FIND_ELEMENT_WIDGET", "Element pk high frequency"))
        self.FREQANG_PRESET_FIELD.setItemText(3, _translate("FIND_ELEMENT_WIDGET", "Common low frequency"))
        self.FREQANG_PRESET_FIELD.setItemText(4, _translate("FIND_ELEMENT_WIDGET", "Common high frequency"))
        self.FREQANG_BURST_FIELD.setSuffix(_translate("FIND_ELEMENT_WIDGET", " Bursts"))
        self.label_17.setText(_translate("FIND_ELEMENT_WIDGET", "Burst Count:"))
        self.label_18.setText(_translate("FIND_ELEMENT_WIDGET", "Frequency (MHz):"))
        self.FREQANG_FREQ_FIELD.setSuffix(_translate("FIND_ELEMENT_WIDGET", " MHz"))
        self.FREQANG_VOLT_FIELD.setSuffix(_translate("FIND_ELEMENT_WIDGET", " mV"))
        self.label_19.setText(_translate("FIND_ELEMENT_WIDGET", "Amplitude (mV):"))
        self.label_20.setText(_translate("FIND_ELEMENT_WIDGET", "Max Angle Variation (Deg):"))
        self.FREQANG_ANG_FIELD.setSuffix(_translate("FIND_ELEMENT_WIDGET", " Degrees"))
        self.FREQANG_ANG_TEST_CHECKBOX.setText(_translate("FIND_ELEMENT_WIDGET", "Include Test"))
        self.FREQANG_POS_TEST_CHECKBOX.setText(_translate("FIND_ELEMENT_WIDGET", "Include Test"))
        self.FREQANG_POS_FIELD.setSuffix(_translate("FIND_ELEMENT_WIDGET", " mm"))
        self.label_21.setText(_translate("FIND_ELEMENT_WIDGET", "Max Position Error (mm):"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    FIND_ELEMENT_WIDGET = QtWidgets.QWidget()
    ui = Ui_FIND_ELEMENT_WIDGET()
    ui.setupUi(FIND_ELEMENT_WIDGET)
    FIND_ELEMENT_WIDGET.show()
    sys.exit(app.exec_())

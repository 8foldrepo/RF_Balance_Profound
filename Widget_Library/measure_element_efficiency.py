# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'measure_element_efficiency.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form_2(object):
    def setupUi(self, Form_2):
        Form_2.setObjectName("Form_2")
        Form_2.resize(640, 470)
        Form_2.setMinimumSize(QtCore.QSize(640, 470))
        self.frame = QtWidgets.QFrame(Form_2)
        self.frame.setGeometry(QtCore.QRect(10, 40, 621, 421))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setGeometry(QtCore.QRect(10, 50, 200, 270))
        self.frame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setLineWidth(2)
        self.frame_2.setObjectName("frame_2")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(10, 10, 161, 16))
        self.label_4.setObjectName("label_4")
        self.label_10 = QtWidgets.QLabel(self.frame_2)
        self.label_10.setGeometry(QtCore.QRect(10, 30, 90, 16))
        self.label_10.setObjectName("label_10")
        self.OSCOPE_CYCLES_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.OSCOPE_CYCLES_FIELD.setGeometry(QtCore.QRect(100, 30, 86, 20))
        self.OSCOPE_CYCLES_FIELD.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD.setPrefix("")
        self.OSCOPE_CYCLES_FIELD.setSuffix("")
        self.OSCOPE_CYCLES_FIELD.setDecimals(0)
        self.OSCOPE_CYCLES_FIELD.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD.setMaximum(1000000.0)
        self.OSCOPE_CYCLES_FIELD.setSingleStep(1.0)
        self.OSCOPE_CYCLES_FIELD.setObjectName("OSCOPE_CYCLES_FIELD")
        self.OSCOPE_CYCLES_FIELD_2 = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.OSCOPE_CYCLES_FIELD_2.setGeometry(QtCore.QRect(100, 60, 86, 20))
        self.OSCOPE_CYCLES_FIELD_2.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_2.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_2.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_2.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_2.setDecimals(1)
        self.OSCOPE_CYCLES_FIELD_2.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD_2.setMaximum(1000000.0)
        self.OSCOPE_CYCLES_FIELD_2.setSingleStep(0.1)
        self.OSCOPE_CYCLES_FIELD_2.setObjectName("OSCOPE_CYCLES_FIELD_2")
        self.label_11 = QtWidgets.QLabel(self.frame_2)
        self.label_11.setGeometry(QtCore.QRect(10, 60, 80, 16))
        self.label_11.setObjectName("label_11")
        self.OSCOPE_CYCLES_FIELD_3 = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.OSCOPE_CYCLES_FIELD_3.setGeometry(QtCore.QRect(100, 90, 86, 20))
        self.OSCOPE_CYCLES_FIELD_3.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_3.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_3.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_3.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_3.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_3.setDecimals(1)
        self.OSCOPE_CYCLES_FIELD_3.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD_3.setMaximum(1000000.0)
        self.OSCOPE_CYCLES_FIELD_3.setSingleStep(0.1)
        self.OSCOPE_CYCLES_FIELD_3.setObjectName("OSCOPE_CYCLES_FIELD_3")
        self.label_12 = QtWidgets.QLabel(self.frame_2)
        self.label_12.setGeometry(QtCore.QRect(10, 90, 85, 16))
        self.label_12.setObjectName("label_12")
        self.OSCOPE_CYCLES_FIELD_4 = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.OSCOPE_CYCLES_FIELD_4.setGeometry(QtCore.QRect(100, 120, 86, 20))
        self.OSCOPE_CYCLES_FIELD_4.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_4.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_4.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_4.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_4.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_4.setDecimals(2)
        self.OSCOPE_CYCLES_FIELD_4.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD_4.setMaximum(1000000.0)
        self.OSCOPE_CYCLES_FIELD_4.setSingleStep(0.01)
        self.OSCOPE_CYCLES_FIELD_4.setObjectName("OSCOPE_CYCLES_FIELD_4")
        self.label_13 = QtWidgets.QLabel(self.frame_2)
        self.label_13.setGeometry(QtCore.QRect(10, 120, 80, 16))
        self.label_13.setObjectName("label_13")
        self.OSCOPE_CYCLES_FIELD_5 = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.OSCOPE_CYCLES_FIELD_5.setGeometry(QtCore.QRect(100, 150, 86, 20))
        self.OSCOPE_CYCLES_FIELD_5.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_5.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_5.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_5.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_5.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_5.setDecimals(1)
        self.OSCOPE_CYCLES_FIELD_5.setMinimum(-1000000.0)
        self.OSCOPE_CYCLES_FIELD_5.setMaximum(1000000.0)
        self.OSCOPE_CYCLES_FIELD_5.setSingleStep(0.1)
        self.OSCOPE_CYCLES_FIELD_5.setObjectName("OSCOPE_CYCLES_FIELD_5")
        self.label_14 = QtWidgets.QLabel(self.frame_2)
        self.label_14.setGeometry(QtCore.QRect(10, 150, 80, 16))
        self.label_14.setObjectName("label_14")
        self.OSCOPE_CYCLES_FIELD_6 = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.OSCOPE_CYCLES_FIELD_6.setGeometry(QtCore.QRect(100, 180, 86, 20))
        self.OSCOPE_CYCLES_FIELD_6.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_6.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_6.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_6.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_6.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_6.setDecimals(0)
        self.OSCOPE_CYCLES_FIELD_6.setMinimum(-360.0)
        self.OSCOPE_CYCLES_FIELD_6.setMaximum(360.0)
        self.OSCOPE_CYCLES_FIELD_6.setSingleStep(1.0)
        self.OSCOPE_CYCLES_FIELD_6.setObjectName("OSCOPE_CYCLES_FIELD_6")
        self.label_15 = QtWidgets.QLabel(self.frame_2)
        self.label_15.setGeometry(QtCore.QRect(10, 180, 90, 16))
        self.label_15.setObjectName("label_15")
        self.ELEMENT_SELECTION_FIELD_2 = QtWidgets.QComboBox(self.frame_2)
        self.ELEMENT_SELECTION_FIELD_2.setGeometry(QtCore.QRect(30, 240, 150, 20))
        self.ELEMENT_SELECTION_FIELD_2.setObjectName("ELEMENT_SELECTION_FIELD_2")
        self.ELEMENT_SELECTION_FIELD_2.addItem("")
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(50, 220, 100, 16))
        self.label_3.setObjectName("label_3")
        self.frame_3 = QtWidgets.QFrame(self.frame)
        self.frame_3.setGeometry(QtCore.QRect(10, 10, 200, 40))
        self.frame_3.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setLineWidth(2)
        self.frame_3.setObjectName("frame_3")
        self.ELEMENT_SELECTION_FIELD = QtWidgets.QComboBox(self.frame_3)
        self.ELEMENT_SELECTION_FIELD.setGeometry(QtCore.QRect(100, 10, 91, 20))
        self.ELEMENT_SELECTION_FIELD.setObjectName("ELEMENT_SELECTION_FIELD")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.ELEMENT_SELECTION_FIELD.addItem("")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 91, 16))
        self.label_2.setObjectName("label_2")
        self.frame_4 = QtWidgets.QFrame(self.frame)
        self.frame_4.setGeometry(QtCore.QRect(210, 50, 200, 270))
        self.frame_4.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_4.setLineWidth(2)
        self.frame_4.setObjectName("frame_4")
        self.label_9 = QtWidgets.QLabel(self.frame_4)
        self.label_9.setGeometry(QtCore.QRect(10, 10, 161, 16))
        self.label_9.setObjectName("label_9")
        self.OSCOPE_CYCLES_FIELD_29 = QtWidgets.QDoubleSpinBox(self.frame_4)
        self.OSCOPE_CYCLES_FIELD_29.setGeometry(QtCore.QRect(100, 150, 86, 20))
        self.OSCOPE_CYCLES_FIELD_29.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_29.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_29.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_29.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_29.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_29.setDecimals(4)
        self.OSCOPE_CYCLES_FIELD_29.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD_29.setMaximum(50.0)
        self.OSCOPE_CYCLES_FIELD_29.setSingleStep(0.0001)
        self.OSCOPE_CYCLES_FIELD_29.setObjectName("OSCOPE_CYCLES_FIELD_29")
        self.label_38 = QtWidgets.QLabel(self.frame_4)
        self.label_38.setGeometry(QtCore.QRect(10, 150, 85, 16))
        self.label_38.setObjectName("label_38")
        self.OSCOPE_CYCLES_FIELD_30 = QtWidgets.QDoubleSpinBox(self.frame_4)
        self.OSCOPE_CYCLES_FIELD_30.setGeometry(QtCore.QRect(100, 180, 86, 20))
        self.OSCOPE_CYCLES_FIELD_30.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_30.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_30.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_30.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_30.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_30.setDecimals(0)
        self.OSCOPE_CYCLES_FIELD_30.setMinimum(-10000.0)
        self.OSCOPE_CYCLES_FIELD_30.setMaximum(10000.0)
        self.OSCOPE_CYCLES_FIELD_30.setSingleStep(1.0)
        self.OSCOPE_CYCLES_FIELD_30.setObjectName("OSCOPE_CYCLES_FIELD_30")
        self.label_39 = QtWidgets.QLabel(self.frame_4)
        self.label_39.setGeometry(QtCore.QRect(10, 180, 90, 16))
        self.label_39.setObjectName("label_39")
        self.label_34 = QtWidgets.QLabel(self.frame_4)
        self.label_34.setGeometry(QtCore.QRect(30, 40, 130, 16))
        self.label_34.setObjectName("label_34")
        self.ELEMENT_SELECTION_FIELD_4 = QtWidgets.QComboBox(self.frame_4)
        self.ELEMENT_SELECTION_FIELD_4.setGeometry(QtCore.QRect(20, 60, 150, 20))
        self.ELEMENT_SELECTION_FIELD_4.setObjectName("ELEMENT_SELECTION_FIELD_4")
        self.ELEMENT_SELECTION_FIELD_4.addItem("")
        self.label_35 = QtWidgets.QLabel(self.frame_4)
        self.label_35.setGeometry(QtCore.QRect(40, 90, 130, 16))
        self.label_35.setObjectName("label_35")
        self.ELEMENT_SELECTION_FIELD_6 = QtWidgets.QComboBox(self.frame_4)
        self.ELEMENT_SELECTION_FIELD_6.setGeometry(QtCore.QRect(20, 110, 150, 20))
        self.ELEMENT_SELECTION_FIELD_6.setObjectName("ELEMENT_SELECTION_FIELD_6")
        self.ELEMENT_SELECTION_FIELD_6.addItem("")
        self.frame_5 = QtWidgets.QFrame(self.frame)
        self.frame_5.setGeometry(QtCore.QRect(410, 50, 200, 270))
        self.frame_5.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_5.setLineWidth(2)
        self.frame_5.setObjectName("frame_5")
        self.label_41 = QtWidgets.QLabel(self.frame_5)
        self.label_41.setGeometry(QtCore.QRect(10, 10, 161, 16))
        self.label_41.setObjectName("label_41")
        self.label_42 = QtWidgets.QLabel(self.frame_5)
        self.label_42.setGeometry(QtCore.QRect(10, 90, 100, 16))
        self.label_42.setObjectName("label_42")
        self.OSCOPE_CYCLES_FIELD_31 = QtWidgets.QDoubleSpinBox(self.frame_5)
        self.OSCOPE_CYCLES_FIELD_31.setGeometry(QtCore.QRect(110, 90, 86, 20))
        self.OSCOPE_CYCLES_FIELD_31.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_31.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_31.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_31.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_31.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_31.setDecimals(0)
        self.OSCOPE_CYCLES_FIELD_31.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD_31.setMaximum(500.0)
        self.OSCOPE_CYCLES_FIELD_31.setSingleStep(1.0)
        self.OSCOPE_CYCLES_FIELD_31.setObjectName("OSCOPE_CYCLES_FIELD_31")
        self.OSCOPE_CYCLES_FIELD_32 = QtWidgets.QDoubleSpinBox(self.frame_5)
        self.OSCOPE_CYCLES_FIELD_32.setGeometry(QtCore.QRect(110, 120, 86, 20))
        self.OSCOPE_CYCLES_FIELD_32.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_32.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_32.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_32.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_32.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_32.setDecimals(0)
        self.OSCOPE_CYCLES_FIELD_32.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD_32.setMaximum(500.0)
        self.OSCOPE_CYCLES_FIELD_32.setSingleStep(1.0)
        self.OSCOPE_CYCLES_FIELD_32.setObjectName("OSCOPE_CYCLES_FIELD_32")
        self.label_43 = QtWidgets.QLabel(self.frame_5)
        self.label_43.setGeometry(QtCore.QRect(10, 120, 100, 16))
        self.label_43.setObjectName("label_43")
        self.OSCOPE_CYCLES_FIELD_33 = QtWidgets.QDoubleSpinBox(self.frame_5)
        self.OSCOPE_CYCLES_FIELD_33.setGeometry(QtCore.QRect(110, 150, 86, 20))
        self.OSCOPE_CYCLES_FIELD_33.setToolTip("")
        self.OSCOPE_CYCLES_FIELD_33.setStatusTip("")
        self.OSCOPE_CYCLES_FIELD_33.setWhatsThis("")
        self.OSCOPE_CYCLES_FIELD_33.setPrefix("")
        self.OSCOPE_CYCLES_FIELD_33.setSuffix("")
        self.OSCOPE_CYCLES_FIELD_33.setDecimals(0)
        self.OSCOPE_CYCLES_FIELD_33.setMinimum(0.0)
        self.OSCOPE_CYCLES_FIELD_33.setMaximum(100.0)
        self.OSCOPE_CYCLES_FIELD_33.setSingleStep(1.0)
        self.OSCOPE_CYCLES_FIELD_33.setObjectName("OSCOPE_CYCLES_FIELD_33")
        self.label_44 = QtWidgets.QLabel(self.frame_5)
        self.label_44.setGeometry(QtCore.QRect(10, 150, 100, 16))
        self.label_44.setObjectName("label_44")
        self.OSCOPE_AUTO_CHECKBOX = QtWidgets.QCheckBox(self.frame_5)
        self.OSCOPE_AUTO_CHECKBOX.setGeometry(QtCore.QRect(50, 60, 91, 17))
        self.OSCOPE_AUTO_CHECKBOX.setObjectName("OSCOPE_AUTO_CHECKBOX")
        self.frame_6 = QtWidgets.QFrame(self.frame)
        self.frame_6.setGeometry(QtCore.QRect(10, 320, 600, 90))
        self.frame_6.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setLineWidth(2)
        self.frame_6.setObjectName("frame_6")
        self.OSCOPE_DATALOC_FIELD = QtWidgets.QComboBox(self.frame_6)
        self.OSCOPE_DATALOC_FIELD.setGeometry(QtCore.QRect(120, 40, 131, 20))
        self.OSCOPE_DATALOC_FIELD.setObjectName("OSCOPE_DATALOC_FIELD")
        self.OSCOPE_DATALOC_FIELD.addItem("")
        self.OSCOPE_DATALOC_FIELD.addItem("")
        self.OSCOPE_DATALOC_FIELD.addItem("")
        self.label_49 = QtWidgets.QLabel(self.frame_6)
        self.label_49.setGeometry(QtCore.QRect(20, 40, 85, 16))
        self.label_49.setObjectName("label_49")
        self.OSCOPE_DATA_DIRECTORY_BUTTON = QtWidgets.QPushButton(self.frame_6)
        self.OSCOPE_DATA_DIRECTORY_BUTTON.setGeometry(QtCore.QRect(510, 40, 75, 20))
        self.OSCOPE_DATA_DIRECTORY_BUTTON.setObjectName("OSCOPE_DATA_DIRECTORY_BUTTON")
        self.OSCOPE_DATA_DIRECTORY_FIELD = QtWidgets.QLineEdit(self.frame_6)
        self.OSCOPE_DATA_DIRECTORY_FIELD.setGeometry(QtCore.QRect(300, 40, 200, 20))
        self.OSCOPE_DATA_DIRECTORY_FIELD.setObjectName("OSCOPE_DATA_DIRECTORY_FIELD")
        self.label_50 = QtWidgets.QLabel(self.frame_6)
        self.label_50.setGeometry(QtCore.QRect(360, 20, 81, 16))
        self.label_50.setObjectName("label_50")
        self.label = QtWidgets.QLabel(Form_2)
        self.label.setGeometry(QtCore.QRect(20, 10, 331, 31))
        self.label.setObjectName("label")

        self.retranslateUi(Form_2)
        QtCore.QMetaObject.connectSlotsByName(Form_2)

    def retranslateUi(self, Form_2):
        _translate = QtCore.QCoreApplication.translate
        Form_2.setWindowTitle(_translate("Form_2", "Measure Element Efficiency (RFB)"))
        self.label_4.setText(_translate("Form_2", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600; text-decoration: underline;\">RFB Parameters</span></p></body></html>"))
        self.label_10.setText(_translate("Form_2", "<html><head/><body><p>RFB on/off Cycles:</p></body></html>"))
        self.OSCOPE_CYCLES_FIELD.setToolTip(_translate("Form_2", "<html><head/><body><p><span style=\" font-size:12pt;\">A non-negative integer that sets the amount of On/Off cycles the RFB will perform.</span></p><p><span style=\" font-size:12pt;\">Maximum: 1000000 Cycles</span></p></body></html>"))
        self.OSCOPE_CYCLES_FIELD_2.setToolTip(_translate("Form_2", "<html><head/><body><p><span style=\" font-size:12pt;\">A non-negative decimal that sets the amount of ON time the RFB will fire in seconds.</span></p><p><span style=\" font-size:12pt;\">Maximum: 1000000 Seconds</span></p></body></html>"))
        self.label_11.setText(_translate("Form_2", "RFB ON time (s):"))
        self.label_12.setText(_translate("Form_2", "RFB OFF time(s):"))
        self.label_13.setText(_translate("Form_2", "RFB Threshold:"))
        self.label_14.setText(_translate("Form_2", "RFB Offset:"))
        self.label_15.setText(_translate("Form_2", "RFB Target Angle:"))
        self.ELEMENT_SELECTION_FIELD_2.setItemText(0, _translate("Form_2", "Average UA RFB Position"))
        self.label_3.setText(_translate("Form_2", "RFB Target Position"))
        self.ELEMENT_SELECTION_FIELD.setToolTip(_translate("Form_2", "<html><head/><body><p><span style=\" font-size:12pt;\">Select the element you would like to measure the efficiency of.</span></p></body></html>"))
        self.ELEMENT_SELECTION_FIELD.setItemText(0, _translate("Form_2", "Current"))
        self.ELEMENT_SELECTION_FIELD.setItemText(1, _translate("Form_2", "Element 1"))
        self.ELEMENT_SELECTION_FIELD.setItemText(2, _translate("Form_2", "Element 2"))
        self.ELEMENT_SELECTION_FIELD.setItemText(3, _translate("Form_2", "Element 3"))
        self.ELEMENT_SELECTION_FIELD.setItemText(4, _translate("Form_2", "Element 4"))
        self.ELEMENT_SELECTION_FIELD.setItemText(5, _translate("Form_2", "Element 5"))
        self.ELEMENT_SELECTION_FIELD.setItemText(6, _translate("Form_2", "Element 6"))
        self.ELEMENT_SELECTION_FIELD.setItemText(7, _translate("Form_2", "Element 7"))
        self.ELEMENT_SELECTION_FIELD.setItemText(8, _translate("Form_2", "Element 8"))
        self.ELEMENT_SELECTION_FIELD.setItemText(9, _translate("Form_2", "Element 9"))
        self.ELEMENT_SELECTION_FIELD.setItemText(10, _translate("Form_2", "Element 10"))
        self.label_2.setText(_translate("Form_2", "Element Selected:"))
        self.label_9.setText(_translate("Form_2", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600; text-decoration: underline;\">Frequency Parameters</span></p></body></html>"))
        self.label_38.setText(_translate("Form_2", "Frequency (MHz):"))
        self.label_39.setText(_translate("Form_2", "Amplitude (mVpp):"))
        self.label_34.setText(_translate("Form_2", "Frequency Range Selected"))
        self.ELEMENT_SELECTION_FIELD_4.setItemText(0, _translate("Form_2", "Low Frequency"))
        self.label_35.setText(_translate("Form_2", "Set Frequency Options"))
        self.ELEMENT_SELECTION_FIELD_6.setItemText(0, _translate("Form_2", "Common Peak Frequency"))
        self.label_41.setText(_translate("Form_2", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600; text-decoration: underline;\">Power Parameters</span></p></body></html>"))
        self.label_42.setText(_translate("Form_2", "Pa max (target, W):"))
        self.label_43.setText(_translate("Form_2", "Pf max (limit, W):"))
        self.label_44.setText(_translate("Form_2", "Reflection Limit (%):"))
        self.OSCOPE_AUTO_CHECKBOX.setText(_translate("Form_2", "Include Test"))
        self.OSCOPE_DATALOC_FIELD.setItemText(0, _translate("Form_2", "UA Results Directory"))
        self.OSCOPE_DATALOC_FIELD.setItemText(1, _translate("Form_2", "Results 2"))
        self.OSCOPE_DATALOC_FIELD.setItemText(2, _translate("Form_2", "Results 3"))
        self.label_49.setText(_translate("Form_2", "Storage Location:"))
        self.OSCOPE_DATA_DIRECTORY_BUTTON.setText(_translate("Form_2", "Browse"))
        self.label_50.setText(_translate("Form_2", "Data Directory:"))
        self.label.setText(_translate("Form_2", "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600; text-decoration: underline;\">Measure Element Efficiency (RFB)</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form_2 = QtWidgets.QWidget()
    ui = Ui_Form_2()
    ui.setupUi(Form_2)
    Form_2.show()
    sys.exit(app.exec_())

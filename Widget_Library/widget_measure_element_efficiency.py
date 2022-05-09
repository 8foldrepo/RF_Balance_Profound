# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_measure_element_efficiency.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


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
        self.RFB_CYCLES_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.RFB_CYCLES_FIELD.setGeometry(QtCore.QRect(100, 30, 86, 20))
        self.RFB_CYCLES_FIELD.setStatusTip("")
        self.RFB_CYCLES_FIELD.setWhatsThis("")
        self.RFB_CYCLES_FIELD.setPrefix("")
        self.RFB_CYCLES_FIELD.setSuffix("")
        self.RFB_CYCLES_FIELD.setDecimals(0)
        self.RFB_CYCLES_FIELD.setMinimum(0.0)
        self.RFB_CYCLES_FIELD.setMaximum(1000000.0)
        self.RFB_CYCLES_FIELD.setSingleStep(1.0)
        self.RFB_CYCLES_FIELD.setObjectName("RFB_CYCLES_FIELD")
        self.RFB_ON_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.RFB_ON_FIELD.setGeometry(QtCore.QRect(100, 60, 86, 20))
        self.RFB_ON_FIELD.setStatusTip("")
        self.RFB_ON_FIELD.setWhatsThis("")
        self.RFB_ON_FIELD.setPrefix("")
        self.RFB_ON_FIELD.setSuffix("")
        self.RFB_ON_FIELD.setDecimals(1)
        self.RFB_ON_FIELD.setMinimum(0.0)
        self.RFB_ON_FIELD.setMaximum(1000000.0)
        self.RFB_ON_FIELD.setSingleStep(0.1)
        self.RFB_ON_FIELD.setObjectName("RFB_ON_FIELD")
        self.label_11 = QtWidgets.QLabel(self.frame_2)
        self.label_11.setGeometry(QtCore.QRect(10, 60, 80, 16))
        self.label_11.setObjectName("label_11")
        self.RFB_OFF_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.RFB_OFF_FIELD.setGeometry(QtCore.QRect(100, 90, 86, 20))
        self.RFB_OFF_FIELD.setToolTip("")
        self.RFB_OFF_FIELD.setStatusTip("")
        self.RFB_OFF_FIELD.setWhatsThis("")
        self.RFB_OFF_FIELD.setPrefix("")
        self.RFB_OFF_FIELD.setSuffix("")
        self.RFB_OFF_FIELD.setDecimals(1)
        self.RFB_OFF_FIELD.setMinimum(0.0)
        self.RFB_OFF_FIELD.setMaximum(1000000.0)
        self.RFB_OFF_FIELD.setSingleStep(0.1)
        self.RFB_OFF_FIELD.setObjectName("RFB_OFF_FIELD")
        self.label_12 = QtWidgets.QLabel(self.frame_2)
        self.label_12.setGeometry(QtCore.QRect(10, 90, 85, 16))
        self.label_12.setObjectName("label_12")
        self.RFB_THRESHOLD_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.RFB_THRESHOLD_FIELD.setGeometry(QtCore.QRect(100, 120, 86, 20))
        self.RFB_THRESHOLD_FIELD.setToolTip("")
        self.RFB_THRESHOLD_FIELD.setStatusTip("")
        self.RFB_THRESHOLD_FIELD.setWhatsThis("")
        self.RFB_THRESHOLD_FIELD.setPrefix("")
        self.RFB_THRESHOLD_FIELD.setSuffix("")
        self.RFB_THRESHOLD_FIELD.setDecimals(2)
        self.RFB_THRESHOLD_FIELD.setMinimum(0.0)
        self.RFB_THRESHOLD_FIELD.setMaximum(1000000.0)
        self.RFB_THRESHOLD_FIELD.setSingleStep(0.01)
        self.RFB_THRESHOLD_FIELD.setObjectName("RFB_THRESHOLD_FIELD")
        self.label_13 = QtWidgets.QLabel(self.frame_2)
        self.label_13.setGeometry(QtCore.QRect(10, 120, 80, 16))
        self.label_13.setObjectName("label_13")
        self.RFB_OFFSET_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.RFB_OFFSET_FIELD.setGeometry(QtCore.QRect(100, 150, 86, 20))
        self.RFB_OFFSET_FIELD.setToolTip("")
        self.RFB_OFFSET_FIELD.setStatusTip("")
        self.RFB_OFFSET_FIELD.setWhatsThis("")
        self.RFB_OFFSET_FIELD.setPrefix("")
        self.RFB_OFFSET_FIELD.setSuffix("")
        self.RFB_OFFSET_FIELD.setDecimals(1)
        self.RFB_OFFSET_FIELD.setMinimum(-1000000.0)
        self.RFB_OFFSET_FIELD.setMaximum(1000000.0)
        self.RFB_OFFSET_FIELD.setSingleStep(0.1)
        self.RFB_OFFSET_FIELD.setObjectName("RFB_OFFSET_FIELD")
        self.label_14 = QtWidgets.QLabel(self.frame_2)
        self.label_14.setGeometry(QtCore.QRect(10, 150, 80, 16))
        self.label_14.setObjectName("label_14")
        self.RFB_ANGLE_FIELD = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.RFB_ANGLE_FIELD.setGeometry(QtCore.QRect(100, 180, 86, 20))
        self.RFB_ANGLE_FIELD.setToolTip("")
        self.RFB_ANGLE_FIELD.setStatusTip("")
        self.RFB_ANGLE_FIELD.setWhatsThis("")
        self.RFB_ANGLE_FIELD.setPrefix("")
        self.RFB_ANGLE_FIELD.setSuffix("")
        self.RFB_ANGLE_FIELD.setDecimals(0)
        self.RFB_ANGLE_FIELD.setMinimum(-360.0)
        self.RFB_ANGLE_FIELD.setMaximum(360.0)
        self.RFB_ANGLE_FIELD.setSingleStep(1.0)
        self.RFB_ANGLE_FIELD.setObjectName("RFB_ANGLE_FIELD")
        self.label_15 = QtWidgets.QLabel(self.frame_2)
        self.label_15.setGeometry(QtCore.QRect(10, 180, 90, 16))
        self.label_15.setObjectName("label_15")
        self.RFB_TARGET_POSITION_FIELD = QtWidgets.QComboBox(self.frame_2)
        self.RFB_TARGET_POSITION_FIELD.setGeometry(QtCore.QRect(30, 240, 150, 20))
        self.RFB_TARGET_POSITION_FIELD.setObjectName("RFB_TARGET_POSITION_FIELD")
        self.RFB_TARGET_POSITION_FIELD.addItem("")
        self.RFB_TARGET_POSITION_FIELD.addItem("")
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
        self.ELEMENT_SELECTION_FIELD.setMaxVisibleItems(11)
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
        self.FREQUENCY_FIELD = QtWidgets.QDoubleSpinBox(self.frame_4)
        self.FREQUENCY_FIELD.setGeometry(QtCore.QRect(100, 150, 86, 20))
        self.FREQUENCY_FIELD.setToolTip("")
        self.FREQUENCY_FIELD.setStatusTip("")
        self.FREQUENCY_FIELD.setWhatsThis("")
        self.FREQUENCY_FIELD.setPrefix("")
        self.FREQUENCY_FIELD.setSuffix("")
        self.FREQUENCY_FIELD.setDecimals(4)
        self.FREQUENCY_FIELD.setMinimum(0.0)
        self.FREQUENCY_FIELD.setMaximum(50.0)
        self.FREQUENCY_FIELD.setSingleStep(0.0001)
        self.FREQUENCY_FIELD.setObjectName("FREQUENCY_FIELD")
        self.label_38 = QtWidgets.QLabel(self.frame_4)
        self.label_38.setGeometry(QtCore.QRect(10, 150, 85, 16))
        self.label_38.setObjectName("label_38")
        self.AMPLITUDE_FIELD = QtWidgets.QDoubleSpinBox(self.frame_4)
        self.AMPLITUDE_FIELD.setGeometry(QtCore.QRect(100, 180, 86, 20))
        self.AMPLITUDE_FIELD.setToolTip("")
        self.AMPLITUDE_FIELD.setStatusTip("")
        self.AMPLITUDE_FIELD.setWhatsThis("")
        self.AMPLITUDE_FIELD.setPrefix("")
        self.AMPLITUDE_FIELD.setSuffix("")
        self.AMPLITUDE_FIELD.setDecimals(0)
        self.AMPLITUDE_FIELD.setMinimum(-10000.0)
        self.AMPLITUDE_FIELD.setMaximum(10000.0)
        self.AMPLITUDE_FIELD.setSingleStep(1.0)
        self.AMPLITUDE_FIELD.setObjectName("AMPLITUDE_FIELD")
        self.label_39 = QtWidgets.QLabel(self.frame_4)
        self.label_39.setGeometry(QtCore.QRect(10, 180, 90, 16))
        self.label_39.setObjectName("label_39")
        self.label_34 = QtWidgets.QLabel(self.frame_4)
        self.label_34.setGeometry(QtCore.QRect(30, 40, 130, 16))
        self.label_34.setObjectName("label_34")
        self.FREQUENCY_SELECTION_FIELD = QtWidgets.QComboBox(self.frame_4)
        self.FREQUENCY_SELECTION_FIELD.setGeometry(QtCore.QRect(20, 60, 150, 20))
        self.FREQUENCY_SELECTION_FIELD.setObjectName("FREQUENCY_SELECTION_FIELD")
        self.FREQUENCY_SELECTION_FIELD.addItem("")
        self.FREQUENCY_SELECTION_FIELD.addItem("")
        self.label_35 = QtWidgets.QLabel(self.frame_4)
        self.label_35.setGeometry(QtCore.QRect(40, 90, 130, 16))
        self.label_35.setObjectName("label_35")
        self.OPTIONS_SELECTION_FIELD = QtWidgets.QComboBox(self.frame_4)
        self.OPTIONS_SELECTION_FIELD.setGeometry(QtCore.QRect(20, 110, 150, 20))
        self.OPTIONS_SELECTION_FIELD.setObjectName("OPTIONS_SELECTION_FIELD")
        self.OPTIONS_SELECTION_FIELD.addItem("")
        self.OPTIONS_SELECTION_FIELD.addItem("")
        self.OPTIONS_SELECTION_FIELD.addItem("")
        self.OPTIONS_SELECTION_FIELD.addItem("")
        self.OPTIONS_SELECTION_FIELD.addItem("")
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
        self.POWER_TARGET_FIELD = QtWidgets.QDoubleSpinBox(self.frame_5)
        self.POWER_TARGET_FIELD.setGeometry(QtCore.QRect(110, 90, 86, 20))
        self.POWER_TARGET_FIELD.setToolTip("")
        self.POWER_TARGET_FIELD.setStatusTip("")
        self.POWER_TARGET_FIELD.setWhatsThis("")
        self.POWER_TARGET_FIELD.setPrefix("")
        self.POWER_TARGET_FIELD.setSuffix("")
        self.POWER_TARGET_FIELD.setDecimals(0)
        self.POWER_TARGET_FIELD.setMinimum(0.0)
        self.POWER_TARGET_FIELD.setMaximum(500.0)
        self.POWER_TARGET_FIELD.setSingleStep(1.0)
        self.POWER_TARGET_FIELD.setObjectName("POWER_TARGET_FIELD")
        self.POWER_MAX_FIELD = QtWidgets.QDoubleSpinBox(self.frame_5)
        self.POWER_MAX_FIELD.setGeometry(QtCore.QRect(110, 120, 86, 20))
        self.POWER_MAX_FIELD.setToolTip("")
        self.POWER_MAX_FIELD.setStatusTip("")
        self.POWER_MAX_FIELD.setWhatsThis("")
        self.POWER_MAX_FIELD.setPrefix("")
        self.POWER_MAX_FIELD.setSuffix("")
        self.POWER_MAX_FIELD.setDecimals(0)
        self.POWER_MAX_FIELD.setMinimum(0.0)
        self.POWER_MAX_FIELD.setMaximum(500.0)
        self.POWER_MAX_FIELD.setSingleStep(1.0)
        self.POWER_MAX_FIELD.setObjectName("POWER_MAX_FIELD")
        self.label_43 = QtWidgets.QLabel(self.frame_5)
        self.label_43.setGeometry(QtCore.QRect(10, 120, 100, 16))
        self.label_43.setObjectName("label_43")
        self.REFLECTION_LIMIT_FIELD = QtWidgets.QDoubleSpinBox(self.frame_5)
        self.REFLECTION_LIMIT_FIELD.setGeometry(QtCore.QRect(110, 150, 86, 20))
        self.REFLECTION_LIMIT_FIELD.setToolTip("")
        self.REFLECTION_LIMIT_FIELD.setStatusTip("")
        self.REFLECTION_LIMIT_FIELD.setWhatsThis("")
        self.REFLECTION_LIMIT_FIELD.setPrefix("")
        self.REFLECTION_LIMIT_FIELD.setSuffix("")
        self.REFLECTION_LIMIT_FIELD.setDecimals(0)
        self.REFLECTION_LIMIT_FIELD.setMinimum(0.0)
        self.REFLECTION_LIMIT_FIELD.setMaximum(100.0)
        self.REFLECTION_LIMIT_FIELD.setSingleStep(1.0)
        self.REFLECTION_LIMIT_FIELD.setObjectName("REFLECTION_LIMIT_FIELD")
        self.label_44 = QtWidgets.QLabel(self.frame_5)
        self.label_44.setGeometry(QtCore.QRect(10, 150, 100, 16))
        self.label_44.setObjectName("label_44")
        self.POWER_TEST_CHECKBOX = QtWidgets.QCheckBox(self.frame_5)
        self.POWER_TEST_CHECKBOX.setGeometry(QtCore.QRect(50, 60, 91, 17))
        self.POWER_TEST_CHECKBOX.setObjectName("POWER_TEST_CHECKBOX")
        self.frame_6 = QtWidgets.QFrame(self.frame)
        self.frame_6.setGeometry(QtCore.QRect(10, 320, 600, 90))
        self.frame_6.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setLineWidth(2)
        self.frame_6.setObjectName("frame_6")
        self.DATALOC_FIELD = QtWidgets.QComboBox(self.frame_6)
        self.DATALOC_FIELD.setGeometry(QtCore.QRect(120, 40, 131, 20))
        self.DATALOC_FIELD.setObjectName("DATALOC_FIELD")
        self.DATALOC_FIELD.addItem("")
        self.DATALOC_FIELD.addItem("")
        self.label_49 = QtWidgets.QLabel(self.frame_6)
        self.label_49.setGeometry(QtCore.QRect(20, 40, 85, 16))
        self.label_49.setObjectName("label_49")
        self.DATA_DIRECTORY_BUTTON = QtWidgets.QPushButton(self.frame_6)
        self.DATA_DIRECTORY_BUTTON.setGeometry(QtCore.QRect(510, 40, 75, 20))
        self.DATA_DIRECTORY_BUTTON.setObjectName("DATA_DIRECTORY_BUTTON")
        self.DATA_DIRECTORY_FIELD = QtWidgets.QLineEdit(self.frame_6)
        self.DATA_DIRECTORY_FIELD.setGeometry(QtCore.QRect(300, 40, 200, 20))
        self.DATA_DIRECTORY_FIELD.setObjectName("DATA_DIRECTORY_FIELD")
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
        self.label_4.setText(
            _translate(
                "Form_2",
                '<html><head/><body><p><span style=" font-size:10pt; font-weight:600; text-decoration: underline;">RFB Parameters</span></p></body></html>',
            )
        )
        self.label_10.setText(
            _translate(
                "Form_2", "<html><head/><body><p>RFB on/off Cycles:</p></body></html>"
            )
        )
        self.RFB_CYCLES_FIELD.setToolTip(
            _translate(
                "Form_2",
                '<html><head/><body><p><span style=" font-size:12pt;">A non-negative integer that sets the amount of On/Off cycles the RFB will perform.</span></p><p><span style=" font-size:12pt;">Maximum: 1000000 Cycles</span></p></body></html>',
            )
        )
        self.RFB_ON_FIELD.setToolTip(
            _translate(
                "Form_2",
                '<html><head/><body><p><span style=" font-size:12pt;">A non-negative decimal that sets the amount of ON time the RFB will fire in seconds.</span></p><p><span style=" font-size:12pt;">Maximum: 1000000 Seconds</span></p></body></html>',
            )
        )
        self.label_11.setText(_translate("Form_2", "RFB ON time (s):"))
        self.label_12.setText(_translate("Form_2", "RFB OFF time(s):"))
        self.label_13.setText(_translate("Form_2", "RFB Threshold:"))
        self.label_14.setText(_translate("Form_2", "RFB Offset:"))
        self.label_15.setText(_translate("Form_2", "RFB Target Angle:"))
        self.RFB_TARGET_POSITION_FIELD.setItemText(
            0, _translate("Form_2", "Average UA RFB Position")
        )
        self.RFB_TARGET_POSITION_FIELD.setItemText(
            1, _translate("Form_2", "RFB Position for Each Item")
        )
        self.label_3.setText(_translate("Form_2", "RFB Target Position"))
        self.ELEMENT_SELECTION_FIELD.setToolTip(
            _translate(
                "Form_2",
                '<html><head/><body><p><span style=" font-size:12pt;">Select the element you would like to measure the efficiency of.</span></p></body></html>',
            )
        )
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
        self.label_9.setText(
            _translate(
                "Form_2",
                '<html><head/><body><p><span style=" font-size:10pt; font-weight:600; text-decoration: underline;">Frequency Parameters</span></p></body></html>',
            )
        )
        self.label_38.setText(_translate("Form_2", "Frequency (MHz):"))
        self.label_39.setText(_translate("Form_2", "Amplitude (mVpp):"))
        self.label_34.setText(_translate("Form_2", "Frequency Range Selected"))
        self.FREQUENCY_SELECTION_FIELD.setItemText(
            0, _translate("Form_2", "Low Frequency")
        )
        self.FREQUENCY_SELECTION_FIELD.setItemText(
            1, _translate("Form_2", "High Frequency")
        )
        self.label_35.setText(_translate("Form_2", "Set Frequency Options"))
        self.OPTIONS_SELECTION_FIELD.setToolTip(
            _translate(
                "Form_2",
                '<html><head/><body><p><span style=" font-size:10pt; text-decoration: underline;">Selections Available:</span></p><p>- From config cluster </p><p>- Element pk low frequency</p><p>- Element pk high frequency</p><p>- Common low frequency</p><p>- Common high frequency</p></body></html>',
            )
        )
        self.OPTIONS_SELECTION_FIELD.setItemText(
            0, _translate("Form_2", "From config cluster")
        )
        self.OPTIONS_SELECTION_FIELD.setItemText(
            1, _translate("Form_2", "Element pk low frequency")
        )
        self.OPTIONS_SELECTION_FIELD.setItemText(
            2, _translate("Form_2", "Element pk high frequency")
        )
        self.OPTIONS_SELECTION_FIELD.setItemText(
            3, _translate("Form_2", "Common low frequency")
        )
        self.OPTIONS_SELECTION_FIELD.setItemText(
            4, _translate("Form_2", "Common high frequency")
        )
        self.label_41.setText(
            _translate(
                "Form_2",
                '<html><head/><body><p><span style=" font-size:10pt; font-weight:600; text-decoration: underline;">Power Parameters</span></p></body></html>',
            )
        )
        self.label_42.setText(_translate("Form_2", "Pa max (target, W):"))
        self.label_43.setText(_translate("Form_2", "Pf max (limit, W):"))
        self.label_44.setText(_translate("Form_2", "Reflection Limit (%):"))
        self.POWER_TEST_CHECKBOX.setText(_translate("Form_2", "Include Test"))
        self.DATALOC_FIELD.setItemText(0, _translate("Form_2", "UA Results Directory"))
        self.DATALOC_FIELD.setItemText(1, _translate("Form_2", "Other directory"))
        self.label_49.setText(_translate("Form_2", "Storage Location:"))
        self.DATA_DIRECTORY_BUTTON.setText(_translate("Form_2", "Browse"))
        self.label_50.setText(_translate("Form_2", "Data Directory:"))
        self.label.setText(
            _translate(
                "Form_2",
                '<html><head/><body><p><span style=" font-size:14pt; font-weight:600; text-decoration: underline;">Measure Element Efficiency (RFB)</span></p></body></html>',
            )
        )


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form_2 = QtWidgets.QWidget()
    ui = Ui_Form_2()
    ui.setupUi(Form_2)
    Form_2.show()
    sys.exit(app.exec_())

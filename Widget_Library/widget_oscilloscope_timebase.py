# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_oscilloscope_timebase.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(604, 451)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 10, 89, 13))
        self.label.setObjectName("label")
        self.horizontal_settings_frame = QtWidgets.QFrame(Form)
        self.horizontal_settings_frame.setGeometry(QtCore.QRect(20, 30, 87, 86))
        self.horizontal_settings_frame.setStyleSheet("background:rgb(220, 242, 255)")
        self.horizontal_settings_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.horizontal_settings_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.horizontal_settings_frame.setObjectName("horizontal_settings_frame")
        self.layoutWidget = QtWidgets.QWidget(self.horizontal_settings_frame)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 95, 86))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horz_set_vert_layout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.horz_set_vert_layout.setContentsMargins(0, 0, 0, 0)
        self.horz_set_vert_layout.setObjectName("horz_set_vert_layout")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.horz_set_vert_layout.addWidget(self.label_2)
        self.timebase_spinbox = QtWidgets.QDoubleSpinBox(self.layoutWidget)
        self.timebase_spinbox.setStyleSheet("background:white")
        self.timebase_spinbox.setDecimals(3)
        self.timebase_spinbox.setMinimum(0.005)
        self.timebase_spinbox.setMaximum(500.0)
        self.timebase_spinbox.setProperty("value", 2.0)
        self.timebase_spinbox.setObjectName("timebase_spinbox")
        self.horz_set_vert_layout.addWidget(self.timebase_spinbox)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.horz_set_vert_layout.addWidget(self.label_3)
        self.delay_spinbox = QtWidgets.QDoubleSpinBox(self.layoutWidget)
        self.delay_spinbox.setStyleSheet("background:white")
        self.delay_spinbox.setMinimum(-500.0)
        self.delay_spinbox.setMaximum(500.0)
        self.delay_spinbox.setObjectName("delay_spinbox")
        self.horz_set_vert_layout.addWidget(self.delay_spinbox)
        self.config_osc_note = QtWidgets.QTextBrowser(Form)
        self.config_osc_note.setGeometry(QtCore.QRect(190, 30, 256, 192))
        self.config_osc_note.setStyleSheet("background:lightyellow")
        self.config_osc_note.setFrameShape(QtWidgets.QFrame.Box)
        self.config_osc_note.setObjectName("config_osc_note")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Horizontal settings"))
        self.label_2.setText(_translate("Form", "Timebase (us/div)"))
        self.label_3.setText(_translate("Form", "Delay (0.0 us)"))
        self.config_osc_note.setHtml(
            _translate(
                "Form",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" text-decoration: underline;">Note:</span></p>\n'
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline;"><br /></p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">This step can be used to ensure the acoustic signal is</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">visible within the scope window.</p>\n'
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Default values:</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">LF: Timebase = 0.2 us/div; Delay = 43 us</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">HF: Timebase = 0.1 us/div; Delay = 34.75</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">(the time delay in particular may need to change</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">depending on the positioning of the hydrophone).</p></body></html>',
            )
        )


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

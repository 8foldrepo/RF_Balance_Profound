# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_function_generator.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class Ui_config_func_generator(object):
    def setupUi(self, config_func_generator):
        config_func_generator.setObjectName("config_func_generator")
        config_func_generator.resize(648, 410)
        config_func_generator.setAutoFillBackground(True)
        config_func_generator.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                            "selection-color: rgb(85, 170, 255);\n"
                                            "selection-background-color: rgb(200, 200, 200);")
        self.label = QtWidgets.QLabel(config_func_generator)
        self.label.setGeometry(QtCore.QRect(20, 30, 158, 13))
        self.label.setObjectName("label")
        self.func_generation_config_frame = QtWidgets.QFrame(config_func_generator)
        self.func_generation_config_frame.setGeometry(QtCore.QRect(20, 50, 201, 145))
        self.func_generation_config_frame.setStyleSheet("background:rgb(220, 242, 255)")
        self.func_generation_config_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.func_generation_config_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.func_generation_config_frame.setObjectName("func_generation_config_frame")
        self.layoutWidget = QtWidgets.QWidget(self.func_generation_config_frame)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 86, 126))
        self.layoutWidget.setObjectName("layoutWidget")
        self.freq_ampl_mode_vert = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.freq_ampl_mode_vert.setContentsMargins(0, 0, 0, 0)
        self.freq_ampl_mode_vert.setObjectName("freq_ampl_mode_vert")
        self.label_7 = QtWidgets.QLabel(self.layoutWidget)
        self.label_7.setObjectName("label_7")
        self.freq_ampl_mode_vert.addWidget(self.label_7)
        self.freq_doublespin = QtWidgets.QDoubleSpinBox(self.layoutWidget)
        self.freq_doublespin.setStyleSheet("background-color:white")
        self.freq_doublespin.setDecimals(4)
        self.freq_doublespin.setMinimum(0.0001)
        self.freq_doublespin.setMaximum(19.9)
        self.freq_doublespin.setSingleStep(0.1)
        self.freq_doublespin.setProperty("value", 4.2)
        self.freq_doublespin.setObjectName("freq_doublespin")
        self.freq_ampl_mode_vert.addWidget(self.freq_doublespin)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.freq_ampl_mode_vert.addWidget(self.label_4)
        self.ampl_doublespin = QtWidgets.QSpinBox(self.layoutWidget)
        self.ampl_doublespin.setStyleSheet("background-color:white")
        self.ampl_doublespin.setMinimum(0)
        self.ampl_doublespin.setMaximum(10000)
        self.ampl_doublespin.setProperty("value", 100)
        self.ampl_doublespin.setObjectName("ampl_doublespin")
        self.freq_ampl_mode_vert.addWidget(self.ampl_doublespin)
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.freq_ampl_mode_vert.addWidget(self.label_5)
        self.mode_combo = QtWidgets.QComboBox(self.layoutWidget)
        self.mode_combo.setMinimumSize(QtCore.QSize(0, 19))
        self.mode_combo.setAutoFillBackground(False)
        self.mode_combo.setStyleSheet("background-color:white;\n"
                                      "selection-color:rgb(255, 255, 255);\n"
                                      "selection-background-color:rgb(85, 170, 255);")
        self.mode_combo.setObjectName("mode_combo")
        self.mode_combo.addItem("")
        self.mode_combo.addItem("")
        self.freq_ampl_mode_vert.addWidget(self.mode_combo)
        self.layoutWidget1 = QtWidgets.QWidget(self.func_generation_config_frame)
        self.layoutWidget1.setGeometry(QtCore.QRect(110, 10, 77, 44))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.enable_output_vert = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.enable_output_vert.setContentsMargins(0, 0, 0, 0)
        self.enable_output_vert.setObjectName("enable_output_vert")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_3.setObjectName("label_3")
        self.enable_output_vert.addWidget(self.label_3)
        self.enable_output_switch = Switch(self.layoutWidget1)
        self.enable_output_switch.setObjectName("enable_output_switch")
        self.enable_output_vert.addWidget(self.enable_output_switch)
        self.layoutWidget2 = QtWidgets.QWidget(self.func_generation_config_frame)
        self.layoutWidget2.setGeometry(QtCore.QRect(144, 97, 41, 39))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.cycles_vert = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.cycles_vert.setContentsMargins(0, 0, 0, 0)
        self.cycles_vert.setObjectName("cycles_vert")
        self.label_6 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_6.setObjectName("label_6")
        self.cycles_vert.addWidget(self.label_6)
        self.no_cycles_spin = QtWidgets.QSpinBox(self.layoutWidget2)
        self.no_cycles_spin.setStyleSheet("background-color:white")
        self.no_cycles_spin.setObjectName("no_cycles_spin")
        self.cycles_vert.addWidget(self.no_cycles_spin)
        self.layoutWidget3 = QtWidgets.QWidget(config_func_generator)
        self.layoutWidget3.setGeometry(QtCore.QRect(240, 30, 159, 41))
        self.layoutWidget3.setObjectName("layoutWidget3")
        self.set_freq_opt_vert = QtWidgets.QVBoxLayout(self.layoutWidget3)
        self.set_freq_opt_vert.setContentsMargins(0, 0, 0, 0)
        self.set_freq_opt_vert.setObjectName("set_freq_opt_vert")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget3)
        self.label_2.setObjectName("label_2")
        self.set_freq_opt_vert.addWidget(self.label_2)
        self.set_freq_opt_combo = QtWidgets.QComboBox(self.layoutWidget3)
        self.set_freq_opt_combo.setAutoFillBackground(False)
        self.set_freq_opt_combo.setStyleSheet("background-color:white;\n"
                                              "selection-color:rgb(255, 255, 255);\n"
                                              "selection-background-color:rgb(85, 170, 255);")
        self.set_freq_opt_combo.setObjectName("set_freq_opt_combo")
        self.set_freq_opt_combo.addItem("")
        self.set_freq_opt_combo.addItem("")
        self.set_freq_opt_combo.addItem("")
        self.set_freq_opt_combo.addItem("")
        self.set_freq_opt_combo.addItem("")
        self.set_freq_opt_vert.addWidget(self.set_freq_opt_combo)

        self.retranslateUi(config_func_generator)
        QtCore.QMetaObject.connectSlotsByName(config_func_generator)

    def retranslateUi(self, config_func_generator):
        _translate = QtCore.QCoreApplication.translate
        config_func_generator.setWindowTitle(_translate("config_func_generator", "Form"))
        self.label.setText(_translate("config_func_generator", "Function generator configuration"))
        self.label_7.setText(_translate("config_func_generator", "Frequency (MHz)"))
        self.label_4.setText(_translate("config_func_generator", "Amplitude (mVpp)"))
        self.ampl_doublespin.setToolTip(_translate("config_func_generator",
                                                   "<html><head/><body><p align=\"justify\">Typical test case is 100mV (less than what is used clinically). Limit of the power amplifier is 1000 mV, with a 10x attenautor the limit raises to 10 Vpp (10,000 mVpp)</p></body></html>"))
        self.label_5.setText(_translate("config_func_generator", "Mode"))
        self.mode_combo.setItemText(0, _translate("config_func_generator", "N Cycle"))
        self.mode_combo.setItemText(1, _translate("config_func_generator", "Continuous"))
        self.label_3.setText(_translate("config_func_generator", "Enable output"))
        self.enable_output_switch.setText(_translate("config_func_generator", "PushButton"))
        self.label_6.setText(_translate("config_func_generator", "#Cycles"))
        self.label_2.setText(_translate("config_func_generator", "Set frequency options"))
        self.set_freq_opt_combo.setToolTip(
            _translate("config_func_generator", "<html><head/><body><p><span style=\" font-size:10pt;\n"
                                                "                                text-decoration: underline;\">Selections Available:</span></p><p>-\n"
                                                "                                From config cluster </p><p>- Element pk low frequency</p><p>-\n"
                                                "                                Element pk high frequency</p><p>- Common low frequency</p><p>-\n"
                                                "                                Common high frequency</p></body></html>\n"
                                                "                            "))
        self.set_freq_opt_combo.setItemText(0, _translate("config_func_generator", "From config cluster"))
        self.set_freq_opt_combo.setItemText(1, _translate("config_func_generator", "Element pk low frequency"))
        self.set_freq_opt_combo.setItemText(2, _translate("config_func_generator", "Element pk high frequency"))
        self.set_freq_opt_combo.setItemText(3, _translate("config_func_generator", "Common low frequency"))
        self.set_freq_opt_combo.setItemText(4, _translate("config_func_generator", "Common high frequency"))


from ui_elements.switch import Switch

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    config_func_generator = QtWidgets.QWidget()
    ui = Ui_config_func_generator()
    ui.setupUi(config_func_generator)
    config_func_generator.show()
    sys.exit(app.exec_())

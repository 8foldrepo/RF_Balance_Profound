# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_rfb.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1021, 657)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 30, 1001, 621))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_23 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_23.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_23.setObjectName("gridLayout_23")
        self.widget_4 = QtWidgets.QWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_4.sizePolicy().hasHeightForWidth())
        self.widget_4.setSizePolicy(sizePolicy)
        self.widget_4.setMinimumSize(QtCore.QSize(400, 200))
        self.widget_4.setObjectName("widget_4")
        self.rfb_graph = Plot(self.widget_4)
        self.rfb_graph.setGeometry(QtCore.QRect(80, 60, 881, 311))
        self.rfb_graph.setObjectName("rfb_graph")
        self.label_121 = QtWidgets.QLabel(self.widget_4)
        self.label_121.setGeometry(QtCore.QRect(10, 10, 61, 16))
        self.label_121.setObjectName("label_121")
        self.label_123 = QtWidgets.QLabel(self.widget_4)
        self.label_123.setGeometry(QtCore.QRect(30, 30, 61, 16))
        self.label_123.setObjectName("label_123")
        self.legendsGroup = QtWidgets.QGroupBox(self.widget_4)
        self.legendsGroup.setGeometry(QtCore.QRect(110, 10, 851, 41))
        self.legendsGroup.setTitle("")
        self.legendsGroup.setObjectName("legendsGroup")
        self.reverse_pwr_img = QtWidgets.QLabel(self.legendsGroup)
        self.reverse_pwr_img.setGeometry(QtCore.QRect(10, 10, 30, 21))
        self.reverse_pwr_img.setText("")
        self.reverse_pwr_img.setPixmap(QtGui.QPixmap("../ui_elements/images/reverse power.png"))
        self.reverse_pwr_img.setObjectName("reverse_pwr_img")
        self.label_125 = QtWidgets.QLabel(self.legendsGroup)
        self.label_125.setGeometry(QtCore.QRect(440, 10, 73, 21))
        self.label_125.setObjectName("label_125")
        self.xsition_pwr_img = QtWidgets.QLabel(self.legendsGroup)
        self.xsition_pwr_img.setGeometry(QtCore.QRect(400, 10, 30, 21))
        self.xsition_pwr_img.setText("")
        self.xsition_pwr_img.setPixmap(QtGui.QPixmap("../ui_elements/images/xsition pts.png"))
        self.xsition_pwr_img.setObjectName("xsition_pwr_img")
        self.label_124 = QtWidgets.QLabel(self.legendsGroup)
        self.label_124.setGeometry(QtCore.QRect(43, 10, 73, 21))
        self.label_124.setObjectName("label_124")
        self.forward_pwr_img = QtWidgets.QLabel(self.legendsGroup)
        self.forward_pwr_img.setGeometry(QtCore.QRect(710, 10, 31, 21))
        self.forward_pwr_img.setMinimumSize(QtCore.QSize(20, 20))
        self.forward_pwr_img.setText("")
        self.forward_pwr_img.setPixmap(QtGui.QPixmap("../ui_elements/images/forward power.png"))
        self.forward_pwr_img.setObjectName("forward_pwr_img")
        self.label_126 = QtWidgets.QLabel(self.legendsGroup)
        self.label_126.setGeometry(QtCore.QRect(750, 10, 91, 21))
        self.label_126.setObjectName("label_126")
        self.gridLayout_23.addWidget(self.widget_4, 1, 0, 1, 4)
        self.verticalWidget_4 = QtWidgets.QWidget(self.layoutWidget)
        self.verticalWidget_4.setMaximumSize(QtCore.QSize(80, 16777215))
        self.verticalWidget_4.setObjectName("verticalWidget_4")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.verticalWidget_4)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_103 = QtWidgets.QLabel(self.verticalWidget_4)
        self.label_103.setObjectName("label_103")
        self.verticalLayout_7.addWidget(self.label_103)
        self.time_s_field = QtWidgets.QLineEdit(self.verticalWidget_4)
        self.time_s_field.setEnabled(False)
        self.time_s_field.setObjectName("time_s_field")
        self.verticalLayout_7.addWidget(self.time_s_field)
        self.label_104 = QtWidgets.QLabel(self.verticalWidget_4)
        self.label_104.setObjectName("label_104")
        self.verticalLayout_7.addWidget(self.label_104)
        self.mass_mg_field = QtWidgets.QLineEdit(self.verticalWidget_4)
        self.mass_mg_field.setEnabled(False)
        self.mass_mg_field.setObjectName("mass_mg_field")
        self.verticalLayout_7.addWidget(self.mass_mg_field)
        self.label_105 = QtWidgets.QLabel(self.verticalWidget_4)
        self.label_105.setObjectName("label_105")
        self.verticalLayout_7.addWidget(self.label_105)
        self.power_w_field = QtWidgets.QLineEdit(self.verticalWidget_4)
        self.power_w_field.setEnabled(False)
        self.power_w_field.setObjectName("power_w_field")
        self.verticalLayout_7.addWidget(self.power_w_field)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_7.addItem(spacerItem)
        self.gridLayout_23.addWidget(self.verticalWidget_4, 0, 0, 1, 1)
        self.results_layout = QtWidgets.QVBoxLayout()
        self.results_layout.setObjectName("results_layout")
        self.label_117 = QtWidgets.QLabel(self.layoutWidget)
        self.label_117.setMinimumSize(QtCore.QSize(0, 20))
        self.label_117.setMaximumSize(QtCore.QSize(16777215, 8))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_117.setFont(font)
        self.label_117.setObjectName("label_117")
        self.results_layout.addWidget(self.label_117)
        self.horizontalFrame = QtWidgets.QFrame(self.layoutWidget)
        self.horizontalFrame.setObjectName("horizontalFrame")
        self.rfb_results_info = QtWidgets.QHBoxLayout(self.horizontalFrame)
        self.rfb_results_info.setObjectName("rfb_results_info")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.label_118 = QtWidgets.QLabel(self.horizontalFrame)
        self.label_118.setMaximumSize(QtCore.QSize(16777215, 9))
        self.label_118.setObjectName("label_118")
        self.verticalLayout_15.addWidget(self.label_118)
        self.rfb_results_on = QtWidgets.QFrame(self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rfb_results_on.sizePolicy().hasHeightForWidth())
        self.rfb_results_on.setSizePolicy(sizePolicy)
        self.rfb_results_on.setMinimumSize(QtCore.QSize(100, 0))
        self.rfb_results_on.setMaximumSize(QtCore.QSize(80, 16777215))
        self.rfb_results_on.setAutoFillBackground(False)
        self.rfb_results_on.setFrameShape(QtWidgets.QFrame.Box)
        self.rfb_results_on.setObjectName("rfb_results_on")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.rfb_results_on)
        self.verticalLayout_8.setContentsMargins(9, -1, -1, -1)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_106 = QtWidgets.QLabel(self.rfb_results_on)
        self.label_106.setMaximumSize(QtCore.QSize(80, 10))
        self.label_106.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_106.setObjectName("label_106")
        self.verticalLayout_8.addWidget(self.label_106)
        self.power_on_w_field = QtWidgets.QLineEdit(self.rfb_results_on)
        self.power_on_w_field.setEnabled(False)
        self.power_on_w_field.setObjectName("power_on_w_field")
        self.verticalLayout_8.addWidget(self.power_on_w_field)
        self.label_107 = QtWidgets.QLabel(self.rfb_results_on)
        self.label_107.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label_107.setObjectName("label_107")
        self.verticalLayout_8.addWidget(self.label_107)
        self.power_on_rand_uc_field = QtWidgets.QLineEdit(self.rfb_results_on)
        self.power_on_rand_uc_field.setEnabled(False)
        self.power_on_rand_uc_field.setObjectName("power_on_rand_uc_field")
        self.verticalLayout_8.addWidget(self.power_on_rand_uc_field)
        self.label_108 = QtWidgets.QLabel(self.rfb_results_on)
        self.label_108.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label_108.setObjectName("label_108")
        self.verticalLayout_8.addWidget(self.label_108)
        self.power_on_total_uc_field = QtWidgets.QLineEdit(self.rfb_results_on)
        self.power_on_total_uc_field.setEnabled(False)
        self.power_on_total_uc_field.setObjectName("power_on_total_uc_field")
        self.verticalLayout_8.addWidget(self.power_on_total_uc_field)
        self.verticalLayout_15.addWidget(self.rfb_results_on)
        self.rfb_results_info.addLayout(self.verticalLayout_15)
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_119 = QtWidgets.QLabel(self.horizontalFrame)
        self.label_119.setMaximumSize(QtCore.QSize(16777215, 9))
        self.label_119.setObjectName("label_119")
        self.verticalLayout_14.addWidget(self.label_119)
        self.rfb_results_off = QtWidgets.QFrame(self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rfb_results_off.sizePolicy().hasHeightForWidth())
        self.rfb_results_off.setSizePolicy(sizePolicy)
        self.rfb_results_off.setMinimumSize(QtCore.QSize(100, 0))
        self.rfb_results_off.setMaximumSize(QtCore.QSize(80, 16777215))
        self.rfb_results_off.setAutoFillBackground(False)
        self.rfb_results_off.setFrameShape(QtWidgets.QFrame.Box)
        self.rfb_results_off.setObjectName("rfb_results_off")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.rfb_results_off)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_109 = QtWidgets.QLabel(self.rfb_results_off)
        self.label_109.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_109.setObjectName("label_109")
        self.verticalLayout_9.addWidget(self.label_109)
        self.power_off_w_field = QtWidgets.QLineEdit(self.rfb_results_off)
        self.power_off_w_field.setEnabled(False)
        self.power_off_w_field.setObjectName("power_off_w_field")
        self.verticalLayout_9.addWidget(self.power_off_w_field)
        self.label_110 = QtWidgets.QLabel(self.rfb_results_off)
        self.label_110.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_110.setObjectName("label_110")
        self.verticalLayout_9.addWidget(self.label_110)
        self.power_off_rand_uc_field = QtWidgets.QLineEdit(self.rfb_results_off)
        self.power_off_rand_uc_field.setEnabled(False)
        self.power_off_rand_uc_field.setObjectName("power_off_rand_uc_field")
        self.verticalLayout_9.addWidget(self.power_off_rand_uc_field)
        self.label_111 = QtWidgets.QLabel(self.rfb_results_off)
        self.label_111.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_111.setObjectName("label_111")
        self.verticalLayout_9.addWidget(self.label_111)
        self.power_off_total_uc_field = QtWidgets.QLineEdit(self.rfb_results_off)
        self.power_off_total_uc_field.setEnabled(False)
        self.power_off_total_uc_field.setObjectName("power_off_total_uc_field")
        self.verticalLayout_9.addWidget(self.power_off_total_uc_field)
        self.verticalLayout_14.addWidget(self.rfb_results_off)
        self.rfb_results_info.addLayout(self.verticalLayout_14)
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_120 = QtWidgets.QLabel(self.horizontalFrame)
        self.label_120.setMaximumSize(QtCore.QSize(16777215, 9))
        self.label_120.setObjectName("label_120")
        self.verticalLayout_13.addWidget(self.label_120)
        self.rfb_results_combined = QtWidgets.QFrame(self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rfb_results_combined.sizePolicy().hasHeightForWidth())
        self.rfb_results_combined.setSizePolicy(sizePolicy)
        self.rfb_results_combined.setMinimumSize(QtCore.QSize(100, 0))
        self.rfb_results_combined.setMaximumSize(QtCore.QSize(80, 16777215))
        self.rfb_results_combined.setAutoFillBackground(False)
        self.rfb_results_combined.setFrameShape(QtWidgets.QFrame.Box)
        self.rfb_results_combined.setObjectName("rfb_results_combined")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.rfb_results_combined)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.label_112 = QtWidgets.QLabel(self.rfb_results_combined)
        self.label_112.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_112.setObjectName("label_112")
        self.verticalLayout_10.addWidget(self.label_112)
        self.power_combined_field = QtWidgets.QLineEdit(self.rfb_results_combined)
        self.power_combined_field.setEnabled(False)
        self.power_combined_field.setObjectName("power_combined_field")
        self.verticalLayout_10.addWidget(self.power_combined_field)
        self.label_113 = QtWidgets.QLabel(self.rfb_results_combined)
        self.label_113.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_113.setObjectName("label_113")
        self.verticalLayout_10.addWidget(self.label_113)
        self.power_combined_rand_uc_field = QtWidgets.QLineEdit(self.rfb_results_combined)
        self.power_combined_rand_uc_field.setEnabled(False)
        self.power_combined_rand_uc_field.setObjectName("power_combined_rand_uc_field")
        self.verticalLayout_10.addWidget(self.power_combined_rand_uc_field)
        self.label_114 = QtWidgets.QLabel(self.rfb_results_combined)
        self.label_114.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_114.setObjectName("label_114")
        self.verticalLayout_10.addWidget(self.label_114)
        self.power_combined_total_uc_field = QtWidgets.QLineEdit(self.rfb_results_combined)
        self.power_combined_total_uc_field.setEnabled(False)
        self.power_combined_total_uc_field.setObjectName("power_combined_total_uc_field")
        self.verticalLayout_10.addWidget(self.power_combined_total_uc_field)
        self.verticalLayout_13.addWidget(self.rfb_results_combined)
        self.rfb_results_info.addLayout(self.verticalLayout_13)
        self.verticalLayout_17 = QtWidgets.QVBoxLayout()
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.label_122 = QtWidgets.QLabel(self.horizontalFrame)
        self.label_122.setMaximumSize(QtCore.QSize(16777215, 9))
        self.label_122.setObjectName("label_122")
        self.verticalLayout_17.addWidget(self.label_122)
        self.rfb_results_combined_2 = QtWidgets.QFrame(self.horizontalFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rfb_results_combined_2.sizePolicy().hasHeightForWidth())
        self.rfb_results_combined_2.setSizePolicy(sizePolicy)
        self.rfb_results_combined_2.setMinimumSize(QtCore.QSize(100, 0))
        self.rfb_results_combined_2.setMaximumSize(QtCore.QSize(80, 16777215))
        self.rfb_results_combined_2.setAutoFillBackground(False)
        self.rfb_results_combined_2.setFrameShape(QtWidgets.QFrame.Box)
        self.rfb_results_combined_2.setObjectName("rfb_results_combined_2")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.rfb_results_combined_2)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_115 = QtWidgets.QLabel(self.rfb_results_combined_2)
        self.label_115.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label_115.setObjectName("label_115")
        self.verticalLayout_12.addWidget(self.label_115)
        self.forward_power_w_field = QtWidgets.QLineEdit(self.rfb_results_combined_2)
        self.forward_power_w_field.setEnabled(False)
        self.forward_power_w_field.setObjectName("forward_power_w_field")
        self.verticalLayout_12.addWidget(self.forward_power_w_field)
        self.label_116 = QtWidgets.QLabel(self.rfb_results_combined_2)
        self.label_116.setMaximumSize(QtCore.QSize(16777215, 10))
        self.label_116.setObjectName("label_116")
        self.verticalLayout_12.addWidget(self.label_116)
        self.reflected_power_w_field = QtWidgets.QLineEdit(self.rfb_results_combined_2)
        self.reflected_power_w_field.setEnabled(False)
        self.reflected_power_w_field.setObjectName("reflected_power_w_field")
        self.verticalLayout_12.addWidget(self.reflected_power_w_field)
        self.verticalLayout_17.addWidget(self.rfb_results_combined_2)
        self.rfb_results_info.addLayout(self.verticalLayout_17)
        self.results_layout.addWidget(self.horizontalFrame)
        self.gridLayout_23.addLayout(self.results_layout, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_23.addItem(spacerItem1, 0, 2, 1, 1)
        self.tooltip = QtWidgets.QWidget(Form)
        self.tooltip.setGeometry(QtCore.QRect(0, 0, 1010, 27))
        self.tooltip.setObjectName("tooltip")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_121.setText(_translate("Form", "Data Display"))
        self.label_123.setText(_translate("Form", "Raw Power"))
        self.label_125.setText(_translate("Form", "Reverse Power"))
        self.label_124.setText(_translate("Form", "Forward Power"))
        self.label_126.setText(_translate("Form", "Acoustic Power"))
        self.label_103.setText(_translate("Form", "Time (s)"))
        self.label_104.setText(_translate("Form", "Mass (mg)"))
        self.label_105.setText(_translate("Form", "Power (W)"))
        self.label_117.setText(_translate("Form", "Results"))
        self.label_118.setText(_translate("Form", "Power On"))
        self.label_106.setText(_translate("Form", "Power (W)"))
        self.label_107.setText(_translate("Form", "Random UC (%)"))
        self.label_108.setText(_translate("Form", "Total UC (%)"))
        self.label_119.setText(_translate("Form", "Power Off"))
        self.label_109.setText(_translate("Form", "Power (W)"))
        self.label_110.setText(_translate("Form", "Random UC (%)"))
        self.label_111.setText(_translate("Form", "Total UC (%)"))
        self.label_120.setText(_translate("Form", "Combined"))
        self.label_112.setText(_translate("Form", "Power (W)"))
        self.label_113.setText(_translate("Form", "Random UC (%)"))
        self.label_114.setText(_translate("Form", "Total UC (%)"))
        self.label_122.setText(_translate("Form", "RF Electrical Power"))
        self.label_115.setText(_translate("Form", "Pf (W)"))
        self.label_116.setText(_translate("Form", "Pr (W)"))
        self.tooltip.setToolTip(_translate("Form", "This tab shows the data captured by the radiation force balance (RFB) and organizes the information into a grid and graph fashion, with a graph legend to explain what various lines represent"))
from ui_elements.ui_oscilloscope_plot import Plot


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

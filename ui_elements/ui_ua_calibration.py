from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import *

from Widget_Library.widget_ua_calibration import Ui_Form


class UACalibration(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ua_interface = None
        self.setupUi(self)
        self.manager = None
        self.config = None
        self.configure_signals()

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

    def set_ua_interface(self, ua_interface):
        self.ua_interface = ua_interface

    @pyqtSlot(list)
    def configure_signals(self):
        self.read_from_ua_button.clicked.connect(self.read_button_clicked)

    def read_button_clicked(self):
        #data, status = self.ua_interface.read_data()

        #Test values, remove later
        data = '1,CH2380,20170801,1,4.29,13.58,-88.1,64.5,72.7,68.0,67.1,72.8,70.0,63.2,69.4,61.4,65.6,' \
                    '32.1,32.5,36.5,30.7,35.2,36.3,31.9,35.2,33.9,35.4'.split(',')
        status = 0

        for i in range(7):
            item = QTableWidgetItem()
            item.setText(data[i])
            self.tableWidget.setItem(i,0, item)

        item = QTableWidgetItem()
        item.setText("CalRead")
        self.tableWidget.setItem(7, 0, item)

        item = QTableWidgetItem()
        item.setText(str(status))
        self.tableWidget.setItem(8, 0, item)

        for i in range(10):
            item = QTableWidgetItem()
            item.setText(data[i+7])
            self.tableWidget.setItem(i, 1, item)

        for i in range(10):
            item = QTableWidgetItem()
            item.setText(data[i+17])
            self.tableWidget.setItem(i, 2, item)

        #todo: fill data into ui

    def fill_labels(self):
        #Todo:
        pass

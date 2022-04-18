from PyQt5.QtWidgets import QDialog
from Widget_Library import write_cal_data_to_ua
from PyQt5.QtCore import pyqtSignal


class WriteCalDataToUA(QDialog, write_cal_data_to_ua.Ui_write_cal_data_to_ua):
    write_ua_signal = pyqtSignal()
    abort_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def configure_signals(self):
        self.cancel_button.clicked.connect(self.cancel_clicked)
        self.write_ua_button.clicked.connect(self.write_to_ua_clicked)

    def write_to_ua_clicked(self):
        self.write_ua_signal.emit()
        self.close()

    def cancel_clicked(self):
        self.abort_signal.emit()
        self.close()


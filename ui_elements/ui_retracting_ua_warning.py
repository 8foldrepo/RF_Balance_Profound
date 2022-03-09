from PyQt5.QtWidgets import QDialog
from Widget_Library import retracting_ua_warning
from PyQt5.QtCore import pyqtSignal


class UARetractDialog(QDialog, retracting_ua_warning.Ui_retracting_ua_warn):
    continue_signal = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def configure_signals(self):
        self.continue_button.clicked.connect(self.continue_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

    def continue_clicked(self):
        self.continue_signal.emit()
        self.close()

    def cancel_clicked(self):
        self.cancel_signal.emit()
        self.close()
from PyQt5.QtWidgets import QDialog
from Widget_Library import wtf_user_prompt_water_too_low
from PyQt5.QtCore import pyqtSignal

class WTFUserPromptWaterTooLow(QDialog, wtf_user_prompt_water_too_low.Ui_wtf_user_prompt_water_too_low):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()

    def __init__(self, high = False):
        super().__init__()
        self.setupUi(self)
        if high:
            self.user_prompt_output.setPlainText("Measurement tank water too high.\n\nPlease fill the measurement tank and click to continue.")
        self.configure_signals()

    def configure_signals(self):
        self.continue_button.clicked.connect(self.continue_clicked)
        self.abort_button.clicked.connect(self.abort_clicked)

    def continue_clicked(self):
        self.continue_signal.emit()
        self.close()

    def abort_clicked(self):
        self.abort_signal.emit()
        self.close()
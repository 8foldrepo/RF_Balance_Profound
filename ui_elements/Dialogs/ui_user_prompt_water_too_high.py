from PyQt5.QtWidgets import QDialog
from Widget_Library import wtf_user_prompt_water_too_high
from PyQt5.QtCore import pyqtSignal

class WTFUserPromptWaterTooHigh(QDialog, wtf_user_prompt_water_too_high.Ui_wtf_user_prompt_water_too_high):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.drain_clicked_bool = False
        self.setupUi(self)
        self.configure_signals()

    def configure_signals(self):
        self.drain_tank_button.clicked.connect(self.drain_clicked)

    # Manager will handle filling the tank, we need only continue the script
    def drain_clicked(self):
        self.drain_clicked_bool = True
        self.continue_signal.emit()
        self.close()

    # aborts the script if the dialog is closed
    def closeEvent(self,event):
        if not self.drain_clicked_bool:
            self.abort_signal.emit()
        event.accept()

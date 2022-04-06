from PyQt5.QtWidgets import QDialog, QApplication
from Widget_Library import wtf_user_prompt_pump_not_running
from PyQt5.QtCore import pyqtSignal

class WTFUserPromptPumpNotRunning(QDialog, wtf_user_prompt_pump_not_running.Ui_wtf_user_prompt_pump_not_running):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()
    set_pump_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.configure_signals()
        self.app = QApplication.instance()

    def configure_signals(self):
        self.continue_button.clicked.connect(self.continue_clicked)
        self.abort_button.clicked.connect(self.abort_clicked)
        self.ua_pump_status.clicked.connect(self.toggle_pump)

    def toggle_pump(self):
        self.ua_pump_status.dPtr.animate(self.ua_pump_status.isChecked())
        self.app.processEvents()
        print(self.ua_pump_status.isChecked())
        self.set_pump_signal.emit(self.ua_pump_status.isChecked())


    def continue_clicked(self):
        self.continue_signal.emit()
        self.close()

    def abort_clicked(self):
        self.abort_signal.emit()
        self.close()

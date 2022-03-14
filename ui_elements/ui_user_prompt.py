from PyQt5.QtWidgets import QDialog
from Widget_Library import wtf_user_prompt
from PyQt5.QtCore import pyqtSignal

class WTFUserPrompt (QDialog, wtf_user_prompt.Ui_wtf_user_prompt):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()
    retry_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def configure_signals(self):
        self.continue_button.clicked.connect(self.continue_clicked)
        self.abort_button.clicked.connect(self.abort_clicked)
        self.retry_button.clicked.connect(self.retry_clicked)

    def continue_clicked(self):
        self.continue_signal.emit()
        self.close()

    def abort_clicked(self):
        self.abort_signal.emit()
        self.close()

    def retry_clicked(self):
        self.retry_signal.emit()
        self.close()
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from Widget_Library import wtf_user_prompt_pump_not_running
from ui_elements.Dialogs.my_qdialog import MyQDialog


class WTFUserPromptPumpNotRunning(
    MyQDialog, wtf_user_prompt_pump_not_running.Ui_wtf_user_prompt_pump_not_running
):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()
    set_pump_signal = pyqtSignal(bool)

    def __init__(self, config=None):
        super().__init__(config=config)
        self.setupUi(self)
        self.configure_signals()
        self.app = QApplication.instance()

    def configure_signals(self):
        self.continue_button.clicked.connect(self.continue_clicked)
        self.abort_button.clicked.connect(self.abort_clicked)

    def continue_clicked(self):
        self.continue_signal.emit()
        self.dialog_resolved = True
        self.close()

    def abort_clicked(self):
        self.abort_signal.emit()
        self.close()

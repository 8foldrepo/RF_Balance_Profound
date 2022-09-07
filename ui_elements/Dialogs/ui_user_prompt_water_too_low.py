from PyQt5.QtCore import pyqtSignal
from Widget_Library import wtf_user_prompt_water_too_low
from ui_elements.Dialogs.my_qdialog import MyQDialog


class WTFUserPromptWaterTooLow(MyQDialog, wtf_user_prompt_water_too_low.Ui_wtf_user_prompt_water_too_low):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.fill_clicked_bool = False
        self.setupUi(self)
        self.configure_signals()

    def configure_signals(self):
        self.fill_tank_button.clicked.connect(self.fill_clicked)

    # Manager will handle filling the tank, we need only continue the script
    def fill_clicked(self):
        self.fill_clicked_bool = True
        self.continue_signal.emit()
        self.close()

    # aborts the script if the dialog is closed
    def closeEvent(self, event):
        if not self.fill_clicked_bool:
            self.abort_signal.emit()
        event.accept()

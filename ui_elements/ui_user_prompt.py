from ui_elements.my_qdialog import MyQDialog
from Widget_Library import wtf_user_prompt
from PyQt5.QtCore import pyqtSignal

class WTFUserPrompt (MyQDialog, wtf_user_prompt.Ui_wtf_user_prompt):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()
    retry_signal = pyqtSignal()

    def __init__(self, config = None):
        super().__init__(config=config)
        self.setupUi(self)
        self.configure_signals()

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

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    form = WTFUserPrompt(config=None)
    form.show()

    app.exec_()
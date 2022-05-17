from PyQt5.QtCore import pyqtSignal

from Widget_Library import wtf_user_prompt
from ui_elements.Dialogs.my_qdialog import MyQDialog


class WTFUserPrompt(MyQDialog, wtf_user_prompt.Ui_wtf_user_prompt):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()
    retry_signal = pyqtSignal()

    def __init__(self, config=None, access_level='Engineer', restrict_continue: bool = False):
        super().__init__(config=config)
        self.setupUi(self)
        self.configure_signals()
        if access_level == 'Operator' and restrict_continue:
            self.continue_button.setEnabled(False)

    def configure_signals(self):
        self.continue_button.clicked.connect(self.continue_clicked)
        self.abort_button.clicked.connect(self.abort_clicked)
        self.retry_button.clicked.connect(self.retry_clicked)

    def continue_clicked(self):
        self.dialog_resolved = True
        self.continue_signal.emit()
        self.close()

    def abort_clicked(self):
        self.close()

    def retry_clicked(self):
        self.dialog_resolved = True
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

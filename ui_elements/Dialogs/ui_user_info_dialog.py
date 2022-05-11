from PyQt5.QtCore import pyqtSignal

from Widget_Library import user_info_dialog
from ui_elements.Dialogs.my_qdialog import MyQDialog


class WTFUserInfo(MyQDialog, user_info_dialog.Ui_user_info_dialog):
    continue_signal = pyqtSignal()

    def __init__(self, config=None):
        super().__init__(config=config)
        self.setupUi(self)
        self.configure_signals()

    def configure_signals(self):
        self.continue_button.clicked.connect(self.continue_clicked)

    def continue_clicked(self):
        self.dialog_resolved = True
        self.continue_signal.emit()
        self.close()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    form = WTFUserPrompt(config=None)
    form.show()

    app.exec_()

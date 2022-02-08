import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Widget_Library import dialog_password


class PasswordDialog(QDialog, dialog_password.Ui_Dialog):
    """
    A dialog that prompts the user for access level and password

    Signals:
        access_granted_signal: emit when ok is pressed and the password check is successful

    """
    access_granted_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.style_ui()
        self.configure_signals()
        self.granted = False

    def style_ui(self):
        pass

    def configure_signals(self):
        self.ok_button.clicked.connect(self.check_password)
        self.cancel_button.clicked.connect(self.cancel_clicked)

    def check_password(self):
        self.granted = True
        self.access_granted_signal.emit(True)
        self.close()

    def cancel_clicked(self):
        self.access_granted_signal.emit(False)
        self.close()

    def closeEvent(self, event):
        if not self.granted:
            self.access_granted_signal.emit(False)
        event.accept()

    def _save_to_path(self, path):
        text = self.textEdit.toPlainText()
        try:
            with open(path, "w") as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path

            # Updating the Feedback window
            Progress = "Notes Saved"
            self.logger_signal.emit(str(Progress))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    form = PasswordDialog()
    form.show()
    app.exec_()

import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Widget_Library import dialog_password
from ui_elements.Dialogs.my_qdialog import MyQDialog


class PasswordDialog(MyQDialog, dialog_password.Ui_Dialog):
    """
    A dialog that prompts the user for access level and password

    Signals:
        access_granted_signal: emit when ok is pressed and the password check is successful

    """

    access_level_signal = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super().__init__(config=config, parent=parent)
        self.config = config
        self.setupUi(self)
        self.style_ui()
        self.configure_signals()

    def style_ui(self):
        pass

    def configure_signals(self):
        self.ok_button.clicked.connect(self.check_password)
        self.cancel_button.clicked.connect(self.cancel_clicked)

    def check_password(self):
        if self.access_level_combo.currentText() == "Operator" and self.password_field.text() == \
                self.config["User Accounts"]["Operator"]:
            self.dialog_resolved = True
            self.access_level_signal.emit("Operator")
            self.close()
        elif self.access_level_combo.currentText() == "Engineer" and self.password_field.text() == \
                self.config["User Accounts"]["Engineer"]:
            self.dialog_resolved = True
            self.access_level_signal.emit("Engineer")
            self.close()
        elif (
            "Administrator".upper() in self.access_level_combo.currentText().upper()
            and self.password_field.text() == self.config["User Accounts"]["Administrator"]
        ):
            self.dialog_resolved = True
            self.access_level_signal.emit("Administrator")
            self.close()

    def cancel_clicked(self):
        self.access_level_signal.emit("Denied")
        self.close()

    def closeEvent(self, event):
        if not self.dialog_resolved:
            self.access_level_signal.emit("Denied")
            self.abort_signal.emit()

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


def print_access(str):
    print(f"access: {str}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    form = PasswordDialog(config=None)
    form.access_level_signal.connect(print_access)
    form.show()

    app.exec_()

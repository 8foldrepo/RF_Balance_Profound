from PyQt5.QtWidgets import QDialog
from Widget_Library import test_data_capture
from PyQt5.QtCore import pyqtSignal
from ui_elements.my_qdialog import MyQDialog

class PretestDialog(MyQDialog, test_data_capture.Ui_test_data_capture):
    pretest_signal = pyqtSignal(str, str, str)  # signal from MainWindow to manager; operator, serial no., comment
    abort_signal = pyqtSignal()

    def __init__(self, parent=None, config=None):
        super().__init__(parent=parent, config=config)
        self.setupUi(self)
        self.configure_signals()

    def configure_signals(self):
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

    def ok_clicked(self):
        if self.ua_serial_no_inputline.text() is None or self.test_operator_inputline.text() is None:
            return

        self.pretest_signal.emit(self.test_operator_inputline.text(), self.ua_serial_no_inputline.text(), self.comment_inputbox.toPlainText())
        self.close()

    def cancel_clicked(self):
        self.abort_signal.emit()
        self.close()

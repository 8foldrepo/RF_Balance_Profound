from Widget_Library import retracting_ua_warning
from PyQt5.QtCore import pyqtSignal
from ui_elements.my_qdialog import MyQDialog

class UARetractDialog(MyQDialog, retracting_ua_warning.Ui_retracting_ua_warn):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()

    def __init__(self, config = None, parent=None):
        super().__init__(parent=parent, config=config)
        self.setupUi(self)
        self.configure_signals()

    def configure_signals(self):
        self.continue_button.clicked.connect(self.continue_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

    def continue_clicked(self):
        self.continue_signal.emit()
        self.close()

    def cancel_clicked(self):
        self.abort_signal.emit()
        self.close()

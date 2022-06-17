import logging
import os
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
from Utilities.useful_methods import log_msg, check_directory
from definitions import ROOT_DIR
log_formatter = logging.Formatter(LOGGER_FORMAT)
balance_logger = logging.getLogger("wtf_log")
check_directory("C:/Users/Isaiah/Documents/UA results/Logs")
with open("C:/Users/Isaiah/Documents/UA results/Logs/wtf.log", 'w+') as f:
    pass
file_handler = logging.FileHandler("C:/Users/Isaiah/Documents/UA results/Logs/wtf.log", mode="w")
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)


# Features common to all the dialogs in this project
class MyQDialog(QDialog):
    abort_signal = QtCore.pyqtSignal()
    root_logger = logging.getLogger(ROOT_LOGGER_NAME)

    def __init__(self, config, parent=None, ):
        super().__init__(parent=parent)

        # If this flag is not true when the dialog is closed, the script will abort
        self.dialog_resolved = False

        if config is not None:
            self.config = config
        else:
            self.config = load_configuration()
        self.set_icon()

    def closeEvent(self, event):
        """
        Abort the script if dialogs are closed without being addressed
        """
        if not self.dialog_resolved:
            self.abort_signal.emit()
        event.accept()

    def set_icon(self):
        """
        Set the icon to the 8Fold logo
        """
        path = os.path.join(ROOT_DIR, "resources", "8foldlogo.ico")
        self.setWindowIcon(QIcon(path))

    def log(self, message, level="info"):
        """
        Ability to log messages
        """
        log_msg(self, self.root_logger, message=message, level=level)

    def reject(self):
        """
        If escape key is pressed
        """
        self.dialog_resolved = False
        self.abort_signal.emit()
        self.close()

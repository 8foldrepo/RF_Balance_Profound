import os

import PyQt5

from definitions import ROOT_DIR
import logging

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtWidgets import QDialog

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
from Utilities.useful_methods import log_msg

log_formatter = logging.Formatter(LOGGER_FORMAT)

balance_logger = logging.getLogger("wtf_log")
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode="w")
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

from PyQt5.QtWidgets import *

from Widget_Library.widget_ua_calibration import Ui_Form


class UACalibration(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.manager = None
        self.config = None

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

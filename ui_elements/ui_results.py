from PyQt5.QtWidgets import *

from Widget_Library.widget_results import Ui_Form

class Results(QWidget, Ui_Form):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.config = None
        self.manager = None

    def set_manager(self, manager):
        self.manager = manager

    def set_config(self, config):
        self.config = config
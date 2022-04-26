import os

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon

from Widget_Library.tank_filling import Ui_Dialog
from definitions import ROOT_DIR
from ui_elements.my_qdialog import MyQDialog


class FillingDialog(MyQDialog, Ui_Dialog):
    def __init__(self, config, parent=None):
        super().__init__(config=config, parent=parent)
        self.config = config
        self.setupUi(self)
        self.granted = False

    @pyqtSlot(str)
    def water_level_slot(self, water_level):
        if water_level == 'level' or water_level == 'above_level':
            # Set dialog resolved to true so the script does not abort upon closing
            self.dialog_resolved = True
            self.close()


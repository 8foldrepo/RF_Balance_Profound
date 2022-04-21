from PyQt5.QtCore import pyqtSlot
from Widget_Library.tank_filling import Ui_Dialog
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
            self.close()
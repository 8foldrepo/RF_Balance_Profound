from PyQt5.QtCore import pyqtSlot

from Widget_Library.tank_filling import Ui_Dialog
from definitions import WaterLevel
from ui_elements.Dialogs.my_qdialog import MyQDialog


class FillingDialog(MyQDialog, Ui_Dialog):
    def __init__(self, config, parent=None):
        super().__init__(config=config, parent=parent)
        self.config = config
        self.setupUi(self)
        self.granted = False

    @pyqtSlot(WaterLevel)
    def water_level_slot(self, water_level):
        if water_level == WaterLevel.level or water_level == WaterLevel.above_level:
            # Set dialog resolved to true so the script does not abort upon closing
            self.dialog_resolved = True
            self.close()


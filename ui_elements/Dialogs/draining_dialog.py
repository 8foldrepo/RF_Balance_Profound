from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

from Widget_Library.tank_draining import Ui_Dialog
from data_structures.variable_containers import WaterLevel
from ui_elements.Dialogs.my_qdialog import MyQDialog


class DrainingDialog(MyQDialog, Ui_Dialog):
    # the str is the target water level, either WaterLevel.level or WaterLevel.below_level
    def __init__(self, config, target_level=WaterLevel.below_level, parent=None):
        super().__init__(config=config, parent=parent)
        if target_level == WaterLevel.below_level or target_level == WaterLevel.level:
            self.target_level = target_level
        else:
            self.log(level='error', message='Invalid target water level in DrainingDialog, defaulting to below_level')
            self.target_level = WaterLevel.below_level

        self.config = config
        self.setupUi(self)
        self.granted = False
        self.style_ui()

    @pyqtSlot()
    def tank_full_slot(self):
        """Dismisses the dialog if the tank was brought to level successfully"""
        if self.target_level == WaterLevel.level:
            self.dialog_resolved = True
            self.close()

    @pyqtSlot(WaterLevel)
    def water_level_slot(self, water_level: WaterLevel) -> None:
        """
        If parameter water_level = self.target_level: Set dialog resolved to true so script does not abort upon closing

        :param water_level:
            The water_level to check against the class' internal
            target_level, must match to mark dialog as resolved
        """
        if self.target_level == WaterLevel.below_level and water_level == WaterLevel.below_level:
            self.dialog_resolved = True
            self.close()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    form = DrainingDialog(config=None)
    form.show()
    app.exec_()

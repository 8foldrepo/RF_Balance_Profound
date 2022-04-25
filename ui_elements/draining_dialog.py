from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from Widget_Library.tank_draining import Ui_Dialog
from ui_elements.my_qdialog import MyQDialog


class DrainingDialog(MyQDialog, Ui_Dialog):
    # the str is the target water level, either 'level' or 'below_level'
    def __init__(self, config, target_level = 'below_level',parent=None):
        super().__init__(config=config, parent=parent)
        if target_level == 'below_level' or target_level == 'level':
            self.target_level = target_level
        else:
            self.log(level='error',message='Invalid target water level in DrainingDialog, defaulting to below_level')
            self.target_level='below_level'

        self.config = config
        self.setupUi(self)
        self.granted = False
        self.style_ui()

    @pyqtSlot(str)
    def water_level_slot(self, water_level):
        if water_level == self.target_level:
            # Set dialog resolved to true so the script does not abort upon closing
            self.dialog_resolved = True
            self.close()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    form = DrainingDialog(config=None)
    form.show()
    app.exec_()
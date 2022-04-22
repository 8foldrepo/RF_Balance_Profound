from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from Widget_Library.tank_draining import Ui_Dialog
from ui_elements.my_qdialog import MyQDialog


class DrainingDialog(MyQDialog, Ui_Dialog):
    def __init__(self, config, parent=None):
        super().__init__(config=config, parent=parent)
        self.config = config
        self.setupUi(self)
        self.granted = False
        self.style_ui()

    @pyqtSlot(str)
    def water_level_slot(self, water_level):
        if water_level == 'below_level':
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
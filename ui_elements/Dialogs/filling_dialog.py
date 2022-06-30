from PyQt5.QtCore import pyqtSlot, pyqtSignal
from Widget_Library.tank_filling import Ui_Dialog
from ui_elements.Dialogs.my_qdialog import MyQDialog


class FillingDialog(MyQDialog, Ui_Dialog):
    tank_full_override_signal = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(config=config, parent=parent)
        self.config = config
        self.setupUi(self)
        self.__configure_signals()
        self.granted = False

    def __configure_signals(self) -> None:
        self.override_button.clicked.connect(self.override_clicked)

    def override_clicked(self) -> None:
        self.tank_full_override_signal.emit()
        self.dialog_resolved = True
        self.close()

    @pyqtSlot()
    def tank_full_slot(self):
        # Set dialog resolved to true so the script does not abort upon closing
        self.dialog_resolved = True
        self.close()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    form = FillingDialog(config=None)
    form.show()
    app.exec_()

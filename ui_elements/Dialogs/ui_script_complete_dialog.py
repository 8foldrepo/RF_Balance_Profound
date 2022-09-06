from typing import List

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QTableWidgetItem, QApplication

from Hardware.signal_light import open_light
from Widget_Library import dialog_script_complete
from ui_elements.Dialogs.my_qdialog import MyQDialog


class ScriptCompleteDialog(MyQDialog, dialog_script_complete.Ui_Dialog):
    continue_signal = pyqtSignal()
    abort_signal = pyqtSignal()

    def __init__(self, config, passed_ray, description_ray=None, parent=None):
        super().__init__(config=config, parent=parent)
        self.setupUi(self)
        self.config = config
        self.style_ui()
        self.configure_signals()
        self.fill_table(passed_ray=passed_ray, description_ray=description_ray)

    def style_ui(self):
        self.tableWidget.horizontalHeader().resizeSection(1, 462)

    def configure_signals(self):
        self.ok_button.clicked.connect(self.ok_clicked)

    # Todo, test and make sure this works as expected
    @pyqtSlot(list, list)
    def fill_table(self, passed_ray: List[str], description_ray):
        for i in range(len(passed_ray)):

            # Create and populate table items
            passed_item = QTableWidgetItem()
            description_item = QTableWidgetItem()

            passed_item.setText(passed_ray[i])

            description_item.setText(description_ray[i])

            # Skip the 10th row
            if i == 10:
                i = 11

            # Add items to the table
            self.tableWidget.setItem(i, 0, passed_item)
            self.tableWidget.setItem(i, 1, description_item)

    def ok_clicked(self):
        # currently close will emit the continue signal. If this is changed, emit continue_signal here
        self.dialog_resolved = True

        # Reset the light
        with open_light(clearOut=False) as dev:
            pass

        self.close()

    def closeEvent(self, event) -> None:
        self.continue_signal.emit()
        self.dialog_resolved = True

        # Reset the light
        with open_light(clearOut=False) as dev:
            pass

        event.accept()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    form = ScriptCompleteDialog(
        config=None,
        passed_ray=["NO TEST"] * 11,
        description_ray=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
    )
    form.show()

    form.continue_signal.connect(lambda: print("Done! Continue script"))

    app.exec_()

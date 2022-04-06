from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QApplication
from Widget_Library import  dialog_script_complete

class ScriptCompleteDialog(QDialog, dialog_script_complete.Ui_Dialog):
    continue_signal = pyqtSignal()

    def __init__(self, config, passed_ray, description_ray = None, parent=None):
        super().__init__(parent=parent)
        self.config = config
        self.setupUi(self)
        self.style_ui()
        self.configure_signals()

    def style_ui(self):
        self.tableWidget.horizontalHeader().resizeSection(1, 462);

    #Todo, test and make sure this works as expected
    def fill_table(self, passed_ray, description_ray):
        for i in range(len(passed_ray)):
            passed_item = QTableWidgetItem()

            if passed_ray[i]:
                passed_item.setText("Pass")
            else:
                passed_item.setText("Fail")

            self.tableWidget.setItem(i, 0, passed_item)

            description_item = QTableWidgetItem()
            description_item.setText(description_ray[i])
            self.tableWidget.setItem(i, 1, description_item)

    def configure_signals(self):
        self.ok_button.clicked.connect(self.ok_clicked)

    def ok_clicked(self):
        print("closing...")
        self.continue_signal.emit()
        self.close()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    form = ScriptCompleteDialog(config=None, passed_ray=[True,True,True,True,True,False,False,False,False,False,False],
                    description_ray = ["1","2","3","4","5","6","7","8","9","10","11"])
    form.show()

    form.continue_signal.connect(lambda:print("Done! Continue script"))

    app.exec_()
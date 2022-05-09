from collections import OrderedDict

from PyQt5.QtWidgets import QWidget, QApplication

from Widget_Library.loop_over_elements import Ui_Form


class LoopOverElements(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict([('Task type', 'Loop over elements'), ('Element 1', 'TRUE'), ('Element 2', 'TRUE'),
                         ('Element 3', 'TRUE'), ('Element 4', 'TRUE'), ('Element 5', 'TRUE'), ('Element 6', 'TRUE'),
                         ('Element 7', 'TRUE'), ('Element 8', 'TRUE'), ('Element 9', 'TRUE'),
                         ('Element 10', 'TRUE')]))
        self.configure_signals()

    def configure_signals(self):
        self.element_checkbox_1.clicked.connect(self.element_1_clicked)
        self.element_checkbox_2.clicked.connect(self.element_2_clicked)
        self.element_checkbox_3.clicked.connect(self.element_3_clicked)
        self.element_checkbox_4.clicked.connect(self.element_4_clicked)
        self.element_checkbox_5.clicked.connect(self.element_5_clicked)
        self.element_checkbox_6.clicked.connect(self.element_6_clicked)
        self.element_checkbox_7.clicked.connect(self.element_7_clicked)
        self.element_checkbox_8.clicked.connect(self.element_8_clicked)
        self.element_checkbox_9.clicked.connect(self.element_9_clicked)
        self.element_checkbox_10.clicked.connect(self.element_10_clicked)

    def element_1_clicked(self):
        self.element_checkbox_1.dPtr.animate(self.element_checkbox_1.isChecked())

    def element_2_clicked(self):
        self.element_checkbox_2.dPtr.animate(self.element_checkbox_2.isChecked())

    def element_3_clicked(self):
        self.element_checkbox_3.dPtr.animate(self.element_checkbox_3.isChecked())

    def element_4_clicked(self):
        self.element_checkbox_4.dPtr.animate(self.element_checkbox_4.isChecked())

    def element_5_clicked(self):
        self.element_checkbox_5.dPtr.animate(self.element_checkbox_5.isChecked())

    def element_6_clicked(self):
        self.element_checkbox_6.dPtr.animate(self.element_checkbox_6.isChecked())

    def element_7_clicked(self):
        self.element_checkbox_7.dPtr.animate(self.element_checkbox_7.isChecked())

    def element_8_clicked(self):
        self.element_checkbox_8.dPtr.animate(self.element_checkbox_8.isChecked())

    def element_9_clicked(self):
        self.element_checkbox_9.dPtr.animate(self.element_checkbox_9.isChecked())

    def element_10_clicked(self):
        self.element_checkbox_10.dPtr.animate(self.element_checkbox_10.isChecked())

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        # todo, fill UI according to dictionary
        self.element_checkbox_1.setChecked(bool(var_dict["Element 1"]))
        self.element_checkbox_2.setChecked(bool(var_dict["Element 2"]))
        self.element_checkbox_3.setChecked(bool(var_dict["Element 3"]))
        self.element_checkbox_4.setChecked(bool(var_dict["Element 4"]))
        self.element_checkbox_5.setChecked(bool(var_dict["Element 5"]))
        self.element_checkbox_6.setChecked(bool(var_dict["Element 6"]))
        self.element_checkbox_7.setChecked(bool(var_dict["Element 7"]))
        self.element_checkbox_8.setChecked(bool(var_dict["Element 8"]))
        self.element_checkbox_9.setChecked(bool(var_dict["Element 9"]))
        self.element_checkbox_10.setChecked(bool(var_dict["Element 10"]))

    # todo: populate var_dict, arrange the arguments in the order of the example script
    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict([])
        var_dict["Task type"] = "Loop over elements"
        var_dict["Element 1"] = str(self.element_checkbox_1.isChecked())
        var_dict["Element 2"] = str(self.element_checkbox_2.isChecked())
        var_dict["Element 3"] = str(self.element_checkbox_3.isChecked())
        var_dict["Element 4"] = str(self.element_checkbox_4.isChecked())
        var_dict["Element 5"] = str(self.element_checkbox_5.isChecked())
        var_dict["Element 6"] = str(self.element_checkbox_6.isChecked())
        var_dict["Element 7"] = str(self.element_checkbox_7.isChecked())
        var_dict["Element 8"] = str(self.element_checkbox_8.isChecked())
        var_dict["Element 9"] = str(self.element_checkbox_9.isChecked())
        var_dict["Element 10"] = str(self.element_checkbox_10.isChecked())

        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = LoopOverElements()
    ui.show()
    sys.exit(app.exec_())

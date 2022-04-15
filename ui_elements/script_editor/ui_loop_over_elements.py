from Widget_Library.loop_over_elements import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication
from collections import OrderedDict


class LoopOverElements(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
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

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        # todo, fill UI according to dictionary
        # example lines
        # self..setText(arg_dict[""])
        # self..setChecked(arg_dict[""])
        # self..setValue(arg_dict[""])
        pass

    # todo: populate arg_dict, arrange the arguments in the order of the example script
    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()
        arg_dict['Task type'] = 'Loop over elements'
        # example lines, insert the name of the argument on the left as it appears in the example script.
        # the name of the ui element goes between the dots
        # self.arg_dict[""] = self..currentText()
        # self.arg_dict[""] = self..isChecked()
        # self.arg_dict[""] = round(self..value(),2)

        return arg_dict

    def read_in(self):
        pass


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = LoopOverElements()
    ui.show()
    sys.exit(app.exec_())

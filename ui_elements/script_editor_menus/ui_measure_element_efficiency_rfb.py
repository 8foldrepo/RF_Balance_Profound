# todo: change this import to the Qtdesigner file for this task type
from collections import OrderedDict

from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_measure_element_efficiency import Ui_Form_2
from ui_elements.my_qwidget import MyQWidget


# todo: change class name to one matching the task type
class MeasureElementefficiency(MyQWidget, Ui_Form_2):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        # fill in with default parameters in name-argument pairs
        self.orderedDict_to_ui(OrderedDict([('', ''), ('', 0)]))

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        # todo, fill UI according to dictionary
        # example lines
        # self..setText(var_dict[""])
        # self..setChecked(var_dict[""])
        # self..setValue(var_dict[""])
        pass

    # todo: populate var_dict, arrange the arguments in the order of the example script
    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()

        # example lines, insert the name of the argument on the left as it appears in the example script.
        # the name of the ui element goes between the dots
        # self.var_dict[""] = self..currentText()
        # self.var_dict[""] = self..isChecked()
        # self.var_dict[""] = round(self..value(),2)

        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = EditTemplate()
    ui.show()
    sys.exit(app.exec_())

#todo: change this import to the Qtdesigner file for this task type
from Widget_Library.measure_element_efficiency import Ui_Form_2
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict

#todo: change class name to one matching the task type
class MeasureElementEffeciency(MyQWidget, Ui_Form_2):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        #fill in with default parameters in name-argument pairs
        self.orderedDict_to_ui(OrderedDict([('', ''), ('', 0)]))

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        # todo, fill UI according to dictionary
        #example lines
        #self..setText(arg_dict[""])
        #self..setChecked(arg_dict[""])
        #self..setValue(arg_dict[""])
        pass

    # todo: populate arg_dict, arrange the arguments in the order of the example script
    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()

        #example lines, insert the name of the argument on the left as it appears in the example script.
        #the name of the ui element goes between the dots
        #self.arg_dict[""] = self..currentText()
        #self.arg_dict[""] = self..isChecked()
        #self.arg_dict[""] = round(self..value(),2)

        return arg_dict

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = EditTemplate()
    ui.show()
    sys.exit(app.exec_())

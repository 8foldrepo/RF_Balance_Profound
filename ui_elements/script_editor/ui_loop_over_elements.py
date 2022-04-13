from Widget_Library.loop_over_elements import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication
from collections import OrderedDict

class LoopOverElements(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.element_checkbox_1.clicked.connect(self.read_in)
        self.element_checkbox_2.clicked.connect(self.read_in)
        self.element_checkbox_3.clicked.connect(self.read_in)
        self.element_checkbox_4.clicked.connect(self.read_in)
        self.element_checkbox_5.clicked.connect(self.read_in)
        self.element_checkbox_6.clicked.connect(self.read_in)
        self.element_checkbox_7.clicked.connect(self.read_in)
        self.element_checkbox_8.clicked.connect(self.read_in)
        self.element_checkbox_9.clicked.connect(self.read_in)
        self.element_checkbox_10.clicked.connect(self.read_in)

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
        arg_dict['Task type'] = 'Loop over elements'
        #example lines, insert the name of the argument on the left as it appears in the example script.
        #the name of the ui element goes between the dots
        #self.arg_dict[""] = self..currentText()
        #self.arg_dict[""] = self..isChecked()
        #self.arg_dict[""] = round(self..value(),2)

        return arg_dict

    def read_in(self):
        element_check_list = [str(self.element_checkbox_1.checkState()),
                              str(self.element_checkbox_2.checkState()),
                              str(self.element_checkbox_3.checkState()),
                              str(self.element_checkbox_4.checkState()),
                              str(self.element_checkbox_5.checkState()),
                              str(self.element_checkbox_6.checkState()),
                              str(self.element_checkbox_7.checkState()),
                              str(self.element_checkbox_8.checkState()),
                              str(self.element_checkbox_9.checkState()),
                              str(self.element_checkbox_10.checkState())]

        # print(element_check_list) # debug terminal print

        element_prefix_list = ['Element 1 = ',
                               'Element 2 = ',
                               'Element 3 = ',
                               'Element 4 = ',
                               'Element 5 = ',
                               'Element 6 = ',
                               'Element 7 = ',
                               'Element 8 = ',
                               'Element 9 = ',
                               'Element 10 = ']

        # print(element_prefix_list) # debug terminal print

        check_list_boolean = ["FALSE" if '0' in x else "TRUE" for x in element_check_list]

        # print(check_list_boolean) # debug terminal print

        check_list_boolean_append = [y + z for y, z in zip(element_prefix_list, check_list_boolean)]

        for i in check_list_boolean_append:
            print(i)

        print('\n')


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = LoopOverElements()
    ui.show()
    sys.exit(app.exec_())

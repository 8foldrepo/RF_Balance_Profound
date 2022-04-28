from Widget_Library.widget_home_system import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication
from collections import OrderedDict

class HomeSystem(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(OrderedDict([('Task type', 'Home system_1'), ('Axis to home', 'Theta')]))

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        if var_dict['Axis to home'] == 'All Axes':
            self.radioButton.setChecked(True)
        elif var_dict['Axis to home'] == 'X':
            self.radioButton_2.setChecked(True)
        elif var_dict['Axis to home'] == 'Theta':
            self.radioButton_3.setChecked(True)

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()
        var_dict['Task type'] = 'Home system'

        if self.radioButton.isChecked():
            var_dict['Axis to home'] = 'All Axes'
        elif self.radioButton_2.isChecked():
            var_dict['Axis to home'] = 'X'
        elif self.radioButton_3.isChecked():
            var_dict['Axis to home'] = 'Theta'

        return var_dict


if __name__ == "__main__":
    import sys
    import time as t

    app = QApplication(sys.argv)
    ui = HomeSystem()
    ui.show()

    print(ui.ui_to_orderedDict())

    # Testing the UIs function and ability to dump to a dictionary and read into one.
    # Expected behavior, the dialog should open, check the first box after one second, return
    # the corresponding dictionary, then check the second box after another second

    #ui.radioButton.setChecked(True)
    #print(ui.ui_to_dictionary())
    #app.processEvents()
    #t.sleep(5)
    #app.processEvents()
    #t.sleep(5)
    #ui.radioButton_2.setChecked(True)
    #print(ui.ui_to_dictionary())


    #app.processEvents()
    #t.sleep(5)
    #app.processEvents()
    #t.sleep(5)
    #ui.radioButton.setChecked(True)
    #print(ui.ui_to_dictionary())
    #app.processEvents()
    #t.sleep(5)
    #ui.radioButton_3.setChecked(False)
    #print(ui.ui_to_dictionary())
    #app.processEvents()
    #print('Now you select one!')
    #t.sleep(5)
    #print(ui.ui_to_dictionary())

    # End of Test.

    sys.exit(app.exec_())

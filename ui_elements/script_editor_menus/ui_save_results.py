from Widget_Library.widget_save_results import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class SaveResults(MyQWidget, Ui_Form):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        # fill in with default parameters in name-argument pairs
        self.orderedDict_to_ui(OrderedDict([('Task type', 'Save results'), ('Save summary file', 'TRUE'),
                                            ('Write UA Calibration', 'TRUE'), ('PromptForCalWrite', '')]))

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        self.Save_Summary_File_Checkbox.setChecked(bool(arg_dict["Save summary file"]))
        self.Write_UA_Calibration_Checkbox.setChecked(bool(arg_dict["Write UA Calibration"]))
        self.With_Prompt_Checkbox.setChecked(bool(arg_dict["PromptForCalWrite"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict([])
        arg_dict["Task type"] = 'Save results'
        arg_dict["Save summary file"] = str(self.Save_Summary_File_Checkbox.isChecked())
        arg_dict["Write UA Calibration"] = str(self.Write_UA_Calibration_Checkbox.isChecked())
        arg_dict["PromptForCalWrite"] = str(self.With_Prompt_Checkbox.isChecked())

        return arg_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = SaveResults()
    ui.show()
    sys.exit(app.exec_())

from Widget_Library.widget_prompt_user_for_action import Ui_Form
from PyQt5.QtWidgets import QApplication
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class PromptUserForAction(MyQWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(OrderedDict([('Task type', 'Prompt user for action')
                                            , ('Prompt type', 'Disable UA pump')
                                            , ('Prompt message', '')]))

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        self.prompt_field.setCurrentText(var_dict['Prompt type'])
        self.prompt_message_field.setText(var_dict['Prompt message'])

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict([])
        var_dict['Task type'] = 'Prompt user for action'
        var_dict["Prompt type"] = self.prompt_field.currentText()
        var_dict["Prompt message"] = self.prompt_message_field.toPlainText()
        return var_dict

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = PromptUserForAction()
    ui.show()
    sys.exit(app.exec_())

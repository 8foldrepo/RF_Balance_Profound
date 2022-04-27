from Widget_Library.widget_prompt_user_for_action import Ui_Form
from PyQt5.QtWidgets import QApplication
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class PromptUserForAction(MyQWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(OrderedDict([('Task type', 'Prompt user for action')
                                            , ('Prompt type', 'Disable UA pump'), ('Message', '')]))

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        self.prompt_field.setCurrentText(arg_dict['Prompt type'])
        self.prompt_message_field.setText(arg_dict['Message'])


    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict([])
        arg_dict['Task type'] = 'Prompt user for action'
        arg_dict["Prompt type"] = self.prompt_field.currentText()
        arg_dict['Message'] = self.prompt_message_field.toPlainText()
        return arg_dict

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = PromptUserForAction()
    ui.show()
    sys.exit(app.exec_())

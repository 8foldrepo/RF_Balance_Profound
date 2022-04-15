from Widget_Library.widget_prompt_user_for_action import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication


class PromptUserForAction(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

    def ui_to_dictionary(self) -> dict:
        arg_dict = dict()
        arg_dict['Task type'] = 'Prompt user for action'

        if self.prompt_field.currentIndex() == 0:
            arg_dict['Prompt type'] = 'Disable UA pump'
        elif self.prompt_field.currentIndex() == 1:
            arg_dict['Prompt type'] = 'Selection 2'
        elif self.prompt_field.currentIndex() == 2:
            arg_dict['Prompt type'] = 'Selection 3'
        return arg_dict

    def orderedDict_to_ui(self, arg_dict: dict):
        if arg_dict['Prompt type'] == 'Disable UA pump':
            self.prompt_field.setCurrentIndex(0)
        elif arg_dict['Prompt type'] == 'Selection 2':  # Placeholder value for key.
            self.prompt_field.setCurrentIndex(1)
        elif arg_dict['Prompt type'] == 'Selection 3':  # Placeholder value for key.
            self.prompt_field.setCurrentIndex(2)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = PromptUserForAction()
    ui.show()
    # Testing UI to dictionary function
    #ui.prompt_field.setCurrentIndex(0)  # Change the number to change selection of prompt field
    #print(ui.ui_to_dictionary())
    # Testing dictionary to UI function # couldn't figure out how to test this
    #arg_dict = {'Task type': 'Prompt user for action',
    #            "Prompt type": 'Selection 3'}
    #print(arg_dict)
    # Testing done.
    sys.exit(app.exec_())

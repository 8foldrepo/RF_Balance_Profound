from Widget_Library.widget_move_system import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class MoveSystem(MyQWidget, Ui_Form):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.configure_signals()
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Move System'), ('Move Type', 'Go To')
                    , ('X POS', '1'), ('Move X', ''), ('Theta POS', '1')
                    , ('Move Theta', ''), ('Element', 'Element 2'), ('Target', 'RFB')]))
        # Left the string value blank because 'False' caused true, BUG

    def configure_signals(self):
        self.x_move_axis_switch.clicked.connect(self.x_axis_selected)
        self.theta_move_switch.clicked.connect(self.theta_axis_selected)

    def x_axis_selected(self):
        self.x_move_axis_switch.dPtr.animate(self.x_move_axis_switch.isChecked())

    def theta_axis_selected(self):
        self.theta_move_switch.dPtr.animate(self.theta_move_switch.isChecked())

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        self.move_type_combo.setCurrentText(arg_dict["Move Type"])
        self.x_pos_spin.setValue(int(arg_dict["X POS"]))
        self.x_move_axis_switch.setChecked(bool(arg_dict["Move X"]))
        self.theta_pos_spin.setValue(int(arg_dict["Theta POS"]))
        self.theta_move_switch.setChecked(bool(arg_dict["Move Theta"]))
        self.element_combo.setCurrentText(arg_dict["Element"])
        self.orientation_target_combo.setCurrentText(arg_dict["Target"])

    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()
        arg_dict["Task type"] = 'Move System'
        arg_dict["Move Type"] = self.move_type_combo.currentText()
        arg_dict["X POS"] = str(self.x_pos_spin.value())
        arg_dict["Move X"] = str(self.x_move_axis_switch.isChecked())
        arg_dict["Theta POS"] = str(self.theta_pos_spin.value())
        arg_dict["Move Theta"] = str(self.theta_move_switch.isChecked())
        arg_dict["Element"] = self.element_combo.currentText()
        arg_dict["Target"] = self.orientation_target_combo.currentText()
        return arg_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = MoveSystem()
    ui.show()
    sys.exit(app.exec_())

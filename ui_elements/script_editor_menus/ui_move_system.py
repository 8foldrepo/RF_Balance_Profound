from collections import OrderedDict

from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_move_system import Ui_Form
from ui_elements.my_qwidget import MyQWidget


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

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        self.move_type_combo.setCurrentText(var_dict["Move Type"])
        self.x_pos_spin.setValue(int(var_dict["X POS"]))
        self.x_move_axis_switch.setChecked(bool(var_dict["Move X"]))
        self.theta_pos_spin.setValue(int(var_dict["Theta POS"]))
        self.theta_move_switch.setChecked(bool(var_dict["Move Theta"]))
        self.element_combo.setCurrentText(var_dict["Element"])
        self.orientation_target_combo.setCurrentText(var_dict["Target"])

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()
        var_dict["Task type"] = 'Move System'
        if self.move_tabs.currentIndex() == 0:
            var_dict["Move Type"] = self.move_type_combo.currentText()
            var_dict["X POS"] = str(self.x_pos_spin.value())
            var_dict["Move X"] = str(self.x_move_axis_switch.isChecked())
            var_dict["Theta POS"] = str(self.theta_pos_spin.value())
            var_dict["Move Theta"] = str(self.theta_move_switch.isChecked())
        else:
            var_dict["Move Type"] = 'Go To Element'
            var_dict["Element"] = self.element_combo.currentText()
            var_dict["Target"] = self.orientation_target_combo.currentText()
        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = MoveSystem()
    ui.show()
    sys.exit(app.exec_())

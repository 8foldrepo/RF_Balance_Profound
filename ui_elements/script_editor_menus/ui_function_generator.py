from collections import OrderedDict

from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_function_generator import Ui_config_func_generator
from ui_elements.my_qwidget import MyQWidget


class FunctionGenerator(MyQWidget, Ui_config_func_generator):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.configure_signals()
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Function Generator'), ('Frequency', '4.2')
                    , ('Output on', 'True'), ('Amplitude (mVpp)', '50'), ('Mode', 'N Cycle')
                    , ('Cycles', '15'), ('Frequency Options', 'From config cluster')]))
        # Left the string value blank because 'False' caused true, BUG

    def configure_signals(self):
        self.enable_output_switch.clicked.connect(self.output_toggle)

    def output_toggle(self):
        self.enable_output_switch.dPtr.animate(self.enable_output_switch.isChecked())

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        self.freq_doublespin.setValue(float(var_dict["Frequency"]))
        self.enable_output_switch.setChecked(bool(var_dict["Output on"]))
        self.ampl_doublespin.setValue(int(var_dict["Amplitude (mVpp)"]))
        self.mode_combo.setCurrentText(var_dict["Mode"])
        self.no_cycles_spin.setValue(int(var_dict["Cycles"]))
        self.set_freq_opt_combo.setCurrentText(var_dict["Frequency Options"])

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()
        var_dict["Task type"] = 'Function Generator'
        var_dict["Frequency"] = str(self.freq_doublespin.value())
        var_dict["Output on"] = str(self.enable_output_switch.isChecked())
        var_dict["Amplitude"] = str(self.ampl_doublespin.value())
        var_dict["Mode"] = self.mode_combo.currentText()
        var_dict["Cycles"] = str(self.no_cycles_spin.value())
        var_dict["Frequency Options"] = self.set_freq_opt_combo.currentText()
        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FunctionGenerator()
    ui.show()
    sys.exit(app.exec_())

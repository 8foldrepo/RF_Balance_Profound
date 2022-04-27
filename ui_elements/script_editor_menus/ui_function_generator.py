from Widget_Library.widget_function_generator import Ui_config_func_generator
from PyQt5.QtWidgets import QWidget, QApplication
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class FunctionGenerator(MyQWidget, Ui_config_func_generator):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.configure_signals()
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Function Generator'), ('Frequency (MHz)', '1')
                    , ('Output on', 'True'), ('Amplitude (mVpp)', '1'), ('Mode', 'N Cycle')
                    , ('Cycles', '1'), ('Frequency Options', 'From config cluster')]))
        # Left the string value blank because 'False' caused true, BUG

    def configure_signals(self):
        self.enable_output_switch.clicked.connect(self.output_toggle)

    def output_toggle(self):
        self.enable_output_switch.dPtr.animate(self.enable_output_switch.isChecked())

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        self.freq_doublespin.setValue(float(arg_dict["Frequency"]))
        self.enable_output_switch.setChecked(bool(arg_dict["Output on"]))
        self.ampl_doublespin.setValue(int(arg_dict["Amplitude (mVpp)"]))
        self.mode_combo.setCurrentText(arg_dict["Mode"])
        self.no_cycles_spin.setValue(int(arg_dict["Cycles"]))
        self.set_freq_opt_combo.setCurrentText(arg_dict["Frequency Options"])

    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()
        arg_dict["Task type"] = 'Function Generator'
        arg_dict["Frequency"] = str(self.freq_doublespin.value())
        arg_dict["Output on"] = str(self.enable_output_switch.isChecked())
        arg_dict["Amplitude"] = str(self.ampl_doublespin.value())
        arg_dict["Mode"] = self.mode_combo.currentText()
        arg_dict["Cycles"] = str(self.no_cycles_spin.value())
        arg_dict["Frequency Options"] = self.set_freq_opt_combo.currentText()
        return arg_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FunctionGenerator()
    ui.show()
    sys.exit(app.exec_())

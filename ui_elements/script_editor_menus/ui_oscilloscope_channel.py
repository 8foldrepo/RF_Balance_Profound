from collections import OrderedDict

from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_oscilloscope_channels import Ui_config_osc_channels
from ui_elements.my_qwidget import MyQWidget


class OscilloscopeChannels(MyQWidget, Ui_config_osc_channels):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict(
                [
                    ("Task type", "Oscilloscope Channel"),
                    ("Channel 1 Enabled", "True"),
                    ("Channel 2 Enabled", ""),
                    ("Gain 1", "10"),
                    ("Gain 2", "10"),
                    ("Offset 1", "0"),
                    ("Offset 2", "0"),
                ]
            )
        )

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        self.channel_1_checkbox.setChecked(bool(var_dict["Channel 1 Enabled"]))
        self.channel_2_checkbox.setChecked(bool(var_dict["Channel 2 Enabled"]))
        self.gain_spin.setValue(int(var_dict["Gain 1"]))
        self.gain_right_spin.setValue(int(var_dict["Gain 2"]))
        self.offset_spin.setValue(int(var_dict["Offset 1"]))
        self.offset_right_spin.setValue(int(var_dict["Offset 2"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()
        var_dict["Task type"] = "Oscilloscope Channel"
        var_dict["Channel 1 Enabled"] = str(self.channel_1_checkbox.isChecked())
        var_dict["Channel 2 Enabled"] = str(self.channel_2_checkbox.isChecked())
        var_dict["Gain 1"] = str(self.gain_spin.value())
        var_dict["Gain 2"] = str(self.gain_right_spin.value())
        var_dict["Offset 1"] = str(self.offset_spin.value())
        var_dict["Offset 2"] = str(self.offset_right_spin.value())
        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = OscilloscopeChannels()
    ui.show()
    sys.exit(app.exec_())

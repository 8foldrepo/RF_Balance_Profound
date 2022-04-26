from Widget_Library.widget_oscilloscope_channels import Ui_config_osc_channels
from PyQt5.QtWidgets import QWidget, QApplication
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class OscilloscopeChannels(MyQWidget, Ui_config_osc_channels):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Oscilloscope Channel'), ('Channel 1 Enabled', 'True')
                    , ('Channel 2 Enabled', ''), ('Gain 1', '3')
                    , ('Gain 2', '3'), ('Offset 1', '5'), ('Offset 2', '5')]))

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        self.channel_1_checkbox.setChecked(bool(arg_dict["Channel 1 Enabled"]))
        self.channel_2_checkbox.setChecked(bool(arg_dict["Channel 2 Enabled"]))
        self.gain_spin.setValue(int(arg_dict["Gain 1"]))
        self.gain_right_spin.setValue(int(arg_dict["Gain 2"]))
        self.offset_spin.setValue(int(arg_dict["Offset 1"]))
        self.offset_right_spin.setValue(int(arg_dict["Offset 2"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()
        arg_dict["Task type"] = 'Oscilloscope Channel'
        arg_dict["Channel 1 Enabled"] = str(self.channel_1_checkbox.isChecked())
        arg_dict["Channel 2 Enabled"] = str(self.channel_2_checkbox.isChecked())
        arg_dict["Gain 1"] = str(self.gain_spin.value())
        arg_dict["Gain 2"] = str(self.gain_right_spin.value())
        arg_dict["Offset 1"] = str(self.offset_spin.value())
        arg_dict["Offset 2"] = str(self.offset_right_spin.value())
        return arg_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = OscilloscopeChannels()
    ui.show()
    sys.exit(app.exec_())

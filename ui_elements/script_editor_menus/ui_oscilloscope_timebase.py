from collections import OrderedDict

from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_oscilloscope_timebase import Ui_Form
from ui_elements.my_qwidget import MyQWidget


class OscilloscopeTimebase(MyQWidget, Ui_Form):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict(
                [
                    ("Task type", "Configure Oscilloscope Timebase"),
                    ("Timebase", ".2"),
                    ("Delay", "43"),
                ]
            )
        )

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        self.timebase_spinbox.setValue(float(var_dict["Timebase"]))
        self.delay_spinbox.setValue(float(var_dict["Delay"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()
        var_dict["Task type"] = "Configure Oscilloscope Timebase"
        var_dict["Timebase"] = str(self.timebase_spinbox.value())
        var_dict["Delay"] = str(self.delay_spinbox.value())
        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = OscilloscopeTimebase()
    ui.show()
    sys.exit(app.exec_())

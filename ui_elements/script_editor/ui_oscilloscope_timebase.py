from Widget_Library.widget_oscilloscope_timebase import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class OscilloscopeTimebase(MyQWidget, Ui_Form):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Oscilloscope Timebase'), ('Timebase', '1')
                    , ('Delay', '1')]))

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        self.timebase_spinbox.setValue(int(arg_dict["Timebase"]))
        self.delay_spinbox.setValue(int(arg_dict["Delay"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()
        arg_dict["Task type"] = 'Oscilloscope Timebase'
        arg_dict["Timebase"] = str(self.timebase_spinbox.value())
        arg_dict["Delay"] = str(self.delay_spinbox.value())
        return arg_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = OscilloscopeTimebase()
    ui.show()
    sys.exit(app.exec_())

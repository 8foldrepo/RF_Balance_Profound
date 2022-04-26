from Widget_Library.widget_select_ua_channel import Ui_select_ua_channel
from PyQt5.QtWidgets import QWidget, QApplication
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class SelectUAChannel(MyQWidget, Ui_select_ua_channel):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Select UA Channel'), ('Channel', '1')]))

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        self.sel_ua_channel_spin.setValue(int(arg_dict["Channel"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()
        arg_dict["Task type"] = 'Select UA Channel'
        arg_dict["Channel"] = str(self.sel_ua_channel_spin.value())
        return arg_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = SelectUAChannel()
    ui.show()
    sys.exit(app.exec_())

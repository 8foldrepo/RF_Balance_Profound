from collections import OrderedDict

from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_select_ua_channel import Ui_select_ua_channel
from ui_elements.my_qwidget import MyQWidget


class SelectUAChannel(MyQWidget, Ui_select_ua_channel):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict([("Task type", "Select UA Channel"), ("Channel", "1")])
        )

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        self.sel_ua_channel_spin.setValue(int(var_dict["Channel"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()
        var_dict["Task type"] = "Select UA Channel"
        var_dict["Channel"] = str(self.sel_ua_channel_spin.value())
        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = SelectUAChannel()
    ui.show()
    sys.exit(app.exec_())

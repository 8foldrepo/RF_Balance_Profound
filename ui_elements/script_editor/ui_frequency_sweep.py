from Widget_Library.widget_frequency_sweep import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class FrequencySweep(MyQWidget, Ui_Form):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Frequency sweep'), ('Frequency Range', 'High frequency')
                    , ('Start Frequency', '5'), ('End Frequency', '5')
                    , ('Coarse Increment', '5'), ('Fine Increment', '5'), ('Burst count', '5')
                    , ('Amplitude', '5'), ('Scope channel', 'Channel 2')
                    , ('Acquisition Type', 'Single Waveform'), ('Averages', '5')
                    , ('Data storage', 'Store'), ('Storage location', 'Custom directory')
                    , ('Data directory', 'Place Holder')
                    , ('Peak VSI threshold', '5'), ('Include test', 'TRUE')]))

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        self.freq_range_combo.setCurrentText(arg_dict["Frequency Range"])
        self.start_freq_spin.setValue(int(arg_dict["Start Frequency"]))
        self.end_freq_doublespin.setValue(float(arg_dict["End Frequency"]))
        self.coarse_inc_doublespin.setValue(float(arg_dict["Coarse Increment"]))
        self.fine_incr_doublespin.setValue(float(arg_dict["Fine Increment"]))
        self.burst_count_spin.setValue(int(arg_dict["Burst count"]))
        self.amplitude_spin.setValue(int(arg_dict["Amplitude"]))
        self.scope_channel_combo.setCurrentText(arg_dict["Scope channel"])
        self.acq_type_combo.setCurrentText(arg_dict["Acquisition Type"])
        self.averages_spinbox.setValue(int(arg_dict["Averages"]))
        self.data_storage_combo.setCurrentText(arg_dict["Data storage"])
        self.storage_loc_combo.setCurrentText(arg_dict["Storage location"])
        self.data_direc_input.setText(arg_dict["Data directory"])
        self.peak_vsi_spinbox.setValue(int(arg_dict["Peak VSI threshold"]))
        self.incl_test_check.setChecked(bool(arg_dict["Include test"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()
        arg_dict["Task type"] = 'Frequency sweep'
        arg_dict["Frequency Range"] = self.freq_range_combo.currentText()
        arg_dict["Start Frequency"] = str(self.start_freq_spin.value())
        arg_dict["End Frequency"] = str(self.end_freq_doublespin.value())
        arg_dict["Coarse Increment"] = str(self.coarse_inc_doublespin.value())
        arg_dict["Fine Increment"] = str(self.fine_incr_doublespin.value())
        arg_dict["Burst count"] = str(self.burst_count_spin.value())
        arg_dict["Amplitude"] = str(self.amplitude_spin.value())
        arg_dict["Scope channel"] = self.scope_channel_combo.currentText()
        arg_dict["Acquisition Type"] = self.acq_type_combo.currentText()
        arg_dict["Averages"] = str(self.averages_spinbox.value())
        arg_dict["Data storage"] = self.data_storage_combo.currentText()
        arg_dict["Storage location"] = self.storage_loc_combo.currentText()
        arg_dict["Data directory"] = self.data_direc_input.text()
        arg_dict["Peak VSI threshold"] = str(self.peak_vsi_spinbox.value())
        arg_dict["Include test"] = str(self.incl_test_check.isChecked())
        return arg_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FrequencySweep()
    ui.show()
    sys.exit(app.exec_())

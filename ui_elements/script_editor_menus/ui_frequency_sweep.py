from collections import OrderedDict

from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_frequency_sweep import Ui_Form
from ui_elements.my_qwidget import MyQWidget


class FrequencySweep(MyQWidget, Ui_Form):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Frequency sweep'), ('Frequency range', 'High frequency')
                    , ('Start frequency (MHz)', '4'), ('End frequency (MHz)', '5')
                    , ('Coarse Increment (MHz)', '.1'), ('Fine Increment (MHz)', '.01'), ('Burst count', '15')
                    , ('Amplitude (mVpp)', '100'), ('Scope channel', 'Channel 1')
                    , ('Acquisition type', 'Single Waveform'), ('Averages', '1')
                    , ('Data storage', 'Store profiles only'), ('Storage location', 'UA Results Directory')
                    , ('Data directory', '')
                    , ('Peak VSI threshold', '1000'), ('Include test', 'True')]))

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        self.freq_range_combo.setCurrentText(var_dict["Frequency range"])
        self.start_freq_spin.setValue(int(var_dict["Start frequency (MHz)"]))
        self.end_freq_doublespin.setValue(float(var_dict["End frequency (MHz)"]))
        self.coarse_inc_doublespin.setValue(float(var_dict["Coarse Increment (MHz)"]))
        self.fine_incr_doublespin.setValue(float(var_dict["Fine Increment (MHz)"]))
        self.burst_count_spin.setValue(int(var_dict["Burst count"]))
        self.amplitude_spin.setValue(int(var_dict["Amplitude (mVpp)"]))
        self.scope_channel_combo.setCurrentText(var_dict["Scope channel"])
        self.acq_type_combo.setCurrentText(var_dict["Acquisition type"])
        self.averages_spinbox.setValue(int(var_dict["Averages"]))
        self.data_storage_combo.setCurrentText(var_dict["Data storage"])
        self.storage_loc_combo.setCurrentText(var_dict["Storage location"])
        self.data_direc_input.setText(var_dict["Data directory"])
        self.peak_vsi_spinbox.setValue(int(var_dict["Peak VSI threshold"]))
        self.incl_test_check.setChecked(bool(var_dict["Include test"]))

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()
        var_dict["Task type"] = "Frequency sweep"
        var_dict["Frequency range"] = self.freq_range_combo.currentText()
        var_dict["Start frequency (MHz)"] = str(self.start_freq_spin.value())
        var_dict["End frequency (MHz)"] = str(self.end_freq_doublespin.value())
        var_dict["Coarse increment (MHz)"] = str(self.coarse_inc_doublespin.value())
        var_dict["Fine increment (MHz)"] = str(self.fine_incr_doublespin.value())
        var_dict["Burst count"] = str(self.burst_count_spin.value())
        var_dict["Amplitude (mVpp)"] = str(self.amplitude_spin.value())
        var_dict["Scope channel"] = self.scope_channel_combo.currentText()
        var_dict["Acquisition type"] = self.acq_type_combo.currentText()
        var_dict["Averages"] = str(self.averages_spinbox.value())
        var_dict["Data storage"] = self.data_storage_combo.currentText()
        var_dict["Storage location"] = self.storage_loc_combo.currentText()
        var_dict["Data directory"] = self.data_direc_input.text()
        var_dict["Peak VSI threshold"] = str(self.peak_vsi_spinbox.value())
        var_dict["Include test"] = str(self.incl_test_check.isChecked())
        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FrequencySweep()
    ui.show()
    sys.exit(app.exec_())

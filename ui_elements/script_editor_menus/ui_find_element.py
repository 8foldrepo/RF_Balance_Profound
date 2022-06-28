from collections import OrderedDict

from PyQt5.QtWidgets import QApplication, QFileDialog

from Utilities.useful_methods import cast_as_bool
from Widget_Library.widget_find_element import Ui_FIND_ELEMENT_WIDGET
from ui_elements.my_qwidget import MyQWidget


class FindElement(MyQWidget, Ui_FIND_ELEMENT_WIDGET):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(
            OrderedDict(
                [
                    ("Task type", 'Find element "n"'),
                    ("Element", "Element 1"),
                    ("X Incr. (mm)", "0.250000"),
                    ("X #Pts.", "21"),
                    ("Theta Incr. (deg)", "-0.400000"),
                    ("Theta #Pts.", "41"),
                    ("Scope channel", "Channel 1"),
                    ("Acquisition type", "N Averaged Waveform"),
                    ("Averages", "16"),
                    ("Data storage", "Do not store"),
                    ("Storage location", "UA results directory"),
                    ("Data directory", ""),
                    ("Max. position error (+/- mm)", "0.200000"),
                    ("ElementPositionTest", "FALSE"),
                    ("Max angle variation (deg)", "2.000000"),
                    ("BeamAngleTest", "FALSE"),
                    ("Frequency settings", "Common low frequency"),
                    ("Auto set timebase", "TRUE"),
                    ("#Cycles.Capture", "10"),
                    ("#Cycles.Delay", "0"),
                    ("Frequency (MHz)", "4.400000"),
                    ("Amplitude (mV)", "50.000000"),
                    ("Burst count", "50"),
                ]
            )
        )
        self.configure_signals()

    def configure_signals(self):
        self.OSCOPE_DATA_DIRECTORY_BUTTON.clicked.connect(self.browse_clicked)

    def browse_clicked(self):
        self.filename = QFileDialog.getExistingDirectory(self)
        self.OSCOPE_DATA_DIRECTORY_FIELD.setText(self.filename)
        return self.filename

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        # todo, fill UI according to dictionary
        self.ELEMENT_SELECTION_FIELD.setCurrentText(var_dict["Element"])
        # self.OSCOPE_CHANNEL_FIELD.setCurrentText(var_dict["Scope channel"].split(" "[1]))
        self.OSCOPE_AQTYPE_FIELD.setCurrentText(var_dict["Acquisition type"])
        self.OSCOPE_SAMPLES_FIELD.setCurrentText(var_dict["Averages"])
        self.OSCOPE_DATASTORE_FIELD.setCurrentText(var_dict["Data storage"])
        self.OSCOPE_DATALOC_FIELD.setCurrentText(var_dict["Storage location"])
        self.FREQANG_PRESET_FIELD.setCurrentText(var_dict["Frequency settings"])
        self.FREQANG_POS_TEST_CHECKBOX.setChecked(cast_as_bool(var_dict["ElementPositionTest"]))
        self.FREQANG_POS_TEST_CHECKBOX.setChecked(cast_as_bool(var_dict["BeamAngleTest"]))
        self.OSCOPE_AUTO_CHECKBOX.setChecked(cast_as_bool(var_dict["Auto set timebase"]))
        self.FREQANG_FREQ_FIELD.setValue(float(var_dict["Frequency (MHz)"]))
        self.FREQANG_BURST_FIELD.setValue(int(var_dict["Burst count"]))
        self.FREQANG_VOLT_FIELD.setValue(float(var_dict["Amplitude (mV)"]))
        self.FREQANG_ANG_FIELD.setValue(float(var_dict["Max angle variation (deg)"]))
        self.FREQANG_POS_FIELD.setValue(float(var_dict["Max. position error (+/- mm)"]))
        self.OSCOPE_CYCLES_FIELD.setValue(float(var_dict["#Cycles.Capture"]))
        self.OSCOPE_DELAYCYCLE_FIELD.setValue(float(var_dict["#Cycles.Delay"]))
        self.X_PNT_FIELD.setValue(int(var_dict["X #Pts."]))
        self.THETA_PNT_FIELD.setValue(int(var_dict["Theta #Pts."]))
        self.X_INCREMENT_FIELD.setValue(float(var_dict["X Incr. (mm)"]))
        self.THETA_INCREMENT_FIELD.setValue(float(var_dict["Theta Incr. (deg)"]))

    # todo: populate var_dict
    # todo: change variable names to dict assignment with correct name like the first line
    # todo: arrange the arguments in the order of the example script
    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict([])
        var_dict["Task type"] = "Find element n"
        var_dict["Element"] = self.ELEMENT_SELECTION_FIELD.currentText()
        var_dict["Scope channel"] = self.OSCOPE_CHANNEL_FIELD.currentText()
        var_dict["Acquisition type"] = self.OSCOPE_AQTYPE_FIELD.currentText()
        var_dict["Averages"] = self.OSCOPE_SAMPLES_FIELD.currentText()
        var_dict["Data storage"] = self.OSCOPE_DATASTORE_FIELD.currentText()
        var_dict["Storage location"] = self.OSCOPE_DATALOC_FIELD.currentText()
        var_dict["Data directory"] = self.OSCOPE_DATA_DIRECTORY_FIELD.text()
        var_dict["Frequency settings"] = self.FREQANG_PRESET_FIELD.currentText()
        var_dict["ElementPositionTest"] = str(
            self.FREQANG_POS_TEST_CHECKBOX.isChecked()
        )
        var_dict["BeamAngleTest"] = str(self.FREQANG_ANG_TEST_CHECKBOX.isChecked())
        var_dict["Auto set timebase"] = str(self.OSCOPE_AUTO_CHECKBOX.isChecked())
        var_dict["Frequency (MHz)"] = "%.4f" % self.FREQANG_FREQ_FIELD.value()
        var_dict["Burst count"] = str(self.FREQANG_BURST_FIELD.value())
        var_dict["Amplitude (mV)"] = str(self.FREQANG_VOLT_FIELD.value())
        var_dict["Max angle variation (deg)"] = str(self.FREQANG_ANG_FIELD.value())
        var_dict["Max. position error (+/- mm)"] = "%.3f" % (
            self.FREQANG_POS_FIELD.value()
        )
        var_dict["#Cycles.Capture"] = str(self.OSCOPE_CYCLES_FIELD.value())
        var_dict["#Cycles.Delay"] = str(self.OSCOPE_DELAYCYCLE_FIELD.value())
        var_dict["X #Pts."] = str(self.X_PNT_FIELD.value())
        var_dict["Theta #Pts."] = str(self.THETA_PNT_FIELD.value())
        var_dict["X Incr. (mm)"] = "%.4f" % (self.X_INCREMENT_FIELD.value())
        var_dict["Theta Incr. (deg)"] = str(self.THETA_INCREMENT_FIELD.value())

        return var_dict


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FindElement()
    ui.show()
    sys.exit(app.exec_())

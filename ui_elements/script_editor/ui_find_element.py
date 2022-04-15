from Widget_Library.widget_find_element import Ui_FIND_ELEMENT_WIDGET
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class FindElement(MyQWidget, Ui_FIND_ELEMENT_WIDGET):
    def __init__(self, config = None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.orderedDict_to_ui(OrderedDict([('Task type', 'Find element \"n\"'), ('Element', 'Element 1'), ('X Incr. (mm)', '0.250000'),
                            ('X #Pts.', '21'), ('Theta Incr. (deg)', '-0.400000'), ('Theta #Pts.', '41'),
                            ('Scope channel', 'Channel 1'), ('Acquisition type', 'N Averaged Waveform'),
                            ('Averages', '16'), ('Data storage', 'Do not store'),
                            ('Storage location', 'UA results directory'), ('Data directory', ''),
                            ('Max. position error (+/- mm)', '0.200000'), ('ElementPositionTest', 'FALSE'),
                            ('Max angle variation (deg)', '2.000000'), ('BeamAngleTest', 'FALSE'),
                            ('Frequency settings', 'Avg. Low frequency'), ('Auto set timebase', 'TRUE'),
                            ('#Cycles.Capture', '10'), ('#Cycles.Delay', '0'), ('Frequency (MHz)', '4.400000'),
                            ('Amplitude (mV)', '50.000000'), ('Burst count', '50')]))

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        #todo, fill UI according to dictionary
        self.ELEMENT_SELECTION_FIELD.setCurrentText(arg_dict["Element"])
        #self.OSCOPE_CHANNEL_FIELD.setCurrentText(arg_dict["Scope channel"].split(" "[1]))
        self.OSCOPE_AQTYPE_FIELD.setCurrentText(arg_dict["Acquisition type"])
        self.OSCOPE_SAMPLES_FIELD.setCurrentText(arg_dict["Averages"])
        self.OSCOPE_DATASTORE_FIELD.setCurrentText(arg_dict["Data storage"])
        self.OSCOPE_DATALOC_FIELD.setCurrentText(arg_dict["Storage location"])
        self.FREQANG_PRESET_FIELD.setCurrentText(arg_dict["Frequency settings"])
        self.FREQANG_POS_TEST_CHECKBOX.setChecked(bool(arg_dict["ElementPositionTest"]))
        self.FREQANG_POS_TEST_CHECKBOX.setChecked(bool(arg_dict["BeamAngleTest"]))
        self.OSCOPE_AUTO_CHECKBOX.setChecked(bool(arg_dict["Auto set timebase"]))
        self.FREQANG_FREQ_FIELD.setValue(float(arg_dict["Frequency (MHz)"]))
        self.FREQANG_BURST_FIELD.setValue(int(arg_dict["Burst count"]))
        self.FREQANG_VOLT_FIELD.setValue(float(arg_dict["Amplitude (mV)"]))
        self.FREQANG_ANG_FIELD.setValue(float(arg_dict["Max angle variation (deg)"]))
        self.FREQANG_POS_FIELD.setValue(float(arg_dict["Max. position error (+/- mm)"]))
        self.OSCOPE_CYCLES_FIELD.setValue(float(arg_dict["#Cycles.Capture"]))
        self.OSCOPE_DELAYCYCLE_FIELD.setValue(float(arg_dict["#Cycles.Delay"]))
        self.X_PNT_FIELD.setValue(int(arg_dict["X #Pts."]))
        self.THETA_PNT_FIELD.setValue(int(arg_dict["Theta #Pts."]))
        self.X_INCREMENT_FIELD.setValue(float(arg_dict["X Incr. (mm)"]))
        self.THETA_INCREMENT_FIELD.setValue(float(arg_dict["Theta Incr. (deg)"]))

    #todo: populate arg_dict
    #todo: change variable names to dict assignment with correct name like the first line
    #todo: arrange the arguments in the order of the example script
    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict([])
        arg_dict["Task type"] = 'Find element n'
        arg_dict["Element"] = self.ELEMENT_SELECTION_FIELD.currentText()
        arg_dict["Scope channel"] = self.OSCOPE_CHANNEL_FIELD.currentText()
        arg_dict["Acquisition type"] = self.OSCOPE_AQTYPE_FIELD.currentText()
        arg_dict["Averages"] = self.OSCOPE_SAMPLES_FIELD.currentText()
        arg_dict["Data storage"] = self.OSCOPE_DATASTORE_FIELD.currentText()
        arg_dict["Storage location"] = self.OSCOPE_DATALOC_FIELD.currentText()
        arg_dict["Frequency settings"] = self.FREQANG_PRESET_FIELD.currentText()
        arg_dict["ElementPositionTest"] = str(self.FREQANG_POS_TEST_CHECKBOX.isChecked())
        arg_dict["BeamAngleTest"] = str(self.FREQANG_ANG_TEST_CHECKBOX.isChecked())
        arg_dict["Auto set timebase"] = str(self.OSCOPE_AUTO_CHECKBOX.isChecked())
        arg_dict["Frequency (MHz)"] = "%.4f" % self.FREQANG_FREQ_FIELD.value()
        arg_dict["Burst count"] = str(self.FREQANG_BURST_FIELD.value())
        arg_dict["Amplitude (mV)"] = str(self.FREQANG_VOLT_FIELD.value())
        arg_dict["Max angle variation (deg)"] = str(self.FREQANG_ANG_FIELD.value())
        arg_dict["Max. position error (+/- mm)"] = "%.3f" % (self.FREQANG_POS_FIELD.value())
        arg_dict["#Cycles.Capture"] = str(self.OSCOPE_CYCLES_FIELD.value())
        arg_dict["#Cycles.Delay"] = str(self.OSCOPE_DELAYCYCLE_FIELD.value())
        arg_dict["X #Pts."] = str(self.X_PNT_FIELD.value())
        arg_dict["Theta #Pts."] = str(self.THETA_PNT_FIELD.value())
        arg_dict["X Incr. (mm)"] = "%.4f" % (self.X_INCREMENT_FIELD.value())
        arg_dict["Theta Incr. (deg)"] = str(self.THETA_INCREMENT_FIELD.value())

        return arg_dict

    def filebrowser(self):
        filename = QFileDialog.getOpenFileName(self, 'Select File', 'Desktop')
        self.OSCOPE_DATA_DIRECTORY_FIELD.setText(filename[0])

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FindElement()
    ui.show()
    sys.exit(app.exec_())

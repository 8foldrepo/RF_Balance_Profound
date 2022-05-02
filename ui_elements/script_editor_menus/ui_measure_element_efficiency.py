from collections import OrderedDict
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QFileDialog
from Widget_Library.widget_measure_element_efficiency import Ui_Form_2
from ui_elements.my_qwidget import MyQWidget


class MeasureElementEfficiency(Ui_Form_2, MyQWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.DATA_DIRECTORY_BUTTON.clicked.connect(self.filebrowser)
        self.configure_signals()
        self.orderedDict_to_ui(
            OrderedDict(
                [('Task type', 'Measure element efficiency (RFB)'), ('Element', 'Current')
                    , ('Frequency range', 'Low frequency'), ('RFB.#on/off cycles', '3')
                    , ('RFB.On time (s)', '10.000000'), ('RFB.Off time (s)', '10.000000'), ('RFB.Threshold', '0.050000')
                    , ('RFB.Offset', '0.500000'), ('Set frequency options', 'Common peak frequency')
                    , ('Frequency (MHz)', '4.200000'), ('Amplitude (mVpp)', '100.000000')
                    , ('Storage location', 'UA results directory'), ('Data directory', '')
                    , ('RFB target position', 'Average UA RFB position')
                    , ('RFB target angle', '-90.000000'), ('EfficiencyTest', 'TRUE'), ('Pa max (target, W)', '4.000000')
                    , ('Pf max (limit, W)', '12.000000'), ('Reflection limit (%)', '70.000000')]))

    def configure_signals(self):
        self.DATALOC_FIELD.currentIndexChanged.connect(self.storage_loc_combo_changed)

    def orderedDict_to_ui(self, var_dict: OrderedDict):
        # todo, fill UI according to dictionary
        self.ELEMENT_SELECTION_FIELD.setCurrentText(var_dict["Element"])
        self.FREQUENCY_SELECTION_FIELD.setCurrentText(var_dict["Frequency range"])
        self.RFB_CYCLES_FIELD.setValue(int(var_dict["RFB.#on/off cycles"]))
        self.RFB_ON_FIELD.setValue(float(var_dict["RFB.On time (s)"]))
        self.RFB_OFF_FIELD.setValue(float(var_dict["RFB.Off time (s)"]))
        self.RFB_THRESHOLD_FIELD.setValue(float(var_dict["RFB.Threshold"]))
        self.RFB_OFFSET_FIELD.setValue(float(var_dict["RFB.Offset"]))
        self.OPTIONS_SELECTION_FIELD.setCurrentText(var_dict["Set frequency options"])
        self.FREQUENCY_FIELD.setValue(float(var_dict["Frequency (MHz)"]))
        self.AMPLITUDE_FIELD.setValue(float(var_dict["Amplitude (mVpp)"]))
        self.DATALOC_FIELD.setCurrentText(var_dict["Storage location"])
        self.storage_loc_combo_changed()
        self.DATA_DIRECTORY_FIELD.setText(var_dict["Data directory"])
        self.RFB_TARGET_POSITION_FIELD.setCurrentText(var_dict["RFB target position"])
        self.RFB_ANGLE_FIELD.setValue(float(var_dict["RFB target angle"]))
        self.POWER_TEST_CHECKBOX.setChecked(bool(var_dict["EfficiencyTest"]))
        self.POWER_TARGET_FIELD.setValue(float(var_dict["Pa max (target, W)"]))
        self.POWER_MAX_FIELD.setValue(float(var_dict["Pf max (limit, W)"]))
        self.REFLECTION_LIMIT_FIELD.setValue(float(var_dict["Reflection limit (%)"]))

        # todo: populate var_dict, arrange the arguments in the order of the example script

    @pyqtSlot()
    def storage_loc_combo_changed(self):
        if 'Results Directory'.upper() in self.DATALOC_FIELD.currentText().upper():
            self.DATA_DIRECTORY_FIELD.setEnabled(False)
            self.DATA_DIRECTORY_BUTTON.setEnabled(False)
        else:
            self.DATA_DIRECTORY_FIELD.setEnabled(True)
            self.DATA_DIRECTORY_BUTTON.setEnabled(True)

    def ui_to_orderedDict(self) -> OrderedDict:
        var_dict = OrderedDict()
        var_dict["Task type"] = 'Measure element efficiency (RFB)'
        var_dict["Element"] = self.ELEMENT_SELECTION_FIELD.currentText()
        var_dict["Frequency range"] = self.FREQUENCY_SELECTION_FIELD.currentText()
        var_dict["RFB.#on/off cycles"] = str(int(self.RFB_CYCLES_FIELD.value()))
        var_dict["RFB.On time (s)"] = "%.1f" % (self.RFB_ON_FIELD.value())
        var_dict["RFB.Off time (s)"] = "%.1f" % (self.RFB_OFF_FIELD.value())
        var_dict["RFB.Threshold"] = "%.2f" % (self.RFB_THRESHOLD_FIELD.value())
        var_dict["RFB.Offset"] = "%.1f" % (self.RFB_OFFSET_FIELD.value())
        var_dict["Set frequency options"] = self.OPTIONS_SELECTION_FIELD.currentText()
        var_dict["Frequency (MHz)"] = "%.4f" % (self.FREQUENCY_FIELD.value())
        var_dict["Amplitude (mVpp)"] = str(self.AMPLITUDE_FIELD.value())
        var_dict["Storage location"] = self.DATALOC_FIELD.currentText()
        var_dict["Data directory"] = self.DATA_DIRECTORY_FIELD.text()
        var_dict["RFB target position"] = self.RFB_TARGET_POSITION_FIELD.currentText()
        var_dict["RFB target angle"] = str(self.RFB_ANGLE_FIELD.value())
        var_dict["EfficiencyTest"] = str(self.POWER_TEST_CHECKBOX.isChecked())
        var_dict["Pa max (target, W)"] = str(self.POWER_TARGET_FIELD.value())
        var_dict["Pf max (limit, W)"] = str(self.POWER_MAX_FIELD.value())
        var_dict["Reflection limit (%)"] = str(self.REFLECTION_LIMIT_FIELD.value())

        # example lines, insert the name of the argument on the left as it appears in the example script.
        # the name of the ui element goes between the dots
        # self.var_dict[""] = self..currentText()
        # self.var_dict[""] = self..isChecked()
        # self.var_dict[""] = round(self..value(),2)
        return var_dict

    def filebrowser(self):
        filename, _ = QFileDialog.getExistingDirectory(self, 'Select Directory')
        self.DATA_DIRECTORY_FIELD.setText(filename)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = MeasureElementEfficiency()
    ui.show()
    sys.exit(app.exec_())

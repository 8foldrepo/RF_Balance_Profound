from Widget_Library.widget_measure_element_efficiency import Ui_Form_2
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict


class MeasureElementEfficiency(Ui_Form_2, MyQWidget):
    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.DATA_DIRECTORY_BUTTON.clicked.connect(self.filebrowser)
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

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        # todo, fill UI according to dictionary
        self.ELEMENT_SELECTION_FIELD.setCurrentText(arg_dict["Element"])
        self.FREQUENCY_SELECTION_FIELD.setCurrentText(arg_dict["Frequency range"])
        self.RFB_CYCLES_FIELD.setValue(float(arg_dict["RFB.#on/off cycles"]))
        self.RFB_ON_FIELD.setValue(float(arg_dict["RFB.On time (s)"]))
        self.RFB_OFF_FIELD.setValue(float(arg_dict["RFB.Off time (s)"]))
        self.RFB_THRESHOLD_FIELD.setValue(float(arg_dict["RFB.Threshold"]))
        self.RFB_OFFSET_FIELD.setValue(float(arg_dict["RFB.Offset"]))
        self.OPTIONS_SELECTION_FIELD.setCurrentText(arg_dict["Set frequency options"])
        self.FREQUENCY_FIELD.setValue(float(arg_dict["Frequency (MHz)"]))
        self.AMPLITUDE_FIELD.setValue(float(arg_dict["Amplitude (mVpp)"]))
        self.DATALOC_FIELD.setCurrentText(arg_dict["Storage location"])
        self.DATA_DIRECTORY_FIELD.setText(arg_dict["Data directory"])
        self.RFB_TARGET_POSITION_FIELD.setCurrentText(arg_dict["RFB target position"])
        self.RFB_ANGLE_FIELD.setValue(float(arg_dict["RFB target angle"]))
        self.POWER_TEST_CHECKBOX.setChecked(bool(arg_dict["EfficiencyTest"]))
        self.POWER_TARGET_FIELD.setValue(float(arg_dict["Pa max (target, W)"]))
        self.POWER_MAX_FIELD.setValue(float(arg_dict["Pf max (limit, W)"]))
        self.REFLECTION_LIMIT_FIELD.setValue(float(arg_dict["Reflection limit (%)"]))

        # example lines
        # self..setText(arg_dict[""])
        # self..setChecked(arg_dict[""])
        # self..setValue(arg_dict[""])
        # pass

        # todo: populate arg_dict, arrange the arguments in the order of the example script

    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()
        arg_dict["Task type"] = 'Measure element efficiency (RFB)'
        arg_dict["Element"] = self.ELEMENT_SELECTION_FIELD.currentText()
        arg_dict["Frequency range"] = self.FREQUENCY_SELECTION_FIELD.currentText()
        arg_dict["RFB.#on/off cycles"] = str(self.RFB_CYCLES_FIELD.value())
        arg_dict["RFB.On time (s)"] = "%.1f" % (self.RFB_ON_FIELD.value())
        arg_dict["RFB.Off time (s)"] = "%.1f" % (self.RFB_OFF_FIELD.value())
        arg_dict["RFB.Threshold"] = "%.2f" % (self.RFB_THRESHOLD_FIELD.value())
        arg_dict["RFB.Offset"] = "%.1f" % (self.RFB_OFFSET_FIELD.value())
        arg_dict["Set frequency options"] = self.OPTIONS_SELECTION_FIELD.currentText()
        arg_dict["Frequency (MHz)"] = "%.4f" % (self.FREQUENCY_FIELD.value())
        arg_dict["Amplitude (mVpp)"] = str(self.AMPLITUDE_FIELD.value())
        arg_dict["Storage location"] = self.DATALOC_FIELD.currentText()
        arg_dict["Data directory"] = self.DATA_DIRECTORY_FIELD.text()
        arg_dict["RFB target position"] = self.RFB_TARGET_POSITION_FIELD.currentText()
        arg_dict["RFB target angle"] = str(self.RFB_ANGLE_FIELD.value())
        arg_dict["EfficiencyTest"] = str(self.POWER_TEST_CHECKBOX.isChecked())
        arg_dict["Pa max (target, W)"] = str(self.POWER_TARGET_FIELD.value())
        arg_dict["Pf max (limit, W)"] = str(self.POWER_MAX_FIELD.value())
        arg_dict["Reflection limit (%)"] = str(self.REFLECTION_LIMIT_FIELD.value())

        # example lines, insert the name of the argument on the left as it appears in the example script.
        # the name of the ui element goes between the dots
        # self.arg_dict[""] = self..currentText()
        # self.arg_dict[""] = self..isChecked()
        # self.arg_dict[""] = round(self..value(),2)
        return arg_dict

    def filebrowser(self):
        filename = QFileDialog.getOpenFileName(self, 'Select File', 'Desktop')
        self.DATA_DIRECTORY_FIELD.setText(filename[0])


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = MeasureElementEfficiency()
    ui.show()
    sys.exit(app.exec_())

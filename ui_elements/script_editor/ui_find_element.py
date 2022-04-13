from Widget_Library.widget_find_element import Ui_FIND_ELEMENT_WIDGET
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from ui_elements.my_qwidget import MyQWidget
from collections import OrderedDict

class FindElement(MyQWidget, Ui_FIND_ELEMENT_WIDGET):
    def __init__(self, config = None, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

    def orderedDict_to_ui(self, arg_dict: OrderedDict):
        #todo, fill UI according to dictionary
        pass

    #todo: populate arg_dict
    #todo: change variable names to dict assignment with correct name like the first line
    #todo: arrange the arguments in the order of the example script
    def ui_to_orderedDict(self) -> OrderedDict:
        arg_dict = OrderedDict()

        arg_dict["Element"] = self.ELEMENT_SELECTION_FIELD.currentText()
        channel_selection = self.OSCOPE_CHANNEL_FIELD.currentText()
        acquisition_selection = self.OSCOPE_AQTYPE_FIELD.currentText()
        sample_selection = self.OSCOPE_SAMPLES_FIELD.currentText()
        data_selection = self.OSCOPE_DATASTORE_FIELD.currentText()
        storage_selection = self.OSCOPE_DATALOC_FIELD.currentText()
        frequency_selection = self.FREQANG_PRESET_FIELD.currentText()
        pos_test_state = self.FREQANG_POS_TEST_CHECKBOX.checkState()
        ang_test_state=self.FREQANG_ANG_TEST_CHECKBOX.checkState()
        auto_time_state = self.OSCOPE_AUTO_CHECKBOX.checkState()

        element_selection = self.ELEMENT_SELECTION_FIELD.currentText()
        channel_selection = self.OSCOPE_CHANNEL_FIELD.currentText()
        acquisition_selection = self.OSCOPE_AQTYPE_FIELD.currentText()
        sample_selection = self.OSCOPE_SAMPLES_FIELD.currentText()
        data_selection = self.OSCOPE_DATASTORE_FIELD.currentText()
        storage_selection = self.OSCOPE_DATALOC_FIELD.currentText()
        frequency_selection = self.FREQANG_PRESET_FIELD.currentText()

        frequency_value = round(self.FREQANG_FREQ_FIELD.value(),4)
        freq_burst_value = round(self.FREQANG_BURST_FIELD.value(),4)
        freq_volt_value = round(self.FREQANG_VOLT_FIELD.value(),0)
        max_ang_value = round(self.FREQANG_ANG_FIELD.value())
        max_pos_value = round(self.FREQANG_POS_FIELD.value(),3)
        cycles_field_value = round(self.OSCOPE_CYCLES_FIELD.value(),0)
        delay_cycles_field_value = round(self.OSCOPE_DELAYCYCLE_FIELD.value(),0)
        x_pnt_value = round(self.X_PNT_FIELD.value(),4)
        theta_pnt_value = round(self.THETA_PNT_FIELD.value(),4)
        x_inc_value = round(self.X_INCREMENT_FIELD.value(),4)
        theta_inc_value = round(self.THETA_INCREMENT_FIELD_2.value(),0)

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

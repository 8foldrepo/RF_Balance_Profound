from Widget_Library.widget_find_element import Ui_FIND_ELEMENT_WIDGET
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog


class FindElement(QWidget, Ui_FIND_ELEMENT_WIDGET):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.combo_check()
        self.OSCOPE_DATA_DIRECTORY_BUTTON.clicked.connect(self.filebrowser)
        self.ELEMENT_SELECTION_FIELD.currentTextChanged.connect(self.update_one)
        self.OSCOPE_CHANNEL_FIELD.currentTextChanged.connect(self.update_two)
        self.OSCOPE_AQTYPE_FIELD.currentTextChanged.connect(self.update_three)
        self.OSCOPE_SAMPLES_FIELD.currentTextChanged.connect(self.update_four)
        self.OSCOPE_DATASTORE_FIELD.currentTextChanged.connect(self.update_five)
        self.OSCOPE_DATALOC_FIELD.currentTextChanged.connect(self.update_six)
        self.FREQANG_PRESET_FIELD.currentTextChanged.connect(self.update_seven)
        self.X_INCREMENT_FIELD.valueChanged.connect(self.x_inc)
        self.THETA_INCREMENT_FIELD_2.valueChanged.connect(self.theta_inc)
        self.X_PNT_FIELD.valueChanged.connect(self.x_pnt)
        self.THETA_PNT_FIELD.valueChanged.connect(self.theta_pnt)
        self.OSCOPE_CYCLES_FIELD.valueChanged.connect(self.cycles_field)
        self.OSCOPE_DELAYCYCLE_FIELD.valueChanged.connect(self.delay_cycles_field)
        self.FREQANG_FREQ_FIELD.valueChanged.connect(self.frequency)
        self.FREQANG_BURST_FIELD.valueChanged.connect(self.freq_burst)
        self.FREQANG_VOLT_FIELD.valueChanged.connect(self.freq_volt)
        self.FREQANG_ANG_FIELD.valueChanged.connect(self.max_ang)
        self.FREQANG_POS_FIELD.valueChanged.connect(self.max_pos)
        self.OSCOPE_AUTO_CHECKBOX.stateChanged.connect(self.auto_time)
        self.FREQANG_ANG_TEST_CHECKBOX.stateChanged.connect(self.ang_test)
        self.FREQANG_POS_TEST_CHECKBOX.stateChanged.connect(self.pos_test)

    def combo_check(self):
        element_selection = self.ELEMENT_SELECTION_FIELD.currentText()
        channel_selection = self.OSCOPE_CHANNEL_FIELD.currentText()
        acquisition_selection = self.OSCOPE_AQTYPE_FIELD.currentText()
        sample_selection = self.OSCOPE_SAMPLES_FIELD.currentText()
        data_selection = self.OSCOPE_DATASTORE_FIELD.currentText()
        storage_selection = self.OSCOPE_DATALOC_FIELD.currentText()
        frequency_selection = self.FREQANG_PRESET_FIELD.currentText()
        print('Element currently selected: ' + element_selection)
        print('Oscilloscope channel currently selected: ' + channel_selection)
        print('Acquisition type currently selected: ' + acquisition_selection)
        print('Number of averages currently selected: ' + sample_selection)
        print('Data stored state: ' + data_selection)
        print('File directory currently selected: ' + storage_selection)
        print('Frequency preset currently selected: ' + frequency_selection)

    def pos_test(self):
        pos_test_state = self.FREQANG_POS_TEST_CHECKBOX.checkState()
        if pos_test_state == 2:
            print('Max position error test is on.')
        else:
            print('Max position error test is off')

    def ang_test(self):
        ang_test_state = self.FREQANG_ANG_TEST_CHECKBOX.checkState()
        if ang_test_state == 2:
            print('Max angle variation test is on.')
        else:
            print('Max angle variation test is off')

    def auto_time(self):
        auto_time_state = self.OSCOPE_AUTO_CHECKBOX.checkState()
        if auto_time_state == 2:
            print('Oscilloscope Auto Time Base is on.')
        else:
            print('Oscilloscope Auto Time Base is off')

    def frequency(self):
        frequency_value = self.FREQANG_FREQ_FIELD.value()
        print(round(frequency_value, 4))

    def freq_burst(self):
        freq_burst_value = self.FREQANG_BURST_FIELD.value()
        print(round(freq_burst_value, 0))

    def freq_volt(self):
        freq_volt_value = self.FREQANG_VOLT_FIELD.value()
        print(round(freq_volt_value, 0))

    def max_ang(self):
        max_ang_value = self.FREQANG_ANG_FIELD.value()
        print(round(max_ang_value, 0))

    def max_pos(self):
        max_pos_value = self.FREQANG_POS_FIELD.value()
        print(round(max_pos_value, 3))

    def cycles_field(self):
        cycles_field_value = self.OSCOPE_CYCLES_FIELD.value()
        print(round(cycles_field_value, 0))

    def delay_cycles_field(self):
        delay_cycles_field_value = self.OSCOPE_DELAYCYCLE_FIELD.value()
        print(round(delay_cycles_field_value, 0))

    def x_pnt(self):
        x_pnt_value = self.X_PNT_FIELD.value()
        print(round(x_pnt_value, 4))

    def theta_pnt(self):
        theta_pnt_value = self.THETA_PNT_FIELD.value()
        print(round(theta_pnt_value, 4))

    def x_inc(self):
        x_inc_value = self.X_INCREMENT_FIELD.value()
        print(round(x_inc_value, 4))

    def theta_inc(self):
        theta_inc_value = self.THETA_INCREMENT_FIELD_2.value()
        print(round(theta_inc_value, 0))

    def filebrowser(self):
        filename = QFileDialog.getOpenFileName(self, 'Select File', 'Desktop')
        self.OSCOPE_DATA_DIRECTORY_FIELD.setText(filename[0])

    def update_one(self):
        element_selection = self.ELEMENT_SELECTION_FIELD.currentText()
        print('Element currently selected: ' + element_selection)

    def update_two(self):
        channel_selection = self.OSCOPE_CHANNEL_FIELD.currentText()
        print('Oscilloscope channel currently selected: ' + channel_selection)

    def update_three(self):
        acquisition_selection = self.OSCOPE_AQTYPE_FIELD.currentText()
        print('Acquisition type currently selected: ' + acquisition_selection)

    def update_four(self):
        sample_selection = self.OSCOPE_SAMPLES_FIELD.currentText()
        print('Number of averages currently selected: ' + sample_selection)

    def update_five(self):
        data_selection = self.OSCOPE_DATASTORE_FIELD.currentText()
        print('Data stored state: ' + data_selection)

    def update_six(self):
        storage_selection = self.OSCOPE_DATALOC_FIELD.currentText()
        print('File directory currently selected: ' + storage_selection)

    def update_seven(self):
        frequency_selection = self.FREQANG_PRESET_FIELD.currentText()
        print('Frequency preset currently selected: ' + frequency_selection)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = FindElement()
    ui.show()
    sys.exit(app.exec_())

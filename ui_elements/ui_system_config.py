import os

import yaml
from PyQt5.QtWidgets import *

from Widget_Library.widget_system_config import Ui_Form


class SystemConfig(QWidget, Ui_Form):
    def __init__(self, parent=None, config = None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.configure_signals()

    def set_config(self, config):
        self.config = config

    def configure_signals(self):
        self.save_config_button.clicked.connect(self.save_config)
        self.show_config_button.clicked.connect(self.show_config)

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

    def show_config(self):
        try:
            osCommandString = "notepad.exe local.yaml"
            os.system(osCommandString)
        except:
            osCommandString = "notepad.exe default.yaml"
            os.system(osCommandString)

    # Save the settings input into the UI field to the local.yaml config file
    def save_config(self):
        self.config["User Accounts"]["Operator"] = self.operator_pass_field.text()
        self.config["User Accounts"]["Engineer"] = self.engineer_pass_field.text()
        self.config["User Accounts"]["Administrator"] = self.admin_pass_field.text()

        self.config["WTF_PositionParameters"]["XHomeCoord"] = self.x_homecoord.value()
        self.config["WTF_PositionParameters"]["ThetaHomeCoord"] = self.theta_homecoord.value()
        self.config["WTF_PositionParameters"]["X-TankInsertionPoint"] = self.x_insertionpoint.value()
        self.config["WTF_PositionParameters"]["X-Element1"] = self.x_element1.value()
        self.config["WTF_PositionParameters"]["X-Element pitch (mm)"] = self.x_elementpitch.value()
        self.config["WTF_PositionParameters"]["ThetaPreHomeMove"] = self.theta_prehomemove.value()
        self.config["WTF_PositionParameters"]["ThetaLoadEnc?"] = self.thetaloadenc.isChecked()
        self.config["WTF_PositionParameters"]["CentreHomeTheta?"] = self.centerhometheta.isChecked()

        self.config["FrequencyParameters"]["LF"]["LowFreqLimit(MHz)"] = self.lf_lowlimit.value()
        self.config["FrequencyParameters"]["LF"]["HighFreqLimit(MHz)"] = self.lf_highlimit.value()
        self.config["FrequencyParameters"]["LF"]["Amplitude(mVpp)"] = self.lf_amplitude.value()
        self.config["FrequencyParameters"]["LF"]["BurstCount"] = self.lf_burstcount.value()
        self.config["FrequencyParameters"]["HF"]["LowFreqLimit(MHz)"] = self.hf_lowlimit.value()
        self.config["FrequencyParameters"]["HF"]["HighFreqLimit(MHz)"] = self.hf_highlimit.value()
        self.config["FrequencyParameters"]["HF"]["HF.Amplitude(mVpp)"] = self.hf_amplitude.value()
        self.config["FrequencyParameters"]["HF"]["HF.BurstCount"] = self.hf_burstcount.value()
        self.config["FrequencyParameters"]["Search"]["CoarseIncr(MHz)"] = self.search_coarseincr.value()
        self.config["FrequencyParameters"]["Search"]["FineIncr(MHz)"] = self.search_fineincr.value()

        self.config["Sequence pass/fail"]["Retries"] = self.retries.value()
        self.config["Sequence pass/fail"]["Pass fail action"] = self.pass_fail_action.currentText()
        self.config["Sequence pass/fail"]["Interrupt action"] = self.interrupt_action.currentText()
        self.config["Sequence pass/fail"]["Dialog timeout (s)"] = self.dialog_timeout.value()

        self.config["WTF_DIO"]["DAQ Device name"] = self.daq_devicename.text()
        self.config["WTF_DIO"]["Water level timeout (s)"] = self.water_timeout.value()
        self.config["WTF_DIO"]["Fill/Drain mode"] = self.fill_mode.currentText()

        self.config["Autoset timebase"]["Min time of flight (us)"] = self.min_time_of_flight.value()
        self.config["Autoset timebase"]["Max time of flight (us)"] = self.max_time_of_flight.value()

        self.config["Paths"]["UA results root directory"] = self.ua_results_directory.text()
        self.config["Paths"]["UA Serial numbers file"] = self.ua_serial_numbers_path.text()

        with open('local.yaml', 'w') as f:
            yaml.dump(self.config, f)

    # Populate fields in config tab with settings from the config file
    def populate_config_ui(self):
        self.operator_pass_field.setText(self.config["User Accounts"]["Operator"])
        self.engineer_pass_field.setText(self.config["User Accounts"]["Engineer"])
        self.admin_pass_field.setText(self.config["User Accounts"]["Administrator"])

        self.x_homecoord.setValue(self.config["WTF_PositionParameters"]["XHomeCoord"])
        self.theta_homecoord.setValue(self.config["WTF_PositionParameters"]["ThetaHomeCoord"])
        self.x_insertionpoint.setValue(self.config["WTF_PositionParameters"]["X-TankInsertionPoint"])
        self.x_element1.setValue(self.config["WTF_PositionParameters"]["X-Element1"])
        self.x_elementpitch.setValue(self.config["WTF_PositionParameters"]["X-Element pitch (mm)"])
        self.theta_prehomemove.setValue(self.config["WTF_PositionParameters"]["ThetaPreHomeMove"])
        self.thetaloadenc.setChecked(self.config["WTF_PositionParameters"]["ThetaLoadEnc?"])
        self.centerhometheta.setChecked(self.config["WTF_PositionParameters"]["CentreHomeTheta?"])

        self.lf_lowlimit.setValue(self.config["FrequencyParameters"]["LF"]["LowFreqLimit(MHz)"])
        self.lf_highlimit.setValue(self.config["FrequencyParameters"]["LF"]["HighFreqLimit(MHz)"])
        self.lf_amplitude.setValue(self.config["FrequencyParameters"]["LF"]["Amplitude(mVpp)"])
        self.lf_burstcount.setValue(self.config["FrequencyParameters"]["LF"]["BurstCount"])
        self.hf_lowlimit.setValue(self.config["FrequencyParameters"]["HF"]["LowFreqLimit(MHz)"])
        self.hf_highlimit.setValue(self.config["FrequencyParameters"]["HF"]["HighFreqLimit(MHz)"])
        self.hf_amplitude.setValue(self.config["FrequencyParameters"]["HF"]["HF.Amplitude(mVpp)"])
        self.hf_burstcount.setValue(self.config["FrequencyParameters"]["HF"]["HF.BurstCount"])
        self.search_coarseincr.setValue(self.config["FrequencyParameters"]["Search"]["CoarseIncr(MHz)"])
        self.search_fineincr.setValue(self.config["FrequencyParameters"]["Search"]["FineIncr(MHz)"])

        self.retries.setValue(self.config["Sequence pass/fail"]["Retries"])
        self.pass_fail_action.setCurrentText(self.config["Sequence pass/fail"]["Pass fail action"])
        self.interrupt_action.setCurrentText(self.config["Sequence pass/fail"]["Interrupt action"])
        self.dialog_timeout.setValue(self.config["Sequence pass/fail"]["Dialog timeout (s)"])

        self.daq_devicename.setText(self.config["WTF_DIO"]["DAQ Device name"])
        self.water_timeout.setValue(self.config["WTF_DIO"]["Water level timeout (s)"])
        self.fill_mode.setCurrentText(self.config["WTF_DIO"]["Fill/Drain mode"])

        self.min_time_of_flight.setValue(self.config["Autoset timebase"]["Min time of flight (us)"])
        self.max_time_of_flight.setValue(self.config["Autoset timebase"]["Max time of flight (us)"])

        self.ua_results_directory.setText(self.config["Paths"]["UA results root directory"])
        self.ua_serial_numbers_path.setText(self.config["Paths"]["UA Serial numbers file"])
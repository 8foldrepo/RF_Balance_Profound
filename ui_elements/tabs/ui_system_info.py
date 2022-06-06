from configparser import ConfigParser

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

from Widget_Library.widget_system_info import Ui_Form
from data_structures.variable_containers import SerialNumbers
from definitions import SYSTEM_INFO_INI_PATH
from ui_elements.my_qwidget import MyQWidget


class SystemInfo(MyQWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

    def load_system_info(self):
        output = ""
        self.parser = ConfigParser()
        self.parser.read(SYSTEM_INFO_INI_PATH)

        # Radio Force Balance Frame (good; checked by Rameen on 4/18)
        self.RFB_MANUFACTURER_FIELD.setText(self.parser['RFB']['Manufacturer'])
        self.RFB_MODELNUM_FIELD.setText(self.parser['RFB']['Model'])
        self.RFB_SN_FIELD.setText(self.parser['RFB']['Serial number'])
        self.RF_FIRMWARE_V_FIELD.setText(self.parser['RFB']['F/W version'])
        self.RFB_CAL_FIELD.setText(self.parser['RFB']['Last calibration'])
        # Wet Test Fixture Frame (good; checked by Rameen on 4/18)
        self.WTF_SN_FIELD.setText(self.parser['System info']['WTF Serial number'])
        self.SW_VERSION_FIELD.setText(self.parser['System info']['Software version'])
        self.UA_WATER_CIRCUIT_FIELD.setText(self.parser['System info']['UA Water circuit'])
        self.TANK_WATER_CIRCUIT_FIELD.setText(self.parser['System info']['Tank water circuit'])
        # Oscilloscope Frame (good; checked by Rameen on 4/18)
        self.OSCOPE_MANUFACTURER_FIELD.setText(self.parser['Oscilloscope']['Manufacturer'])
        self.OSCOPE_MODELNUM_FIELD.setText(self.parser['Oscilloscope']['Model'])
        self.OSCOPE_SN_FIELD.setText(self.parser['Oscilloscope']['Serial number'])
        self.OSCOPE_FIRMWARE_V_FIELD.setText(self.parser['Oscilloscope']['F/W version'])
        # Arbitrary Waveform Generator Frame (done)
        self.AWG_MANUFACTURER_FIELD.setText(self.parser['Function generator']['Manufacturer'])
        self.AWG_MODELNUM_FIELD.setText(self.parser['Function generator']['Model'])
        self.AWG_SN_FIELD.setText(self.parser['Function generator']['Serial number'])
        self.AWG_FIRMWARE_V_FIELD.setText(self.parser['Function generator']['F/W version'])
        # Forward Power Meter Frame (done)
        self.FPM_MANUFACTURER_FIELD.setText(self.parser['Forward power meter']['Manufacturer'])
        self.FPM_MODELNUM_FIELD.setText(self.parser['Forward power meter']['Model'])
        self.FPM_SN_FIELD.setText(self.parser['Forward power meter']['Serial number'])
        self.FPM_FIRMWARE_V_FIELD.setText(self.parser['Forward power meter']['F/W version'])
        # Reflected Power Meter Frame (done)
        self.RPM_MANUFACTURER_FIELD.setText(self.parser['Reflected power meter']['Manufacturer'])
        self.RPM_MODELNUM_FIELD.setText(self.parser['Reflected power meter']['Model'])
        self.RPM_SN_FIELD.setText(self.parser['Reflected power meter']['Serial number'])
        self.RPM_FIRMWARE_V_FIELD.setText(self.parser['Reflected power meter']['F/W version'])
        # Power Amplifier Frame (done)
        self.AMP_MANUFACTURER_FIELD.setText(self.parser['Power Amplifier']['Manufacturer'])
        self.AMP_MODELNUM_FIELD.setText(self.parser['Power Amplifier']['Model'])
        self.AMP_SN_FIELD.setText(self.parser['Power Amplifier']['Serial number'])
        self.AMP_REV_FIELD.setText(self.parser['Power Amplifier']['Rev#'])
        # Thermocouple Frame (done)
        self.THERMO_MANUFACTURER_FIELD.setText(self.parser['Thermocouple']['Manufacturer'])
        self.THERMO_MODELNUM_FIELD.setText(self.parser['Thermocouple']['Model'])
        self.THERMO_SN_FIELD.setText(self.parser['Thermocouple']['Serial number'])
        self.THERMO_FIRMWARE_V_FIELD.setText(self.parser['Thermocouple']['F/W version'])
        # Power Measurement & Switching Module Frame
        self.POWERSWITCH_MANUFACTURER_FIELD.setText(self.parser['RF measurement and switching module']['Manufacturer'])
        self.POWERSWITCH_MODELNUM_FIELD.setText(self.parser['RF measurement and switching module']['Model'])
        self.POWERSWITCH_SN_FIELD.setText(self.parser['RF measurement and switching module']['Serial number'])
        # Wet Test Fixture Interface Board Frame
        self.WTFIB_MODELNUM_FIELD.setText(self.parser['WTFiB']['Model'])
        self.WTFIB_SN_FIELD.setText(self.parser['WTFiB']['Serial number'])
        self.WTFIB_FIRMWARE_V_FIELD.setText(self.parser['WTFiB']['F/W version'])
        # Radio Force Balance Frame
        self.HYDRO_TYPE_FIELD.setText(self.parser['Hydrophone system']['Hydrophone Type'])
        self.HYDR_DIAM_FIELD.setText(self.parser['Hydrophone system']['Hydrophone Diameter'])
        self.HYDRO_SN_FIELD.setText(self.parser['Hydrophone system']['Hydrophone SN'])
        self.PREAMP_SN_FIELD.setText(self.parser['Hydrophone system']['Preamplifier SN'])
        self.DC_SN_FIELD.setText(self.parser['Hydrophone system']['DC Coupler SN'])

    @pyqtSlot(SerialNumbers)
    def serial_numbers_slot(self, serial_numbers: SerialNumbers):
        if serial_numbers.oscilloscope_sn is not None:
            self.parser.set('Oscilloscope', 'Serial number', serial_numbers.oscilloscope_sn)
        if serial_numbers.awg_sn is not None:
            self.parser.set('Function generator', 'Serial number', serial_numbers.awg_sn)
        if serial_numbers.forward_power_sn is not None:
            self.parser.set('Forward power meter', 'Serial number', serial_numbers.forward_power_sn)
        if serial_numbers.reflected_power_sn is not None:
            self.parser.set('Reflected power meter', 'Serial number', serial_numbers.reflected_power_sn)
        if serial_numbers.thermocouple_sn is not None:
            self.parser.set('Thermocouple', 'Serial number', serial_numbers.thermocouple_sn)

        if serial_numbers.rf_balance_sn is not None:
            self.parser.set('RFB', 'Serial number', str(serial_numbers.rf_balance_sn))

        # Writing our configuration file to 'example.ini'
        with open(SYSTEM_INFO_INI_PATH, 'w') as configfile:
            self.parser.write(configfile)

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled):
        self.HYDRO_TYPE_FIELD.setEnabled(enabled)
        self.HYDR_DIAM_FIELD.setEnabled(enabled)
        # all other buttons are disabled by default


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ui = SystemInfo()
    ui.load_system_info()
    ui.show()
    sys.exit(app.exec_())

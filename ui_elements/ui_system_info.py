from Widget_Library.widget_system_info import Ui_Form
from PyQt5.QtWidgets import QWidget, QApplication
from configparser import ConfigParser
from definitions import SYSTEM_INFO_INI_PATH
from ui_elements.my_qwidget import MyQWidget

class SystemInfo(MyQWidget, Ui_Form):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setupUi(self)

    def load_system_info(self):
        output = ''
        parser = ConfigParser()
        parser.read(SYSTEM_INFO_INI_PATH)

        # Radio Force Balance Frame
        self.RFB_MANUFACTURER_FIELD.setText(parser['RFB']['Manufacturer'])
        self.RFB_MODELNUM_FIELD.setText(parser['RFB']['Model'])
        self.RFB_SN_FIELD.setText(parser['RFB']['serial number'])
        self.RF_FIRMWARE_V_FIELD.setText(parser['RFB']['F/W version'])
        self.RFB_CAL_FIELD.setText(parser['RFB']['Last calibration'])
        # Wet Test Fixture Frame
        self.WTF_SN_FIELD.setText(parser['System info']['WTF Serial number'])
        self.SW_VERSION_FIELD.setText(parser['RFB']['Last calibration'])                  # Requires Updated Information
        self.UA_WATER_CIRCUIT_FIELD.setText(parser['System info']['UA Water circuit'])
        self.TANK_WATER_CIRCUIT_FIELD.setText(parser['System info']['Tank water circuit'])
        # Oscilloscope Frame
        self.OSCOPE_MANUFACTURER_FIELD.setText(parser['RFB']['Last calibration'])         # Requires Updated Information
        self.OSCOPE_MODELNUM_FIELD.setText(parser['RFB']['Last calibration'])             # Requires Updated Information
        self.OSCOPE_SN_FIELD.setText(parser['RFB']['Last calibration'])                   # Requires Updated Information
        self.OSCOPE_FIRMWARE_V_FIELD.setText(parser['RFB']['Last calibration'])           # Requires Updated Information
        # Arbitrary Waveform Generator Frame
        self.AWG_MANUFACTURER_FIELD.setText(parser['RFB']['Last calibration'])            # Requires Updated Information
        self.AWG_MODELNUM_FIELD.setText(parser['RFB']['Last calibration'])                # Requires Updated Information
        self.AWG_SN_FIELD.setText(parser['RFB']['Last calibration'])                      # Requires Updated Information
        self.AWG_FIRMWARE_V_FIELD.setText(parser['RFB']['Last calibration'])              # Requires Updated Information
        # Forward Power Meter Frame
        self.FPM_MANUFACTURER_FIELD.setText(parser['RFB']['Last calibration'])            # Requires Updated Information
        self.FPM_MODELNUM_FIELD.setText(parser['RFB']['Last calibration'])                # Requires Updated Information
        self.FPM_SN_FIELD.setText(parser['RFB']['Last calibration'])                      # Requires Updated Information
        self.FPM_FIRMWARE_V_FIELD.setText(parser['RFB']['Last calibration'])              # Requires Updated Information
        # Reflected Power Meter Frame
        self.RPM_MANUFACTURER_FIELD.setText(parser['RFB']['Last calibration'])            # Requires Updated Information
        self.RPM_MODELNUM_FIELD.setText(parser['RFB']['Last calibration'])                # Requires Updated Information
        self.RPM_SN_FIELD.setText(parser['RFB']['Last calibration'])                      # Requires Updated Information
        self.RPM_FIRMWARE_V_FIELD.setText(parser['RFB']['Last calibration'])              # Requires Updated Information
        # Power Amplifier Frame
        self.AMP_MANUFACTURER_FIELD.setText(parser['Power Amplifier']['Manufacturer'])
        self.AMP_MODELNUM_FIELD.setText(parser['Power Amplifier']['Model'])
        self.AMP_SN_FIELD.setText(parser['Power Amplifier']['Serial number'])
        self.AMP_REV_FIELD.setText(parser['Power Amplifier']['Rev#'])
        # Thermocouple Frame
        self.THERMO_MANUFACTURER_FIELD.setText(parser['RFB']['Last calibration'])         # Requires Updated Information
        self.THERMO_MODELNUM_FIELD.setText(parser['RFB']['Last calibration'])             # Requires Updated Information
        self.THERMO_SN_FIELD.setText(parser['RFB']['Last calibration'])                   # Requires Updated Information
        self.THERMO_FIRMWARE_V_FIELD.setText(parser['RFB']['Last calibration'])           # Requires Updated Information
        # Power Measurement & Switching Module Frame
        self.POWERSWITCH_MANUFACTURER_FIELD.setText(parser['RF measurement and switching module']['Manufacturer'])
        self.POWERSWITCH_MODELNUM_FIELD.setText(parser['RF measurement and switching module']['Model'])
        self.POWERSWITCH_SN_FIELD.setText(parser['RF measurement and switching module']['Serial number'])
        # Wet Test Fixture Interface Board Frame
        self.WTFIB_MODELNUM_FIELD.setText(parser['WTFiB']['Model'])
        self.WTFIB_SN_FIELD.setText(parser['WTFiB']['Serial number'])
        self.WTFIB_FIRMWARE_V_FIELD.setText(parser['RFB']['Last calibration'])            # Requires Updated Information
        # Radio Force Balance Frame
        self.HYDRO_TYPE_FIELD.setText(parser['Hydrophone system']['Hydrophone Type'])
        self.HYDR_DIAM_FIELD.setText(parser['Hydrophone system']['Hydrophone Diameter'])
        self.HYDRO_SN_FIELD.setText(parser['Hydrophone system']['Hydrophone SN'])
        self.PREAMP_SN_FIELD.setText(parser['Hydrophone system']['Preamplifier SN'])
        self.DC_SN_FIELD.setText(parser['Hydrophone system']['DC Coupler SN'])


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ui = SystemInfo()
    ui.load_system_info()
    ui.show()
    sys.exit(app.exec_())

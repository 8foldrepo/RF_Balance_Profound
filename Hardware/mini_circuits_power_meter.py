import ctypes
import sys
import time as t
from typing import Union
from PyQt5 import QtCore
from Hardware.Abstract.abstract_sensor import AbstractSensor
from definitions import POWER_METER_DLL_PATH
sys.path.append(POWER_METER_DLL_PATH)

# Setup power meter library (do not rearrange)
import clr  # pythonnet
clr.AddReference("mcl_pm_NET45")  # Reference the DLL
from mcl_pm_NET45 import usb_pm  # This can still run if this shows a red underline

class PowerMeter(AbstractSensor):
    """"
    Control Mini-Circuits' PWR series power meters via USB
    Requirements:
    1: Python.Net (pip install pythonnet)
    2: Mini-Circuits' DLL API file (mcl_pm_NET45.dll)
    https://www.minicircuits.com/softwaredownload/mcl_pm64_dll.zip
    Note: - Windows may block the DLL file after download as a precaution
    - Right-click on the file, select properties, click "Unblock" (if shown)
    3: Ensure the above dll file is placed in the directory specified in definitions.py
    """

    reading_signal = QtCore.pyqtSignal(float)
    connected_signal = QtCore.pyqtSignal(bool)

    def __init__(self, config, parent=None, device_key="Forward_Power_Meter"):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.last_reading_time = None
        self.serial_number = None
        self.pwr = usb_pm()
        self.connected = False
        self.fields_setup()

    def fields_setup(self):
        """Sets the class' serial number to the one specified in the config file"""
        self.serial_number = self.config[self.device_key]["serial_number"]

    # def declare_methods(self):
    #     hllApiProto = ctypes.WINFUNCTYPE(
    #         ctypes.c_int,  # Return type.
    #         ctypes.c_,  # Parameters 1 ...
    #         ctypes.c_void_p,
    #         ctypes.c_void_p,
    #         ctypes.c_void_p)  # ... thru 4.
    #     hllApiParams = (1, "p1", 0), (1, "p2", 0), (1, "p3", 0), (1, "p4", 0),

    def connect_hardware(self):
        """
        Sets the model name, serial number, power average, frequency,
        and format of the power meter. Also sends connected signals.
        """
        self.pwr.Open_Sensor(self.serial_number)
        model_name = self.pwr.GetSensorModelName()
        serial_no = self.pwr.GetSensorSN()
        if len(model_name) == 20 or len(serial_no) == 20:
            self.log(level="error", message=f"{self.device_key} could not connect")
            self.connected = False
        else:
            self.serial_number = serial_no
            self.connected = True
            self.log(level="info", message=f"{self.device_key} (model {model_name}, serial "
                                           f"{serial_no} connected successfully")
            self.pwr.Freq = 1000  # Set measurement frequency
            self.pwr.AvgCount = 1  # Set averaging count to 1
            self.pwr.AVG = 1  # Enable averaging
            self.pwr.Format_mW = True

        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def disconnect_hardware(self):
        """Closes the sensors, and changes/emits the connected variable to false"""
        self.pwr.Close_Sensor()
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        """Gets an immediate reading from the power meter"""
        power = self.pwr.ReadImmediatePower()
        self.reading_signal.emit(power)
        self.last_reading_time = t.time()
        return power

    def get_serial_number(self) -> Union[str, None]:
        """Returns the class' stored serial number for the power meter"""
        if not self.connected:
            return None

        return self.serial_number


if __name__ == "__main__":
    forward_meter = PowerMeter(config=None, device_key="Forward_Power_Meter")
    forward_meter.connect_hardware()

    start_time = t.time()
    # while True:
    #     cycle_start_time = t.time()
    #     print(f"Forward power: {forward_meter.get_reading()} Watts")

    forward_meter.disconnect_hardware()
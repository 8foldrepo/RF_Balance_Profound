# Control Mini-Circuits' PWR series power meters via USB
# Requirements:
#   1: Python.Net (pip install pythonnet)
#   2: Mini-Circuits' DLL API file (mcl_pm_NET45.dll)
#      https://www.minicircuits.com/softwaredownload/mcl_pm64_dll.zip
#      Note: - Windows may block the DLL file after download as a precaution
#            - Right-click on the file, select properties, click "Unblock" (if shown)
import clr # pythonnet
from abc import abstractmethod
from PyQt5.QtCore import pyqtSignal
import random
from Hardware.Abstract.abstract_sensor import AbstractSensor
import ctypes
from definitions import POWER_METER_DLL_PATH
import sys
from definitions import POWER_METER_DLL_PATH
sys.path.append(POWER_METER_DLL_PATH)
clr.AddReference('mcl_pm_NET45')    # Reference the DLL
from mcl_pm_NET45 import usb_pm

class PowerMeter(AbstractSensor):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config, parent=None, device_key = "Forward_Power_Meter"):
        super().__init__(parent=parent,config=config,  device_key = device_key)
        self.pwr = usb_pm()
        self.connected = False
        self.fields_setup()

    def fields_setup(self):
        self.serial_number = self.config[self.device_key]["serial_number"]

    def declare_methods(self):
        hllApiProto = ctypes.WINFUNCTYPE(
            ctypes.c_int,  # Return type.
            ctypes.c_,  # Parameters 1 ...
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p)  # ... thru 4.
        hllApiParams = (1, "p1", 0), (1, "p2", 0), (1, "p3", 0), (1, "p4", 0),

    def connect_hardware(self):
        self.pwr.Open_Sensor(self.serial_number)
        ModelName = self.pwr.GetSensorModelName()
        SerialNo = self.pwr.GetSensorSN()
        self.log(ModelName, SerialNo)
        self.pwr.Freq = 1000  # Set measurement frequency
        self.pwr.AvgCount = 1  # Set averaging count to 1
        self.pwr.AVG = 1  # Enable averaging
        self.pwr.Format_mW = True

        self.connected = True
        self.connected_signal.emit(self.connected)

    def disconnect_hardware(self):
        self.pwr.Close_Sensor()
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        # Todo: read a wattage value and emit it via the reading signal
        Power = self.pwr.ReadPower()
        self.reading_signal.emit(Power)
        return Power

if __name__ == '__main__':
    reflected_meter = PowerMeter(config=None, device_key='Reflected_Power_Meter')
    forward_meter = PowerMeter(config=None, device_key='Forward_Power_Meter')
    forward_meter.connect_hardware()
    reflected_meter.connect_hardware()

    print(f'Forward power: {forward_meter.get_reading()} Watts')
    print(f'Reflected power: {reflected_meter.get_reading()} Watts')

    forward_meter.disconnect_hardware()
    reflected_meter.disconnect_hardware()


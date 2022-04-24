# Control Mini-Circuits' PWR series power meters via USB
# Requirements:
#   1: Python.Net (pip install pythonnet)
#   2: Mini-Circuits' DLL API file (mcl_pm_NET45.dll)
#      https://www.minicircuits.com/softwaredownload/mcl_pm64_dll.zip
#      Note: - Windows may block the DLL file after download as a precaution
#            - Right-click on the file, select properties, click "Unblock" (if shown
import random
from Hardware.Abstract.abstract_sensor import AbstractSensor
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class PowerMeter(AbstractSensor):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config, parent=None, device_key = "Forward_Power_Meter"):
        super().__init__(parent=parent,config=config,  device_key = device_key)
        self.connected = False
        self.fields_setup()

    def fields_setup(self):
        self.serial_number = self.config[self.device_key]["serial_number"]

    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        t.sleep(.5)
        reading = random.random()
        self.reading_signal.emit(reading)
        return reading

if __name__ == '__main__':
    reflected_meter = PowerMeter(config=None, device_key='Reflected_Power_Meter')
    forward_meter = PowerMeter(config=None, device_key='Forward_Power_Meter')
    forward_meter.connect_hardware()
    reflected_meter.connect_hardware()

    print(f'Forward power: {forward_meter.get_reading()} Watts')
    print(f'Reflected power: {reflected_meter.get_reading()} Watts')

    forward_meter.disconnect_hardware()
    reflected_meter.disconnect_hardware()


import nidaqmx
from PyQt5.QtCore import pyqtSignal
from Hardware.Abstract.abstract_sensor import AbstractSensor

class Thermocouple(AbstractSensor):
    reading_signal = pyqtSignal(float)
    connected_signal = pyqtSignal(bool)

    def __init__(self, config, parent=None, device_key = "TempMon"):
        super().__init__(parent=parent,config=config,  device_key = device_key)
        self.connected = False
        self.fields_setup()

    def fields_setup(self):
        self.name = self.config[self.device_key]['DeviceName']

    def connect_hardware(self):
        try:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_thrmcpl_chan(f"{self.name}/ai0")
            self.connected = True
        except Exception as e:
            self.log(level='error', message=f'Error connecting to thermocouple: {e}')
            self.connected = False

        self.connected_signal.emit(self.connected)

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    def get_reading(self):
        if not self.connected:
            return

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_thrmcpl_chan(f"{self.name}/ai0")
            reading = task.read()

        self.reading_signal.emit(reading)
        return reading

if __name__ == '__main__':
    therm = Thermocouple(config=None)
    therm.connect_hardware()

    while True:
        print(therm.get_reading())


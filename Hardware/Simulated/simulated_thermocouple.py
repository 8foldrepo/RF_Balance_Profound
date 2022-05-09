import random
from abc import abstractmethod

from Hardware.Abstract.abstract_sensor import AbstractSensor


class SimulatedThermocouple(AbstractSensor):
    @abstractmethod
    def __init__(self, config, parent=None, device_key=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.connected = True

    @abstractmethod
    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    @abstractmethod
    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(self.connected)

    @abstractmethod
    def get_reading(self):
        if self.config["Debugging"]["simulate_errors"]:
            return None

        noise = 0.1 * random.random()
        signal = 23.2 + noise
        reading = round(signal, 1)

        self.reading_signal.emit(reading)
        return reading

    def get_serial_number(self) -> str:
        return '"Simulated"'

from Utilities.load_config import load_configuration
from Hardware.Abstract.abstract_relay import AbstractRelay
from abc import abstractmethod


class SimulatedRelay(AbstractRelay):

    def __init__(self, config=None, device_key='Pump', parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)
        self.ser = None
        self.fields_setup()
        self.on = False

    @abstractmethod
    def fields_setup(self):
        if self.config is None:
            self.config = load_configuration()
        self.timeout_s = self.config[self.device_key]['timeout_s']
        self.on_by_default = self.config[self.device_key]['on_by_default']
        self.port = self.config[self.device_key]['port']
        # retrieve config settings from config file

    @abstractmethod
    def connect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ''

    @abstractmethod
    def disconnect_hardware(self):
        self.connected_signal.emit(False)

    @abstractmethod
    def relay_read(self):
        return self.on

    @abstractmethod
    def relay_write(self, on: bool):
        self.on = on

    def get_serial_number(self) -> str:
        return '\"Simulated\"'

if __name__ == '__main__':
    switch = SimulatedRelay()
    switch.connect_hardware()
    switch.relay_write(True)
    switch.relay_write(False)

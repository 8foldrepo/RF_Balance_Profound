import random

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from Hardware.relay_board import Relay_Board
from Hardware.Abstract.abstract_device import AbstractDevice
import time as t

class IO_Board(AbstractDevice):
    pump_reading_signal = pyqtSignal(bool)
    water_level_reading_signal = pyqtSignal(str)

    def __init__(self, config=None, device_key="NI_DAQ", parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)
        self.power_relay = Relay_Board(device_key="Power_Relay")
        self.power_relay.connect_hardware()
        self.pump_on = False
        self.active_channel = 0  # 0 means all channels are off

    def get_active_relay_channel(self) -> int:
        return self.active_channel

    def set_pump_on(self, on) -> bool:
        self.pump_on = on

    def get_pump_reading(self) -> bool:
        return self.pump_on

    '''Return the state of the water level sensor. possible values are below_level, above_level, and level'''

    def get_water_level(self) -> str:
        states = ['below_level', 'above_level', 'level']
        return random.choice(states)

    def fields_setup(self):
        pass

    def connect_hardware(self):
        self.connected_signal.emit(True)
        return True

    def activate_relay_channel(self, channel_number: int):
        pass

    def disconnect_hardware(self):
        self.is_connected = True
        self.connected_signal.emit(self.is_connected)

    def connected(self):
        return self.is_connected

    def wrap_up(self):
        self.disconnect_hardware()


if __name__ == '__main__':
    daq = NI_DAQ()
    daq.connect_hardware()
    daq.active_channel(1)
    # for i in range(11):
    #     print(f"turning on relay {i}")
    #     daq.activate_relay_channel(i)
    #     t.sleep(5)


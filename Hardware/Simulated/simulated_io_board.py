import random
from Hardware.Abstract.abstract_io_board import AbstractIOBoard
from definitions import WaterLevel
from PyQt5.QtCore import pyqtSignal
from Hardware.relay_board import RelayBoard
import time as t

'''Class defining the functions of a WTF digital IO board. It can be instantiated with simulated or real hardware'''


class SimulatedIOBoard(AbstractIOBoard):
    pump_reading_signal = pyqtSignal(bool)
    water_level_reading_signal = pyqtSignal(WaterLevel)
    filling_signal = pyqtSignal()

    draining_signal = pyqtSignal(WaterLevel)

    def __init__(self, config=None, device_key="NI_DAQ", parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)
        self.power_relay = RelayBoard(device_key="Daq_Power_Relay")
        self.power_relay.connect_hardware()
        self.pump_on = False
        self.ua_pump_on = True
        self.water_level = WaterLevel.below_level
        self.active_channel = 0  # 0 means all channels are off
        self.get_water_level()

    def get_active_relay_channel(self) -> int:
        return self.active_channel

    def set_pump_on(self, on):
        self.pump_on = on

    def get_ua_pump_reading(self) -> bool:
        self.pump_reading_signal.emit(self.ua_pump_on)
        return self.ua_pump_on

    def fill_tank(self):
        self.filling_signal.emit()
        t.sleep(2)
        self.water_level = WaterLevel.level
        self.get_water_level()
        return True

    def drain_tank(self):
        self.draining_signal.emit(WaterLevel.below_level)
        t.sleep(2)
        start_time = t.time()
        while t.time() - start_time < 20:
            if self.get_water_level() == WaterLevel.below_level:
                return True
        return False

    def drain_tank_to_level(self):
        self.draining_signal.emit(WaterLevel.level)
        t.sleep(2)
        start_time = t.time()
        while t.time() - start_time < 20:
            if self.get_water_level() == WaterLevel.level:
                return True
        return False

    '''Return the state of the water level sensor as a WaterLevel Enum'''

    def get_water_level(self) -> WaterLevel:
        self.water_level_reading_signal.emit(self.water_level)
        return self.water_level

    def fields_setup(self):
        pass

    def connect_hardware(self):
        self.get_water_level()
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ''


    def activate_relay_channel(self, channel_number: int):
        pass

    def disconnect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)

    def is_connected(self):
        return self.connected

import random

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from Hardware.relay_board import Relay_Board
from Hardware.Simulated.simulated_device import SimulatedDevice
import time as t

class IO_Board(SimulatedDevice):
    pump_reading_signal = pyqtSignal(bool)
    water_level_reading_signal = pyqtSignal(str)
    filling_signal = pyqtSignal()
    #the str is the target water level, either 'level' or 'below_level'
    draining_signal = pyqtSignal(str)

    def __init__(self, config=None, device_key="NI_DAQ", parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)
        self.power_relay = Relay_Board(device_key="Daq_Power_Relay")
        self.power_relay.connect_hardware()
        self.pump_on = False
        self.ua_pump_on = False
        self.active_channel = 0  # 0 means all channels are off
        self.get_water_level()

    def get_active_relay_channel(self) -> int:
        return self.active_channel

    def set_pump_on(self, on) -> bool:
        self.pump_on = on

    def get_ua_pump_reading(self) -> bool:
        self.ua_pump_on = random.choice([True,False])
        return self.ua_pump_on

    '''Return the state of the water level sensor. possible values are below_level, above_level, and level'''

    def fill_tank(self):
        self.filling_signal.emit()
        t.sleep(2)
        starttime= t.time()
        while t.time()-starttime<20:
            if self.get_water_level() == 'level' or self.get_water_level() == 'above_level':
                return True
        return False

    def drain_tank(self):
        self.draining_signal.emit('below_level')
        t.sleep(2)
        starttime= t.time()
        while t.time()-starttime<20:
            if self.get_water_level() == 'below_level':
                return True
        return False

    def drain_tank_to_level(self):
        self.draining_signal.emit('level')
        t.sleep(2)
        start_time = t.time()
        while t.time() - start_time < 20:
            if self.get_water_level() == 'level':
                return True
        return False

    def get_water_level(self) -> str:
        states = ['below_level', 'above_level', 'level']
        state = random.choice(states)
        print(f"get_water_level called in simulated_io_board.py, water level is {state}")
        self.water_level_reading_signal.emit(state)
        return state

    def fields_setup(self):
        pass

    def connect_hardware(self):
        self.connected_signal.emit(True)
        self.get_water_level()
        return True

    def activate_relay_channel(self, channel_number: int):
        pass

    def disconnect_hardware(self):
        self.connected = True
        self.connected_signal.emit(self.connected)

    def is_connected(self):
        return self.connected

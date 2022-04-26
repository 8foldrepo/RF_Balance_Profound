import random
from abc import abstractmethod, ABCMeta

from definitions import WaterLevel
from PyQt5.QtCore import pyqtSignal
from Hardware.Abstract.abstract_device import AbstractDevice
from Hardware.relay_board import RelayBoard
import time as t


class AbstractIOBoard(AbstractDevice):
    __metaclass__ = ABCMeta

    pump_reading_signal = pyqtSignal(bool)
    water_level_reading_signal = pyqtSignal(WaterLevel)
    filling_signal = pyqtSignal()
    draining_signal = pyqtSignal(WaterLevel)

    def __init__(self, config=None, device_key="NI_DAQ", parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)

    @abstractmethod
    def get_active_relay_channel(self) -> int:
        ...

    @abstractmethod
    def set_tank_pump_on(self, on):
        ...

    @abstractmethod
    def get_ua_pump_reading(self) -> bool:
        ...

    @abstractmethod
    def fill_tank(self):
        ...

    @abstractmethod
    def drain_tank(self):
        ...

    @abstractmethod
    def drain_tank_to_level(self):
        ...

    '''Return the state of the water level sensor as a WaterLevel Enum'''

    @abstractmethod
    def get_water_level(self) -> WaterLevel:
        ...

    '''Activates the specified relay channel and deactivates all others. returns whether it was successful'''
    @abstractmethod
    def activate_relay_channel(self, channel_number: int) -> bool:
        pass

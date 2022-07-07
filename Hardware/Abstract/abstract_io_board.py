from abc import abstractmethod, ABCMeta

from PyQt5.QtCore import pyqtSignal

from Hardware.Abstract.abstract_device import AbstractDevice
from Hardware.Abstract.abstract_relay import AbstractRelay
from data_structures.variable_containers import WaterLevel


class AbstractIOBoard(AbstractDevice):
    __metaclass__ = ABCMeta
    tank_full_signal = pyqtSignal()
    pump_reading_signal = pyqtSignal(bool)
    water_level_reading_signal = pyqtSignal(WaterLevel)
    filling_signal = pyqtSignal()
    draining_signal = pyqtSignal(WaterLevel)
    stop_filling_draining_var: bool
    power_relay: AbstractRelay
    def __init__(self, config=None, device_key="NI_DAQ", parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)

    @abstractmethod
    def get_active_relay_channel(self) -> int:
        ...

    @abstractmethod
    def set_tank_pump_on(self, on: bool, clockwise: bool):
        ...

    @abstractmethod
    def get_ua_pump_reading(self) -> bool:
        ...

    @abstractmethod
    def drain_tank(self):
        ...

    @abstractmethod
    def bring_tank_to_level(self):
        ...

    @abstractmethod
    def get_water_level(self) -> WaterLevel:
        """Return the state of the water level sensor as a WaterLevel Enum"""

        ...

    @abstractmethod
    def tank_full_override_slot(self) -> None:
        self.water_level = WaterLevel.level
        self.water_level_reading_signal.emit(self.water_level)
        self.tank_full_signal.emit()
        self.stop_filling_draining_var = True
        self.set_tank_pump_on(False, False)

    @abstractmethod
    def activate_relay_channel(self, channel_number: int) -> bool:
        """Activates the specified relay channel and deactivates all others. returns whether it was successful"""

        pass

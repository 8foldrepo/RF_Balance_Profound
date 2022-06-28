"""
A simulation class for the national-instruments digital IO board
"""
import random
import time as t
from typing import Tuple

from PyQt5 import QtCore
from Hardware.Abstract.abstract_io_board import AbstractIOBoard
from Hardware.Simulated.simulated_relay import SimulatedRelay
from data_structures.variable_containers import WaterLevel


class SimulatedIOBoard(AbstractIOBoard):
    """Class defining the functions of a WTF digital IO board. It can be instantiated with simulated or real hardware"""
    pump_reading_signal = QtCore.pyqtSignal(bool)  # connected to update_pump_indicator in main window
    water_level_reading_signal = QtCore.pyqtSignal(WaterLevel)  # connected to main window's water level indicator
    filling_signal = QtCore.pyqtSignal()  # connected to show filling tank dialog in main window
    draining_signal = QtCore.pyqtSignal(WaterLevel)  # connected to show draining tank dialog in main window
    stop_filling_draining_var: bool

    def __init__(self, config: dict, device_key: str = "NI_DAQ", parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)
        self.stop_filling_draining_var = False
        self.clockwise = False  # presumably direction of water flow
        self.power_relay = SimulatedRelay(config=config, device_key="Daq_Power_Relay")
        self.power_relay.connect_hardware()
        self.pump_on = False
        self.ua_pump_on = True
        self.water_level = WaterLevel.below_level
        self.active_channel = 0  # 0 means all channels are off
        self.get_water_level()

    def get_active_relay_channel(self) -> int:
        """
        :return: self.active_channel as an integer
        """
        return self.active_channel

    def set_tank_pump_on(self, on: bool, clockwise: bool) -> None:
        """
        Turns tank pump on of off

        :param on: Whether thank should be on or not
        :param clockwise: Direction of water pump
        """
        self.pump_on = on
        self.clockwise = clockwise

    def get_ua_pump_reading(self) -> bool:
        """
        Returns whether ua pump is on or not

        :return: whether the ua pump is on or not
        """
        self.pump_reading_signal.emit(self.ua_pump_on)
        return self.ua_pump_on

    def drain_tank(self) -> bool:
        """
        Command to drain the tank in the wet test fixture tank

        :return: Whether drain completed successfully
        """
        self.draining_signal.emit(WaterLevel.below_level)
        t.sleep(2)
        start_time = t.time()
        while t.time() - start_time < 20:
            if self.stop_filling_draining_var:
                self.set_tank_pump_on(False, False)
                return True
            self.water_level = random.choice([WaterLevel.level, WaterLevel.below_level, WaterLevel.above_level])
            if self.get_water_level() == WaterLevel.below_level:
                return True
        return False

    def bring_tank_to_level(self) -> bool:
        """
        Command to bring the water level up/down to perfect level for testing

        :return: Whether leveling completed successfully
        """
        if self.water_level == WaterLevel.level:
            self.log("WaterLevel is already level")
            return True

        if self.water_level == WaterLevel.below_level:
            self.filling_signal.emit()
        else:
            self.draining_signal.emit(WaterLevel.level)

        t.sleep(2)
        start_time = t.time()
        while t.time() - start_time < 20:
            if self.stop_filling_draining_var:
                self.set_tank_pump_on(False, False)
                return True
            self.water_level = random.choice([WaterLevel.level, WaterLevel.below_level, WaterLevel.above_level])
            if self.get_water_level() == WaterLevel.level:
                self.tank_full_signal.emit()
                return True
        return False

    def get_water_level(self) -> WaterLevel:
        """
        Return the state of the water level sensor as a WaterLevel Enum

        :returns: water level as WaterLevel enumerator object
        """
        self.water_level_reading_signal.emit(self.water_level)
        return self.water_level

    def fields_setup(self) -> None:
        """Does nothing at the moment"""
        pass

    def connect_hardware(self) -> Tuple[bool, str]:
        """
        Runs the get_water_level method, sets connected flag to true and emits it via connected_signal; returns new
        connected flag value (True) and empty string since no possibility of failing

        :return:
            Tuple where first value represents whether simulated IO board is connected and second string value
            representing feedback if issue occurred (won't in simulated)
        """
        self.get_water_level()
        self.connected = True
        self.connected_signal.emit(self.connected)
        return self.connected, ""

    def activate_relay_channel(self, channel_number: int) -> None:
        """
        Changes the class' active channel variable to passed channel_number argument

        :param channel_number: the channel number you want the IO board to have active
        """
        self.active_channel = channel_number

    def disconnect_hardware(self) -> None:
        """
        Sets connected flag to false and emits new value via the connected_signal
        """
        self.connected = False
        self.connected_signal.emit(self.connected)

    def is_connected(self):
        """
        returns current value of class' self.connected boolean variable

        :return: boolean representing whether simulated IO board is connected
        """
        return self.connected

    def get_serial_number(self) -> str:
        """
        Get the serial number of IO board, since simulated, return
        value will be same everytime for clarity during logging

        :return: Will return 'Simulated' every time
        """
        return '"Simulated"'

    def tank_full_override_slot(self) -> None:
        self.water_level = WaterLevel.level
        self.water_level_reading_signal.emit(self.water_level)
        self.tank_full_signal.emit()
        self.stop_filling_draining_var = True
        self.set_tank_pump_on(False, False)

    def wrap_up(self):
        """
        Relay method calling disconnect_hardware(); used for multi-hardware disconnection automation in manager
        """
        self.disconnect_hardware()

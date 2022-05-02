import random
import time as t

import nidaqmx
from PyQt5.QtCore import pyqtSignal
from nidaqmx.constants import LineGrouping

from Hardware.Abstract.abstract_io_board import AbstractIOBoard
from Hardware.relay_board import RelayBoard
from definitions import WaterLevel

"""Class for interfacing with an National instruments usb-6009 digital IO board"""


class DIOBoard(AbstractIOBoard):
    pump_reading_signal = pyqtSignal(bool)
    water_level_reading_signal = pyqtSignal(WaterLevel)

    # used for showing UI dialogs in MainWindow
    filling_signal = pyqtSignal()
    draining_signal = pyqtSignal(WaterLevel)

    def __init__(self, config=None, device_key="WTF_DIO", simulate_sensors=False, parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)
        self.simulate_sensors = simulate_sensors
        if simulate_sensors:
            self.water_level = WaterLevel.below_level
            self.ua_pump_on = False

        self.water_level = None
        self.ua_pump_on = None
        self.power_relay = RelayBoard(config=config, device_key="Daq_Power_Relay")
        self.power_relay.connect_hardware()
        self.pump_on = False
        self.fields_setup()
        self.active_channel = 0  # 0 means all channels are off

    def connect_hardware(self):
        self.log('Connecting to DIO board... ')
        self.connected = self.activate_relay_channel(-1)
        if self.connected:
            self.log(f'{self.device_key} connected successfully')
        else:
            self.log(f'{self.device_key} failed to connect')

        self.connected_signal.emit(self.connected)
        return self.connected, ''

    def activate_relay_channel(self, channel_number: int) -> bool:
        with nidaqmx.Task() as task:
            try:
                task.do_channels.add_do_chan(f"{self.name}/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                task.do_channels.add_do_chan(f"{self.name}/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                pin_ray = [False] * 10
                if 0 < channel_number < 11:
                    pin_ray[channel_number - 1] = True
                task.write(pin_ray, auto_start=True)
                return True
            except nidaqmx.errors.DaqError as e:
                if str(e) == 'Specified operation cannot be performed when there are no channels in the task':
                    self.log(level='error', message='Channel not found')
                elif 'Device identifier is invalid' in str(e):
                    self.log(level='error', message='Device not found, check connection and device name in config')
                else:
                    self.log(level='error', message=f'Unknown error {str(e)}')
                return False

    def get_active_relay_channel(self) -> int:
        return self.active_channel

    # Todo: test
    def fill_tank(self):
        water_level = self.get_water_level()

        if water_level == WaterLevel.above_level:
            self.log("Tank is already full")
            return True
        if water_level == WaterLevel.below_level or WaterLevel.level:
            self.log("Filling tank, please wait...")
            self.set_tank_pump_on(on=True, clockwise=True)
            self.filling_signal.emit()

            start_time = t.time()
            while t.time() - start_time < self.config[self.device_key]["Water level timeout (s)"]:
                elapsed_time_s = t.time() - start_time
                # If we are simulating hardware wait 10 seconds and then change the simulated water level
                if self.simulate_sensors:
                    if elapsed_time_s >= 10:
                        self.water_level = WaterLevel.level
                        self.water_level_reading_signal.emit(self.water_level)

                if self.get_water_level() == WaterLevel.level or self.get_water_level() == WaterLevel.above_level:
                    self.log("Tank full")
                    return True
        return False

    # Todo: test
    def drain_tank(self):
        water_level = self.get_water_level()

        if water_level == WaterLevel.below_level:
            self.log("Tank is already below level")
            return True
        if water_level == WaterLevel.above_level or WaterLevel.level:
            self.log("Draining tank, please wait...")
            self.draining_signal.emit(WaterLevel.below_level)
            self.set_tank_pump_on(on=True, clockwise=False)
            start_time = t.time()

            while t.time() - start_time < self.config[self.device_key]["Water level timeout (s)"]:
                elapsed_time_s = t.time() - start_time
                # If we are simulating hardware wait 10 seconds and then change the simulated water level
                if self.simulate_sensors:
                    if elapsed_time_s >= 10:
                        self.water_level = WaterLevel.below_level
                        self.water_level_reading_signal.emit(self.water_level)

                if self.get_water_level() == WaterLevel.below_level:
                    self.log("Tank drained")
                    return True
        return False

    # Todo: test
    def drain_tank_to_level(self):
        water_level = self.get_water_level()

        if water_level == WaterLevel.level:
            self.log("Tank is already level")
            return True
        elif water_level == WaterLevel.above_level:
            self.log("Draining tank, please wait...")
            self.draining_signal.emit(WaterLevel.level)
            self.set_tank_pump_on(on=True, clockwise=False)
            start_time = t.time()

            while t.time() - start_time < self.config[self.device_key]["Water level timeout (s)"]:
                elapsed_time_s = t.time() - start_time
                # If we are simulating hardware wait 10 seconds and then change the simulated water level
                if self.simulate_sensors:
                    if elapsed_time_s >= 10:
                        self.water_level = WaterLevel.level
                        self.water_level_reading_signal.emit(self.water_level)

                if self.get_water_level() == WaterLevel.level or WaterLevel.below_level:
                    self.log("Tank drained")
                    return True
        elif water_level == WaterLevel.below_level:
            self.log("Filling tank, please wait...")
            self.set_tank_pump_on(on=True, clockwise=True)
            self.filling_signal.emit()
            start_time = t.time()

            while t.time() - start_time < self.config[self.device_key]["Water level timeout (s)"]:
                elapsed_time_s = t.time() - start_time
                # If we are simulating hardware wait 10 seconds and then change the simulated water level
                if self.simulate_sensors:
                    if elapsed_time_s >= 10:
                        self.water_level = WaterLevel.level
                        self.water_level_reading_signal.emit(self.water_level)

                if self.get_water_level() == WaterLevel.level or self.get_water_level() == WaterLevel.above_level:
                    self.log("Tank full")
                    return True
        return False

    def set_tank_pump_on(self, on, clockwise):
        with nidaqmx.Task() as task:  # enabling the appropriate ports to enable pump
            # ON/OFF
            task.do_channels.add_do_chan(f"{self.name}/port1/line4:4", line_grouping=LineGrouping.CHAN_PER_LINE)

            # CW/CCW
            task.do_channels.add_do_chan(f"{self.name}/port1/line6:6", line_grouping=LineGrouping.CHAN_PER_LINE)

            task.write([not on, clockwise], auto_start=True)

    def get_ua_pump_reading(self) -> bool:
        if self.simulate_sensors:
            self.pump_on = random.choice([True, False])
            self.pump_reading_signal.emit(self.pump_on)
            return self.pump_on

        # todo: check whether the pump is on or off and return a boolean
        with nidaqmx.Task() as task:  # enabling the appropriate ports to enable pump reading
            task.di_channels.add_di_chan(f"{self.name}/port1/line3:3", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.3

            P1_3 = task.read()

            if not P1_3:  # if value in list is false
                self.pump_on = True  # then pump is on
            elif P1_3:  # if value in list is true
                self.pump_on = False  # pump is off

            self.pump_reading_signal.emit(self.pump_on)
            return self.pump_on

    def disconnect_hardware(self):
        self.connected = False
        self.connected_signal.emit(False)

    def get_water_level(self) -> WaterLevel:
        """Return the state of the water level sensor. possible values are below_level, above_level, and level"""

        if self.simulate_sensors: return self.water_level

        with nidaqmx.Task() as task:  # enabling the appropriate ports to read water levels
            # task.di_channels.add_di_chan(f"{self.name}/port1/line2:2", line_grouping=LineGrouping.CHAN_PER_LINE)  #
            # P1.2
            task.di_channels.add_di_chan(f"{self.name}/port1/line5:5", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.5
            task.di_channels.add_di_chan(f"{self.name}/port1/line2:2", line_grouping=LineGrouping.CHAN_PER_LINE)  # P2.2

            list_of_values = task.read()

            P1_2 = list_of_values[0]
            P1_5 = list_of_values[1]

            if P1_2 and not P1_5:
                level = WaterLevel.level
            elif P1_5 and not P1_2:
                level = WaterLevel.below_level
            else:
                level = WaterLevel.above_level

            self.water_level_reading_signal.emit(level)
            return level

    def wrap_up(self):
        self.power_relay.wrap_up()
        self.disconnect_hardware()
        self.disconnect_hardware()

    def fields_setup(self):
        self.name = self.config[self.device_key]['DAQ Device name']
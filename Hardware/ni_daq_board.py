import random
import nidaqmx
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from nidaqmx.constants import LineGrouping
from pyqtgraph.parametertree.parameterTypes import action

from Hardware.relay_board import Relay_Board
from Hardware.Abstract.abstract_device import AbstractDevice
import time as t

class NI_DAQ(AbstractDevice):
    pump_reading_signal = pyqtSignal(bool)
    water_level_reading_signal = pyqtSignal(str)

    #used for showing UI dialogs in mainwindow
    filling_signal = pyqtSignal()
    draining_signal = pyqtSignal()

    def __init__(self, config=None, device_key="WTF_DIO", simulate_sensors = False, parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)
        self.simulate_sensors = simulate_sensors
        if simulate_sensors:
            self.water_level = 'below_level'
            self.ua_pump_on = False

        self.water_level = None
        self.ua_pump_on = None
        self.power_relay = Relay_Board(device_key="Daq_Power_Relay")
        self.power_relay.connect_hardware()
        self.pump_on = False
        self.fields_setup()
        self.active_channel = 0  # 0 means all channels are off

    def get_active_relay_channel(self) -> int:
        return self.active_channel

    #Todo: test
    def fill_tank(self):
        water_level = self.get_water_level()

        if water_level == "above_level":
            self.log("Tank is already full")
            return True
        if water_level == "below_level" or 'level':
            self.log("Filling tank, please wait...")
            self.set_tank_pump_on(on=True,clockwise=True)
            self.filling_signal.emit()
            starttime = t.time()

            while t.time() - starttime < self.config[self.device_key]["Water level timeout (s)"]:
                elapsed_time_s = t.time()-starttime
                # If we are simulating hardware wait 10 seconds and then change the simulated water level
                if self.simulate_sensors:
                    if elapsed_time_s >= 10:
                        self.water_level = 'level'
                        self.water_level_reading_signal.emit(self.water_level)

                if self.get_water_level() == 'level' or self.get_water_level() == 'above_level':
                    self.log("Tank full")
                    return True
        return False

    #Todo: test
    def drain_tank(self):
        water_level = self.get_water_level()

        if water_level == "below_level":
            self.log("Tank is already below level")
            return True
        if water_level == "below_level" or 'level':
            self.log("Draining tank, please wait...")
            self.draining_signal.emit()
            self.set_tank_pump_on(on=True, clockwise=False)
            starttime = t.time()

            while t.time() - starttime < self.config[self.device_key]["Water level timeout (s)"]:
                elapsed_time_s = t.time() - starttime
                # If we are simulating hardware wait 10 seconds and then change the simulated water level
                if self.simulate_sensors:
                    if elapsed_time_s >= 10:
                        self.water_level = 'below_level'
                        self.water_level_reading_signal.emit(self.water_level)

                if self.get_water_level() == 'below_level':
                    self.log("Tank drained")
                    return True
        return False

    def set_tank_pump_on(self, on, clockwise):
        with nidaqmx.Task() as task:  # enabling the appropriate ports to enable pump
            #ON/OFF
            task.do_channels.add_do_chan(f"{self.name}/port1/line4:4", line_grouping=LineGrouping.CHAN_PER_LINE)

            # CW/CCW
            task.do_channels.add_do_chan(f"{self.name}/port1/line6:6", line_grouping=LineGrouping.CHAN_PER_LINE)

            task.write([not on, clockwise], auto_start=True)

    def get_ua_pump_reading(self) -> bool:
        if self.simulate_sensors:
            self.pump_on = random.choice([True,False])
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

    '''Return the state of the water level sensor. possible values are below_level, above_level, and level'''

    def get_water_level(self) -> str:
        if self.simulate_sensors: return self.water_level

        states = ['below_level', 'above_level', 'level']
        with nidaqmx.Task() as task:  # enabling the appropriate ports to read water levels
            #task.di_channels.add_di_chan(f"{self.name}/port1/line2:2", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.2
            task.di_channels.add_di_chan(f"{self.name}/port1/line5:5", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.5
            task.di_channels.add_di_chan(f"{self.name}/port1/line2:2", line_grouping=LineGrouping.CHAN_PER_LINE)  # P2.2

            list_of_values = task.read()

            P1_2 = list_of_values[0]
            P1_5 = list_of_values[1]

            # Todo: change this to reflect model number of switches
            if P1_2 and not P1_5:  # making up random combinations, should change once get documentation
                level = states[1]
            elif P1_5 and not P1_2:
                level = states[0]
            else:
                level = states[2]

            self.water_level_reading_signal.emit(level)
            return level

    def fields_setup(self):
        self.name = self.config[self.device_key]['DAQ Device name']

    def connect_hardware(self):
        try:
            self.activate_relay_channel(-1)
            self.connected_signal.emit(True)
        except Exception as e:
            if str(e) == '\'Task\' object has no attribute \'_handle\'':
                self.log(level='error', message=f'Error with nidaqmx library: {e}')
                self.log(level='error',
                         message=f'Make sure you are using python 3.8, pip install nidaqmx version 0.6.1, '
                                 f'and reinstall the software from the NI website')
            else:
                self.log(level='error', message=f'Error in connect hardware: {e}')
        # Todo: setup all channels

    def activate_relay_channel(self, channel_number: int):
        with nidaqmx.Task() as task:
            try:
                task.do_channels.add_do_chan(f"{self.name}/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                task.do_channels.add_do_chan(f"{self.name}/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)

                pin_ray = [False]*10

                if 0 < channel_number < 11:
                    pin_ray[channel_number-1] = True

                task.write(pin_ray, auto_start=True)

            except nidaqmx.errors.DaqError as e:
                print(e)
                if str(e) == 'Specified operation cannot be performed when there are no channels in the task':
                    self.log(level='error', message='Channel not found')
                else:
                    self.log(level='error', message=f'Unknown error {str(e)}')

    def disconnect_hardware(self):
        self.is_connected = True
        self.connected_signal.emit(self.is_connected)
        self.power_relay.relay_write(False)

    def connected(self):
        return self.is_connected

    def wrap_up(self):
        self.disconnect_hardware()


if __name__ == '__main__':
    daq = NI_DAQ()
    daq.connect_hardware()

    # while True:
    #     print(daq.get_ua_pump_reading())

    # for i in range(11):
    #     daq.activate_relay_channel(i)
    #     t.sleep(.5)
    #
    daq.set_tank_pump_on(True, False)
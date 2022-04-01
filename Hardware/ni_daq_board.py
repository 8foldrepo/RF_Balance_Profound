import nidaqmx
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from nidaqmx.constants import LineGrouping
from Hardware.relay_board import Relay_Board
from Hardware.Abstract.abstract_device import AbstractDevice
import time as t

class NI_DAQ(AbstractDevice):
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
        # todo: activate or deactivate the pump and return whether the operation was successful
        with nidaqmx.Task() as task:  # enabling the appropriate ports to enable pump
            task.do_channels.add_do_chan("Dev1/port1/line0:6", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.4 and 1.6

            if on:
                task.write([True, True, True, True, True, True, False], auto_start=True)  # I've only seen P1.6 react
            elif not on:
                task.write([True, True, True, True, True, True, True],
                           auto_start=True)  # I think true should turn the pump off
        pass

    def get_pump_reading(self) -> bool:
        # todo: check whether the pump is on or off and return a boolean
        with nidaqmx.Task() as task:  # enabling the appropriate ports to enable pump reading
            task.di_channels.add_di_chan("Dev1/port1/line0:4", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.3

            list_of_values = task.read()
            P1_3 = list_of_values[3]

            if not P1_3:  # if value in list is false
                self.pump_on = True  # then pump is on
            elif P1_3:  # if value in list is true
                self.pump_on = False  # pump is off

            self.pump_reading_signal.emit(self.pump_on)
            return self.pump_on

    '''Return the state of the water level sensor. possible values are below_level, above_level, and level'''

    def get_water_level(self) -> str:
        states = ['below_level', 'above_level', 'level']
        with nidaqmx.Task() as task:  # enabling the appropriate ports to read water levels
            task.di_channels.add_di_chan("Dev1/port1/line0:5", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.2 and 1.5
            task.di_channels.add_di_chan("Dev1/port2/line0:2", line_grouping=LineGrouping.CHAN_PER_LINE)  # P2.2

            list_of_values = task.read()

            P1_5 = list_of_values[5]  # seen True
            P1_2 = list_of_values[2]  # seen True
            P2_2 = list_of_values[8]  # can't see this change, this value from the doc

            if P1_5 and P1_2:  # making up random combinations, should change once get documentation
                return states[0]
            elif P1_5 and not P1_2:
                return states[1]
            elif not P1_5 and not P1_2:
                return states[3]

    def fields_setup(self):
        pass

    def connect_hardware(self):
        try:
            self.activate_relay_channel(-1)
            self.connected_signal.emit(True)
        except Exception as e:
            if str(e) == '\'Task\' object has no attribute \'_handle\'':
                self.log(level='error', message=f'Error with nidaqmx library: {e}')
                self.log(level='error', message=f'Make sure you are using python 3.8, pip install nidaqmx version 0.6.1, and reinstall the software from the NI website')
            else:
                self.log(level='error', message=f'Error in connect hardware: {e}')
        # Todo: setup all channels

    def activate_relay_channel(self, channel_number: int):
        with nidaqmx.Task() as task:
            try:
                if channel_number == 1:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([True, False, False, False, False, False, False, False, False, False], auto_start=True)
                elif channel_number == 2:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, True, False, False, False, False, False, False, False, False], auto_start=True)
                elif channel_number == 3:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, True, False, False, False, False, False, False, False], auto_start=True)
                elif channel_number == 4:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, False, True, False, False, False, False, False, False], auto_start=True)
                elif channel_number == 5:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, False, False, True, False, False, False, False, False], auto_start=True)
                elif channel_number == 6:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, False, False, False, True, False, False, False, False], auto_start=True)
                elif channel_number == 7:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, False, False, False, False, True, False, False, False], auto_start=True)
                elif channel_number == 8:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, False, False, False, False, False, True, False, False], auto_start=True)
                elif channel_number == 9:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, False, False, False, False, False, False, True, False], auto_start=True)
                elif channel_number == 10:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, False, False, False, False, False, False, False, True], auto_start=True)
                else:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write([False, False, False, False, False, False, False, False, False, False], auto_start=True)
            except nidaqmx.errors.DaqError as e:
                print(e)
                if str(e) == 'Specified operation cannot be performed when there are no channels in the task':
                    self.log(level='error', message='Channel not found')

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
    daq.active_channel(1)
    # for i in range(11):
    #     print(f"turning on relay {i}")
    #     daq.activate_relay_channel(i)
    #     t.sleep(5)


import nidaqmx
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from nidaqmx.constants import LineGrouping

from Hardware.Abstract.abstract_device import AbstractDevice
import time as t

class NI_DAQ(AbstractDevice):
    def __init__(self, config=None, device_key="NI_DAQ", parent=None):
        super().__init__(config=config, parent=parent, device_key=device_key)
        self.active_channel = 0  # 0 means all channels are off

    # def activate_relay_channel(self, channel = 0):  # No longer needed
    #      self.active_channel = channel
    #
    #      for i in range(1,11):
    #           if i == channel:
    #                self.set_channel(i,True)
    #           else:
    #                self.set_channel(i, False)

    def get_active_relay_channel(self) -> int:
        return self.active_channel

    def set_pump_on(self, on) -> bool:
        # todo: activate or deactivate the pump and return whether the operation was successful
        with nidaqmx.Task() as task:  # enabling the appropriate ports to enable pump
            task.do_channels.add_do_chan("Dev1/port1/line0:6", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.4 and 1.6
            task.write_data()
        pass

    def get_pump_reading(self) -> bool:
        # todo: check whether the pump is on or off and return a boolean
        with nidaqmx.Task() as task:  # enabling the appropriate ports to enable pump reading
            task.do_channels.add_do_chan("Dev1/port0/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)  # P0.0
            task.do_channels.add_do_chan("Dev1/port1/line0:4", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.4
            task.write_data()
        pass

    '''Return the state of the water level sensor. possible values are below_level, above_level, and level'''

    def get_water_level(self) -> str:
        states = ['below_level', 'above_level', 'level']
        with nidaqmx.Task() as task:  # enabling the appropriate ports to read water levels
            task.do_channels.add_do_chan("Dev1/port1/line0:5", line_grouping=LineGrouping.CHAN_PER_LINE)  # P1.2 and 1.5
            task.do_channels.add_do_chan("Dev1/port2/line0:2", line_grouping=LineGrouping.CHAN_PER_LINE)  # P2.2
            task.write_data()



    def fields_setup(self):
        pass

    def connect_hardware(self):
        self.set_channel(-1)
        # Todo: setup all channels

    def set_channel(self, channel_number: int):
        with nidaqmx.Task() as task:
            try:
                if channel_number == 1:
                    task.do_channels.add_do_chan("Dev1/port0/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 2:
                    task.do_channels.add_do_chan("Dev1/port0/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 3:
                    task.do_channels.add_do_chan("Dev1/port0/line0:2", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 4:
                    task.do_channels.add_do_chan("Dev1/port0/line0:3", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 5:
                    task.do_channels.add_do_chan("Dev1/port0/line0:4", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 6:
                    task.do_channels.add_do_chan("Dev1/port0/line0:5", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 7:
                    task.do_channels.add_do_chan("Dev1/port0/line0:6", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 8:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 9:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == 10:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
                elif channel_number == -1:
                    task.do_channels.add_do_chan("Dev1/port0/line0:7", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.do_channels.add_do_chan("Dev1/port1/line0:1", line_grouping=LineGrouping.CHAN_PER_LINE)
                    task.write_data()
            except nidaqmx.errors.DaqError as e:
                print(e)
                if str(e) == 'Specified operation cannot be performed when there are no channels in the task':
                    self.log(level='error', message='Channel not found')

    def disconnect_hardware(self):
        self.is_connected = False
        self.connected_signal.emit(self.is_connected)

    def connected(self):
        return self.is_connected

    def wrap_up(self):
        self.disconnect_hardware()


if __name__ == '__main__':
    daq = NI_DAQ()
    daq.connect_hardware()  # sets all channels to false

    # while True:
    #     for i in range(1,10):
    #          daq.activate_relay_channel(i)
    #         t.sleep(1)

    daq.activate_relay_channel(1)  # sets the channel to activate and disables all other channels

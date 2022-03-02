from abc import ABC, abstractmethod

from PyQt5.QtCore import *
import time as t
from Utilities.useful_methods import bound
import gclib
from Hardware.dummy_motors import  DummyMotors

from Utilities.useful_methods import create_coord_rays

import numpy as np

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
log_formatter = logging.Formatter(LOGGER_FORMAT)

import os
from definitions import ROOT_DIR
balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR,"./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)


class AbstractOscilloscope(QObject):
        """
        """

        # Dummy code, replace when developing a hardware interface
        dummy_command_signal = pyqtSignal(str)

        # For accessing parameters in config file
        device_key = 'Dummy_Oscilloscope'

        def __init__(self, config: dict):
            super().__init__()
            self.config = config
            self.connected = False

            self.fields_setup()

        def fields_setup(self):
            self.range_mv = self.config[self.device_key]['range_mv']
            self.channel = self.config[self.device_key]['channel']
            self.averages = self.config[self.device_key]['averages']
            self.capture_period_ns = self.config[self.device_key]['capture_period_ns']
            self.signal_frequency_MHz = 4.2
            self.signal_period_ns = 1/self.signal_frequency_MHz * 1000
            self.cycles = self.config[self.device_key]['cycles']
            self.delay_cycles = self.config[self.device_key]['delay_cycles']
            self.captures = int(self.cycles*self.signal_period_ns/self.capture_period_ns)

        @property
        def configure(self, parameters:dict):
            for key in parameters:
                if key == 'range_mv':
                    self.range_mv = parameters[key]
                if key == 'channel':
                    self.channel = parameters[key]
                if key == 'averages':
                    self.averages = parameters[key]
                if key == 'capture_period_ns':
                    self.capture_period_ns = parameters[key]
                if key == 'signal_frequency_MHz':
                    self.signal_frequency_MHz = parameters[key]
                    self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
                    self.captures = int(self.cycles*self.signal_period_ns/self.capture_period_ns)
                if key == 'cycles':
                    self.cycles = parameters[key]
                    self.signal_period_ns = 1 / self.signal_frequency_MHz * 1000
                    self.captures = int(self.cycles * self.signal_period_ns / self.capture_period_ns)
                if key == 'delay_cycles':
                    self.delay_cycles = parameters[key]

        @property
        def scan_speed(self):
            return self._scan_speed

        @property
        def calibrate(self):
            print("calibration getter called")
            return (
                self._x_calibrate,
                self._y_calibrate,
                self._z_calibrate,
                self._r_calibrate,
            )

        # Hardware interfacing functions
        def toggle_connection(self):
            if self.connected():
                return self.connect()
            else:
                return self.disconnect()

        @abstractmethod
        def connect(self):
            self.connected = True
            #return self.connected()

        @abstractmethod
        def disconnect(self):
            self.connected = False

        @abstractmethod
        def connected(self):
            return self.Motors.connected

        @abstractmethod
        def jog(self, axis=None, direction=None, feedback=True):
            # Dummy code, replace when developing a hardware interface
            self.jogging = True

            if axis == 'R' and direction > 0:
                self.dummy_command_signal.emit('Begin Motion R+')
            elif axis == 'R' and direction < 0:
                self.dummy_command_signal.emit('Begin Motion R-')
            elif axis == 'X' and direction > 0:
                self.dummy_command_signal.emit('Begin Motion X+')
            elif axis == 'X' and direction < 0:
                self.dummy_command_signal.emit('Begin Motion X-')
            else:
                self.jogging = False

        @abstractmethod
        def stop_motion(self):
            self.jogging = False
            self.dummy_command_signal.emit("Stop Motion")

        @abstractmethod
        def set_origin(self, origin_mm: list):
            origin_steps = list()

            for i in range(len(self.ax_letters)):
                origin_steps[i] = -1 * origin_mm[i] * self.calibrations[i] + float(self.coords[i])
                if self.reverse_ray[i]:
                    origin_steps[i] = origin_steps * -1

                self.dummy_command_signal.emit(f'Set {self.ax_letters[i]} {origin_steps}')

            self.get_position()

        @abstractmethod
        def set_origin_here(self):
            for i in range(len(self.ax_letters)):
                self.dummy_command_signal.emit(f"Set {self.ax_letters[i]} 0")

        @abstractmethod
        def set_origin_here_1d(self, axis):
            self.dummy_command_signal.emit(f"Set {axis} {0}")

        @abstractmethod
        def go_home(self):
            zeroes = list()
            for i in range(len(self.ax_letters)):
                zeroes.append(0)

            self.go_to_position(self.ax_letters, zeroes)

        # Tells one axis what coordinate to travel to
        # Axis must be 'x' , 'y' , 'z' , or 'r'

        def go_to_position(self, axes:list, coords:list):
            if not len(axes) == len(coords):
                log_msg(self, root_logger,level='error',message="Axes length does not match coordinates length")
                return

            for i in range(len(coords)):
                if isinstance(coords[i], str):
                    try:
                        coords[i] = float(coords[i])
                    except TypeError:
                        log_msg(self, root_logger,level='Error', message='Invalid coordinate string in go_to_position')
                        return

            coord_strings = list()
            ax_strings = list()

            for i in range(len(coords)):
                ax_index = self.ax_letters.index(axes[i])

                #Zero coordinates that are too close to zero (they have caused bugs)
                coords[i] = bound(coords[i])
                #Reverse the direction if the config says to
                if self.reverse_ray[ax_index]:
                    coords[i] = -1 * coords[i]

                self.dummy_command_signal.emit(f'Scan Speed {(self.calibrate_ray[ax_index] * self.scan_speed)}')
                coord_strings.append(str(coords[i] * self.calibrate_ray[ax_index]))
                ax_strings.append(axes[i].upper())

            self.scanning = True


            self.dummy_command_signal.emit(f'GO {",".join(coord_strings)}')

        @abstractmethod
        def capture(self):
            start_time = self.delay_cycles*self.signal_period_ns
            end_time = start_time + self.captures * self.capture_period_ns
            time = np.linspace(start_time, end_time, self.captures)

            signal = np.sin(time)

            noise = np.random.rand(self.captures)*.1

            voltage = signal + noise

            return time, voltage

        def exec_command(self, command):
            command = command.upper()
            cmd_ray = command.split(' ')

            if cmd_ray[0] == 'SCOPE':
                cmd_ray.pop(0)
                command = command[6:]

            if command == 'Disconnect'.upper():
                self.disconnect()

        def clean_up(self):
            if self.connected():
                self.handle.GCommand("ST")
                self.handle.GCommand("MO")
                self.handle.GClose()

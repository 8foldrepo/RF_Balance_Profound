from abc import ABC, abstractmethod

from PyQt5.QtCore import *
import time as t
from Utilities.useful_methods import bound
import gclib
from Hardware.dummy_motors import  DummyMotors

import logging
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.useful_methods import create_coord_rays

log_formatter = logging.Formatter(LOGGER_FORMAT)

motor_logger = logging.getLogger('motor_log')

file_handler = logging.FileHandler("./logs/motor.log", mode='w')
file_handler.setFormatter(log_formatter)
motor_logger.addHandler(file_handler)

motor_logger.setLevel(logging.INFO)

root_logger = logging.getLogger(ROOT_LOGGER_NAME)

#from Hardware.abstract_motor_controller import  AbstractMotorController

                            #Replace these parentheses with (AbstractMotorController) when inheriting this class
class AbstractMotorController(QObject):
        """
        An abstract class that serves as a base for classes that interface with motor controllers.
        Used on its own, this class will create a DummyMotors object, which runs in a separate thread and simulates a
        generic motor controller. Remove the DummyMotors object and all uses of the dummy_command_signal when inheriting.

        Signals:
            logger_signal(str)   : communicates feedback (errors, messages) to the feedback widget

            x_pos_signal(str)    : communicates x position with scan area
            y_pos_signal(str)    : communicates y position with scan area
            z_pos_signal(str)    : communicates z position with scan area

        Slots:
            none

        Attributes:
            none

        Properties:
            _jog_speed : used in the jog method, controls how fast the gantry jogs
            _scan_speed : used in scanning, or any PA command

            each property's setter method raises an error if the type is not an int

        Methods:
            toggle_connection()
                attempts to connect to the controller if not connected
                disconnects from the controller if connected

            connected()
                checks connection to controller, return true if yes, false if no

            jog(axis, direction)
                sends jog command to controller given an axis and direction (+/-)
                uses jog speed property getter

            begin_motion(axis)
                sends begin motion command to controller given an axis
                for multiple axes, use 'AB', 'ABC' etc

            stop_motion()
                sends stop command to controller
                motors remain on after command is sent

            set_origin()
                sets coordinate system of controller to 0,0,0
                good for defining the center of a scan

            go_home()
                tells gantry to go to position 0,0,0

            mm_to_steps()
                uses calibrate property to convert a number of mm to a number of steps

            is_moving()
                poll controller, if the controller is moving return true
                else return false

            get_position()
                emits x,y,z position signals with current controller position

            clean_up()
                stop motors, and disconnect form the controller if connected
        """

        # Dummy code, replace when developing a hardware interface
        dummy_command_signal = pyqtSignal(str)

        # For accessing parameters in config file
        device_key = 'Dummy_Oscilloscope'

        def __init__(self, config: dict):
            super().__init__()

            self.config = config

            #For tracking latest known coordinates in steps
            self.coords = list()
            for i in range(self.num_axes):
                self.coords.append(0)

            #Tracks whther or not the gantry is going to a position
            self.scanning = False

            self.fields_setup()

        def fields_setup(self):
            self.range = self.config[self.device_key]['range']
            self.channel = self.config[self.device_key]['channel']
            self.averages = self.config[self.device_key]['averages']
            self.capture_period_ns = self.config[self.device_key]['capture_period_ns']
            self.signal_frequency_MHz = 4.2
            self.signal_period_ns = 1/self.signal_frequency_MHz * 1000
            self.cycles = self.config[self.device_key]['cycles']
            self.captures = int(self.cycles*self.signal_period_ns/self.capture_period_ns)

        @property
        def configure(self, parameters:dict):
            for key in parameters:
                if key == 'range':
                    self.range = parameters[key]
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
                self.log_msg(level='error',message="Axes length does not match coordinates length")
                return

            for i in range(len(coords)):
                if isinstance(coords[i], str):
                    try:
                        coords[i] = float(coords[i])
                    except TypeError:
                        self.log_msg(level='Error', message='Invalid coordinate string in go_to_position')
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
            pass

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


        def log_msg(self, level: str, message: str) -> None:
            """
            Convenience function to log messages in a compact way with useful info.

                Parameters:
                    level (str): A string indicating the logger level, can be either
                    'info', 'debug' or 'error'
                    message (str): A string that contains the message to be logged

                Returns:
                    None
            """
            thread_name = QThread.currentThread().objectName()
            log_entry = f"[{type(self).__name__}] [{thread_name}] : {message}"
            if level == 'debug':
                root_logger.debug(log_entry)
                motor_logger.debug(log_entry)
            elif level == 'error':
                root_logger.error(log_entry)
                motor_logger.error(log_entry)
            elif level == 'warning':
                root_logger.warning(log_entry)
                motor_logger.warning(log_entry)
            else:
                root_logger.info(log_entry)
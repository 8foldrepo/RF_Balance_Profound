from abc import ABC, abstractmethod

from PyQt5.QtCore import *
import time as t
from Utilities.useful_methods import bound
import gclib
from Hardware.dummy_motors import DummyMotors

import logging
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT

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

        # SIGNALS

        position_signal = pyqtSignal(str)  # Send position into position widget
        logger_signal = pyqtSignal(str)  # Send other information to the logger

        x_pos_signal = pyqtSignal(float)
        y_pos_signal = pyqtSignal(float)
        z_pos_signal = pyqtSignal(float)
        r_pos_signal = pyqtSignal(float)

        # Dummy code, replace when developing a hardware interface
        dummy_command_signal = pyqtSignal(str)

        # For accessing parameters in config file
        device_key = 'Dummy_Motors'

        def __init__(self, config: dict):
            super().__init__()

            self.config = config

            #For tracking latest known coordinates in steps
            self.x = 0
            self.y = 0
            self.z = 0
            self.r = 0

            #Tracks whther or not the gantry is going to a position
            self.scanning = False

            self.fields_setup()

        def fields_setup(self):
            self.reverseX = self.config[self.device_key]['reverse_x']
            self.reverseY = self.config[self.device_key]['reverse_y']
            self.reverseZ = self.config[self.device_key]['reverse_z']
            self.reverseR = self.config[self.device_key]['reverse_r']

            self._jog_speed = self.config[self.device_key]['jog_speed']
            self._scan_speed = self.config[self.device_key]['scan_speed']
            self._x_calibrate = self.config[self.device_key]['x_calibrate']
            self._y_calibrate = self.config[self.device_key]['y_calibrate']
            self._z_calibrate = self.config[self.device_key]['z_calibrate']
            self._r_calibrate = self.config[self.device_key]['r_calibrate']

            # Dummy code, replace when developing a hardware interface
            self.Motors = DummyMotors(parent=None)
            self.dummy_command_signal.connect(self.Motors.command_received)
            self.Motors.start(priority=4)

        @property
        def jog_speed(self):
            return self._jog_speed

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

        # Setters for each class property
        @jog_speed.setter
        def jog_speed(self, value):
            if type(value) is int:
                print(f"jog speed set: {value}")
                self._jog_speed = value

                self.dummy_command_signal.emit("Jog Speed")
            else:
                print("failed to set jog speed")
                raise Exception

        @scan_speed.setter
        def scan_speed(self, value):
            if type(value) is int:
                self._scan_speed = value
                print(f"scan speed set: {value}")
            else:
                print("failed to set scan speed")
                raise Exception

        @calibrate.setter
        def calibrate(self, value):
            print("calibration setter called")

            if type(value) is int:
                print(f"scan speed set: {value}")
                self._calibrate = value
                self.logger_signal.emit(f"calibration factor set: {value}")
            else:
                self.logger_signal.emit("failed to set calibration factor")
                raise Exception

        # Hardware interfacing functions
        def toggle_connection(self):
            if self.connected():
                return self.connect()
            else:
                return self.disconnect()

        @abstractmethod
        def connect(self):
            self.dummy_command_signal.emit("Connect")
            #return self.connected()

        @abstractmethod
        def disconnect(self):
            self.dummy_command_signal.emit("Disconnect")
            return not self.connected()

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
        def set_origin(self, x=0, y=0, z=0, r=0):
            xHome = -1 * x * self._x_calibrate + float(self.x)
            yHome = -1 * y * self._y_calibrate + float(self.y)
            zHome = -1 * z * self._z_calibrate + float(self.z)
            rHome = -1 * r * self._r_calibrate + float(self.r)

            if self.reverseX:
                xHome = xHome * -1
            if self.reverseY:
                yHome = yHome * -1
            if self.reverseZ:
                zHome = zHome * -1
            if self.reverseR:
                rHome = rHome * -1

            self.dummy_command_signal.emit(f"Set X {xHome}")
            self.dummy_command_signal.emit(f"Set Y {yHome}")
            self.dummy_command_signal.emit(f"Set Z {zHome}")
            self.dummy_command_signal.emit(f"Set R {rHome}")

            self.get_position()

        @abstractmethod
        def set_origin_here(self):
            self.dummy_command_signal.emit(f"Set X {0}")
            self.dummy_command_signal.emit(f"Set Y {0}")
            self.dummy_command_signal.emit(f"Set Z {0}")
            self.dummy_command_signal.emit(f"Set R {0}")

        @abstractmethod
        def set_origin_here_1d(self, axis):
            self.dummy_command_signal.emit(f"Set {axis} {0}")

        @abstractmethod
        def go_home(self):
            self.go_to_position(0, 0, 0)

        # Tells one axis what coordinate to travel to
        # Axis must be 'x' , 'y' , 'z' , or 'r'

        def go_to_position(self, axes:list, coords:list):
            if not len(axes) == len(coords):
                self.log_msg(level='error',message="Invalid coordinates")

            self.handle.GCommand("ST")
            self.handle.GCommand("SH ABCD")

            x_coord_str = ''
            y_coord_str = ''
            z_coord_str = ''
            r_coord_str = ''
            x_ax_str = ''
            y_ax_str = ''
            z_ax_str = ''
            r_ax_str = ''

            for i in range(len(coords)):
                coords[i] = bound(coords[i])

                #Reverse directions when the config file says to
                if self.config[self.device_key][f'reverse_{axes[i].lower()}']:
                    coords[i] = -1 * coords[i]

                if axes[i].upper() == 'X':
                    self.handle.GCommand("SP %d" % (self._x_calibrate * self.scan_speed))
                    x_coord_str = coords[i]*self.config[self.device_key]['x_calibrate']
                    x_ax_str = 'A'
                elif axes[i].lower() == 'Y':
                    self.handle.GCommand("SP ,%d" % (self._y_calibrate * self.scan_speed))
                    y_coord_str = coords[i] * self.config[self.device_key]['y_calibrate']
                    y_ax_str = 'B'
                elif axes[i].lower() == 'Z':
                    self.handle.GCommand("SP ,,%d" % (self._z_calibrate * self.scan_speed))
                    z_coord_str = coords[i] * self.config[self.device_key]['z_calibrate']
                    z_ax_str = 'C'
                elif axes[i].lower() == 'R':
                    self.handle.GCommand("SP ,,,%d" % (self._r_calibrate * self.scan_speed))
                    r_coord_str = coords[i] * self.config[self.device_key]['r_calibrate']
                    r_ax_str = 'D'

            self.scanning = True

            if sum(coords) > 1000:
                self.logger_signal.emit(
                    "Coordinates entered for the motors are too large. Double check in the code that they are given in mm"
                )
                return

            self.dummy_command_signal.emit(f'PA {x_coord_str},{y_coord_str},{z_coord_str},{r_coord_str}')
            self.dummy_command_signal.emit(f"BG {x_ax_str}{y_ax_str}{z_ax_str}{r_ax_str}")
            self.get_position()

            while self.is_moving():
                if not self.scanning:
                    self.stop_motion()
                    self.get_position()
                    return

                t.sleep(0.05)
                self.get_position()
            # self.handle.GCommand('ST')
            self.dummy_command_signal.emit("MO")

        @abstractmethod
        def is_moving(self):
            return not (self.Motors.dR == 0 and self.Motors.dX == 0)

        @abstractmethod
        def get_position(self):
            self.x = self.Motors.x
            self.r = self.Motors.r

            self.x_pos_signal.emit(self.x)
            self.y_pos_signal.emit(self.y)
            self.z_pos_signal.emit(self.z)
            self.r_pos_signal.emit(self.r)

        def center_r(self, degreesMax):
            try:
                rmin = -1 * degreesMax
                rmax = degreesMax

                self.go_to_position_1d('r', rmin)

                self.get_position()
                rMinLimit = self.r / self.config["galil_r_degreesConversion"]

                self.go_to_position_1d('r', rmax)
                rMaxLimit = self.r / self.config["galil_r_degreesConversion"]
                rCenter = (rMaxLimit + rMinLimit) / 2

                self.go_to_position_1d('r', rCenter)
                self.set_origin_here_1d('r')

                self.get_position()
            except gclib.GclibError as e:
                stop_code = self.tell_error()
                if stop_code is not None:
                    print(f"error in hardware_galil.center_r: {stop_code}")
                else:
                    print(f"error in hardware_galil.center_r: {e}")

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
                motor_logger.info(log_entry)
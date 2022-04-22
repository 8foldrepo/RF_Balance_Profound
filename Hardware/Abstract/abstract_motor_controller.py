from abc import abstractmethod

from PyQt5.QtCore import *
from Utilities.useful_methods import bound
from Hardware.Simulators.dummy_motors import  DummyMotors
from Utilities.useful_methods import create_coord_rays, create_comma_string
import time as t
from Hardware.Abstract.abstract_device import AbstractDevice

class AbstractMotorController(AbstractDevice):
        """
        A class providing a crude imitation of the functionality of motor controller hardware classes.
        """

        #Signals
        x_pos_mm_signal = pyqtSignal(float)
        y_pos_signal = pyqtSignal(float)
        r_pos_mm_signal = pyqtSignal(float)
        z_pos_signal = pyqtSignal(float)

        moving_signal = pyqtSignal(bool)
        connected_signal = pyqtSignal(bool)
        ready_signal = pyqtSignal()

        num_axes = 2
        ax_letters = ['X', 'R']
        increment_ray: object = [1,1]
        speeds_ray = [1,1]

        coords_mm = list()
        home_coords = list()

        for i in range(num_axes):
            coords_mm.append(0)


        def __init__(self, config: dict, device_key = 'VIX_Motors', parent = None):
            super().__init__(parent = parent, config=config, device_key=device_key)
            #For tracking latest known coordinates in steps
            self.coords_mm = list()
            for i in range(self.num_axes):
                self.coords_mm.append(0)

            #Tracks whther or not the gantry is going to a position
            self.scanning = False
            self.moving = False
            self.fields_setup()

        def go_home_1d(self, axis):
            if axis == 'R':
                self.coords_mm[1] = -90
            elif axis == 'X':
                self.coords_mm[0] = 273
            self.get_position()

        def fields_setup(self):
            self.ax_letters = self.config[self.device_key]['axes']
            num_axes = len(self.ax_letters)
            for i in range(num_axes):
                self.coords_mm.append(0)
            self.reverse_ray = self.config[self.device_key]['reverse_ray']
            self.movement_mode = self.config[self.device_key]['movement_mode']
            self.ax_letters = self.config[self.device_key]['axes']
            self.calibrate_ray_steps_per = self.config[self.device_key]['calibrate_ray']
            self.speeds_ray = self.config[self.device_key]['speeds_ray']
            self.increment_ray = self.config[self.device_key]['increment_ray']
            self.timeout_s = self.config[self.device_key]['timeout_s']
            self.time_limit_s = self.config[self.device_key]['time_limit_s']
            self.on_by_default = self.config[self.device_key]['on_by_default']
            self.port = self.config[self.device_key]['port']

        '''Setup all axes according to a dictionary of settings. R is configured according to rotational settings.'''
        @pyqtSlot(dict)
        def setup(self, settings):
            self.increment_ray[0] = settings['steps_per_mm']
            self.increment_ray[0] = settings['lin_incr']
            self.speeds_ray = settings["speed_ray"]
            self.cal_ray_steps_per[0] = settings['steps_per_deg']
            self.cal_ray_steps_per[1] = settings['ang_incr']

            for i in range(len(self.ax_letters)):
                self.setup_1d(axis=self.ax_letters[i], settings=settings)
            self.get_position()

        '''Setup an axis according to a dictionary of settings. R is configured according to rotational settings.'''
        def setup_1d(self,axis, settings):
            axis_index = self.ax_letters.index(axis)
            axis_number = axis_index + 1
            self.movement_mode = settings['movement_mode']

            if settings['movement_mode'] == 'Incremental':
                self.command(f'{axis_number}MI')
            elif settings['movement_mode'] == 'Continuous':
                self.command(f'{axis_number}MC')
            elif settings['movement_mode'] == 'Distance':
                self.command(f'{axis_number}MA')

            steps_per_s = self.cal_ray_steps_per[axis_index] * self.speeds_ray[axis_index]
            self.command(f'{axis_number}V{steps_per_s}')
            self.command(f'{axis_number}D{self.increment_ray[axis_index]}')

        def command(self, command):
            pass

        @property
        def jog_speed(self):
            return self._jog_speed

        @property
        def scan_speed(self):
            return self._scan_speed

        @property
        def calibrate(self):
            return (
                self._x_calibrate,
                self._y_calibrate,
                self._z_calibrate,
                self._r_calibrate,
            )

        def set_jog_speed(self, axis, value):
            if type(value) is float:
                self._jog_speed = value
                self.dummy_command_signal.emit(f'Jog Speed {axis} {self.scan_speed}')
                self.log(f"scan speed set: {value}")
            else:
                self.log(level='error',message="failed to set jog speed")

        def set_scan_speed(self, axis, value):
            if type(value) is float:
                self._scan_speed = value
                self.dummy_command_signal.emit(f'Scan Speed {axis} {self.scan_speed}')
                self.log(f"scan speed set: {value}")
            else:
                self.log(level='error',message="failed to set scan speed")

        # Hardware interfacing functions
        def toggle_connection(self):
            if self.connected():
                return self.connect_hardware()
            else:
                return self.disconnect_hardware()

        @abstractmethod
        def connect_hardware(self):
            self.connected = True
            self.connected_signal.emit(self.connected)

        @abstractmethod
        def disconnect_hardware(self):
            self.connected = False
            self.connected_signal.emit(self.connected)

        @abstractmethod
        def is_connected(self):
            return self.connected

        @abstractmethod
        def begin_motion(self, axis=None, direction=None, feedback=True):
            axis_index = self.ax_letters.index(axis)
            current_coordinate_mm = self.coords_mm[axis_index]

            if direction < 0:
                go_to_coord_mm = int((current_coordinate_mm - abs(self.increment_ray[axis_index])))
            else:
                go_to_coord_mm = int((current_coordinate_mm + abs(self.increment_ray[axis_index])))

            self.go_to_position([axis], [go_to_coord_mm])

        @abstractmethod
        def stop_motion(self):
            self.moving_signal.emit(False)
            self.jogging = False
            self.dummy_command_signal.emit("Stop Motion")

        @abstractmethod
        def set_origin(self, origin_mm: list):
            origin_steps = list()

            for i in range(len(self.ax_letters)):
                origin_steps[i] = -1 * origin_mm[i] * self.calibrations[i] + float(self.coords_mm[i])
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
            self.coords_mm[1] = -90
            self.coords_mm[0] = 273
            self.get_position()

        @pyqtSlot(list, list)
        def go_to_position(self, axes: list, coords_mm: list) -> bool:
            for i in range(len(axes)):
                self.coords_mm[self.ax_letters.index(axes[i])] = coords_mm[i]

            t.sleep(.2)
            self.get_position()

            self.ready_signal.emit()
            return True

        @abstractmethod
        def is_moving(self):
            return self.moving

        @abstractmethod
        def get_position(self, mutex_locked = False):
            self.x_pos_mm_signal.emit(self.coords_mm[self.ax_letters.index('X')])
            self.r_pos_mm_signal.emit(self.coords_mm[self.ax_letters.index('R')])

        def exec_command(self, command):
            command = command.upper()
            cmd_ray = command.split(' ')

            if cmd_ray[0] == 'MOTOR':
                cmd_ray.pop(0)
                command = command[6:]

            if command == 'Disconnect'.upper():
                self.disconnect()
            elif command == 'Connect'.upper():
                self.connect()
            elif cmd_ray[0] == 'JOG' and cmd_ray[1] == 'SPEED':
                self.set_jog_speed(cmd_ray[2], float(cmd_ray[3]))
            elif cmd_ray[0] == 'SCAN' and cmd_ray[1] == 'SPEED':
                self.set_scan_speed(axis=cmd_ray[2], value=float(cmd_ray[3]))
            elif command == 'Stop Motion'.upper():
                self.stop_motion()
            elif command == 'Get Position'.upper():
                self.get_position()
            elif cmd_ray[0] == 'GO':
                axes, coords = create_coord_rays(cmd_ray[1], self.ax_letters)
                self.go_to_position(axes=axes, coords_mm=coords)
            elif cmd_ray[0] == 'Origin'.upper():
                if cmd_ray[1] == 'Here'.upper():
                    self.set_origin_here()

        def wrap_up(self):
            self.disconnect_hardware()
            self.dummy_command_signal.emit("CLOSE")
from abc import abstractmethod

from PyQt5.QtCore import *
from Utilities.useful_methods import bound
from Hardware.Abstract.abstract_motor_controller import AbstractMotorController
from Utilities.useful_methods import create_coord_rays, create_comma_string
import serial
import time as t
from Hardware.Abstract.abstract_device import AbstractDevice

class VIX_Motor_Controller(AbstractMotorController):
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

        #Signals
        x_pos_mm_signal = pyqtSignal(float)
        y_pos_signal = pyqtSignal(float)
        r_pos_mm_signal = pyqtSignal(float)
        z_pos_signal = pyqtSignal(float)

        moving_signal = pyqtSignal(bool)

        connected_signal = pyqtSignal(bool)

        num_axes = 2
        ax_letters = ['X', 'R']

        coords = list()
        home_coords = list()

        for i in range(num_axes):
            coords.append(0)

        # Dummy code, replace when developing a hardware interface
        dummy_command_signal = pyqtSignal(str)

        def __init__(self, config: dict, device_key = 'VIX_Motors', parent = None):
            super().__init__(parent = parent, config=config, device_key=device_key)
            #For tracking latest known coordinates in steps
            self.coords = list()
            for i in range(self.num_axes):
                self.coords.append(0)

            #Tracks whther or not the gantry is going to a position
            self.scanning = False

            self.fields_setup()

        def fields_setup(self):
            self.reverse_ray = self.config[self.device_key]['reverse_ray']
            self.ax_letters = self.config[self.device_key]['axes']
            self.calibrate_ray = self.config[self.device_key]['calibrate_ray']

            self._jog_speed = self.config[self.device_key]['jog_speed']
            self._scan_speed = self.config[self.device_key]['scan_speed']

            self.timeout_s = self.config[self.device_key]['timeout_s']
            self.on_by_default = self.config[self.device_key]['on_by_default']
            self.port = self.config[self.device_key]['port']

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

        def connect_hardware(self):
            try:
                self.ser = serial.Serial(
                    port=self.port,  # May vary depending on computer
                    baudrate=19200,
                    timeout=self.timeout_s,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                )
                self.connected = True
            except serial.serialutil.SerialException:
                self.connected = False
                self.log(level='error', message=
                f"{self.device_key} not connected. Check that it is plugged in and look at Device manager "
                "to determine which COM port to use. It is currently hard coded")

            #TODO: remove this when limits are added self.disable_limits()
            self.setup_for_jogging()
            self.connected_signal.emit(self.connected)

        @abstractmethod
        def disconnect_hardware(self):
            try:
                self.ser.close()
            except:
                pass
            self.connected = False
            self.connected_signal.emit(self.connected)

        @abstractmethod
        def connected(self):
            return self.Motors.connected

        @abstractmethod
        def getBaud(self):
            if self.ser is None:
                self.log(level='error', message=f'{self.device_key} not connected')
                return
            self.command("1R(BR)")
            response = self.get_response()
            print(response)
            if str(b'19200') in str(response):
                return 19200
            elif str(b'9600') in str(response):
                return 9600
            else:
                return -1

        '''Attempt to send command until it is faithfully echoed by the controller'''
        def command(self, command):
            starttime = t.time()
            while t.time() - starttime < self.timeout_s:
                starttime = t.time()
                bites = command.encode('utf-8')
                output = bites+b'\r\n'
                self.log(f'Output:{output}')
                self.ser.write(output)
                echo = self.ser.readline().strip(b'\r\n')
                self.log(f'Echo:{echo}')
                if echo == bites:
                    t.sleep(.2)
                    return True
            self.log(level='error', message=f'command not sent successfully')
            return False

        '''Print every line of the controller's output until timeout is reached'''
        def print_response(self):
            starttime = t.time()
            while t.time() - starttime < self.timeout_s:
                starttime = t.time()
                y = self.ser.readline().strip(b'\r\n')
                self.log(f'Response:{y}')
            self.log(level='error', message=f'{self.device_key} timed out')

        '''Return the next non-empty line of the controller's response over serial. Assumes echo has already been read'''
        def get_response(self):
            starttime = t.time()
            while t.time() - starttime < self.timeout_s:
                y = self.ser.readline().strip(b'\r\n')
                self.log(f'Response:{y}')
                if y != b'':
                    return y
            self.log(level='error', message=f'{self.device_key} timed out')

        def motors_on(self):
            for i in range(len(self.ax_letters)):
                self.setup_for_jogging_1d(axis=self.ax_letters[i])

        def motor_on(self):
            axis_number = self.ax_letters.index(axis) + 1
            self.command(f'{axis_number}ON')

        def setup_for_jogging(self):
            for i in range(len(self.ax_letters)):
                self.setup_for_jogging_1d(axis=self.ax_letters[i])

        def setup_for_jogging_1d(self, axis):
            axis_number = self.ax_letters.index(axis) + 1

            self.command(f'{axis_number}V5')
            self.command(f'{axis_number}MC')

        def jog(self, axis=None, direction=None, feedback=True):
            axis_number = self.ax_letters.index(axis) + 1
            if direction < 0:
                self.command('1D-1')
            else:
                self.command('1D1')
            self.command(f'{axis_number}G')
            self.moving_signal.emit(True)
            self.jogging = True

        def position_relative(self, axis=None, direction=None):

            self.command(f'{axis_number}MA')

            axis_number = self.ax_letters.index(axis) + 1
            if direction < 0:
                self.command('1D-1')
            else:
                self.command('1D1')
            self.command(f'{axis_number}G')
            self.moving_signal.emit(True)
            self.jogging = True

        @pyqtSlot(int)
        def set_increment(self, increment):
            for i in range(len(self.ax_letters)):
                self.set_increment_1d(axis = self.ax_letters[i], increment=increment)

        def set_increment_1d(self, axis, increment):
            axis_number = self.ax_letters.index(axis) + 1
            self.command(f'{axis_number}D{increment}')

        def stop_motion(self):
            for i in range(len(self.ax_letters)):
                self.stop_motion_1d(axis = self.ax_letters[i])

            self.moving_signal.emit(False)
            self.jogging = False


        def stop_motion_1d(self, axis):
            axis_number = self.ax_letters.index(axis) + 1
            self.command(f'{axis_number}S')

        def set_origin(self, origin_mm: list):
            origin_steps = list()

            for i in range(len(self.ax_letters)):
                origin_steps[i] = -1 * origin_mm[i] * self.calibrations[i] + float(self.coords[i])
                if self.reverse_ray[i]:
                    origin_steps[i] = origin_steps * -1

                self.dummy_command_signal.emit(f'Set {self.ax_letters[i]} {origin_steps}')

            self.get_position()

        def set_origin_here(self):
            for i in range(len(self.ax_letters)):
                self.dummy_command_signal.emit(f"Set {self.ax_letters[i]} 0")

        def disable_limits(self):
            self.command("1LIMITS(3,0,0)")
            self.command("2LIMITS(3,0,0)")

        @abstractmethod
        def set_origin_here_1d(self, axis):
            axis_number = self.ax_letters.index(axis) + 1
            self.command(f'{axis_number}W(PA,0)')

        @abstractmethod
        def go_home(self):
            self.command("1ON")
            self.command("1GH")

        # Tells one axis what coordinate to travel to
        # Axis must be 'x' , 'y' , 'z' , or 'r'
        def go_to_position(self, axes:list, coords:list):
            if not len(axes) == len(coords):
                self.log(level='error',message="Axes length does not match coordinates length")
                return

            for i in range(len(coords)):
                if isinstance(coords[i], str):
                    try:
                        coords[i] = float(coords[i])
                    except TypeError:
                        self.log(level='Error', message='Invalid coordinate string in go_to_position')
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

                coord_strings.append(str(coords[i] * self.calibrate_ray[ax_index]))
                ax_strings.append(axes[i].upper())

            self.scanning = True

            comma_string = create_comma_string(axes=axes,coords=coords,ax_letters=self.ax_letters)

            self.dummy_command_signal.emit(f'GO {comma_string}')

        @abstractmethod
        def is_moving(self):
            return not (self.Motors.dR == 0 and self.Motors.dX == 0)

        @abstractmethod
        def get_position(self):
            self.coords = self.Motors.coords

            self.x_pos_mm_signal.emit(self.coords[self.ax_letters.index('X')])
            self.r_pos_mm_signal.emit(self.coords[self.ax_letters.index('R')])

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
                self.set_jog_speed(cmd_ray[2],float(cmd_ray[3]))
            elif cmd_ray[0] == 'SCAN' and cmd_ray[1] == 'SPEED':
                self.set_scan_speed(axis=cmd_ray[2],value=float(cmd_ray[3]))
            elif command == 'Begin Motion X+'.upper():
                self.jog('X', 1)
            elif command == 'Begin Motion X-'.upper():
                self.jog('X', -1)
            elif command == 'Begin Motion R+'.upper():
                self.jog('R', 1)
            elif command == 'Begin Motion R-'.upper():
                self.jog('R', -1)
            elif command == 'Stop Motion'.upper():
                self.stop_motion()
            elif command == 'Get Position'.upper():
                self.get_position()
            elif cmd_ray[0] == 'GO':
                axes, coords = create_coord_rays(cmd_ray[1], self.ax_letters)
                self.go_to_position(axes=axes, coords=coords)
            elif cmd_ray[0] == 'Origin'.upper():
                if cmd_ray[1] == 'Here'.upper():
                    self.set_origin_here()

        def wrap_up(self):
            self.disconnect_hardware()
            self.dummy_command_signal.emit("CLOSE")

if __name__ == '__main__':
    motors = VIX_Motor_Controller(config=None)
    motors.connect_hardware()
    motors.disable_limits()
    motors.set_increment(4000)
    motors.jog(axis='X', direction=1)
    motors.jog(axis='R', direction=-1)
    t.sleep(1)
    motors.stop_motion()

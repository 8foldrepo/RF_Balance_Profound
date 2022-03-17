from abc import abstractmethod
from PyQt5.QtCore import *
from Utilities.useful_methods import bound
from Hardware.Simulators.dummy_motors import  DummyMotors
from Utilities.useful_methods import create_coord_rays, create_comma_string
from Hardware.Abstract.abstract_motor_controller import AbstractMotorController

class AbstractMotorController(AbstractMotorController):
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
        x_pos_signal = pyqtSignal(float)
        y_pos_signal = pyqtSignal(float)
        r_pos_signal = pyqtSignal(float)
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

        def __init__(self, config: dict, device_key = 'Dummy_Motors', parent = None):
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

            # Dummy code, replace when developing a hardware interface
            self.Motors = DummyMotors(parent=None)
            self.Motors.set_config(self.config)
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
            self.Motors.connected = True
            self.connected_signal.emit(self.connected())

            port_list = self.handle.GAddresses()
            print("pre-connection handle status: {0}".format(self.handle))
            _bConnected = False

            for port in port_list.keys():
                print("port: {0} , handle status: {1}".format(port, self.handle))
                try:
                    self.handle.GOpen("192.168.42.100 --direct -s ALL")
                    print(self.handle.GInfo())
                    _bConnected = True
                except gclib.GclibError as e:
                    print("Something went wrong: {0}".format(e))

                if _bConnected:
                    break
            print("post connection handle status: {0}".format(self.handle))
            self.handle.GCommand("GR 0,0,0,0")
            self.handle.GCommand("GM 0,0,0,0")

            # self.handle.GCommand('PF 7')
            self.handle.GCommand("ST")
            self.handle.GCommand(
                f"SP {self._x_calibrate}, {self._y_calibrate}, {self._z_calibrate}, {self._r_calibrate}"
            )  # yaml file value

            self.handle.GCommand("AC 1000000,1000000,1000000,1000000")
            self.handle.GCommand("DC 1000000,1000000,1000000,1000000")
            # self.set_origin()
            self.get_position()

            self.connected_signal.emit(True)

        @abstractmethod
        def disconnect_hardware(self):
            self.handle.GCommand("ST")
            self.handle.GCommand("MO")
            self.handle.GClose()
            print("Connection terminated")
            self.connected_signal.emit(False)

            self.Motors.connected = False
            self.connected_signal.emit(self.connected())
            self.dummy_command_signal.emit("CLOSE")

        @abstractmethod
        def connected(self):
            return self.Motors.connected

        @abstractmethod
        def jog(self, axis=None, direction=None, feedback=True):
            # Dummy code, replace when developing a hardware interface
            self.jogging = True
            self.moving_signal.emit(True)
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
            self.moving_signal.emit(False)
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

            self.x_pos_signal.emit(self.coords[self.ax_letters.index('X')])
            self.r_pos_signal.emit(self.coords[self.ax_letters.index('R')])

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
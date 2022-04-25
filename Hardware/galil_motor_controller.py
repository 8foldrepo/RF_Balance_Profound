#Used on its own, this class will act as a simulated motor controller
from Utilities.load_config import load_configuration
import time as t
from Utilities.useful_methods import bound
import gclib
from PyQt5 import QtWidgets
from Hardware.Simulated.simulated_motor_controller import SimulatedMotorController


class Galil(SimulatedMotorController):
        """
        A hardware interface class for communicating with the Galil_DMC_4143

        Signals:
            logger_signal(str)   : communicates feedback (errors, messages) to the feedback widget

            x_pos_signal(str)    : communicates x position with scan area
            y_pos_signal(str)    : communicates y position with scan area
            z_pos_signal(str)    : communicates z position with scan area

        Slots:
            none

        Attributes:
            handle : gclib wrapper class, sends and receives information from DMC 4143

        Properties:
            _jog_speed : used in the jog method, controls how fast the gantry jogs
            _scan_speed : used in scanning, or any PA command
            _calibrate : steps to mm conversion factor

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

        def __init__(self, config=None, device_key = 'Galil', parent = None):
            super().__init__(config=config, device_key=device_key, parent=None)

            self.x = 0  # The galil may not actually start at the origin, but these will be updated when get_position is called
            self.y = 0
            self.z = 0
            self.r = 0
            self.app = QtWidgets.QApplication.instance()
            self.paused = False
            self.scanning = False
            self.config = None

            self.handle = gclib.py()  # initialize the library object

        def __str__(
                self,
        ):  # string representation of the class, called with the print function, may be useful
            # Debugging purposes, print class properties to console with print()
            return (
                f"Motor Controller Class with following config: \n"
                f"\tjog speed: {self._jog_speed} \n"
                f"\tscan speed: {self._scan_speed} \n"
                f"\tcalibration factor: {self._x_calibrate} \n"
            )  # String representation of the class

        # overwrite get and set methods for each of the different properties
        # each property is a dictionary, with the axis as the key

        # logger signal is emitted on each setter, giving user visual feedback for controller configuration
        # print statements can easily be changed to self.signal_logger.emit()

        def set_config(self, config):
            if config is not None:
                self.config = config
            else:
                self.config = load_configuration()
            self.fields_setup()

        def fields_setup(self):
            # PROPERTIES - allow us to overwrite the get, set, and delete methods
            #   this means that we can implement error checking at the class level
            #   which is important, as the user potentially has the ability to circumvent
            #   the error checking made at the UI level
            self._jog_speed = self.config[
                "galil_jog_speed"
            ]  # Default config for controller properties
            self._scan_speed = self.config["galil_scan_speed"]
            self._x_calibrate = self.config["galil_x_mmConversion"]
            self._y_calibrate = self.config["galil_y_mmConversion"]
            self._z_calibrate = self.config["galil_z_mmConversion"]
            self._r_calibrate = self.config["galil_r_degreesConversion"]

            self.jog_speed = self._jog_speed
            self.scan_speed = self._scan_speed

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

        # Setters for each class property
        @jog_speed.setter
        def jog_speed(self, value):
            if type(value) is int:
                self._jog_speed = value
            else:
                raise Exception

        @scan_speed.setter
        def scan_speed(self, value):
            if type(value) is int:
                self._scan_speed = value
            else:
                raise Exception

        @calibrate.setter
        def calibrate(self, value):

            if type(value) is int:
                self._calibrate = value
            else:
                raise Exception

        # Hardware interfacing functions

        def toggle_connection(self):
            if self.connected():
                self.handle.GCommand("ST")
                self.handle.GCommand("MO")
                self.handle.GClose()
                print("Connection terminated")
                return False
            else:
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

                return self.setup_axes()

        def setup_axes(self):
            # Setup
            try:
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
                return True
            except gclib.GclibError as e:
                print(f"Connection error: {self.tell_error()}")
                return False

        def is_connected(self):
            try:
                self.handle.GCommand("WH")
                print("Handle is OK")
                return True
            except gclib.GclibError as e:
                print("No handle available: {0}".format(e))
                return False

        def jog(self, axis=None, direction=None, feedback=True):
            self.jogging = feedback
            count = 0
            try:
                self.handle.GCommand("ST")
                if axis == "x":
                    if self.config["galil_reverse_x"]:
                        direction = direction * -1
                    self.handle.GCommand(
                        "JG %d" % (self._x_calibrate * self.jog_speed * direction)
                    )
                    self.begin_motion("A")
                elif axis == "y":
                    if self.config["galil_reverse_y"]:
                        direction = direction * -1
                    self.handle.GCommand(
                        "JG ,%d" % (self._y_calibrate * self.jog_speed * direction)
                    )
                    self.begin_motion("B")
                elif axis == "z":
                    if self.config["galil_reverse_z"]:
                        direction = direction * -1
                    self.handle.GCommand(
                        "JG ,,%d" % (self._z_calibrate * self.jog_speed * direction)
                    )
                    self.begin_motion("C")
                elif axis == "r":
                    if self.config["galil_reverse_r"]:
                        direction = direction * -1
                    self.handle.GCommand(
                        "JG ,,,%d" % (self._r_calibrate * self.jog_speed * direction)
                    )
                    self.begin_motion("D")
                else:
                    raise Exception

                if self.app is not None:
                    while self.jogging:
                        count = count + 1
                        self.get_position()
                        self.app.processEvents()
                        if count > 2000:
                            break

                self.handle.GCommand("MO D")
            except gclib.GclibError as e:
                print(f"error in jog: {self.tell_error()}")

        def begin_motion(self, axis=None):
            try:
                self.handle.GCommand("SH ABCD")
                self.handle.GCommand(f"BG {axis}")
            except gclib.GclibError as e:
                stop_code = self.tell_error()
                if stop_code is not None:
                    print(f"error in begin_motion: {stop_code}")
                if stop_code == "22 Begin not possible due to limit switch":
                    self.logger_signal.emit("Limit switch reached")

        def stop_motion(self):
            self.jogging = False
            try:
                self.handle.GCommand("ST")
            except gclib.GclibError as e:
                stop_code = self.tell_error()
                if stop_code is not None:
                    print(f"error in stop_motion: {stop_code}")
            finally:
                self.get_position()

        def set_origin(self, x=0, y=0, z=0, r=0):
            if x + y + z > 1000:
                print(
                    "Coordinates entered for the motors are too large. Double check in the code that they are given in mm"
                )
                return
            try:
                self.handle.GCommand("ST")
            except:
                pass

            xHome = -1 * x * self.config["galil_x_mmConversion"] + float(self.x)
            yHome = -1 * y * self.config["galil_y_mmConversion"] + float(self.y)
            zHome = -1 * z * self.config["galil_z_mmConversion"] + float(self.z)
            rHome = -1 * r * self.config["galil_r_degreesConversion"] + float(self.r)

            if self.config["galil_reverse_x"]:
                xHome = xHome * -1
            if self.config["galil_reverse_y"]:
                yHome = yHome * -1
            if self.config["galil_reverse_z"]:
                zHome = zHome * -1
            if self.config["galil_reverse_r"]:
                rHome = rHome * -1

            try:
                self.handle.GCommand(
                    f'DP {xHome},'
                    f'{yHome},'
                    f'{zHome},'
                    f'{rHome}'
                )
            except gclib.GclibError as e:
                stop_code = self.tell_error()
                if stop_code is not None:
                    print(f"error in set_origin: {stop_code}")
            finally:
                self.get_position()

        def set_origin_here(self):
            try:
                self.handle.GCommand("ST")
            except:
                pass
            try:
                self.handle.GCommand(f"DP 0,0,0,0")
            except gclib.GclibError as e:
                stop_code = self.tell_error()
                if stop_code is not None:
                    print(f"error in set_origin: {stop_code}")
            finally:
                self.get_position()

        def set_origin_here_1d(self, axis):
            try:
                self.handle.GCommand("ST")
            except:
                pass
            try:
                if axis == 'x':
                    self.handle.GCommand("DP 0")
                elif axis == 'y':
                    self.handle.GCommand("DP ,0")
                elif axis == 'z':
                    self.handle.GCommand("DP ,,0")
                elif axis == 'r':
                    self.handle.GCommand("DP ,,,0")

            except gclib.GclibError as e:
                stop_code = self.tell_error()
                if stop_code is not None:
                    print(f"error in set_origin: {stop_code}")
            finally:
                self.get_position()

        def go_home(self):
            try:
                self.go_to_position(0, 0, 0)
            except gclib.GclibError as e:
                stop_code = self.tell_error()
                if stop_code is not None:
                    print(f"error in go_home: {self.tell_error()}")
                else:
                    print(f"error in go_home: {e}")
            finally:
                self.get_position()

        def go_to_position(self, axes: list, coords: list):
            if not len(axes) == len(coords):
                self.log(level='error', message="Invalid coordinates")

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

                # Reverse directions when the config file says to
                if self.config[self.device_key][f'reverse_{axes[i].lower()}']:
                    coords[i] = -1 * coords[i]

                if axes[i].upper() == 'X':
                    self.handle.GCommand("SP %d" % (self._x_calibrate * self.scan_speed))
                    x_coord_str = coords[i] * self.config[self.device_key]['x_calibrate']
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

            self.handle.GCommand(f'PA {x_coord_str},{y_coord_str},{z_coord_str},{r_coord_str}')
            self.handle.GCommand(f"BG {x_ax_str}{y_ax_str}{z_ax_str}{r_ax_str}")
            self.get_position()

            while self.is_moving():
                if not self.scanning:
                    self.stop_motion()
                    self.get_position()
                    return

                t.sleep(0.05)
                if self.app is not None:
                    self.app.processEvents()
                self.get_position()
            # self.handle.GCommand('ST')
            self.handle.GCommand("MO")

        def tell_error(self):
            try:
                return (self.handle.GCommand("TC 1"))
            except:
                return None

        def is_moving(self):
            stat_a = self.handle.GCommand("MG_BGA")
            stat_b = self.handle.GCommand("MG_BGB")
            stat_c = self.handle.GCommand("MG_BGC")
            stat_d = self.handle.GCommand("MG_BGD")

            # print("statA: %s, statB %s, statC %s" % (statA, statB, statC))
            if (
                    stat_a == "0.0000"
                    and stat_b == "0.0000"
                    and stat_c == "0.0000"
                    and stat_d == "0.0000"
            ):
                return False
            else:
                return True

        def get_position(self):
            try:
                if self.config["galil_reverse_x"]:
                    self.x = -1 * float(self.handle.GCommand("RP A"))
                else:
                    self.x = self.handle.GCommand("RP A")
                if self.config["galil_reverse_y"]:
                    self.y = -1 * float(self.handle.GCommand("RP B"))
                else:
                    self.y = self.handle.GCommand("RP B")
                if self.config["galil_reverse_z"]:
                    self.z = -1 * float(self.handle.GCommand("RP C"))
                else:
                    self.z = self.handle.GCommand("RP C")
                if self.config["galil_reverse_r"]:
                    self.r = -1 * float(self.handle.GCommand("RP D"))
                else:
                    self.r = self.handle.GCommand("RP D")

                self.x_pos_mm_signal.emit(f"X: {self.x} mm")
                self.y_pos_signal.emit(f"Y: {self.y} mm")
                self.z_pos_signal.emit(f"Z: {self.z} mm")
                self.r_pos_mm_signal.emit(f"R: {self.r} mm")
            except gclib.GclibError as e:
                stop_code = self.tell_error()
                if stop_code is not None:
                    print(f"error in get_position: {stop_code}")
                else:
                    print(f"error in get_position: {e}")

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

from PyQt5.QtCore import QMutex, QObject, QThread, QWaitCondition, pyqtSignal

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT

from typing import Optional

import numpy as np
import logging
import time

log_formatter = logging.Formatter(LOGGER_FORMAT)

motor_logger = logging.getLogger('motor_log')

file_handler = logging.FileHandler("./logs/motor.log", mode='w')
file_handler.setFormatter(log_formatter)
motor_logger.addHandler(file_handler)

motor_logger.setLevel(logging.INFO)

root_logger = logging.getLogger(ROOT_LOGGER_NAME)

IS_GCLIB_LOADED = True
try:
    import gclib

except ImportError:
    root_logger.error('Galil libraries not loaded')
    IS_GCLIB_LOADED = False


class GalilDMC41x3(QObject):
    sTerminalMsg = pyqtSignal(str)  # -> mostly for debug purposes
    sConnectStatus = pyqtSignal(bool)
    sMotionComplete = pyqtSignal(bool)

    def __init__(self, parent: Optional[QObject], config: dict) -> None:
        super().__init__(parent=parent)

        if IS_GCLIB_LOADED is False:
            msg = '[-] The Galil motor libraries failed to load, motor functions will NOT work.'
            self.log_msg(level='warning', message=msg)

            return  # -> short-circuit class creation here

        self.handle = gclib.py()

        device = config['WTF']['Device']

        # => define the protected motor control variables from the config file
        self._sp = config[device]['Speed']
        self._tm = config[device]['TM']
        self._k1 = config[device]['K1']
        self._k2 = config[device]['K2']
        self._k3 = config[device]['K3']
        self._kp = config[device]['KP']
        self._ki = config[device]['KI']
        self._kd = config[device]['KD']
        self._db = config[device]['DB']
        self._ds = config[device]['DS']
        self._fc = config[device]['FC']
        self._fn = config[device]['FN']
        self._zp = config[device]['ZP']
        self._zn = config[device]['ZN']
        self._jg = config[device]['JG']

        self._return_latch_A = config[device]['ReturnLatchA']
        self._return_latch_B = config[device]['ReturnLatchB']
        # self._return_latch_C = config[device]['ReturnLatchC']

        self._counts_per_mm = config[device]['counts_per_mm']

        scale_LR_key = 'LR_scale_factor'
        if scale_LR_key in config[device].keys():
            self._scale_LR = config[device][scale_LR_key]
        else:
            self._scale_LR = 1.0

        scale_AP_key = 'AP_scale_factor'
        if scale_AP_key in config[device].keys():
            self._scale_AP = config[device][scale_AP_key]
        else:
            self._scale_AP = 1.0

        scale_SI_key = 'SI_scale_factor'
        if scale_SI_key in config[device].keys():
            self._scale_SI = config[device][scale_SI_key]
        else:
            self._scale_SI = 1.0

        # -> define the home coordinate in MRI coordinates
        self.home_coords_MRI = np.array([0.0, 0.0, 0.0])

        self.motor_mutex = QMutex()
        self.motor_condition = QWaitCondition()

        self.ip_address = config['WTF']['Motor']['ip']

        # -> check if we are simulating hardware
        self.SIMULATE_HARDWARE = config['WTF']['Motor']['simulate_hw']

    def toggle_handle(self) -> bool:
        """
        Class member function to initialize the connection to the motors.
        """
        if self.has_handle() is False:  # -> create a connection to the Galil
            status = self.connect_motor()

            # => for now we immediately disconnect for testing.
            # self.disconnect_motor()
        else:  # -> close the existing connection
            status = self.disconnect_motor()

        return status

    def connect_motor(self) -> bool:
        """
        Class member function to connect to the Galil motor controller.
        """
        status = True
        # -> check if we are simulating hardware
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(100)  # -> simulate something that takes time
            return status

        self.motor_mutex.lock()
        try:
            self.handle.GOpen(f"-a {self.ip_address} -s ALL -t 100")            
        except gclib.GclibError as e:
            msg = f"{e} : Failed to connect to address: {self.ip_address}"
            self.log_msg(level='error', message=msg)
            status = False

        if status is True:
            galil_info = self.handle.GInfo()
            self.motor_mutex.unlock()

            msg = f"Connection to the Galil established. {galil_info}"
            self.log_msg(level='info', message=msg)

            self.execute_init()

            self.sConnectStatus.emit(status)

        return status

    def disconnect_motor(self) -> None:
        """
        Class member function to disconnect from the Galil motor controller.
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(100)  # -> simulate something that takes time            
        else:
            self.motor_mutex.lock()
            self.handle.GCommand('ST')
            self.handle.GCommand('MO')
            self.handle.GClose()
            self.motor_mutex.unlock()

        msg = 'Closed connection to the Galil controller.'
        self.log_msg(level='info', message=msg)

    def has_handle(self) -> bool:
        """
        Ask the controller what kind of connection is being used to communicate
        """
        msg = 'Checking if a connection exists to the Galil'
        self.log_msg(level='info', message=msg)

        self.motor_mutex.lock()

        try:
            self.handle.GCommand('WH')
            self.motor_mutex.unlock()
            return True

        except:
            self.motor_mutex.unlock()
            return False

    def execute_init(self) -> None:
        """
        Class member function to initialize the control parameters for the
        RK-300 motor controller
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(100)  # -> simulate something that takes time
            return  # -> exit the function here 

        self.motor_mutex.lock()

        # -> any programs should be from the config file
        # galil_program_path = r"C:\Users\RKPC\Documents\Galil\LP100_move_program.dmc"
        # self.handle.GProgramDownloadFile(galil_program_path, '')

        # self.handle.GCommand(r"XQ #init;")

        self.handle.GCommand('MO;')

        self.handle.GCommand(f"SP {self._sp[0]},{self._sp[1]};")
        self.handle.GCommand(f"TM {self._tm};")
        self.handle.GCommand(f"K1 {self._k1[0]},{self._k1[1]};")
        self.handle.GCommand(f"K2 {self._k2[0]},{self._k2[1]};")
        self.handle.GCommand(f"K3 {self._k3[0]},{self._k3[1]};")
        self.handle.GCommand(f"KP {self._kp[0]},{self._kp[1]};")
        self.handle.GCommand(f"KI {self._ki[0]},{self._ki[1]};")
        self.handle.GCommand(f"KD {self._kd[0]},{self._kd[1]};")
        self.handle.GCommand(f"DB {self._db[0]},{self._db[1]};")
        self.handle.GCommand(f"DS {self._ds[0]},{self._ds[1]};")
        self.handle.GCommand(f"ZP {self._zp[0]},{self._zp[1]};")
        self.handle.GCommand(f"ZN {self._zn[0]},{self._zn[1]};")
        self.handle.GCommand(f"FC {self._fc[0]},{self._fc[1]};")
        self.handle.GCommand(f"FN {self._fn[0]},{self._fn[1]};")
        self.handle.GCommand(f"JG {self._jg[0]},{self._jg[1]};")
        # self.handle.GCommand('OFC=0;')
        # -> set the initial position at 0,0,0
        self.handle.GCommand('DP -1,-1;')

        # -> set the initial conditions of some internal variables
        self.handle.GCommand(f"latchA={self._return_latch_A};")
        self.handle.GCommand(f"latchB={self._return_latch_B};")
        # self.handle.GCommand(f"latchC={self._return_latch_C};")

        self.handle.GCommand('SH;')

        recv_galil = self.handle.GCommand('MG _SPA,_SPB;')
        # recv_galil = self.handle.GCommand('MG _OFC;')

        self.motor_mutex.unlock()

    def set_home_pos(self, home_pos: np.ndarray) -> None:
        """
        Sets the home position and all positional movements are made relative to
        the home position
        """
        self.home_coords_MRI = home_pos

        msg = f"home coords are: {self.home_coords_MRI}"
        self.log_msg(level='info', message=msg)

    def prepare_for_motion(self) -> None:
        """
        Class member function to set the appropriate speeds of the motors for
        movement outside the homing sequence
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(100)  # -> simulate something that takes time
            return  # -> exit the function here

        self.motor_mutex.lock()

        self.handle.GCommand('ST')
        self.handle.GCommand('MO')

        self.handle.GCommand(f"SP {self._sp[0]},{self._sp[1]};")

        self.handle.GCommand('SH')

        self.motor_mutex.unlock()

    def prepare_for_homing(self, invert_A: bool, invert_B: bool) -> None:
        """
        Class member function to set the jog speeds appropriately for motor
        movement during the homing sequence
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(100)  # -> simulate something that takes time
            return  # -> exit the function here

        self.motor_mutex.lock()        

        # -> set the jog speeds for motor homing
        if invert_A is False:
            if invert_B is False:
                self.handle.GCommand(f"JG {self._jg[0]},{self._jg[1]};")
            else:
                self.handle.GCommand(f"JG {self._jg[0]},{-self._jg[1]};")
        else:
            if invert_B is False:
                self.handle.GCommand(f"JG {-self._jg[0]},{self._jg[1]};")
            else:  # -> should never get here
                self.handle.GCommand(f"JG {-self._jg[0]},{-self._jg[1]};")      

        self.handle.GCommand('SH')

        self.motor_mutex.unlock()

    def execute_home(self) -> None:
        """
        Class member function
        """
        self.motor_mutex.lock()
        self.handle.GCommand(r"XQ #homeABC;")
        # logger.info(f"Got back: {self.get_msg()}")
        self.motor_mutex.unlock()

    def read_pos(self) -> list:
        """
        Class member function to read the motor position back to the software
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
            pos_list = [5, -5, 5]  # -> dummy value
            return pos_list

        self.motor_mutex.lock()
        try:
            pos_str = self.handle.GCommand('TP')
            pos_list = self.parse_response(response=pos_str)
        except gclib.GclibError as e:
            msg = f"{e}: Caught excption in read pos"
            self.log_msg(level='warning', message=msg)

        self.motor_mutex.unlock()

        return pos_list

    def index_axis_A(self) -> None:
        """
        Class member function to begin the homing sequence on Axis A
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
            return  # -> exit the function here

        self.motor_mutex.lock()

        self.handle.GCommand('FIA')
        self.handle.GCommand('BGA')

        self.motor_mutex.unlock()

    def index_axis_B(self) -> None:
        """
        Class member function to begin the homing sequence on Axis B
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
            return  # -> exit the function here

        self.motor_mutex.lock()

        self.handle.GCommand('FIB')
        self.handle.GCommand('BGB')

        self.motor_mutex.unlock()

    def home_axis_A(self) -> None:
        """
        docstring
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
            return  # -> exit the function here

        self.motor_mutex.lock()

        # self.handle.GCommand('DPA=latchA')
        self.handle.GCommand(f"DPA={self._return_latch_A};")
        home_tgt_A = 0 - 30
        self.handle.GCommand(f"PAA={home_tgt_A}")
        # self.handle.GCommand('PAA=0')
        self.handle.GCommand('BGA')

        self.motor_mutex.unlock()

    def home_axis_B(self) -> None:
        """
        docstring
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
            return  # -> exit the function here

        self.motor_mutex.lock()

        # self.handle.GCommand('DPB=latchB')
        self.handle.GCommand(f"DPB={self._return_latch_B};")
        home_tgt_B = 0 - 30
        self.handle.GCommand(f"PAB={home_tgt_B}")
        # self.handle.GCommand('PAB=0')
        self.handle.GCommand('BGB')

        self.motor_mutex.unlock()

    # def home_axis_C(self) -> None:
    #     """
    #     Class member function to begin the homing sequence on Axis C
    #     """
    #     self.motor_mutex.lock()

    #     self.handle.GCommand(r"XQ #homeC;")

    #     self.motor_mutex.unlock()

    # def is_homing_C(self) -> bool:
    #     """
    #     Class member function to check if the motor homing sequence is being
    #     performed on axis C
    #     """
    #     self.motor_mutex.lock()

    #     homing_flag = self.handle.GCommand('MG hm_flagC;')
    #     homing_flag = int(float(homing_flag))

    #     self.motor_mutex.unlock()

    #     if homing_flag == 1:
    #         homing_bool = True
    #     else:
    #         homing_bool = False

    #     return homing_bool

    def homing_status_A(self) -> int:
        """
        Class member function to check the motor status on Axis A, a return
        value of 0 indicates the motion is complete
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(100)  # -> simulate something that takes time
            home_stat_A = 0
            return home_stat_A  # -> exit the function here

        self.motor_mutex.lock()

        home_stat_A = self.handle.GCommand('MG _BGA;')
        home_stat_A = int(float(home_stat_A))

        self.motor_mutex.unlock()

        return home_stat_A

    def homing_status_B(self) -> int:
        """
        Class member function to check the motor status on Axis B, a return
        value of 0 indicates the motion is complete
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(100)  # -> simulate something that takes time
            home_stat_B = 0
            return home_stat_B  # -> exit the function here

        self.motor_mutex.lock()

        home_stat_B = self.handle.GCommand('MG _BGB;')
        home_stat_B = int(float(home_stat_B))

        self.motor_mutex.unlock()

        return home_stat_B

    # def homing_status_C(self) -> int:
    #     """
    #     Class member function to check the motor status on Axis C
    #     """
    #     self.motor_mutex.lock()

    #     home_stat_C = self.handle.GCommand('MG stat_C;')
    #     home_stat_C = int(float(home_stat_C))

    #     self.motor_mutex.unlock()

    #     return home_stat_C

    def stop_homing_A(self) -> None:
        """
        Class member functino to interrupt the homing sequence and stop motion
        on Axis A
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
            return  # -> exit the function here

        self.motor_mutex.lock()

        self.handle.GCommand('ST;')
        # -> without call to GMotionComplete this will not work !!
        self.handle.GMotionComplete('A;')
        self.handle.GCommand('MO;')

        self.motor_mutex.unlock()

    def stop_homing_B(self) -> None:
        """
        Class member functino to interrupt the homing sequence and stop motion
        on Axis B
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
            return  # -> exit the function here

        self.motor_mutex.lock()

        self.handle.GCommand('ST;')
        # -> without call to GMotionComplete this will not work !!
        self.handle.GMotionComplete('B;')
        self.handle.GCommand('MO;')

        self.motor_mutex.unlock()

    def stop_motion_AB(self) -> None:
        """
        Class member function to stop the motion of the motors on axis AB
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
        else:
            self.motor_mutex.lock()

            self.handle.GCommand('ST')
            # -> without calls to GMotionComplete this will not work !!
            self.handle.GMotionComplete('A')
            self.handle.GMotionComplete('B')
            self.handle.GCommand('MO')

            self.motor_mutex.unlock()

        # -> notify the main application that motion is complete, from a STOP
        # self.sMotionComplete.emit(False)

    def stop_motion_C(self) -> None:
        """
        Compatibility with LP-100 commands
        """
        pass
    # def stop_motion_C(self) -> None:
    #     """
    #     Class member function to stop the motion of the motors on axis C
    #     """
    #     self.motor_mutex.lock()

    #     # self.handle.GCommand('ST')  # -> this causes a problem!
    #     self.handle.GCommand('MO')

    #     QThread.msleep(1)  # -> this works ...
    #     self.handle.GCommand('SH')

    #     self.motor_mutex.unlock()

    #     # -> notify the main application that motion is complete, from a STOP
    #     self.sMotionComplete.emit(False)

    def move_to_target(self, tgt_index: int) -> None:
        """
        Class member function to move the motors to the specified target
        """
        QThread.msleep(250)

        self.sMotionComplete.emit(True)  # -> TODO: actually move to a target

    # def start_motion_C(self, target_coords: np.ndarray) -> None:
    #     """
    #     Class member function to move the motors to the specified target on the
    #     C axis
    #     """
    #     self.motor_mutex.lock()

    #     self.handle.GCommand('SH')

    #     target_counts = self.coords_to_counts(target_coords=target_coords)

    #     msg = f"target counts are: {target_counts}"
    #     self.log_msg(level='info', message=msg)

    #     target_C = int(target_counts[2])  # -> AP

    #     msg = f"tgtC={target_C};"
    #     self.log_msg(level='info', message=msg)

    #     self.handle.GCommand(f"tgtC={target_C};")
    #     self.handle.GCommand(r"XQ #moveC;")

    #     self.motor_mutex.unlock()

    def start_motion_AB(self, target_coords: np.ndarray) -> None:
        """
        Class member function to move the motors to the specified target on the
        A and B axis
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(1)  # -> simulate something that takes time
            return  # -> exit the function here

        self.handle.GCommand('SH')

        target_counts = self.coords_to_counts(target_coords=target_coords)

        msg = f"target counts are: {target_counts}"
        self.log_msg(level='info', message=msg)

        target_A = int(target_counts[0])  # -> LR
        target_B = int(target_counts[1])  # -> SI

        self.motor_mutex.lock()

        self.handle.GCommand(f"PA {target_A},{target_B},;")
        self.handle.GCommand('BGAB;')

        self.motor_mutex.unlock()

    # def motion_status_C(self) -> bool:
    #     """
    #     Class member function to tell if the motors have finished their movement
    #     along the C axis
    #     """
    #     self.motor_mutex.lock()

    #     move_stat_C = self.handle.GCommand('MG stat_C;')
    #     move_stat_C = int(float(move_stat_C))

    #     self.motor_mutex.unlock()

    #     msg = f"motion status C: {move_stat_C}"
    #     self.log_msg(level='info', message=msg)

    #     if move_stat_C == 0:
    #         motion_complete_flag = True
    #     else:
    #         motion_complete_flag = False

    #     return motion_complete_flag

    def motion_status_AB(self) -> bool:
        """
        Class member function to tell if the motors have finished their
        movement, returns True if motion is complete
        """
        if self.SIMULATE_HARDWARE is True:
            QThread.msleep(100)  # -> simulate something that takes time
            # self.sMotionComplete.emit(True)  # -> emit our motion complete signal
            return True  # -> exit the function here

        self.motor_mutex.lock()

        stat_AB = self.handle.GCommand('MG _BGA,_BGB;')

        self.motor_mutex.unlock()

        stat_AB = self.parse_motion_response(response=stat_AB)

        # -> check if all values in stat_AB are zeros
        if all(stat == 0.0 for stat in stat_AB) is True:
            # -> motion is complete
            # self.sMotionComplete.emit(True)
            self.handle.GCommand('ST')
            self.handle.GCommand('MO')
            return True
        else:
            # -> motion is not complete
            return False

    def get_home_coords(self, code: str) -> float:
        """
        Returns the home coordinates of the specified axis
        """
        if code == 'LR':
            return self.home_coords_MRI[0]
        elif code == 'AP':
            return self.home_coords_MRI[1]
        else:  # -> 'SI'
            return self.home_coords_MRI[2]

    def get_counts_per_mm(self) -> float:
        """
        Returns the counts per mm on the specified axis
        """
        return self._counts_per_mm

    def get_counts_scale(self, code: str) -> float:
        """
        Returns the scale factor on a particular axis
        """
        if code == 'LR':
            return self._scale_LR
        elif code == 'AP':
            return self._scale_AP
        else:  # -> 'SI'
            return self._scale_SI

    def coords_to_counts(self, target_coords: np.ndarray) -> np.ndarray:
        """
        Class member function to convert from MRI coordinates (mm) to encoder
        counts
        """
        # -> subtract the home coordinates to get the correct motion dimensions
        # -> having target coords on the left side of the equals sign here can cause changes to stored value in memory
        # -> either put target coords on the right side of the equals sign or make sure we send a copy
        coords = target_coords - self.home_coords_MRI

        counts_A = round(coords[0] * self.get_counts_per_mm() * self._scale_LR)  # -> LR
        counts_B = round(coords[2] * self.get_counts_per_mm() * self._scale_SI)  # -> SI
        counts_C = round(coords[1] * self.get_counts_per_mm() * self._scale_AP)  # -> AP

        target_counts = np.array([counts_A, counts_B, counts_C], dtype=int)

        return target_counts

    def parse_response(self, response: str) -> list:
        """
        Class member function to parse the response from the Galil
        """
        buffer = str(response).split(',')  # -> comma separator
        output = list()

        for element in buffer:
            output.append(float(element))

        return output

    def parse_motion_response(self, response: str) -> list:
        """
        Class member function to parse the response from the Galil.
        """
        buffer = str(response).split()  # -> whitespace separator
        output = list()

        for element in buffer:
            output.append(float(element))

        return output

    def get_msg(self) -> str:
        """
        Class member function to return unsolicited messages from the Galil
        during programs ONLY
        """
        return self.handle.GMessage()

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

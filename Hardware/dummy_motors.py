from PyQt5.QtCore import *
import logging

from typing import Optional

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.useful_methods import is_number
log_formatter = logging.Formatter(LOGGER_FORMAT)

motor_logger = logging.getLogger('motor_log')

file_handler = logging.FileHandler("./logs/motor.log", mode='w')
file_handler.setFormatter(log_formatter)
motor_logger.addHandler(file_handler)

motor_logger.setLevel(logging.INFO)

root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class DummyMotors(QThread):
    x = 0
    y = 0
    z = 0
    r = 0

    dX = 0
    dY = 0
    dZ = 0
    dR = 0

    x_motor_on = False
    r_motor_on = False

    x_target = 0
    y_target = 0
    z_target = 0
    r_target = 0

    x_pos_signal = pyqtSignal(float)
    r_pos_signal = pyqtSignal(float)

    scanning_signal = pyqtSignal(bool)

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent=parent, objectName="manager_thread")

        self.stay_alive = True

        self.cmd = 'NONE'

        self.connected = False

        self.scanning = False

        self.jog_speed = 1
        self.scan_speed = 1

        self.mutex = QMutex()
        self.condition = QWaitCondition()

    def run(self) -> None:
        """
        Overloaded function from QThread, this is the main scope control thread
        function.
        """
        self.mutex.lock()
        self.stay_alive = True

        while self.stay_alive is True:

            # root_logger.info('Waiting in motor thread.')
            # wait_bool = self.condition.wait(self.mutex)
            wait_bool = self.condition.wait(self.mutex, 50)
            # root_logger.info(f"Finished waiting in motor thread. {wait_bool}")

            if self.stay_alive is False:
                break

            self.cmd = self.cmd.upper()
            cmd_ray = self.cmd.split(' ')

            if self.connected:
                if self.cmd == 'Disconnect'.upper():
                    self.connected = False
                elif cmd_ray[0] == 'JOG' and cmd_ray[1] == 'SPEED':
                    self.jog_speed = float(cmd_ray[2])
                    self.log_msg(level = 'info', message=f"Jog Speed Set: {cmd_ray[2]}")
                elif cmd_ray[0] == 'SCAN' and cmd_ray[1] == 'SPEED':
                    self.scan_speed = float(cmd_ray[2])
                    self.log_msg(level = 'info', message=f"Scan Speed Set: {cmd_ray[2]}")
                elif self.cmd == 'Begin Motion X+'.upper():
                    self.dX = 1*self.jog_speed
                elif self.cmd == 'Begin Motion X-'.upper():
                    self.dX = -1*self.jog_speed
                elif self.cmd == 'Begin Motion R+'.upper():
                    self.dR = 1*self.jog_speed
                elif self.cmd == 'Begin Motion R-'.upper():
                    self.dR = -1*self.jog_speed
                elif self.cmd == 'Stop Motion'.upper():
                    self.dX = 0
                    self.dR = 0
                elif cmd_ray[0] == 'GO':
                    coords = cmd_ray[1].split(',')
                    if is_number(coords[0]):
                        self.x_target = coords[0]
                    if is_number(coords[1]):
                        self.y_target = coords[0]
                    if is_number(coords[2]):
                        self.z_target = coords[0]
                    if is_number(coords[3]):
                        self.r_target = coords[0]
                elif cmd_ray[0] == 'BG':
                    axes = cmd_ray[1]
                    self.scanning = True
                    self.scanning_signal.emit(True)
                    if 'A' in axes:
                        if self.x_target > self.x:
                            self.dX = abs(self.scan_speed)
                        elif self.x_target < self.x:
                            self.dX = -1 * abs(self.scan_speed)
                    if 'B' in axes:
                        if self.y_target > self.y:
                            self.dY = abs(self.scan_speed)
                        elif self.y_target < self.y:
                            self.dY = -1 * abs(self.scan_speed)
                    if 'C' in axes:
                        if self.z_target > self.z:
                            self.dZ = abs(self.scan_speed)
                        elif self.z_target < self.z:
                            self.dZ = -1 * abs(self.scan_speed)
                    if 'D' in axes:
                        if self.r_target > self.r:
                            self.dR = abs(self.scan_speed)
                        elif self.r_target < self.r:
                            self.dR = -1 * abs(self.scan_speed)
                elif self.cmd == 'Get Position'.upper():
                    self.x_pos_signal.emit(self.x)
                    self.r_pos_signal.emit(self.r)
                elif cmd_ray[0] == 'SET' and cmd_ray[1] == 'R':
                    self.R = float(cmd_ray[2])
                elif cmd_ray[0] == 'SET' and cmd_ray[1] == 'X':
                    self.X = float(cmd_ray[2])
            else:
                if self.cmd == 'Connect'.upper():
                    self.connected = True

            self.cmd = ""

            if self.scanning:
                if (self.x_target - self.x) * self.dX < 0:
                    self.dX = 0
                if (self.y_target - self.y) * self.dY < 0:
                    self.dY = 0
                if (self.z_target - self.z) * self.dZ < 0:
                    self.dZ = 0
                if (self.r_target - self.r) * self.dR < 0:
                    self.dR = 0
                if self.dX == 0 and self.dY == 0 and self.dZ == 0 and self.dR == 0:
                    self.scanning = False
                    self.scanning_signal.emit(False)

            self.x = self.x + self.dX
            self.r = self.r + self.dR

        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    @pyqtSlot(str)
    def command_received(self, command):
        self.cmd = command
        self.condition.wakeAll()
        self.log_msg(level='Info', message=command)

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
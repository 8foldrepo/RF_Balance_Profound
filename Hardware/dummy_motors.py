from PyQt5.QtCore import *
import logging

from typing import Optional

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT

log_formatter = logging.Formatter(LOGGER_FORMAT)

motor_logger = logging.getLogger('motor_log')

file_handler = logging.FileHandler("./logs/motor.log", mode='w')
file_handler.setFormatter(log_formatter)
motor_logger.addHandler(file_handler)

motor_logger.setLevel(logging.INFO)

root_logger = logging.getLogger(ROOT_LOGGER_NAME)

class DummyMotors(QThread):
    x = 0
    r = 0
    dX = 0
    dR = 0

    x_motor_on = False
    r_motor_on = False

    x_target = 0
    r_target = 0

    x_pos_signal = pyqtSignal(float)
    r_pos_signal = pyqtSignal(float)

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent=parent, objectName=u"manager_thread")

        self.stay_alive = True

        self.cmd = 'NONE'

        self.connected = False

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
                elif self.cmd_ray[0] == 'JOG' and self.cmd_ray[1] == 'SPEED':
                    self.jog_speed = float(self.cmd_ray[2])
                    self.log_msg(f"Jog Speed Set: {self.cmd_ray[2]}")
                elif self.cmd_ray[0] == 'SCAN' and self.cmd_ray[1] == 'SPEED':
                    self.scan_speed = float(self.cmd_ray[2])
                    self.log_msg(f"Jog Speed Set: {self.cmd_ray[2]}")
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
                elif self.cmd == 'Get Position'.upper():
                    self.x_pos_signal.emit(self.x)
                    self.r_pos_signal.emit(self.r)
                elif self.cmd_ray[0] == 'SET' and self.cmd_ray[1] == 'R':
                    self.R = float(self.cmd_ray[2])
                elif self.cmd_ray[0] == 'SET' and self.cmd_ray[1] == 'X':
                    self.X = float(self.cmd_ray[2])
            else:
                if self.cmd == 'Connect'.upper():
                    self.connected = True

            self.x = self.x + self.dX
            self.r = self.r + self.dR

        self.wrap_up()
        self.mutex.unlock()

        return super().run()

    @pyqtSlot(str)
    def command_received(self, command):
        self.cmd = command
        self.condition.wakeAll()

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
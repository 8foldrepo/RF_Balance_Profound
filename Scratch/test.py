from signal import signal

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from abc import  abstractmethod

class abstract_device(QObject):
    dummy_command_signal = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)

    def connect(self):
        log("Connecting")

    def disconnect(self):
        print("disconnecting")


class abstract_motor_controller(abstract_device):
    dummy_command_signal = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dummy_command_signal.connect(self.recieveCommand)

    @pyqtSlot(str)
    def recieveCommand(self, command):
        print(command)

if __name__ == '__main__':
    controller = abstract_motor_controller()
    controller.connect()
    controller.disconnect()
    controller.dummy_command_signal.emit("Hello")

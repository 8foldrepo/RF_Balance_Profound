from abc import ABCMeta, abstractmethod
from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractUAInterface(AbstractDevice):
    __metaclass__ = ABCMeta

    cal_data_signal = pyqtSignal(list, int)
    read_result = False
    write_result = False

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)

    '''Read data from the UA, check status of the operation, return/emit these, and update read_result'''

    @pyqtSlot()
    def read_data(self) -> Tuple[List[str], int]:
        ...

    @abstractmethod
    def write_data(self, data: List[str]):
        ...

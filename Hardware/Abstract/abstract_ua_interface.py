from abc import ABCMeta, abstractmethod
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from Hardware.Abstract.abstract_device import AbstractDevice


class AbstractUAInterface(AbstractDevice):
    __metaclass__ = ABCMeta

    cal_data_signal = pyqtSignal(list, int)

    def __init__(self, config, device_key="UAInterface", parent=None):
        super().__init__(parent=parent, config=config, device_key=device_key)
        self.UA_Write_Result = False
        self.UA_Read_Result = False

    @pyqtSlot()
    def read_data(self):
        self.UA_Read_Result = True
        self.cal_data_signal.emit(['1', 'GG1138', '20201005', '3', '4.29', '13.58', '-89.6', '63.6', '65.4', '67.5',
                                   '66.8', '65.2',
                                   '62.4', '70.0', '69.8', '71.2', '68.1', '38.7', '38.7', '42.5', '37.3', '44.6',
                                   '46.0', '45.5',
                                   '45.0', '40.8', '39.7'], 0)
        return ['1', 'GG1138', '20201005', '3', '4.29', '13.58', '-89.6', '63.6', '65.4', '67.5', '66.8', '65.2',
                '62.4', '70.0', '69.8', '71.2', '68.1', '38.7', '38.7', '42.5', '37.3', '44.6', '46.0', '45.5',
                '45.0', '40.8', '39.7'], 0

    @abstractmethod
    def write_data(self):
        self.UA_Write_Result = True
        return True


if __name__ == "__main__":
    wtf = UAInterfaceBox(config=None)
    print(wtf.read_data())

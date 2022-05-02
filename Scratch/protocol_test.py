from abc import ABC, ABCMeta, abstractmethod

from PyQt5.QtCore import QObject

from Utilities.useful_methods import log_msg


class device(QObject):
    __metaclass__ = ABCMeta

    def __init__(self, config, device_key, parent=None):
        super().__init__(parent=parent)
        from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
        import logging
        log_formatter = logging.Formatter(LOGGER_FORMAT)
        import os
        from definitions import ROOT_DIR
        balance_logger = logging.getLogger('wtf_log')
        file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
        file_handler.setFormatter(log_formatter)
        balance_logger.addHandler(file_handler)
        balance_logger.setLevel(logging.INFO)
        self.root_logger = logging.getLogger(ROOT_LOGGER_NAME)
        if config is not None:
            self.config = config
        else:
            self.config = load_configuration()
        self.device_key = device_key
        self.connected = False
        pass

    @abstractmethod
    def connect_hardware(self):
        ...


class AWG(device, ABC):
    def __init__(self, config, device_key, parent=None):
        super().__init__(config=config, device_key=device_key, parent=parent)
        self.log("HELLO WORLD")
        self.connect_hardware()

    def log(self, message, level='info'):
        log_msg(self, self.root_logger, message=message, level=level)


if __name__ == '__main__':
    awg = AWG(config=None, device_key=None, parent=None)

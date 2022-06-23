import logging
import sys
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from definitions import ROOT_DIR
log_formatter = logging.Formatter(LOGGER_FORMAT)
balance_logger = logging.getLogger("wtf_log")
with open(ROOT_DIR + "\logs\wtf.log", 'w') as f:
    pass
file_handler = logging.FileHandler(ROOT_DIR + "\logs\wtf.log", mode="w")
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)


def main():
    """Script which instantiates the main window, and performs all tasks that occur upon program startup"""
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    QThread.currentThread().setObjectName("ui_thread")
    window = MainWindow()
    window.show()
    app.processEvents()  # Ensure UI appears before running the rest of this script

    # Populate ui fields with system and config info

    window.system_info_tab.load_system_info()
    window.system_config.populate_config_ui()
    window.access_level_combo.setCurrentText("Administrator")

    try:
        if not window.config['Debugging']['disable_password_prompt']:
            window.prompt_for_password()
    except KeyError:
        window.log('Debugging:disable_password_prompt not found in config, defaulting to true', str(logging.INFO))

    window.begin_manager_thread()
    code = app.exec_()

    root_logger.info(f"[{QThread.currentThread().objectName()}] : app exited with code {code}")
    sys.exit(code)


if __name__ == "__main__":
    main()

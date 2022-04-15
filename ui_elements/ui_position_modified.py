import logging

import yaml
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.useful_methods import is_number
from Utilities.useful_methods import log_msg
from Widget_Library.widget_position import Ui_Form
from ui_elements.my_qwidget import MyQWidget

log_formatter = logging.Formatter(LOGGER_FORMAT)
import os
from definitions import ROOT_DIR

balance_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
balance_logger.addHandler(file_handler)
balance_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)


class Position(MyQWidget, Ui_Form):
    command_signal = QtCore.pyqtSignal(str)
    setup_signal = QtCore.pyqtSignal(dict)
    # Only the sign of the integer matters, and determines the direction of motion.
    begin_motion_signal = QtCore.pyqtSignal(str, int)
    stop_motion_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.motors = None
        self.manager = None
        self.config = None

    def set_config(self, config):
        self.config = config
        self.populate_default_ui()

    def set_manager(self, manager):
        self.manager = manager

    def set_motors(self, motors):
        self.motors = motors
        self.setup_signal.connect(self.motors.setup)
        self.stop_motion_signal.connect(self.motors.stop_motion)
        self.begin_motion_signal.connect(self.motors.begin_motion)

    def setup_pressed(self):
        self.setup_signal.emit({'movement_mode': self.movement_mode_comboBox.currentText(),
                                'steps_per_mm': self.steps_per_mm_sb.value(),
                                'lin_incr': self.lin_incr_double_sb.value(),
                                'lin_speed': self.linear_speed_mm_s_sb.value(),
                                'rot_speed': self.rotational_speed_deg_s_sb.value(),
                                'steps_per_deg': self.steps_per_degree_sb.value(),
                                'ang_incr': self.ang_inc_double_sb.value(), })

    def populate_default_ui(self):
        self.movement_mode_comboBox.setCurrentText(self.config[self.motors.device_key]['movement_mode'])
        self.steps_per_mm_sb.setValue(self.config[self.motors.device_key]['calibrate_ray'][0])
        self.steps_per_degree_sb.setValue(self.config[self.motors.device_key]['calibrate_ray'][1])
        self.lin_incr_double_sb.setValue(self.config[self.motors.device_key]['increment_ray'][0])
        self.ang_inc_double_sb.setValue(self.config[self.motors.device_key]['increment_ray'][1])
        self.linear_speed_mm_s_sb.setValue(self.config[self.motors.device_key]['speeds_ray'][0])
        self.rotational_speed_deg_s_sb.setValue(self.config[self.motors.device_key]['speeds_ray'][1])

    def save_config_ui(self):
        self.config[self.motors.device_key]['movement_mode'] = self.movement_mode_comboBox.currentText()
        self.config[self.motors.device_key]['calibrate_ray'][0] = self.steps_per_mm_sb.value()
        self.config[self.motors.device_key]['calibrate_ray'][1] = self.steps_per_degree_sb.value()
        self.config[self.motors.device_key]['increment_ray'][0] = self.lin_incr_double_sb.value()
        self.config[self.motors.device_key]['increment_ray'][1] = self.ang_inc_double_sb.value()
        self.config[self.motors.device_key]['speeds_ray'][0] = self.linear_speed_mm_s_sb.value()
        self.config[self.motors.device_key]['speeds_ray'][1] = self.rotational_speed_deg_s_sb.value()

        with open('local.yaml', 'w') as f:
            yaml.dump(self.config, f)

    def configure_signals(self):
        self.command_signal.connect(self.manager.exec_command)

        # Hardware control signals
        self.x_pos_button.pressed.connect(lambda: self.begin_motion("X", 1))
        self.x_pos_button.released.connect(self.attempt_to_stop_motion)
        self.x_neg_button.pressed.connect(lambda: self.begin_motion("X", -1))
        self.x_neg_button.released.connect(self.attempt_to_stop_motion)
        self.theta_pos_button.pressed.connect(lambda: self.begin_motion("R", 1))
        self.theta_pos_button.released.connect(self.attempt_to_stop_motion)
        self.theta_neg_button.pressed.connect(lambda: self.begin_motion("R", -1))
        self.theta_neg_button.released.connect(self.attempt_to_stop_motion)
        self.go_x_button.clicked.connect(lambda: self.command_signal.emit(f"Motor Go {self.go_x_sb.value()}"))
        self.go_theta_button.clicked.connect(lambda: self.command_signal.emit(f"Motor Go ,{self.go_theta_sb.value()}"))
        self.reset_zero_button.clicked.connect(lambda: self.command_signal.emit("Motor Origin Here"))
        self.manual_home_button.clicked.connect(self.manual_home_clicked)
        self.retract_ua_button.clicked.connect(self.retract_button_clicked)
        self.insert_ua_button.clicked.connect(self.insert_button_clicked)
        self.retract_ua_button.clicked.connect(self.retract_button_clicked)
        self.go_element_button.clicked.connect(self.go_element_button_clicked)
        self.setup_button.clicked.connect(self.setup_pressed)
        self.save_settings_button.clicked.connect(self.save_config_ui)

        # Hardware info signals
        self.manager.Motors.x_pos_mm_signal.connect(self.update_x_postion)
        self.manager.Motors.r_pos_mm_signal.connect(self.update_r_postion)

    '''Begin motion in with the specified axis letter is the specified direction. Example text: X+ '''

    def begin_motion(self, axis, direction):
        # Setting this to true causes the UI to assume that motors have begun moving, even if they may have not.
        # self.motors.moving = True
        self.begin_motion_signal.emit(axis, direction)
        self.log("Beginning motion")

    def attempt_to_stop_motion(self):
        while True:
            if self.motors.moving == False:
                return
            self.stop_motion_signal.emit()

    """Command the motors to go to the insertion point"""

    @pyqtSlot()
    def insert_button_clicked(self):
        self.command_signal.emit(f"Motor Go {self.config['WTF_PositionParameters']['X-TankInsertionPoint']}")

    @pyqtSlot(float)
    def update_x_postion(self, mm):
        try:
            self.x_pos_lineedit.setText(str(mm))
        except KeyboardInterrupt:
            pass

    @pyqtSlot(float)
    def update_r_postion(self, mm):
        try:
            self.theta_pos_lineedit.setText(str(mm))
        except KeyboardInterrupt:
            pass

    @pyqtSlot()
    def go_element_button_clicked(self):
        element_number = self.go_element_combo.currentText()
        if is_number(element_number):
            target_position = self.manager.element_x_coordinates[element_number]
            self.command_signal.emit(f"Motor Go {target_position}")
        else:
            # TODO: fill in later to handle "current" element condition
            return

    """Command the motors to retract until a sensor is reached"""

    @pyqtSlot()
    def retract_button_clicked(self):
        # TODO: fill in later with the code that uses the retraction sensor
        self.command_signal.emit(f"Motor Go {-50}")

    """Command the motors to blindly go to an element as defined by the 
    element number times the offset from element 1"""

    @pyqtSlot()
    def manual_home_clicked(self):
        if self.x_home_radio.isChecked():
            self.command_signal.emit("Motor go 0")
        elif self.theta_home_radio.isChecked():
            self.command_signal.emit("Motor go ,0")
        elif self.all_axes_radio.isChecked():
            self.command_signal.emit("Motor go 0,0")

    def log(self, message, level='info'):
        log_msg(self, root_logger, message=message, level=level)

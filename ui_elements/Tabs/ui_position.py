import logging

import yaml
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *

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
    """Disables buttons of entire UI that may interfere with operations in progress"""
    home_1d_signal = QtCore.pyqtSignal(str)
    home_all_signal = QtCore.pyqtSignal()
    setup_signal = QtCore.pyqtSignal(dict)
    reset_zero_signal = QtCore.pyqtSignal()
    go_to_signal = QtCore.pyqtSignal(list, list)
    begin_motion_signal = QtCore.pyqtSignal(str, int)
    stop_motion_signal = QtCore.pyqtSignal()

    def __init__(self, config=None, parent=None):
        super().__init__(parent=parent)
        self.app = QApplication.instance()
        self.setupUi(self)
        self.motors = None
        self.manager = None
        self.config = None

    def set_config(self, config):
        self.config = config

    def set_manager(self, manager):
        self.manager = manager

    def set_motors(self, motors):
        self.motors = motors
        self.populate_default_ui()

        self.setup_signal.connect(self.motors.setup)
        self.stop_motion_signal.connect(self.motors.stop_motion)
        self.begin_motion_signal.connect(self.motors.begin_motion)
        self.motors.ready_signal.connect(self.motors_ready)
        self.home_all_signal.connect(self.motors.go_home)
        self.home_1d_signal.connect(self.motors.go_home_1d)
        self.reset_zero_signal.connect(self.motors.set_origin_here)
        self.go_to_signal.connect(self.motors.go_to_position)

        self.configure_signals()

    # Enable ui to control motors unless the manager is running a script
    def motors_ready(self):
        if not self.manager.scripting:
            self.set_buttons_enabled_signal.emit(True)

    def setup_pressed(self):
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.setup_signal.emit({'movement_mode': self.movement_mode_comboBox.currentText(),
                                'lin_incr': self.lin_incr_double_sb.value(),
                                'lin_speed': self.linear_speed_mm_s_sb.value(),
                                'rot_speed': self.rotational_speed_deg_s_sb.value(),
                                'steps_per_deg': self.steps_per_degree_sb.value(),
                                'steps_per_mm': self.steps_per_mm_sb.value(),
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

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled):
        self.theta_neg_button.setEnabled(enabled)
        self.setup_button.setEnabled(enabled)
        self.x_pos_button.setEnabled(enabled)
        self.x_neg_button.setEnabled(enabled)
        self.theta_pos_button.setEnabled(enabled)
        self.save_settings_button.setEnabled(enabled)
        self.insert_ua_button.setEnabled(enabled)
        self.retract_ua_button.setEnabled(enabled)
        self.go_x_button.setEnabled(enabled)
        self.go_theta_button.setEnabled(enabled)
        self.manual_home_button.setEnabled(enabled)
        self.go_element_button.setEnabled(enabled)
        self.reset_zero_button.setEnabled(enabled)

    def configure_signals(self):
        self.stop_button.clicked.connect(lambda: self.set_buttons_enabled_signal.emit(True))
        # Hardware control signals
        self.x_pos_button.clicked.connect(lambda: self.begin_motion("X", 1))
        self.x_neg_button.clicked.connect(lambda: self.begin_motion("X", -1))
        self.theta_pos_button.clicked.connect(lambda: self.begin_motion("R", 1))
        self.theta_neg_button.clicked.connect(lambda: self.begin_motion("R", -1))
        self.stop_button.clicked.connect(self.attempt_to_stop_motion)
        self.go_x_button.clicked.connect(self.go_to_x_clicked)
        self.go_theta_button.clicked.connect(self.go_to_theta_clicked)
        self.reset_zero_button.clicked.connect(self.reset_zero_clicked)
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

    """Begin motion in with the specified axis letter is the specified direction. Example text: X+ """

    @pyqtSlot(str, int)
    def begin_motion(self, axis, direction):
        # Setting this to true causes the UI to assume that motors have begun moving, even if they may have not.
        # self.motors.moving = True
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.begin_motion_signal.emit(axis, direction)

    @pyqtSlot()
    def go_to_x_clicked(self):
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.go_to_signal.emit(['X'], [self.go_x_sb.value()])

    @pyqtSlot()
    def go_to_theta_clicked(self):
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.go_to_signal.emit(['R'], [self.go_theta_sb.value()])

    @pyqtSlot()
    def reset_zero_clicked(self):
        self.reset_zero_signal.emit()

    @pyqtSlot()
    def attempt_to_stop_motion(self):
        self.set_buttons_enabled_signal.emit(True)
        self.stop_motion_signal.emit()

    """Command the motors to go to the insertion point"""

    @pyqtSlot()
    def insert_button_clicked(self):
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.go_to_signal.emit(['X'], [int(self.config['WTF_PositionParameters']['X-TankInsertionPoint'])])

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
        element_1_pos = self.config['WTF_PositionParameters']['X-Element1']
        element_pitch = self.config['WTF_PositionParameters']['X-Element pitch (mm)']

        if is_number(self.go_element_combo.currentText()):
            offset = (int(self.go_element_combo.currentText()) - 1) * element_pitch
            target_position = element_1_pos + offset
            self.go_to_signal.emit(['X'], [target_position])
        else:
            # TODO: fill in later to handle "current" element condition
            return

    """Command the motors to retract until a sensor is reached"""

    @pyqtSlot()
    def retract_button_clicked(self):
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        # TODO: fill in later with the code that uses the retraction sensor
        self.home_1d_signal.emit('X')

    """Command the motors to blindly go to an element as defined by the element number times the offset from element 1"""

    @pyqtSlot()
    def manual_home_clicked(self):
        if self.x_home_radio.isChecked():
            self.home_1d_signal.emit('X')
        elif self.theta_home_radio.isChecked():
            self.home_1d_signal.emit('R')
        elif self.all_axes_radio.isChecked():
            self.home_all_signal.emit()

    def log(self, message, level='info'):
        log_msg(self, root_logger, message=message, level=level)

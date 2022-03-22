import yaml
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *

from Utilities.useful_methods import is_number
from Widget_Library.widget_position import Ui_Form


class Position(QWidget, Ui_Form):

    command_signal = QtCore.pyqtSignal(str)
    setup_signal = QtCore.pyqtSignal(dict)

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

    def setup_pressed(self):
        self.setup_signal.emit({'movement_mode': self.movement_mode_comboBox.currentText(),
                                'steps_per_mm': self.steps_per_mm_sb.value(),
                                'lin_incr': self.lin_incr_double_sb.value(),
                                'lin_speed': self.linear_speed_mm_s_sb.value(),
                                'rot_speed': self.rotational_speed_deg_s_sb.value(),
                                'steps_per_deg': self.steps_per_degree_sb.value(),
                                'ang_incr':self.ang_inc_double_sb.value(),})

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
        self.x_pos_button.pressed.connect(lambda: self.command_signal.emit("Motor Begin Motion X+"))
        self.x_pos_button.released.connect(lambda: self.command_signal.emit("Motor Stop Motion"))
        self.x_neg_button.pressed.connect(lambda: self.command_signal.emit("Motor Begin Motion X-"))
        self.x_neg_button.released.connect(lambda: self.command_signal.emit("Motor Stop Motion"))
        self.theta_pos_button.pressed.connect(lambda: self.command_signal.emit("Motor Begin Motion R+"))
        self.theta_pos_button.released.connect(lambda: self.command_signal.emit("Motor Stop Motion"))
        self.theta_neg_button.pressed.connect(lambda: self.command_signal.emit("Motor Begin Motion R-"))
        self.theta_neg_button.released.connect(lambda: self.command_signal.emit("Motor Stop Motion"))
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
        element_1_pos = self.config['WTF_PositionParameters']['X-Element1']
        element_pitch = self.config['WTF_PositionParameters']['X-Element pitch (mm)']

        if is_number(self.go_element_combo.currentText()):
            offset = (int(self.go_element_combo.currentText()) - 1) * element_pitch
            target_position = element_1_pos + offset
            self.command_signal.emit(f"Motor Go {target_position}")
        else:
            # TODO: fill in later to handle "current" element condition
            return

    """Command the motors to retract until a sensor is reached"""
    @pyqtSlot()
    def retract_button_clicked(self):
        # TODO: fill in later with the code that uses the retraction sensor
        self.command_signal.emit(f"Motor Go {-50}")


    """Command the motors to blindly go to an element as defined by the element number times the offset from element 1"""
    @pyqtSlot()
    def manual_home_clicked(self):
        if self.x_home_radio.isChecked():
            self.command_signal.emit("Motor go 0")
        elif self.theta_home_radio.isChecked():
            self.command_signal.emit("Motor go ,0")
        elif self.all_axes_radio.isChecked():
            self.command_signal.emit("Motor go 0,0")

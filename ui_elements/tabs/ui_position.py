"""
This class is to control the flow in information and
commands to and from the position tab of main window.
"""
import logging
import yaml
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.useful_methods import is_number, check_directory
from Utilities.useful_methods import log_msg
from Widget_Library.widget_position import Ui_Form
from manager import Manager
from definitions import ROOT_DIR
from ui_elements.my_qwidget import MyQWidget

log_formatter = logging.Formatter(LOGGER_FORMAT)
balance_logger = logging.getLogger("wtf_log")
with open(ROOT_DIR + "\logs\wtf.log", 'w') as f:
    print("attempting to open log file in ui_position, will write if doesn't exist")
file_handler = logging.FileHandler(ROOT_DIR + "\logs\wtf.log", mode="w")
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
        self.rotational_ray = None
        self.encoder_ray = None
        self.gearing_ray = None
        self.calibrate_ray = None
        self.app = QApplication.instance()
        self.setupUi(self)
        self.motors = None
        self.manager = None
        self.config = config
        self.com_port = None
        self.settings_ray = list()
        self.stop_button.setEnabled(False)

    def set_config(self, config: dict) -> None:
        """
        setter method for class' local config variable; passed in main window class

        :param config: the config variable to be passed to the ui_position class
        """
        self.config = config

    def set_manager(self, manager: Manager):
        """
        setter method for class' local manager variable; passed in main window class

        :param manager: the manager class variable to be passed to the ui_position class
        """
        self.manager = manager

    def set_motors(self, motors):
        """
        Setter method for class' local motors variable; relayed in main window class.
        Also sets up the com port, and connects motor-related class methods to methods in
        motor class.

        :param motors: the motor variable to be passed to the ui_position class
        """
        self.motors = motors
        self.populate_default_ui()
        self.com_port = self.config[self.motors.device_key]['port']
        self.setup_signal.connect(self.motors.setup)
        self.stop_motion_signal.connect(self.motors.stop_motion)
        self.begin_motion_signal.connect(self.motors.begin_motion)
        self.motors.ready_signal.connect(self.motors_ready)
        self.home_all_signal.connect(self.motors.go_home)
        self.home_1d_signal.connect(self.motors.go_home_1d)
        self.reset_zero_signal.connect(self.motors.set_origin_here)
        self.go_to_signal.connect(self.motors.go_to_position)
        self.populate_settings_ray()
        self.configure_signals()

    def populate_settings_ray(self) -> None:
        """
        The automatic and default values for the position tab regarding motors,
        is automatically called via the class' set_motor method. Alters Qt objects
        """
        self.trans_1_indicator.setChecked(True)
        self.trans_1_indicator.dPtr.animate(True)
        self.theta_rotation_indicator.setChecked(True)
        self.theta_rotation_indicator.dPtr.animate(True)
        self.visa_resource_field.setText(self.com_port)
        self.axis_spinbox.setValue(2)
        self.calibrate_ray = self.config[self.motors.device_key]['calibrate_ray']
        self.steps_mm_doublespinbox.setValue(self.calibrate_ray[0])
        self.gearing_ray = self.config[self.motors.device_key]['gearing_ray']
        self.gearing_double_spinbox.setValue(self.gearing_ray[1])
        self.encoder_ray = self.config[self.motors.device_key]['encoder_installed_ray']
        self.encoded_indicator.setChecked(self.encoder_ray[1])
        self.rotational_ray = self.config[self.motors.device_key]['rotational_ray']
        if self.rotational_ray[1]:
            self.type_combobox.setCurrentText("Rotational")
        else:
            self.type_combobox.setCurrentText("Translational")

    def motors_ready(self) -> None:
        """
        Enable ui to control motors unless the manager is running a script
        """
        if not self.manager.currently_scripting:
            self.set_buttons_enabled_signal.emit(True)

    def setup_pressed(self) -> None:
        """
        Changes various buttons to disabled to prevent user disruption, processes events
        to prevent lag and calls motors' setup method passing class variables as parameters
        """
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.setup_signal.emit({
            'lin_incr': self.lin_incr_double_sb.value(),
            'lin_speed': self.linear_speed_mm_s_sb.value(),
            'rot_speed': self.rotational_speed_deg_s_sb.value(),
            'steps_per_deg': self.steps_per_degree_sb.value(),
            'steps_per_mm': self.steps_per_mm_sb.value(),
            'ang_incr': self.ang_inc_double_sb.value(),
            'x_gearing': self.gearing_ray[0],
            'r_gearing': self.gearing_ray[1]
        })

    def populate_default_ui(self) -> None:
        """
        Default values to fill in the various Qt objects, all come from the
        config files. Called automatically with the set_motors method
        """
        self.steps_per_mm_sb.setValue(self.config[self.motors.device_key]["calibrate_ray"][0])
        self.steps_per_degree_sb.setValue(self.config[self.motors.device_key]["calibrate_ray"][1])
        self.lin_incr_double_sb.setValue(self.config[self.motors.device_key]["increment_ray"][0])
        self.ang_inc_double_sb.setValue(self.config[self.motors.device_key]["increment_ray"][1])
        self.linear_speed_mm_s_sb.setValue(self.config[self.motors.device_key]["speeds_ray"][0])
        self.rotational_speed_deg_s_sb.setValue(self.config[self.motors.device_key]["speeds_ray"][1])

    def save_config_ui(self) -> None:
        """
        If the user fills in the values in the position tab, clicking the update or
        save button will adjust the config's values to reflect the user inputted ones
        """
        self.config[self.motors.device_key]["calibrate_ray"][0] = self.steps_per_mm_sb.value()
        self.config[self.motors.device_key]["calibrate_ray"][1] = self.steps_per_degree_sb.value()
        self.config[self.motors.device_key]["increment_ray"][0] = self.lin_incr_double_sb.value()
        self.config[self.motors.device_key]["increment_ray"][1] = self.ang_inc_double_sb.value()
        self.config[self.motors.device_key]["speeds_ray"][0] = self.linear_speed_mm_s_sb.value()
        self.config[self.motors.device_key]["speeds_ray"][1] = self.rotational_speed_deg_s_sb.value()

        with open("local.yaml", "w") as config_file:
            yaml.dump(self.config, config_file)

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled: bool) -> None:
        """
        Controls whether all user-interactive Qt objects
        are disabled to prevent user disruption.

        :param enabled: If true, turns on all the user-interactive object, and vice versa
        """
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
        self.steps_per_mm_sb.setEnabled(enabled)
        self.lin_incr_double_sb.setEnabled(enabled)
        self.linear_speed_mm_s_sb.setEnabled(enabled)
        self.steps_per_degree_sb.setEnabled(enabled)
        self.ang_inc_double_sb.setEnabled(enabled)
        self.rotational_speed_deg_s_sb.setEnabled(enabled)
        self.doubleSpinBox.setEnabled(enabled)  # todo: rename this element to something more intuitive like
        # gearing_double_sb
        self.setup_button.setEnabled(enabled)
        self.save_settings_button.setEnabled(enabled)
        self.x_neg_button.setEnabled(enabled)
        self.x_pos_button.setEnabled(enabled)
        self.insert_ua_button.setEnabled(enabled)
        self.theta_pos_button.setEnabled(enabled)
        self.theta_neg_button.setEnabled(enabled)
        self.go_x_button.setEnabled(enabled)
        self.go_theta_button.setEnabled(enabled)
        self.go_element_button.setEnabled(enabled)
        self.go_element_combo.setEnabled(enabled)
        self.reset_zero_button.setEnabled(enabled)
        self.manual_home_button.setEnabled(enabled)
        self.type_combobox.setEnabled(enabled)
        self.axis_spinbox.setEnabled(enabled)
        self.go_x_sb.setEnabled(enabled)
        self.go_theta_sb.setEnabled(enabled)
        self.all_axes_radio.setEnabled(enabled)
        self.x_home_radio.setEnabled(enabled)
        self.theta_home_radio.setEnabled(enabled)

        # The stop button is the only one where once enabled it can no longer be disabled by this method
        if enabled:
            self.stop_button.setEnabled(enabled)

    def configure_signals(self) -> None:
        """
        Sets up relay actions between various user-interactive objects and methods that pertain
        to those objects. Such as if a spinbox value is changed, the signal will cause a method
        be launched to reflect the changed value.
        """
        # self.set_button.clicked.connect(self.set_clicked)
        self.axis_spinbox.valueChanged.connect(self.axis_changed)
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
        self.manager.Motors.x_pos_mm_signal.connect(self.update_x_position)
        self.manager.Motors.r_pos_mm_signal.connect(self.update_r_position)

    def axis_changed(self) -> None:
        """Change the settings displayed in the UI to reflect the current axis"""
        axis = self.axis_spinbox.value() - 1
        self.steps_per_mm_sb.setValue(self.motors.calibrate_ray_steps_per[axis])
        self.gearing_double_spinbox.setValue(self.motors.gearing_ray[axis])
        self.encoded_indicator.setChecked(self.motors.encoder_ray[axis])
        if self.motors.rotational_ray[axis]:
            self.type_combobox.setCurrentText("Rotational")
        else:
            self.type_combobox.setCurrentText("Translational")

    # todo: this is disabled in the UI
    # def set_clicked(self):
    #     """Update the motor settings to reflect the UI"""
    #     axis = self.axis_spinbox.value() - 1
    #     self.motors.

    @pyqtSlot(str, int)
    def begin_motion(self, axis: str, direction: int) -> None:
        """
        Begin motion in with the specified axis letter and the specified direction. Example text: X+

        :param axis: String that can be X or R, the axis to start movement
        :param direction: Can be 1 or -1 to represent forward and reverse respectively
        """
        # Setting this to true causes the UI to assume that motors have begun moving, even if they may have not.
        # self.motors.moving = True
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.begin_motion_signal.emit(axis, direction)

    @pyqtSlot()
    def go_to_x_clicked(self) -> None:
        """
        The method that's called when to 'go to' button is clicked for the x-axis.
        Turns off the tab buttons triggers motors' go_to_position method.
        """
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.go_to_signal.emit(["X"], [self.go_x_sb.value()])

    @pyqtSlot()
    def go_to_theta_clicked(self) -> None:
        """
        The method that's called when to 'go to' button is clicked for the r-axis.
        Turns off the tab buttons triggers motors' go_to_position method.
        """
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.go_to_signal.emit(["R"], [self.go_theta_sb.value()])

    @pyqtSlot()
    def reset_zero_clicked(self) -> None:
        """activates the reset_zero_signal, which activates the motors' set_origin_here method"""
        self.reset_zero_signal.emit()

    @pyqtSlot()
    def attempt_to_stop_motion(self) -> None:
        """Triggers the set_buttons_enabled_signal(True) and the stop_motion_signal"""
        self.set_buttons_enabled_signal.emit(True)
        self.stop_motion_signal.emit()

    @pyqtSlot()
    def insert_button_clicked(self) -> None:
        """Command the motors to go to the insertion point"""
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        self.go_to_signal.emit(['X'], [int(self.config['WTF_PositionParameters']['X-TankInsertionPoint'])])

    @pyqtSlot(float)
    def update_x_position(self, mm: float) -> None:
        """
        Changes the value shown in the x position Qt object to the passed mm value.
        Includes try/exception for KeyboardInterrupt.

        :param mm: The position the x-axis is currently in mm
        """
        try:
            self.x_pos_lineedit.setText("%.2f" % mm)
        except KeyboardInterrupt:
            pass

    @pyqtSlot(float)
    def update_r_position(self, mm: float):
        """
        Changes the value shown in the r position Qt object to the passed mm value.
        Includes try/exception for KeyboardInterrupt.

        :param mm: The position the r-axis is currently in mm
        """
        try:
            self.theta_pos_lineedit.setText("%.2f" % mm)
        except KeyboardInterrupt:
            pass

    @pyqtSlot()
    def go_element_button_clicked(self) -> None:
        """
        Takes the position and pitch of the element from the config file
        and moves the x-axis motor to meet the element. Handles case where
        manager variable isn't filled, and if the go_element_combo isn't a number
        """
        element_1_pos = self.config["WTF_PositionParameters"]["X-Element1"]
        element_pitch = self.config["WTF_PositionParameters"]["X-Element pitch (mm)"]

        if self.manager is not None:
            if is_number(self.go_element_combo.currentText()):
                target_position = self.manager.assumed_element_x_coords[int(self.go_element_combo.currentText())]
                self.go_to_signal.emit(["X"], [target_position])
            else:
                target_position = self.manager.assumed_element_x_coords[self.manager.element]
                self.go_to_signal.emit(["X"], [target_position])
        else:
            if is_number(self.go_element_combo.currentText()):
                offset = (int(self.go_element_combo.currentText()) - 1) * element_pitch
                target_position = element_1_pos + offset
                self.go_to_signal.emit(["X"], [target_position])

    @pyqtSlot()
    def retract_button_clicked(self) -> None:
        """Command the motors to retract until a sensor is reached"""
        self.set_buttons_enabled_signal.emit(False)
        self.app.processEvents()
        # TODO: fill in later with the code that uses the retraction sensor
        self.home_1d_signal.emit("X")

    @pyqtSlot()
    def manual_home_clicked(self) -> None:
        """
        Command the motors to blindly go to an element as defined
        by the element number times the offset from element 1
        """
        self.set_buttons_enabled_signal.emit(False)

        if self.x_home_radio.isChecked():
            self.home_1d_signal.emit("X")
        elif self.theta_home_radio.isChecked():
            self.home_1d_signal.emit("R")
        elif self.all_axes_radio.isChecked():
            self.home_all_signal.emit()

    def log(self, message: str, level: str = "info") -> None:
        """
        Relay method for the root logger if log messages are needed in this class

        :param message: the message to be written to console and the log file
        :param level: the level if importance this message has to the user
        """
        log_msg(self, root_logger, message=message, level=level)

"""
This class controls the Main Window GUI thread. In contrast to the manager class, this class focuses on the GUI
interaction logic between the user and the application. Several methods in the class control the presentation of
information, layout of dialogs/prompts, triggers and synchronization between this class' and the manager's signals,
etc.
"""
import logging
import os
import sys
import time as t
import webbrowser
from typing import List
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import QThread, QEvent
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtGui import QIcon
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QTreeWidgetItem, QFileDialog, QAction, QMessageBox, QApplication, QMainWindow
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
from Utilities.load_config import load_configuration
from Utilities.useful_methods import log_msg, tab_text_to_index, check_directory
from Widget_Library import window_wet_test
from data_structures.variable_containers import WaterLevel
from definitions import ROOT_DIR
from manager import Manager
from ui_elements.Dialogs.draining_dialog import DrainingDialog
from ui_elements.Dialogs.filling_dialog import FillingDialog
from ui_elements.Dialogs.ui_password_dialog import PasswordDialog
from ui_elements.Dialogs.ui_pretest_dialog import PretestDialog
from ui_elements.Dialogs.ui_retracting_ua_warning import UARetractDialog
from ui_elements.Dialogs.ui_script_complete_dialog import ScriptCompleteDialog
from ui_elements.Dialogs.ui_user_info_dialog import WTFUserInfo
from ui_elements.Dialogs.ui_user_prompt import WTFUserPrompt
from ui_elements.Dialogs.ui_user_prompt_pump_not_running import WTFUserPromptPumpNotRunning
from ui_elements.Dialogs.ui_user_prompt_water_too_high import WTFUserPromptWaterTooHigh
from ui_elements.Dialogs.ui_user_prompt_water_too_low import WTFUserPromptWaterTooLow
from ui_elements.Dialogs.ui_write_cal_to_ua import WriteCalDataToUA

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger("wtf_log")
directory = os.path.join(ROOT_DIR, "Logs")
check_directory(directory)
with open(os.path.join(directory,"wtf.log"), 'w+') as f:
    pass
file_handler = logging.FileHandler(os.path.join(directory, 'wtf.log'), mode="w+")
file_handler.setFormatter(log_formatter)
wtf_logger.addHandler(file_handler)
wtf_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)
log_formatter = logging.Formatter(LOGGER_FORMAT)


class MainWindow(QMainWindow, window_wet_test.Ui_MainWindow):
    """
    this class oversees the user interface of the application. It contains a layout of
    widgets, each with their own functions. It relays the signals from the widgets to each other,
    as well as relaying signals from the UI widgets to the manager routine and vise versa.

    Attributes:
        manager: Manager() object which runs in a separate thread and carries out scripts and hardware instructions.

    Signals:
        load_script_signal(str): tell the manager to load the script with a given path
    Slots:
        complete: this method is run when the manager object is terminated.
    """

    # Enable colored terminal for logging
    os.system('color')

    manager: Manager

    threading = False
    thread_list: List[QThread]

    command_signal = QtCore.pyqtSignal(str)
    abort_instantly_signal = QtCore.pyqtSignal()
    load_script_signal = QtCore.pyqtSignal(str)  # str is the path to the script file
    yes_signal = QtCore.pyqtSignal()
    no_signal = QtCore.pyqtSignal()
    # list containing one str element matching the text of the scan sub-tab
    set_scan_tab_signal = QtCore.pyqtSignal(list)
    num_tasks = 0  # the number of tasks in the current script. Used to calculate progress
    progress_bar_ready = True  # variables to prevent signals from refreshing UI elements too quickly
    script_changed = False  # prevents user from running a script if it has been modified and not reloaded

    # List of dictionaries representing each task and its arguments (repeats excluded)

    def __init__(self):
        # Load default.yaml file to self.config as a python dictionary
        super(MainWindow, self).__init__()
        self.script_info = None
        self.UAInterface = None
        self.access_level = None
        self.thread_list = list()
        self.list_of_var_dicts = list()
        self.app = QApplication.instance()
        self.config = load_configuration()

        self.setupUi(self)
        self.activateWindow()
        self.connect_ui_thread_devices()
        self.pass_config_and_ui_elements_to_tabs()
        self.style_ui()
        self.configure_non_manager_signals()

    def connect_ui_thread_devices(self) -> None:
        """
        Note: the UA interface box is instantiated in both the manager and the UI thread.
        This is done to improve responsiveness, as triggering UI dialogs with a signal causes a delay.
        There should be no conflicts between the two objects, as they both just send commands to the exe file
        """
        if self.config["Debugging"]["simulate_ua_interface"]:
            from Hardware.Simulated.simulated_ua_interface import SimulatedUAInterface
            self.UAInterface = SimulatedUAInterface(config=self.config)
        else:
            from Hardware.ua_interface import UAInterface

            self.UAInterface = UAInterface(config=self.config)

    def style_ui(self) -> None:
        """
        Initializes several output/information fields of the main window, along with
        disabling the appropriate main with disabling the appropriate main window buttons
        """
        self.setWindowTitle("Wet Test Fixture Python Interface")

        path = os.path.join(ROOT_DIR, "images", "8foldlogo.ico")
        self.setWindowIcon(QIcon(path))
        self.tabWidget.setCurrentIndex(0)

        # Format tree widget
        self.script_step_view.setColumnCount(2)
        self.script_step_view.setHeaderLabels(["Task", "Arguments"])
        self.script_step_view.header().resizeSection(0, 220)

        # Set defaults for indicators
        self.system_indicator.setStyleSheet("BUSY")
        self.system_indicator.setStyleSheet("background-color: yellow")
        self.script_status_indicator.setStyleSheet("background-color: grey")
        self.script_status_indicator.setText("NO SCRIPT")
        self.system_indicator.setText("IDLE")
        self.system_indicator.setStyleSheet("background-color: grey")
        self.moving_indicator.setStyleSheet("background-color:grey")
        self.moving_indicator.setText("STATIONARY")
        self.ua_pump_indicator.setStyleSheet("background-color: grey")
        self.ua_pump_indicator.setText("UA PUMP OFF")
        self.tank_level_indicator.setStyleSheet("background-color: red")
        self.tank_level_indicator.setText("TANK LOW")
        self.ua_on_indicator.setStyleSheet("background-color: grey")
        self.ua_on_indicator.setText("UA OFF")

        # Default to buttons disabled until done setting up manager
        self.set_buttons_enabled(False)

    def pass_config_and_ui_elements_to_tabs(self) -> None:
        """
        Pass config file to tab widgets
        """
        self.system_config.set_config(self.config)
        self.position_tab.set_config(self.config)
        self.rfb.set_config(self.config)
        self.results_tab.set_config(self.config)
        self.ua_calibration_tab.set_config(self.config)
        self.scan_tab_widget.set_config(self.config)
        self.scan_tab_widget.set_tabWidget(self.tabWidget)
        self.script_editor.set_tree_widget(self.script_step_view)

    def begin_manager_thread(self) -> None:
        """
        Initializes the manager class instantiation and its thread logic.
        Also synchronizes and hardware to the various tabs in the main window
        """
        self.manager = Manager(parent=self, config=self.config, system_info=self.system_info_tab.parser)
        self.thread_list.append(self.manager)
        self.configure_manager_signals()
        self.pass_manager_and_hardware_to_tabs()

        # Begin the thread
        self.threading = True
        self.manager.start(priority=QThread.HighPriority)
        self.command_signal.emit("CONNECT")

    def pass_manager_and_hardware_to_tabs(self) -> None:
        """
        Sends manager or manager components to RFB, position, calibration,
        scan, results, and script tabs via tab class setter methods
        """
        self.rfb.set_manager(self.manager)
        self.rfb.set_balance(self.manager.Balance)
        self.position_tab.set_manager(self.manager)
        self.position_tab.set_motors(self.manager.Motors)
        self.ua_calibration_tab.set_manager(self.manager)
        self.ua_calibration_tab.set_ua_interface(self.manager.UAInterface)
        self.scan_tab_widget.set_manager(self.manager)
        self.results_tab.set_manager(self.manager)
        self.script_editor.set_manager(self.manager)

    # noinspection PyArgumentList
    def visualize_script(self, var_dicts: list) -> None:
        """
        Display the task names and arguments from the script parser with a QTreeView

        :param var_dicts:
            A list of dictionaries containing every task in the outer level and task variables in the
            dictionary level
        """
        self.upon_script_reloaded()
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        self.script_step_view.clear()
        self.list_of_var_dicts = var_dicts

        task_dict = {}
        for i in range(len(self.list_of_var_dicts)):  # go through every entry in list_of_var_dicts
            if "# of Tasks" not in self.list_of_var_dicts[i].keys():
                arg_list = list()
                for key in self.list_of_var_dicts[i]:
                    if key != "Task type":  # if key does not equal "Task type"
                        arg_list.append([key, self.list_of_var_dicts[i][key]])

                task_dict[self.list_of_var_dicts[i]["Task type"]] = arg_list

        tree_items = []
        for key, values in task_dict.items():
            item = QTreeWidgetItem([key])
            for value in values:
                child = QTreeWidgetItem(value)
                item.addChild(child)

            tree_items.append(item)

        self.script_step_view.insertTopLevelItems(0, tree_items)

        text = self.script_description_field.toPlainText()
        if text != '' and text is not None and not text.isspace():
            for i in range(2):
                self.script_description_field.setStyleSheet("QFrame\n{\n	border: 2px solid lightblue;\n}")
                self.script_description_field.setText(text)
                QTest.qWait(250)
                self.script_description_field.setStyleSheet("QFrame\n{\n	color: black;\n}")
                self.script_description_field.setText(text)
                if i != 1:
                    QTest.qWait(250)

    def update_script_visual_element_number(self, element_number: str) -> None:
        """
        If the variable name contains the word current, update it with the current element number

        :param element_number: The current element the manager is keeping track of to be shown in the script visualizer
        """
        if "Element" in element_number:
            return
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        root_item = self.script_step_view.invisibleRootItem()
        for i in range(root_item.childCount()):
            task = root_item.child(i)
            for j in range(task.childCount()):
                var = task.child(j)
                var_name = var.text(0)
                var_value = var.text(1)
                # If the variable is an element number that is looped
                if var_name == "Element" and ("Current" in var_value):
                    var.setText(1, f"Current: {self.live_element_field.text()}")

    @pyqtSlot(list)
    def set_tab_slot(self, tab_ray: list) -> None:
        """
        A relay method to change the current tab in main window from a manager signal. TabWidget variable is updated
        to reflect tab change for nested tab switching operation. **Is connected to manager's set_tab_signal**

        :param tab_ray:
            The list of string(s) that represents which tab/sub-tab the program should display.
            Options include - 'Welcome', 'System Info', 'Edit Script', 'RFB', 'UA Calibration',
            'Results', 'Scan' ('1D Scan','Acquire Waveform', 'Scan Setup'), 'Position', 'System Config'
        """
        if len(tab_ray) < 1:
            return
        index = tab_text_to_index(tab_ray[0], self.tabWidget)
        if index == -1:
            return
        self.tabWidget.setCurrentIndex(index)

        if tab_ray[0].upper() == "SCAN":
            if len(tab_ray) < 2:
                return

            self.set_scan_tab_signal.emit([tab_ray[1]])

    @pyqtSlot(int)
    def expand_step(self, step_index: int) -> None:  # current_step should match "Task type" from above
        """
        Climbs down all nodes of root visualizer node until step index is reached, then sends
        the setExpanded(True) command to child node **connected to manager's task_number_signal**

        :param step_index:
            The supposed index number of the task that is to be expanded down the linear list of tasks in the visualizer
        """
        root_item = self.script_step_view.invisibleRootItem()
        child_count = root_item.childCount()

        for i in range(child_count):
            item = root_item.child(i)

            if i == step_index:
                item.setExpanded(True)
                yellow_background = QColor(255, 255, 0)
                brush_for_background = QBrush(yellow_background)
                item.setBackground(0, brush_for_background)
            else:
                item.setExpanded(False)
                white_background = QColor(255, 255, 255)
                brush_for_background = QBrush(white_background)
                item.setBackground(0, brush_for_background)

    def prompt_for_password(self) -> None:
        """
        Launches a Qt PasswordDialog object whilst connecting the dialog's access level a feature limiter method
        """
        dlg = PasswordDialog(parent=self, config=self.config)
        dlg.access_level_signal.connect(self.password_result)
        dlg.exec()

    @pyqtSlot(str)
    def password_result(self, access_level: str) -> None:
        """
        Disabled certain functionality depending on the access level. Engineers cannot access the "System Config"
        tab, Operators additionally can't access the "Position," "Edit Script" tabs, nor the run step button. Has
        check for invalid access level

        :param access_level: String that should either be 'Engineer', 'Operator', or 'Administrator'
        """
        self.access_level_combo.setCurrentText(access_level)
        self.access_level = access_level

        if access_level == "Engineer":
            self.tabWidget.removeTab(self.tab_text_to_index("System Config"))
        elif access_level == "Operator":
            # Todo: Remove position tab, add more stuff like this later
            self.tabWidget.removeTab(self.tab_text_to_index("System Config"))
            self.tabWidget.removeTab(self.tab_text_to_index("Position"))
            self.tabWidget.removeTab(self.tab_text_to_index("Edit Script"))
            self.run_step_button.setEnabled(False)
        elif access_level == "Administrator":
            self.log(message="Access level maximum, no features restricted", level='info')
        else:
            self.log(message="Invalid access level provided, exiting", level='error')
            sys.exit()

    def tab_text_to_index(self, text: str) -> int:
        """
        Returns the index of the tab with specified text in the main
        tab widget. If no match exists, returns -1. Not case sensitive.

        :param text: The tab text to be searched for in the tabWidget's list of tabs
        :returns: integer representing the index of the tab
        """
        for i in range(self.tabWidget.count()):
            if self.tabWidget.tabText(i).upper() == text.upper():
                return i
        return -1

    # signal connections
    def configure_non_manager_signals(self) -> None:
        """
        As the name describes, connects internal events (such as quit_button.clicked)
        to internal methods that handles additional logic regarding the action/operation
        (former method example connected to class' internal quit_clicked())
        """
        self.quit_button.clicked.connect(self.quit_clicked)

        self.script_editor.script_changed_signal.connect(self.upon_script_changed)
        self.load_button.clicked.connect(self.load_script_clicked)
        self.run_button.clicked.connect(self.run_button_clicked)

        self.run_step_button.clicked.connect(self.run_step_clicked)

        # Hardware control signals
        self.insert_button.clicked.connect(self.position_tab.insert_button_clicked)
        self.retract_button.clicked.connect(self.position_tab.retract_button_clicked)

        # enable/disable buttons signals
        self.position_tab.set_buttons_enabled_signal.connect(self.set_buttons_enabled)
        self.ua_calibration_tab.set_buttons_enabled_signal.connect(self.set_buttons_enabled)
        self.set_scan_tab_signal.connect(self.scan_tab_widget.set_tab_slot)

    # noinspection PyTypeChecker
    def configure_manager_signals(self) -> None:
        """
        Configures all the signals pertaining to manager so various main window events can
        activate methods in the manager class and vice versa.
        """
        self.abort_button.clicked.connect(self.manager.abort_after_step)
        self.abort_immediately_button.clicked.connect(self.manager.abort_immediately)

        self.command_signal.connect(self.manager.exec_command)
        self.yes_signal.connect(self.manager.yes_clicked)
        self.no_signal.connect(self.manager.no_clicked)
        self.manager.enable_ui_signal.connect(self.set_buttons_enabled)

        # Script metadata signals
        self.manager.script_name_signal.connect(self.script_name_field.setText)
        self.manager.created_by_signal.connect(self.created_by_field.setText)
        self.manager.created_on_signal.connect(self.created_on_field.setText)
        self.manager.description_signal.connect(self.script_description_field.setText)
        self.manager.num_tasks_signal.connect(self.set_num_tasks)

        # Calculate progress according to the index of the step, including repeats
        self.manager.task_index_signal.connect(self.visualize_progress)
        # Expand the step according to the number of the step in the .wtf file, excluding repeats
        self.manager.task_number_signal.connect(self.expand_step)

        # When manager loads a script, visualize it in the left pane as well as loading it into the script editor
        self.manager.script_info_signal.connect(self.visualize_script)
        self.manager.script_info_signal.connect(self.script_editor.visualize_script)
        self.manager.script_info_signal.connect(self.update_script_indicator)

        self.manager.test_data.show_results_summary.connect(self.results_tab.populate_results_table)

        self.manager.test_data.show_script_log.connect(self.results_tab.populate_log_table)
        self.manager.element_number_signal.connect(self.live_element_field.setText)
        self.manager.element_number_signal.connect(self.update_script_visual_element_number)

        # Hardware indicator signals
        self.manager.AWG.frequency_signal.connect(self.update_frequency_field)
        self.manager.Balance.connected_signal.connect(self.rfb_indicator.setChecked)
        self.manager.AWG.connected_signal.connect(self.fgen_indicator.setChecked)
        self.manager.thermocouple.connected_signal.connect(self.tcouple_indicator.setChecked)
        self.manager.Oscilloscope.connected_signal.connect(self.scope_indicator.setChecked)
        self.manager.UAInterface.connected_signal.connect(self.wtfib_indicator.setChecked)
        self.manager.IO_Board.connected_signal.connect(self.dio_indicator.setChecked)
        self.manager.thermocouple.reading_signal.connect(self.update_temp_reading)
        self.manager.Motors.connected_signal.connect(self.motion_indicator.setChecked)
        self.manager.Motors.x_pos_mm_signal.connect(self.update_x_pos_field)
        self.manager.Motors.r_pos_mm_signal.connect(self.update_theta_pos_field)
        self.manager.Forward_Power_Meter.connected_signal.connect(self.power_meter_indicator.setChecked)
        self.manager.UAInterface.cal_data_signal.connect(self.ua_calibration_tab.populate_results_table)
        self.manager.script_complete_signal.connect(self.show_script_complete_dialog)
        self.manager.user_prompt_signal.connect(self.show_user_prompt)
        self.manager.user_info_signal.connect(self.show_user_info_dialog)
        self.manager.user_prompt_pump_not_running_signal.connect(self.show_user_prompt_pump_not_running)
        self.manager.user_prompt_signal_water_too_low_signal.connect(self.show_user_prompt_water_too_low)
        self.manager.user_prompt_signal_water_too_high_signal.connect(self.show_user_prompt_water_too_high)
        self.manager.show_write_cal_data_dialog_signal.connect(self.show_write_cal_data_prompt)
        self.manager.retracting_ua_warning_signal.connect(self.show_ua_retract_warn_prompt)
        self.manager.show_filling_dialog_signal.connect(self.show_filling_tank_dialog)
        self.manager.show_draining_dialog_signal.connect(self.show_draining_tank_dialog)
        self.manager.IO_Board.pump_reading_signal.connect(self.update_pump_indicator)
        self.manager.IO_Board.water_level_reading_signal.connect(self.update_water_level_indicator)
        self.manager.Motors.moving_signal.connect(self.update_motors_moving_indicator)
        self.manager.AWG.output_signal.connect(self.update_ua_indicator)
        self.manager.system_info_signal.connect(self.system_info_tab.serial_numbers_slot)
        self.manager.user_question_signal.connect(self.dialog_question)

        # Manager communication signals
        self.load_script_signal.connect(self.manager.load_script)
        self.manager.set_tab_signal.connect(self.set_tab_slot)
        self.manager.set_abort_buttons_enabled_signal.connect(self.abort_buttons_toggle)
        self.manager.no_script_loaded_signal.connect(self.no_script_loaded)
        self.manager.critical_error_signal.connect(self.dialog_critical)

    @pyqtSlot(float)
    def update_frequency_field(self, frequency_mhz: float) -> None:
        """
        Sets the frequency Qt Object to reflect passed frequency parameter of method

        :param frequency_mhz: Frequency of the frequency to show to user in main window fields
        """
        self.frequency_field.setText("%.2f" % frequency_mhz)

    @pyqtSlot(float)
    def update_x_pos_field(self, position_mm: float) -> None:
        """
        Sets the position in x-axis mm Qt Object to reflect passed method parameter

        :param position_mm: position of the x-axis motor to show to user in main window fields
        """
        self.x_pos_field.setText("%.2f" % position_mm)

    @pyqtSlot(float)
    def update_theta_pos_field(self, position_mm: float) -> None:
        """
        Sets the position in r-axis mm Qt Object to reflect passed method parameter

        :param position_mm: position of the r-axis motor to show to user in main window fields
        """
        self.theta_pos_field.setText("%.2f" % position_mm)

    def run_button_clicked(self) -> None:
        """sets the buttons to disabled once a script is running"""
        self.set_buttons_enabled(False)
        self.show_pretest_dialog(begin_script=True)

    def run_step_clicked(self) -> None:
        """
        Tell the manager to advance the script once. If the manager does not have
        test metadata this will load data from the UA and prompt the user for more info
        """
        # If the manager has not yet received test metadata
        if self.manager.test_data.serial_number == "":
            self.show_pretest_dialog(begin_script=False)

        self.abort_buttons_toggle(True)
        self.set_buttons_enabled(False)
        self.command_signal.emit("STEP")

    def upon_script_changed(self) -> None:
        """
        Sets the script_changed flag to true, and changes the
        run button to "SAVE BEFORE RUNNING" in red background
        """
        self.script_changed = True
        self.run_button.setEnabled(False)
        self.run_button.setStyleSheet("background-color:red")
        self.run_button.setText("SAVE BEFORE RUNNING")
        self.run_step_button.setEnabled(False)
        self.run_step_button.setStyleSheet("background-color:red")
        self.run_step_button.setText("SAVE BEFORE RUNNING")

    def upon_script_reloaded(self) -> None:
        """
        Activates if user saved/reloaded script upon change. Resets run
        button to normal text/colors and sets script_changed flag to false
        """
        self.script_changed = False
        self.run_button.setEnabled(True)
        self.run_button.setStyleSheet("background-color:white")
        self.run_button.setText("RUN SCRIPT")
        self.run_step_button.setEnabled(True)
        self.run_step_button.setStyleSheet("background-color:white")
        self.run_step_button.setText("RUN STEP")

    @pyqtSlot(bool)
    def update_ua_indicator(self, on: bool) -> None:
        """
        Changes the UA power indicator to passed parameter for user knowledge

        :param on: True if UA is on, false otherwise
        """
        if on:
            self.ua_on_indicator.setStyleSheet("background-color:green")
            self.ua_on_indicator.setText("UA ON")
        else:
            self.ua_on_indicator.setStyleSheet("background-color:grey")
            self.ua_on_indicator.setText("UA OFF")

    @pyqtSlot(str)
    def update_system_status(self, status: str) -> None:
        """
        Changes text and color of the system indicator according to passed status parameter

        :param status: can be "IDLE" to make background green or something else to make it red
        """
        self.system_indicator.setText(status)
        if status == "IDLE":
            self.system_indicator.setStyleSheet("IDLE")
            self.system_indicator.setStyleSheet("background-color: green")
        else:
            self.system_indicator.setStyleSheet("BUSY")
            self.system_indicator.setStyleSheet("background-color: yellow")

    @pyqtSlot(list)
    def update_script_indicator(self, script_info: list) -> None:
        """
        Changes the script indicator to reflect that a script has been successfully loaded

        :param script_info:
            Unneeded in this method but the signal attached to this method is connected to other
            methods that do need it
        """
        self.script_info = script_info  # INFO: placed here to make unused parameter warning go away
        self.script_status_indicator.setStyleSheet("background-color:green")
        self.script_status_indicator.setText("SCRIPT LOADED")

    @pyqtSlot(bool)
    def update_motors_moving_indicator(self, moving: bool) -> None:
        """
        Changes the moving indicator of the main window to reflect motor movement to the user

        :param moving: True if motors are moving, false otherwise
        """
        if moving:
            self.moving_indicator.setStyleSheet("background-color:green")
            self.moving_indicator.setText("MOVING")
        else:
            self.moving_indicator.setStyleSheet("background-color:grey")
            self.moving_indicator.setText("STATIONARY")

    @pyqtSlot(WaterLevel)
    def update_water_level_indicator(self, water_level: WaterLevel) -> None:
        """
        changes the main window's water level indicator text and
        color according to passed enumerator parameter water_level

        :param water_level: can be below_level, above_level, or level
        """
        if water_level == WaterLevel.below_level:
            self.tank_level_indicator.setStyleSheet("background-color:red")
            self.tank_level_indicator.setText("TANK LOW")
        elif water_level == WaterLevel.above_level:
            self.tank_level_indicator.setStyleSheet("background-color:red")
            self.tank_level_indicator.setText("TANK HIGH")
        elif water_level == WaterLevel.level:
            self.tank_level_indicator.setStyleSheet("background-color:green")
            self.tank_level_indicator.setText("TANK LEVEL")
        else:
            self.log(message="invalid WaterLevel value passed, cannot change indicator", level='warning')

    @pyqtSlot(bool)
    def update_pump_indicator(self, is_on: bool) -> None:
        """
        Changes main window's pump indicator according to passed boolean is_on parameter

        :param is_on: If on, will change indicator to green with on text, grey if false
        """
        if is_on:
            self.ua_pump_indicator.setStyleSheet("background-color: green")
            self.ua_pump_indicator.setText("UA PUMP ON")
        else:
            self.ua_pump_indicator.setStyleSheet("background-color: grey")
            self.ua_pump_indicator.setText("UA PUMP OFF")

    @pyqtSlot(float)
    def update_temp_reading(self, temp: float) -> None:
        """Display the latest temperature reading in the UI"""
        self.temp_field.setText("%.1f" % temp)

    @pyqtSlot(object, object, float)
    def plot(self, x: list, y: list, refresh_rate: float) -> None:
        """
        Triggers the scan_tab_widget's plot_scope method relaying passed variables

        :param x: The list of x-values to plot for the scan tab
        :param y: The list of y-values that must correspond to the x-values
        :param refresh_rate: number of times values are updated per second, shown to user
        """
        self.scan_tab_widget.plot_scope(x, y, refresh_rate)

    def load_script_clicked(self) -> None:
        """
        Launches find file dialog box to locate either a .wtf or .txt script file; also emits the load script signal
        """
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", ROOT_DIR + "/Scripts", "Script files (*.wtf *.txt)"
        )

        if path == "":
            return

        self.load_script_signal.emit(path)

    @pyqtSlot(bool)
    def load_results(self, triggered: bool) -> None:
        """
        call's the result tab's load_test_results method and tries to populate its table with exception handling

        :param triggered:
            Unused variable, presumably needed since attached signal is connected to other methods that needs parameter
        """
        self.results_tab.load_test_results()
        try:
            self.results_tab.populate_results_table()
        except Exception:
            self.log(f"Invalid file; passed triggered value = {triggered}")

    @pyqtSlot(int)
    def set_num_tasks(self, num_tasks: int) -> None:
        """
        Setter method for the number of tasks script has, stores to self.num_tasks

        :param num_tasks: Number of tasks script has
        """
        self.num_tasks = num_tasks

    @pyqtSlot(int)
    def visualize_progress(self, step_index: int) -> None:
        """
        Updates the progress bar as the script runs to reflect how many tasks are completed out of total tasks

        :param step_index: Which task the program is currently on, used to calculate progress percentage
        """
        if not self.progress_bar_ready:
            return
        self.progress_bar_ready = False  # acts as mutex to prevent Qt's progressBar from being accessed simultaneously
        if self.num_tasks != 0:
            self.progressBar.setValue(int(step_index / self.num_tasks * 100))
        self.progress_bar_ready = True

    def popup(self, text_to_show: str) -> None:
        """
        Launches generic Qt message box with passed string as text to be shown

        :param text_to_show: String to show the user upon message popup
        """
        popup = QMessageBox()
        popup.setWindowTitle(" ")
        popup.setText(text_to_show)
        popup.exec()
        self.cont_signal.emit()

    # QUESTION: what does the parameter win do?
    # noinspection PyUnresolvedReferences
    def setupUi(self, win) -> None:
        """
        Sets up various signals and tool tips for basic window elements such as open file actions and help button, etc.

        :param win: Unused parameter, unsure why it's here
        """
        super().setupUi(self)

        file_menu = self.menuBar().addMenu("&File")

        # INFO: commented out because this variable is never used
        # open_file_action = QAction(
        #     QIcon(os.path.join("images", "blue-folder-open-document.png")),
        #     "Open scan data",
        #     self,
        # )
        open_result_file_action = QAction(
            QIcon(os.path.join("images", "blue-folder-open-document.png")),
            "Open result data",
            self,
        )
        open_result_file_action.setStatusTip("Open file")
        open_result_file_action.triggered.connect(self.load_results)
        file_menu.addAction(open_result_file_action)

        print_action = QAction(QIcon(os.path.join("images", "printer.png")), "Print notes", self)
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)

        # adding Help on menu bar and open a specific file saved as "Help"
        file_menu = self.menuBar().addMenu("&Help")

        show_help_action = QAction(
            QIcon(os.path.join("images", "blue-folder-open-document.png")),
            "Open Help",
            self,
        )
        show_help_action.setStatusTip("Open Help")
        show_help_action.triggered.connect(self.show_help)
        file_menu.addAction(show_help_action)

    @staticmethod
    def show_help() -> None:
        """Opens the help document (help.txt in project directory)"""
        # todo: fill in help.txt
        webbrowser.open("readme.md")

    # INFO: editor Qt object doesn't exist, from old project, no save as action in toolbar
    # Menu bar Actions
    # def file_save_as(self) -> None:
    #     """
    #     Relay helper method that launches path selection box, checks
    #     its validity and launches class' _save_to_path method
    #     """
    #     path, _ = QFileDialog.getSaveFileName(
    #         self, caption="Save file", directory="", filter="Text documents (*.txt)"
    #     )
    #
    #     if not path:
    #         # If dialog is cancelled, will return ''
    #         return
    #
    #     self._save_to_path(path=path)
    #
    # def _save_to_path(self, path: str) -> None:
    #     """
    #     Writes text file with main window's 'editor' object as the content of the new text file
    #
    #     :param path: path to save contents of main windows 'editor' object in text file
    #     """
    #     text = self.editor.toPlainText()
    #     try:
    #         with open(path, "w") as output_file:
    #             output_file.write(text)
    #
    #     except Exception as e:
    #         self.dialog_critical(str(e))
    #
    #     else:  # if no exceptions occurred above
    #         self.path = path
    #
    #         # Updating the Feedback window
    #         progress = "Document Saved"
    #         self.feedback_Update.append(str(progress))

    def file_print(self) -> None:
        """
        notes widget does not exist, from old project
        """
        from PyQt5.QtPrintSupport import QPrintDialog

        dlg = QPrintDialog()
        if dlg.exec_():
            self.NotesWidget.textEdit.print_(dlg.printer())

        # Updating the Feedback window
        progress = "Notes Printed"
        self.log(str(progress))

    def quit_clicked(self) -> None:
        """
        Activated when the user wants to exit the application. Lessens chance of accidental closure
        """
        b_quit = False
        q_reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Do you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if q_reply == QMessageBox.Yes:
            b_quit = True
            self.manager.wrap_up()
            t.sleep(0.1)
            self.manager.exit()
        if b_quit:
            self.close()

    # WARNING: do not change name, overrides Qt's default closeEvent() method
    def closeEvent(self, event: QEvent) -> None:
        """
        Launches confirmation dialog if user closes the application from the scope of the Windows OS

        :param event: The close event that we want to confirm
        """
        b_quit = False
        q_reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Do you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if q_reply == QMessageBox.Yes:
            b_quit = True
            self.manager.wrap_up()
            self.manager.exit()
        if b_quit:
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def show_filling_tank_dialog(self) -> None:
        """
        Launches dialog signifying that the tank is filling for the user's knowledge
        """
        dlg = FillingDialog(config=self.config)
        self.manager.IO_Board.tank_full_signal.connect(dlg.tank_full_slot)
        dlg.tank_full_override_signal.connect(self.manager.IO_Board.tank_full_override_slot)
        dlg.exec()

    @pyqtSlot(WaterLevel)
    def show_draining_tank_dialog(self, target_level: WaterLevel) -> None:
        """
        Launches the tank draining dialog for the user

        :param target_level: Either should be draining to level or complete drain
        """
        dlg = DrainingDialog(config=self.config, target_level=target_level)
        self.manager.IO_Board.water_level_reading_signal.connect(dlg.water_level_slot)
        dlg.exec()

    @pyqtSlot(str)
    def show_pretest_dialog(self, begin_script: bool = True) -> None:
        """
        Launches the pretest initialisation dialog where the user may input their operator name, UA
        serial number with the option to look it up and auto-populate the LF, HF, and hardware code
        with an optional override tick, and an optional comment (hence the str in the pyqtSlot).

        :param begin_script:
            whether the manager should begin scripting after the dialog is handled. If The run button
            was clicked this will be true, if the run step button was clicked this will be false.
        """
        # Read UA serial number
        ua_read_data, firmware_version, status = self.UAInterface.read_data()
        # If their access level is operator, do not proceed with the script unless the read was successful.

        if status != 0:
            if self.access_level_combo.currentText() == "Operator":
                self.dialog_critical("UA Read failed, aborting test")
                self.abort_instantly_signal.emit()
                return
            elif self.config["Debugging"]["end_script_on_errors"]:
                self.dialog_critical(
                    "UA Read failed, aborting test. Disable end_script_on_errors in the "
                    "config if you wish to continue"
                )
        if ua_read_data:  # ua_read_data != [] is just "ua_read_data"
            serial_no = ua_read_data[1]
        else:
            serial_no = None

        if len(ua_read_data) < 1:
            ua_read_data.append("UA Not Connected")

        dlg = PretestDialog(serial_no=serial_no, schema=ua_read_data[0],
                            access_level=self.access_level_combo.currentText(),
                            config=self.config, begin_script=begin_script)
        # below: calls method in manager that latches all input variables from dialog box to variables in manager class
        # when OK button is clicked
        dlg.pretest_metadata_signal.connect(self.manager.test_metadata_slot)
        dlg.abort_signal.connect(self.manager.abort_clicked)
        dlg.abort_signal.connect(lambda: self.set_buttons_enabled(True))
        dlg.exec()

    @pyqtSlot(str, bool)
    def show_user_prompt(self, message: str, restrict_continue: bool) -> None:
        """
        Method to launch the user prompt dialog where the user can select between continue, retry, and abort.

        :param message: String message to show the user for the prompt
        :param restrict_continue: Disables the continue button if true, for users that do not have elevated privileges
        """
        dlg = WTFUserPrompt(config=self.config, access_level=self.access_level, restrict_continue=restrict_continue)
        dlg.user_prompt_output.setText(message)
        if message == "Do you want to write calibration data to UA?":
            # dlg.continue_button.setText('Yes')
            dlg.continue_button.setText('No')
            # dlg.continue_signal.connect(self.manager.yes_clicked)
            dlg.continue_signal.connect(self.manager.no_clicked)
            # dlg.abort_button.setText('No')
            dlg.abort_button.setText('Yes')
            # dlg.abort_signal.connect(self.manager.no_clicked)
            dlg.abort_signal.connect(self.manager.yes_clicked)
            dlg.retry_button.hide()
            dlg.retry_button.setVisible(False)
            dlg.retry_button.setEnabled(False)
        elif message == "Warning: the on or off intervals are less than the sensor settling time specified in the " \
                        "config file. Either change it or load a different script":
            dlg.abort_signal.connect(self.manager.abort_immediately)
        else:
            dlg.abort_signal.connect(self.manager.abort_clicked)
            dlg.retry_signal.connect(self.manager.retry_clicked)
            dlg.continue_signal.connect(self.manager.continue_clicked)

        dlg.exec()

    @pyqtSlot(str)
    def show_user_info_dialog(self, message: str) -> None:
        """
        Method to show the user a simple information dialog, the user can only click continue.

        :param message: Informational message to show the user
        """
        dlg = WTFUserInfo(config=self.config)
        dlg.user_prompt_output.setText(message)
        dlg.continue_signal.connect(self.manager.continue_clicked)
        dlg.exec()

    @pyqtSlot()
    def show_ua_retract_warn_prompt(self):
        """method to launch the ultrasound actuator retracting warning dialog """
        dlg = UARetractDialog(config=self.config)
        dlg.continue_signal.connect(self.manager.continue_clicked)
        dlg.abort_signal.connect(self.manager.abort_immediately)
        dlg.exec()

    @pyqtSlot(list, list)
    def show_script_complete_dialog(self, passed_ray: list, description_ray: list) -> None:
        """
        Launches the script complete message that shows the various
        details of the tests for all the elements and connects various

        :param passed_ray: The pass/fail/DNF list for all actuators and overall device
        :param description_ray: The description list for all actuators and overall device
        """
        dlg = ScriptCompleteDialog(
            passed_ray=passed_ray, description_ray=description_ray, config=self.config
        )
        dlg.continue_signal.connect(self.manager.continue_clicked)
        dlg.abort_signal.connect(self.manager.abort_clicked)

    @pyqtSlot(str)
    def dialog_critical(self, text: str) -> None:
        """
        Method to show a customizable critical error dialog for the user and sets the buttons and icon of the dialog
        popup.

        :param text: Sets text of dialog to string text parameter
        """
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Error")
        dlg.setText("The application has encountered a critical error")
        dlg.setInformativeText(f"{text}\n\nYou may launch this application with the command"
                               f" prompt to see more verbose information, you may also contact "
                               f"the developers for assistance via email: isaiah@8foldmfg.com")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Critical)
        dlg.setWindowFlag(Qt.Qt.WindowType.WindowStaysOnTopHint)
        dlg.exec()

    @pyqtSlot(str)
    def dialog_question(self, question_str: str) -> None:
        """
        Method to ask the user a question and record/emit the response via GUI

        :param question_str: The question text to show the user
        """
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Question")
        dlg.setIcon(QMessageBox.Question)
        answer = dlg.question(self, '', question_str, dlg.Yes | dlg.No)
        if answer == dlg.Yes:
            self.yes_signal.emit()
        elif answer == dlg.No:
            self.no_signal.emit()

    @pyqtSlot(list)
    def show_write_cal_data_prompt(self, calibration_data: list) -> None:
        """
        Shows the user a prompt to write the calibration data to the ultrasound actuator and connects various signals.

        :param calibration_data: a 2d list representing the calibration data to be written to the prompt
        """
        dlg = WriteCalDataToUA()
        dlg.schema.setText(calibration_data[0][0])
        dlg.serial_no.setText(calibration_data[0][1])
        dlg.prod_date.setText(calibration_data[0][2])
        dlg.hardware_code.setText(calibration_data[0][3])
        dlg.common_lo_freq.setText(calibration_data[0][4])
        dlg.common_hi_freq.setText(calibration_data[0][5])
        dlg.beam_align.setText(calibration_data[0][6])
        dlg.command.setText(calibration_data[0][7])
        dlg.status.setText(calibration_data[0][8])
        dlg.fw_version.setText(calibration_data[0][9])

        dlg.schema_lo.setText(calibration_data[1][0])
        dlg.serial_no_lo.setText(calibration_data[1][1])
        dlg.prod_date_lo.setText(calibration_data[1][2])
        dlg.hardware_code_lo.setText(calibration_data[1][3])
        dlg.common_lo_freq_lo.setText(calibration_data[1][4])
        dlg.common_hi_freq_lo.setText(calibration_data[1][5])
        dlg.beam_align_lo.setText(calibration_data[1][6])
        dlg.command_lo.setText(calibration_data[1][7])
        dlg.status_lo.setText(calibration_data[1][8])
        dlg.fw_version_lo.setText(calibration_data[1][9])

        dlg.schema_hi.setText(calibration_data[2][0])
        dlg.serial_no_hi.setText(calibration_data[2][1])
        dlg.prod_date_hi.setText(calibration_data[2][2])
        dlg.hardware_code_hi.setText(calibration_data[2][3])
        dlg.common_lo_freq_hi.setText(calibration_data[2][4])
        dlg.common_hi_freq_hi.setText(calibration_data[2][5])
        dlg.beam_align_hi.setText(calibration_data[2][6])
        dlg.command_hi.setText(calibration_data[2][7])
        dlg.status_hi.setText(calibration_data[2][8])
        dlg.fw_version_hi.setText(calibration_data[2][9])

        # dlg.write_ua_signal.connect(self.manager.write_calibration_data_to_ua_button)
        dlg.abort_signal.connect(self.manager.abort_after_step)
        dlg.exec()

    @pyqtSlot(str)
    def show_user_prompt_pump_not_running(self, pump_status: str) -> None:
        """
        Shows the user a warning that the ultrasound actuator pump is not running. Waits for the user's response
        and connects the dialog's continue and abort signals to the manager's respective internal variables

        :param pump_status: The UA pump status to be shown to the user for their knowledge
        """
        dlg = WTFUserPromptPumpNotRunning(config=self.config)
        dlg.label.setText(pump_status)
        # todo: have ua_pump_status switch react to pump_status var
        dlg.continue_signal.connect(self.manager.continue_clicked)
        dlg.abort_signal.connect(self.manager.abort_clicked)
        dlg.exec()

    @pyqtSlot()
    def show_user_prompt_water_too_low(self) -> None:
        """
        Shows the user a warning that the water level is too low and waits for their response to the dialog via
        connecting the dialog's continue and abort buttons to the manager's internal respective variables
        """
        dlg = WTFUserPromptWaterTooLow()
        # todo: have ua_water_level switch react to water_level var
        dlg.continue_signal.connect(self.manager.continue_clicked)
        dlg.abort_signal.connect(self.manager.abort_clicked)
        dlg.exec()

    @pyqtSlot()
    def show_user_prompt_water_too_high(self) -> None:
        """
        Shows the user a warning that the water level is too high, connects the 'continue' and 'abort'
        signal from the dialog to the manager's respective variables via a signal connect relay.
        """
        dlg = WTFUserPromptWaterTooHigh()
        # todo: have ua_water_level switch react to water_level var
        dlg.continue_signal.connect(self.manager.continue_clicked)
        dlg.abort_signal.connect(self.manager.abort_clicked)
        dlg.exec()

    @pyqtSlot()
    def no_script_loaded(self) -> None:
        """
        disables the run, abort, run_step and abort_immediately buttons
        """
        self.run_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.run_step_button.setEnabled(False)
        self.abort_immediately_button.setEnabled(False)

    @pyqtSlot(bool)
    def abort_buttons_toggle(self, enabled: bool) -> None:
        """
        Boolean toggle for the abort and abort_immediately buttons

        :param enabled: if true, enables buttons; disables if false
        """
        self.abort_button.setEnabled(enabled)
        self.abort_immediately_button.setEnabled(enabled)

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled: bool) -> None:
        # Todo: make this enable/disable all buttons of all tabs that could interfere with operations in progress
        """
        Enables/disables various buttons in the UI depending on the boolean parameter 'enabled'

        :param enabled: if true, enables all buttons specified in method; disables if false
        """

        if enabled:
            self.update_system_status("IDLE")
        else:
            self.update_system_status("BUSY")

        # section for tabs
        # todo: add more calls to tabs' set buttons enabled
        self.position_tab.set_buttons_enabled(enabled)
        self.scan_tab_widget.set_buttons_enabled(enabled)
        self.results_tab.set_buttons_enabled(enabled)
        self.ua_calibration_tab.set_buttons_enabled(enabled)
        self.system_config.set_buttons_enabled(enabled)
        self.system_info_tab.set_buttons_enabled(enabled)
        self.rfb.set_buttons_enabled(enabled)
        self.script_editor.set_buttons_enabled(enabled)

        # main window buttons
        self.insert_button.setEnabled(enabled)
        self.retract_button.setEnabled(enabled)
        self.run_button.setEnabled(enabled and not self.script_changed)
        self.load_button.setEnabled(enabled)
        # user must be above operator permissions to run individual steps
        if self.access_level_combo.currentText().upper() != "Operator".upper():
            self.run_step_button.setEnabled(enabled)
        else:
            self.run_step_button.setEnabled(False)

    def log(self, message, level="info") -> None:
        """
        relay method to write log commands faster, takes the message and log level as arguments

        :param message: The string to be shown in the console and in the log file
        :param level: the severity level of the message to be shown to the user (warn, info, debug, or error)
        """
        log_msg(self, root_logger, message=message, level=level)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyle("fusion")
    window.show()
    sys.exit(app.exec_())

import time as t
import webbrowser
from typing import List
from ui_elements.Dialogs.ui_password_dialog import PasswordDialog
from ui_elements.Dialogs.ui_script_complete_dialog import ScriptCompleteDialog
from ui_elements.Dialogs.ui_pretest_dialog import PretestDialog
from ui_elements.Dialogs.ui_user_prompt import WTFUserPrompt
from ui_elements.Dialogs.ui_retracting_ua_warning import UARetractDialog
from ui_elements.Dialogs.ui_user_prompt_water_too_high import WTFUserPromptWaterTooHigh
from ui_elements.Dialogs.ui_write_cal_to_ua import WriteCalDataToUA
from ui_elements.Dialogs.ui_user_prompt_pump_not_running import WTFUserPromptPumpNotRunning
from ui_elements.Dialogs.ui_user_prompt_water_too_low import WTFUserPromptWaterTooLow
from ui_elements.Dialogs.filling_dialog import FillingDialog
from ui_elements.Dialogs.draining_dialog import DrainingDialog
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeWidgetItem, QFileDialog, QAction, QMessageBox, QApplication, QMainWindow
from PyQt5.QtGui import QColor, QBrush
from Widget_Library import window_wet_test
from manager import Manager
from Utilities.load_config import load_configuration
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT
import logging
from Utilities.useful_methods import log_msg
import os
from definitions import ROOT_DIR, WaterLevel

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
wtf_logger.addHandler(file_handler)
wtf_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)
log_formatter = logging.Formatter(LOGGER_FORMAT)

import sys

from PyQt5.QtCore import (QThread)


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

    manager: Manager

    threading = False
    thread_list: List[QThread]

    command_signal = QtCore.pyqtSignal(str)
    abort_instantly_signal = QtCore.pyqtSignal()
    load_script_signal = QtCore.pyqtSignal(str)  # str is the path to the file
    num_tasks = 0  # the number of tasks in the current script. Used to calculate progress
    progress_bar_ready = True  # variables to prevent signals from refreshing UI elements too quickly
    script_changed = False  # prevents user from running a script if it has been modified and not reloaded

    # List of dictionaries representing each task and its arguments (repeats excluded)

    def __init__(self):
        # Load default.yaml file to self.config as a python dictionary
        super(MainWindow, self).__init__()
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
        self.pass_config_and_ui_elements_to_tabs()

    def connect_ui_thread_devices(self):
        # Note: the UA interface box is instantiated in both the manager and the UI thread.
        # This is done to improve responsiveness, as triggering UI dialogs with a signal causes a delay.
        # There should be no conflicts between the two objects, as they both just send commands to the exe file
        if self.config['Debugging']['simulate_hw']:
            from Hardware.Simulated.simulated_ua_interface import SimulatedUAInterface
            self.UAInterface = SimulatedUAInterface(config=self.config)
        else:
            from Hardware.ua_interface import UAInterface
            self.UAInterface = UAInterface(config=self.config)

    def style_ui(self):
        self.setWindowTitle('Wet Test Fixture Python Interface')

        self.setWindowIcon(QIcon('resources/8foldlogo.ico'))
        self.tabWidget.setCurrentIndex(0)

        # Format treewidget
        self.script_step_view.setColumnCount(2)
        self.script_step_view.setHeaderLabels(["Task", "Arguments"])
        self.script_step_view.header().resizeSection(0, 220)

        # Set defaults for indicators
        self.system_indicator.setStyleSheet('BUSY')
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

    def pass_config_and_ui_elements_to_tabs(self):
        # Pass config file to tab widgets
        self.system_config.set_config(self.config)
        self.position_tab.set_config(self.config)
        self.rfb.set_config(self.config)
        self.results_tab.set_config(self.config)
        self.ua_calibration_tab.set_config(self.config)
        self.scan_tab_widget.set_config(self.config)
        self.scan_tab_widget.set_tabWidget(self.tabWidget)
        self.script_editor.set_tree_widget(self.script_step_view)

    def begin_manager_thread(self):
        self.manager = Manager(parent=self, config=self.config)
        self.thread_list.append(self.manager)
        self.configure_manager_signals()
        self.pass_manager_and_hardware_to_tabs()

        # Begin the thread
        self.threading = True
        self.manager.start(priority=QThread.HighPriority)
        self.command_signal.emit('CONNECT')

    def pass_manager_and_hardware_to_tabs(self):
        self.rfb.set_manager(self.manager)
        self.rfb.set_balance(self.manager.Balance)
        self.position_tab.set_manager(self.manager)
        self.position_tab.set_motors(self.manager.Motors)
        self.ua_calibration_tab.set_manager(self.manager)
        self.ua_calibration_tab.set_ua_interface(self.manager.UAInterface)
        self.scan_tab_widget.set_manager(self.manager)

    # Display the task names and arguments from the script parser with a QTreeView
    def visualize_script(self, var_dicts: list):
        self.upon_script_reloaded()
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        self.script_step_view.clear()
        self.list_of_var_dicts = var_dicts

        task_dict = {}
        for i in range(len(self.list_of_var_dicts)):
            if not '# of Tasks' in self.list_of_var_dicts[i].keys():
                arg_list = list()
                for key in self.list_of_var_dicts[i]:
                    if not key == "Task type":
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

    def update_script_visual_element_number(self, element_number):
        if 'Element' in element_number:
            return
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        rootItem = self.script_step_view.invisibleRootItem()
        for i in range(rootItem.childCount()):
            task = rootItem.child(i)
            for j in range(task.childCount()):
                var = task.child(j)
                var_name = var.text(0)
                var_value = var.text(1)
                # If the variable is an element number that is looped
                if var_name == 'Element' and ('Current' in var_value or not 'Element' in var_value):
                    var.setText(1, f'Current: {self.live_element_field.text()}')

    @pyqtSlot(int)
    def set_tab_slot(self, index):
        self.tabWidget.setCurrentIndex(index)

    @pyqtSlot(int)
    def expand_step(self, step_index):  # current_step should match "Task type" from above
        root_item = self.script_step_view.invisibleRootItem()
        child_count = root_item.childCount()

        for i in range(child_count):
            item = root_item.child(i)

            if i == step_index:
                item.setExpanded(True)
                blue_background = QColor(95, 180, 230)
                brush_for_background = QBrush(blue_background)
                item.setBackground(0, brush_for_background)
            else:
                item.setExpanded(False)
                white_background = QColor(255, 255, 255)
                brush_for_background = QBrush(white_background)
                item.setBackground(0, brush_for_background)

    def prompt_for_password(self):
        dlg = PasswordDialog(parent=self, config=self.config)
        dlg.access_level_signal.connect(self.password_result)
        dlg.exec()

    @pyqtSlot(str)
    def password_result(self, access_level):
        if access_level == 'Engineer':

            self.tabWidget.removeTab(7)
        elif access_level == 'Operator':
            # Remove position tab, add more stuff like this later
            self.tabWidget.removeTab(6)
            self.tabWidget.removeTab(6)
        elif access_level == 'Administrator':
            self.tabWidget.removeTab(6)
        else:
            sys.exit()

    def configure_non_manager_signals(self):
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

    def configure_manager_signals(self):
        self.abort_button.clicked.connect(self.manager.abort)
        self.command_signal.connect(self.manager.exec_command)
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
        self.manager.user_prompt_pump_not_running_signal.connect(self.show_user_prompt_pump_not_running)
        self.manager.user_prompt_signal_water_too_low_signal.connect(self.show_user_prompt_water_too_low)
        self.manager.user_prompt_signal_water_too_high_signal.connect(self.show_user_prompt_water_too_high)
        self.manager.write_cal_data_to_ua_signal.connect(self.show_write_cal_data_prompt)
        self.manager.retracting_ua_warning_signal.connect(self.show_ua_retract_warn_prompt)
        self.manager.IO_Board.filling_signal.connect(self.show_filling_tank_dialog)
        self.manager.IO_Board.draining_signal.connect(self.show_draining_tank_dialog)
        self.manager.IO_Board.pump_reading_signal.connect(self.update_pump_indicator)
        self.manager.IO_Board.water_level_reading_signal.connect(self.update_water_level_indicator)
        self.manager.Motors.moving_signal.connect(self.update_motors_moving_indicator)
        self.manager.AWG.output_signal.connect(self.update_ua_indicator)
        self.manager.system_info_signal.connect(self.system_info_tab.system_info_slot)

        # Manager communication signals
        self.abort_instantly_signal.connect(self.manager.abort)
        self.load_script_signal.connect(self.manager.load_script)
        self.manager.set_tab_signal.connect(self.set_tab_slot)

    @pyqtSlot(float)
    def update_frequency_field(self, frequency_MHz):
        self.frequency_field.setText('%.2f' % frequency_MHz)

    @pyqtSlot(float)
    def update_x_pos_field(self, position_mm):
        self.x_pos_field.setText('%.2f' % position_mm)

    @pyqtSlot(float)
    def update_theta_pos_field(self, position_mm):
        self.theta_pos_field.setText('%.2f' % position_mm)

    def run_button_clicked(self):
        self.set_buttons_enabled(False)
        self.show_pretest_dialog()

    def run_step_clicked(self):
        self.set_buttons_enabled(False)
        self.command_signal.emit("STEP")

    def upon_script_changed(self):
        self.script_changed = True
        self.run_button.setEnabled(False)
        self.run_button.setStyleSheet("background-color:red")
        self.run_button.setText("RUN SCRIPT (Reload)")

    def upon_script_reloaded(self):
        self.script_changed = False
        self.run_button.setEnabled(True)
        self.run_button.setStyleSheet("background-color:white")
        self.run_button.setText("RUN SCRIPT")

    @pyqtSlot(bool)
    def update_ua_indicator(self, on):
        if on:
            self.ua_on_indicator.setStyleSheet("background-color:green")
            self.ua_on_indicator.setText("UA ON")
        else:
            self.ua_on_indicator.setStyleSheet("background-color:grey")
            self.ua_on_indicator.setText("UA OFF")

    @pyqtSlot(str)
    def update_system_status(self, status):
        self.system_indicator.setText(status)
        if status == 'IDLE':
            self.system_indicator.setStyleSheet('IDLE')
            self.system_indicator.setStyleSheet("background-color: green")
        else:
            self.system_indicator.setStyleSheet('BUSY')
            self.system_indicator.setStyleSheet("background-color: yellow")

    @pyqtSlot(list)
    def update_script_indicator(self, script_info):
        self.script_status_indicator.setStyleSheet("background-color:green")
        self.script_status_indicator.setText("SCRIPT LOADED")

    @pyqtSlot(bool)
    def update_motors_moving_indicator(self, moving):
        if moving:
            self.moving_indicator.setStyleSheet("background-color:green")
            self.moving_indicator.setText("MOVING")
        else:
            self.moving_indicator.setStyleSheet("background-color:grey")
            self.moving_indicator.setText("STATIONARY")

    @pyqtSlot(WaterLevel)
    def update_water_level_indicator(self, water_level):
        if water_level == WaterLevel.below_level:
            self.tank_level_indicator.setStyleSheet("background-color:red")
            self.tank_level_indicator.setText("TANK LOW")
        elif water_level == WaterLevel.above_level:
            self.tank_level_indicator.setStyleSheet("background-color:red")
            self.tank_level_indicator.setText("TANK HIGH")
        elif water_level == WaterLevel.level:
            self.tank_level_indicator.setStyleSheet("background-color:green")
            self.tank_level_indicator.setText("TANK LEVEL")

    @pyqtSlot(bool)
    def update_pump_indicator(self, is_on):
        if is_on:
            self.ua_pump_indicator.setStyleSheet("background-color: green")
            self.ua_pump_indicator.setText("UA PUMP ON")
        else:
            self.ua_pump_indicator.setStyleSheet("background-color: grey")
            self.ua_pump_indicator.setText("UA PUMP OFF")

    """Command the motors to go to the insertion point"""

    @pyqtSlot(float)
    def update_temp_reading(self, temp):
        self.temp_field.setText('%.1f' % (temp / 50))  # todo: remove /50 its for demo purposes

    @pyqtSlot(object, object, float)
    def plot(self, x, y, refresh_rate):
        self.scan_tab_widget.plot_scope(x, y, refresh_rate)

    def load_script_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Script files (*.wtf *.txt)")

        if path == '':
            return

        self.load_script_signal.emit(path)

    @pyqtSlot(bool)
    def load_results(self, triggered):
        self.results_tab.load_test_results()
        try:
            self.results_tab.populate_results_table()
        except:
            self.log("Invalid file")

    @pyqtSlot(int)
    def set_num_tasks(self, num_tasks):
        self.num_tasks = num_tasks

    @pyqtSlot(int)
    def visualize_progress(self, step_index):
        if not self.progress_bar_ready:
            return
        self.progress_bar_ready = False
        if not self.num_tasks == 0:
            self.progressBar.setValue(int((step_index) / self.num_tasks * 100))
        self.progress_bar_ready = True

    def popup(self, s):
        popup = QMessageBox()
        popup.setWindowTitle(" ")
        popup.setText(s)
        popup.exec()
        self.cont_signal.emit()

    def setupUi(self, MainWindow):
        super().setupUi(self)

        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(
            QIcon(os.path.join("images", "blue-folder-open-document.png")),
            "Open scan data",
            self,
        )
        open_result_file_action = QAction(
            QIcon(os.path.join("images", "blue-folder-open-document.png")),
            "Open result data",
            self,
        )
        open_result_file_action.setStatusTip("Open file")
        open_result_file_action.triggered.connect(self.load_results)
        file_menu.addAction(open_result_file_action)

        print_action = QAction(
            QIcon(os.path.join("images", "printer.png")), "Print notes", self
        )
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)

        # adding Help on menu bar and open a specific file saved as "Help"
        file_menu = self.menuBar().addMenu("&Help")

        Show_Help_action = QAction(
            QIcon(os.path.join("images", "blue-folder-open-document.png")),
            "Open Help",
            self,
        )
        Show_Help_action.setStatusTip("Open Help")
        Show_Help_action.triggered.connect(self.Show_Help)
        file_menu.addAction(Show_Help_action)

    # Open help document
    def Show_Help(self):
        webbrowser.open("Help.txt")

    # Menu bar Actions
    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save file", "", "Text documents (*.txt)"
        )

        if not path:
            # If dialog is cancelled, will return ''
            return

        self._save_to_path(path)

    def _save_to_path(self, path):
        text = self.editor.toPlainText()
        try:
            with open(path, "w") as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path

            # Updating the Feedback window
            Progress = "Document Saved"
            self.feedback_Update.append(str(Progress))

    def file_print(self):
        from PyQt5.QtPrintSupport import QPrintDialog

        dlg = QPrintDialog()
        if dlg.exec_():
            self.NotesWidget.textEdit.print_(dlg.printer())

        # Updating the Feedback window
        Progress = "Notes Printed"
        self.log(str(Progress))

    def closeEvent(self, event):
        bQuit = False
        qReply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Do you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if qReply == QMessageBox.Yes:
            bQuit = True
            self.manager.wrap_up()
            t.sleep(.1)
            self.manager.exit()
        if bQuit:
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def show_filling_tank_dialog(self):
        dlg = FillingDialog(config=self.config)
        self.manager.IO_Board.water_level_reading_signal.connect(dlg.water_level_slot)
        dlg.exec()

    @pyqtSlot(WaterLevel)
    def show_draining_tank_dialog(self, target_level):
        dlg = DrainingDialog(config=self.config, target_level=target_level)
        self.manager.IO_Board.water_level_reading_signal.connect(dlg.water_level_slot)
        dlg.exec()

    @pyqtSlot(str)
    def show_pretest_dialog(self):
        # Read UA serial number
        UA_read_data, status = self.UAInterface.read_data()

        # If their access level is operator, do not proceed with the script unless the read was successful.

        if status != 0:
            if self.access_level_combo.currentText() == "Operator":
                self.dialog_critical("UA Read failed, aborting test")
                self.abort_instantly_signal.emit()
                return
            elif self.config["Debugging"]["end_script_on_errors"]:
                self.dialog_critical("UA Read failed, aborting test. Disable end_script_on_errors in the "
                                     "config if you wish to continue")
        if UA_read_data != []:
            serial_no = UA_read_data[1]
        else:
            serial_no = None

        dlg = PretestDialog(serial_no=serial_no)
        # below: calls method in manager that latches all input variables from dialog box to variables in manager class
        # when OK button is clicked
        dlg.pretest_metadata_signal.connect(self.manager.pretest_metadata_slot)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot(str)
    def show_user_prompt(self, message):
        dlg = WTFUserPrompt(config=self.config)
        dlg.user_prompt_output.setText(message)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.retry_signal.connect(self.manager.retry)
        dlg.continue_signal.connect(self.manager.cont)
        dlg.exec()

    @pyqtSlot()
    def show_ua_retract_warn_prompt(self):
        dlg = UARetractDialog(config=self.config)
        dlg.continue_signal.connect(self.manager.cont)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot(list, list)
    def show_script_complete_dialog(self, passed_ray, description_ray):
        dlg = ScriptCompleteDialog(passed_ray=passed_ray, description_ray=description_ray, config=self.config)
        dlg.continue_signal.connect(self.manager.cont)
        dlg.abort_signal.connect(self.manager.abort)

    def dialog_critical(self, text):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Error")
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Critical)
        dlg.exec()

    # todo: test
    @pyqtSlot()
    def show_write_cal_data_prompt(self, calibration_data):  # calibration data var is 2d list
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

        dlg.write_ua_signal.connect(self.manager.write_cal_data_to_ua_button)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot(str)
    def show_user_prompt_pump_not_running(self, pump_status):
        dlg = WTFUserPromptPumpNotRunning(config=self.config)
        dlg.label.setText(pump_status)
        # todo: have ua_pump_status switch react to pump_status var
        dlg.continue_signal.connect(self.manager.cont)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot()
    def show_user_prompt_water_too_low(self):
        dlg = WTFUserPromptWaterTooLow()
        # todo: have ua_water_level switch react to water_level var
        dlg.continue_signal.connect(self.manager.cont)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot()
    def show_user_prompt_water_too_high(self):
        dlg = WTFUserPromptWaterTooHigh()
        # todo: have ua_water_level switch react to water_level var
        dlg.continue_signal.connect(self.manager.cont)
        dlg.abort_signal.connect(self.manager.abort)
        dlg.exec()

    @pyqtSlot(list, list)
    def show_script_complete_dialog(self, passed_ray, description_ray):
        dlg = ScriptCompleteDialog(config=self.config, passed_ray=passed_ray, description_ray=description_ray)
        dlg.abort_signal.connect(self.manager.cont)
        dlg.continue_signal.connect(self.manager.cont)
        dlg.exec()

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled):
        # Todo: make this ebable/disable all buttons of all tabs that could interfere with operations in progress
        if enabled:
            self.update_system_status('IDLE')
        else:
            self.update_system_status('BUSY')

        self.position_tab.set_buttons_enabled(enabled)
        self.insert_button.setEnabled(enabled)
        self.retract_button.setEnabled(enabled)
        self.run_button.setEnabled(enabled and not self.script_changed)
        self.load_button.setEnabled(enabled)
        self.run_step_button.setEnabled(enabled)

    def log(self, message, level='info'):
        log_msg(self, root_logger, message=message, level=level)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    I = MainWindow()
    app.setStyle("fusion")
    I.show()
    sys.exit(app.exec_())

import logging
import os

import yaml
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *

from Utilities.load_config import LOGGER_FORMAT, ROOT_LOGGER_NAME
from Widget_Library.widget_results import Ui_Form
from definitions import ROOT_DIR
from ui_elements.my_qwidget import MyQWidget

"""This widget visualizes scan_data[results_summary], which is a 2d list of lists containing strings."""


class Results(MyQWidget, Ui_Form):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.config = None
        self.manager = None
        self.test_data = dict()
        self.style_ui()
        self.configure_signals()
        self.log_2d_list = list()

    # load log file, put it into a 2d list, store it in self.test_data['script_log'], and also return it
    def load_log_data(self, path=None):
        if path is None:
            path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Results files (*.txt)")
        log_2d_list = list()
        log_file = open(path, 'r')
        for line in log_file:
            line_ray = line.split('\t')
            log_2d_list.append(line_ray)  # populates class' internal 2d log list

        self.test_data['script_log'] = log_2d_list
        self.populate_log_table()  # populate the log table since we're done loading it
        return self.test_data['script_log']

    # populates the ui given a 2d list
    def populate_log_table(self, log_table=None):
        if log_table is None:
            log_table = self.test_data["script_log"]

        for line_counter in range(len(log_table)):
            line_ray = log_table[line_counter]
            self.script_log_table.insertRow(self.script_log_table.rowCount())  # insert a row to the script table
            for x in range(len(line_ray)):
                item = QTableWidgetItem()
                item.setText(line_ray[x].strip())
                self.script_log_table.setItem(line_counter, x, item)

    @pyqtSlot()
    def populate_results_table(self, results_summary=None):
        if results_summary is not None:
            self.test_data["results_summary"] = results_summary

        results_summary = self.test_data["results_summary"]

        for i in range(11):  # covers range of all elements and "UA Common"
            for x in range(15):  # covers all the data units in each element
                item = QTableWidgetItem()
                item.setText(results_summary[i][x + 1])  # skip the header data and ignore name of element
                if i == 10:  # if we're on the "UA Common" line
                    self.results_table.setItem(i + 2, x, item)  # there is a line break between elements and "UA Common"
                else:
                    self.results_table.setItem(i + 1, x, item)  # first row is reserved for units

        for i in range(11, 13):  # LF and HF are in the last two rows of test_contents
            for x in range(len(results_summary[-2])):
                item = QTableWidgetItem()
                item.setText(results_summary[i][x])  # Elements with manual LF starts at row number 15 in table
                self.results_table.setItem(i + 2, x, item)  # offset for table alignment
            for x in range(len(results_summary[-1])):
                item = QTableWidgetItem()
                item.setText(results_summary[i][x])  # Elements with manual LF starts at row number 15 in table
                self.results_table.setItem(i + 2, x, item)

    def style_ui(self):
        self.results_table.horizontalHeader().resizeSection(15, 362)
        self.script_log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.script_log_table.horizontalHeader().setStretchLastSection(True)
        self.script_log_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.script_log_table.verticalHeader().setDefaultSectionSize(1)  # minimum height

    # turn a 2d list into a .log file (a text file with a different extension
    '''this method must be called manually'''
    def save_log_file(self, log_table=None):
        if log_table is None:
            log_table = self.test_data["script_log"]

        try:
            log_path = self.config["Paths"]["Script log directory"] + "ScriptResults.log"
        except TypeError:
            self.log("config has not been loaded and therefore the log path cannot be pulled from there, defaulting log path")
            log_path = "../logs2/ScriptResults.log"

        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))

        f = open(log_path, 'w')
        for x in range(len(log_table)):
            f.write('\t'.join(log_table[x]))

    """saves the results as a text file with a path specified in the config file."""

    @pyqtSlot()
    def save_test_results_summary(self):
        if not self.test_data:  # if dictionary is empty return
            return

        path = self.config['Paths']['UA results root directory'] + "\\" + self.test_data["serial_number"] + "-" + \
               self.test_data["test_date_time"] + ".txt"  # retrieve path

        try:  # path might not be populated
            pass
        except (TypeError, KeyError):
            self.log("UA results root directory not defined in either yaml, defaulting to output.txt")
            if not os.path.exists("..\\results"):
                os.makedirs("..\\results")
            path = "..\\results\\" + self.test_data["serial_number"] + "-" + self.test_data["test_date_time"] + ".txt"

        self.log(f"Saving results summary to: {path}")

        if not os.path.exists(os.path.dirname(path)):
            self.log("creating results path...")
            os.makedirs(os.path.dirname(path))

        f = open(path, "w")

        f.write(self.test_data["serial_number"] + '-' + self.test_data["test_date_time"] + '\n')
        f.write("Test operator\t" + self.test_data['operator_name'] + '\n')
        f.write("Comment\t" + self.test_data['test_comment'] + '\n')
        f.write("Software Version\t" + self.test_data['software_version'] + '\n')
        f.write("Script\t" + self.test_data['script_name'] + '\n')
        if self.test_data["write_result"]:
            f.write("UA Write\tOK\n")
        else:
            f.write("UA Write\tFAIL\n")
        f.write("UA hardware code\t" + self.test_data['hardware_code'] + '\n')
        f.write('\n')  # empty line
        f.write("\tX\tTheta\tLF (MHz)\tLF.VSI (V^2s)\tHF (MHz)\tHF.VSI (V^2s)\tLF.Eff (%)\tLF.Rfl (%)\tLF.Pf(max) (W)\tLF.WTemp (degC)\tHF.Eff (%)\tHF.Rfl (%)\tHF.Pf(max) (W)\tHF.WTemp (degC)\tElement result\tFailure description\n")

        element_data_list = self.test_data['results_summary']
        for x in range(len(element_data_list)):
            if 0 <= x <= 10:  # for all the element lines and the UA Common line
                if x == 10:
                    f.write('\n')  # there are empty lines around "UA Common" row
                f.write('\t'.join(element_data_list[x]))
                f.write('\n')
            if x == 11:  # for the elements with manual LF...
                f.write('\n')
                f.write('Elements with manual LF\t' + ','.join(element_data_list[x]))
                f.write('\n')
            if x == 12:  # for the elements with manual HF...
                f.write('Elements with manual HF\t' + ','.join(element_data_list[x]))

    def set_manager(self, manager):
        self.manager = manager
        self.manager.save_results_signal.connect(self.retrieve_data_from_manager)

    def configure_signals(self):
        self.save_button.clicked.connect(self.save_test_results_summary)

    """Recieve the test_data dictionary from manager, visualize the summary and the scriptlog, and save both to disk"""

    @pyqtSlot(dict)
    def retrieve_data_from_manager(self, dict):
        self.log("Saving test results")
        self.test_data = dict
        self.save_test_results_summary()
        self.populate_results_table()

        self.populate_log_table()
        self.save_log_file()

    def set_config(self, config):
        self.config = config

    def load_test_results(self, path=None):
        if path is None:
            path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Results files (*.txt)")

        """header of the table starts at 0th row so start populating it at row 1 and down"""
        if path == '':
            return
        test_results_file = open(path, "r")
        test_contents = list()
        line_counter = 0

        for line in test_results_file:
            line_ray = line.split("\t")
            if len(line_ray) > 0:  # ignore blank lines

                if line_counter == 0:  # the first line of the test results summary file will have the serial no. and date
                    delimited_line = line.split("-")  # separates the serial number from the date
                    self.test_data['serial_number'] = delimited_line[0]
                    removed_new_line = delimited_line[2].replace('\n', '')
                    date_time_pre = delimited_line[1] + "-" + removed_new_line
                    self.test_data['test_date_time'] = date_time_pre

                if 0 < line_counter < 7:  # do not include the first line in the header and stop this form of dict importing after the header block
                    if '\n' in line_ray[1]:
                        removed_new_line = line_ray[1].replace('\n', '')  # weird workaround for removing new line in value
                        line_ray[1] = removed_new_line
                    test_contents.append([line_ray[0], line_ray[1]])

                elif "Element_" in line_ray[0] or "UA Common" in line_ray[0]:  # if the line we're on is an element data line
                    temp_list_for_element = list()

                    for i in range(0, 17):  # there are 14 columns in the data block
                        try:
                            if '\n' in line_ray[i]:
                                a = line_ray[i].replace('\n', '')  # remove trailing new lines
                                temp_list_for_element.append(a)
                            else:
                                temp_list_for_element.append(line_ray[i])
                        except IndexError:  # sometimes failure description is empty in element data line
                            temp_list_for_element.append('')

                    test_contents.append(temp_list_for_element)  # line_ray[0] is element name, value is the data list for that element

                elif "Elements with manual LF" in line_ray[0]:  # if the line is for listing the elements with manual low freq.
                    list_of_elements = line_ray[1].split(",")
                    test_contents.append(list_of_elements)

                elif "Elements with manual HF" in line_ray[0]:  # if the line is for listing the elements with manual high freq.
                    list_of_elements = line_ray[1].split(",")
                    test_contents.append(list_of_elements)

            line_counter = line_counter + 1  # increments our line counter, so we know where we are; count blank lines

        self.test_data['operator_name'] = test_contents[0][1]
        self.test_data['comment'] = test_contents[1][1]
        self.test_data['software_version'] = test_contents[2][1]
        self.test_data["script_name"] = test_contents[3][1]
        self.test_data["write_result"] = test_contents[4][1]
        self.test_data["hardware_code"] = test_contents[5][1]
        self.test_data['results_summary'] = test_contents[6:][:]

        # print_dict(self.test_data)
        # print_list(self.test_data['results_summary'])

        self.populate_results_table()

        return self.test_data


# '''create a new method called loadconfig which turns a txt file into a list of lists; 3 methods lower method returns a
# list of lists given a txt file, other 2 take a list of lists and either save/display it; for the load method, use QFileDialog.get_open_file_name, will create prompt to find and select file'''

def print_list(a):
    print("*** beginning of list ***")
    for x in range(len(a)):
        print(f"{x}: ", a[x])
    print("*** end of list ***")


def print_dict(a):
    for key, value in a.items():
        if type(value) is dict:
            print(key, " :")
            print_indent_dict(value)
            pass
        elif type(value) is list:
            print(key, " :")
            print_list(value)
        else:
            print(key, ':', value)


def print_indent_dict(a):
    for key, value in a.items():
        print('\t', key, ':', value)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    res_widget = Results()

    res_widget.load_test_results()
    res_widget.save_test_results_summary()
    res_widget.load_log_data("../logs/ScriptResults.log")
    res_widget.save_log_file()

    res_widget.show()
    sys.exit(app.exec_())

    '''test all three steps: load one, display it, then save it'''

    # The expected result will be a open file prompt, the user selects the example file (on the desktop), it is displayed correctly in the widget,
    # Then the file is saved to the path specified in local.yaml

    # so the save function will turn 2d list to txt file and display function takes txt file and turns it into list of list

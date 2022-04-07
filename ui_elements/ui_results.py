from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import *
from Widget_Library.widget_results import Ui_Form
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
        # connects to the

    """Takes 2d list of strings"""

    @pyqtSlot(object)
    def populate_table(self, test_contents):
        self.results_summary = self.test_data["results_summary"]
        self.ua_serial_number = self.test_data['ua_serial_number']
        self.operator_name = self.test_data['operator_name']
        self.script_name = self.test_data["script_name"]
        self.write_test_result = self.test_data["UA hardware code"]

        for i in range(11):  # covers range of all elements and "UA Common"
            for x in range(16):  # covers all the data units in each element
                item = QTableWidgetItem()
                item.setText(test_contents[i+6][x+1])  # skip the header data and ignore name of element
                if i == 10:  # if we're on the "UA Common" line
                    self.results_table.setItem(i + 2, x, item)  # there is a line break between elements and "UA Common"
                else:
                    self.results_table.setItem(i+1, x, item)  # first row is reserved for units

        for i in range(17, 19):  # LF and HF are in the last two rows of test_contents
            for x in range(len(test_contents[-2])):
                item = QTableWidgetItem()
                item.setText(test_contents[i][x])  # Elements with manual LF starts at row number 15 in table
                self.results_table.setItem(i-4, x, item)  # offset for table alignment
            for x in range(len(test_contents[-1])):
                item = QTableWidgetItem()
                item.setText(test_contents[i][x])  # Elements with manual LF starts at row number 15 in table
                self.results_table.setItem(i-3, x, item)

    """saves the results as a text file with a path specified in the config file."""

    def style_ui(self):
        self.results_table.horizontalHeader().resizeSection(15, 362)

    @pyqtSlot(dict)
    def save_test_results_summary(self, test_data):
        path = self.config['UA results root directory']  # retrieve path
        f = open("output.txt", "w")
        # serial no of UA goes first
        serial_no = self.manager.ua_serial_number
        pass

    def set_manager(self, manager):
        self.manager = manager
        #by referemce, whemever manager changes these, this object will be updated
        self.test_data = manager.test_data

        #self.populate_table_signal.connect(self.manager.visualize_scan_data)
    def configure_signals(self):
        self.save_button.clicked.connect(self.save_test_results_summary())

    def set_config(self, config):
        self.config = config

    def load_test_results(self):
        """header of the table starts at 0th row so start populating it at row 1 and down"""
        path_to_load_test_results = "C:\\Users\\RKPC\\Desktop\\Test results summary.txt"
        test_results_file = open(path_to_load_test_results, "r")
        test_contents = list()
        line_counter = 0

        #update all of
        self.test_data['results_summary']
        self.test_data['ua_serial_number']
        self.test_data['operator_name']
        self.test_data["script_name"]
        self.test_data["UA hardware code"]

        for line in test_results_file:
            line_ray = line.split("\t")
            if len(line_ray) > 0:  # ignore blank lines

                if 0 < line_counter < 7:  # do not include the first line in the header and stop this form of dict importing after the header block
                    if '\n' in line_ray[1]:
                        a = line_ray[1].replace('\n', '')  # weird workaround for removing new line in value
                        line_ray[1] = a
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

        print_list(test_contents)
        return test_contents


# '''create a new method called loadconfig which turns a txt file into a list of lists; 3 methods lower method returns a
# list of lists given a txt file, other 2 take a list of lists and either save/display it; for the load method, use QFileDialog.get_open_file_name, will create prompt to find and select file'''

def print_list(a):
    for x in range(len(a)):
        print(a[x])


def print_dict(a):
    for key, value in a.items():
        if type(value) is dict:
            print(key, " :")
            print_indent_dict(value)
            pass
        else:
            print(key, ':', value)


def print_indent_dict(a):
    for key, value in a.items():
        print('\t', key, ':', value)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    res_widget = Results()

    results_ray = res_widget.load_test_results()
    res_widget.populate_table(results_ray)
    # res_widget.save_results(results_ray)

    res_widget.show()
    sys.exit(app.exec_())

    '''test all three steps: load one, display it, then save it'''

    # The expected result will be a open file prompt, the user selects the example file (on the desktop), it is displayed correctly in the widget,
    # Then the file is saved to the path specified in local.yaml

    # so the save function will turn 2d list to txt file and display function takes txt file and turns it into list of list

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
        # connects to the

    """Takes 2d list of strings"""

    @pyqtSlot(object)
    def populate_table(self):
        pass

    """saves the results as a text file with a path specified in the config file."""

    @pyqtSlot(object)
    def save_test_results_summary(self):
        path = self.config['UA results root directory']  # retrieve path
        pass

    def set_manager(self, manager):
        self.manager = manager
        self.populate_table_signal.connect(self.manager.visualize_scan_data)

    def set_config(self, config):
        self.config = config

    def load_test_results(self):
        """header of the table starts at 0th row so start populating it at row 1 and down"""
        path_to_load_test_results = "C:\\Users\\RKPC\\Desktop\\Test results summary.txt"
        test_results_file = open(path_to_load_test_results, "r")
        test_contents = dict()
        category_line = list()
        line_counter = 0
        for line in test_results_file:
            line_ray = line.split("\t")
            if len(line_ray) > 0:  # ignore blank lines

                if 0 < line_counter < 7:  # do not include the first line in the header and stop this form of dict importing after the header block
                    if '\n' in line_ray[1]:
                        a = line_ray[1].replace('\n', '')  # weird workaround for removing new line in value
                        line_ray[1] = a
                    test_contents[line_ray[0]] = line_ray[1]

                elif line_counter == 8:  # column definitions should be in the eight line
                    while "" in line_ray:  # remove empty entries in line_ray
                        line_ray.remove("")

                    for column_name in line_ray:  # for each element in the \t delimited line
                        if '\n' in column_name:
                            a = column_name.replace('\n', '')  # remove newline spaces
                            category_line.append(a)
                        else:
                            category_line.append(column_name)

                elif "Element_" in line_ray[0] or "UA Common" in line_ray[0]:  # if the line we're on is an element data line
                    temp_dict_for_element = dict()

                    for i in range(len(category_line)):
                        try:
                            if '\n' in line_ray[i + 1]:
                                a = line_ray[i + 1].replace('\n', '')
                                temp_dict_for_element[category_line[i]] = a
                            else:
                                temp_dict_for_element[category_line[i]] = line_ray[i + 1]
                        except IndexError:  # sometimes failure description is empty in element data line
                            temp_dict_for_element[category_line[i]] = ''

                    test_contents[line_ray[0]] = temp_dict_for_element  # line_ray[0] is element name, value is the data list for that element

                elif "Elements with manual LF" in line_ray[0]:  # if the line is for listing the elements with manual low freq.
                    list_of_elements = line_ray[1].split(",")
                    test_contents[line_ray[0]] = list_of_elements

                elif "Elements with manual HF" in line_ray[0]:  # if the line is for listing the elements with manual high freq.
                    list_of_elements = line_ray[1].split(",")
                    test_contents[line_ray[0]] = list_of_elements

            line_counter = line_counter + 1  # increments our line counter, so we know where we are; count blank lines

        print_dict(test_contents)
        pass


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
            print(key, ' : ', value)


def print_indent_dict(a):
    for key, value in a.items():
        print('\t', key, ' : ', value)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    res_widget = Results()

    results_ray = res_widget.load_test_results()
    # res_widget.populate_table(results_ray)
    # res_widget.save_results(results_ray)

    res_widget.show()
    sys.exit(app.exec_())

    '''test all three steps: load one, display it, then save it'''

    # The expected result will be a open file prompt, the user selects the example file (on the desktop), it is displayed correctly in the widget,
    # Then the file is saved to the path specified in local.yaml

    # so the save function will turn 2d list to txt file and display function takes txt file and turns it into list of list

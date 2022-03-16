import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, QtCore
import time
from Widget_Library.widget_script_editor import  Ui_Form

class ScriptEditor(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.configure_signals()

        self.arg_dicts = None

    # Display the task names and arguments from the script parser with a QTreeView
    def visualize_script(self, arg_dicts: list):
        self.arg_dicts = arg_dicts
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        self.treeWidget.clear()
        self.arg_dicts = arg_dicts
        print(self.arg_dicts)

        task_dict = {}
        for i in range(len(self.arg_dicts)):
            if not '# of Tasks' in self.arg_dicts[i].keys():
                arg_list = list()
                for key in self.arg_dicts[i]:
                    if not key == "Task type":
                        arg_list.append([key, self.arg_dicts[i][key]])

                task_dict[self.arg_dicts[i]["Task type"]] = arg_list

        tree_items = []
        for key, values in task_dict.items():
            item = QTreeWidgetItem([key])
            for value in values:
                child = QTreeWidgetItem(value)
                item.addChild(child)

            tree_items.append(item)

        #Add invisible item to allow inserting at the end
        tree_items.append(QTreeWidgetItem([]))

        self.treeWidget.invisibleRootItem().addChildren(tree_items)

        self.treeWidget.setHeaderHidden(True)
        # self.script_editor.treeWidget.insertTopLevelItems(0, tre)

    def header_dict(self):
        return {'# of Tasks': '14', 'Createdby': 'PSM', 'Createdon': '25/08/2016',
         'Description': 'Script runs through finding elements (Beam angle test), '
                        'HF and LF efficiency only. Manual setting of frequency at start of test.'}

    def measure_effeciency_dict(self):
        return {'Amplitude (mVpp)': '100.000000', 'Data directory': '', 'EfficiencyTest': 'TRUE', 'Element': 'Current',
         'Frequency (MHz)': '4.200000', 'Frequency range': 'Low frequency', 'Pa max (target, W)': '4.000000',
         'Pf max (limit, W)': '12.000000', 'RFB target angle': '-90.000000',
         'RFB target position': 'Average UA RFB position', 'RFB.#on/off cycles': '3', 'RFB.Off time (s)': '10.000000',
         'RFB.Offset': '0.500000', 'RFB.On time (s)': '10.000000', 'RFB.Threshold': '0.050000',
         'Reflection limit (%)': '70.000000', 'Set frequency options': 'Common peak frequency',
         'Storage location': 'UA results directory', 'Task type': 'Measure element efficiency (RFB)'}

    def pre_test_dict(self):
        return  {'Task type': 'Pre-test initialisation'}

    def find_element_dict(self):
        return {'#Cycles.Capture': '10', '#Cycles.Delay': '0', 'Acquisition type': 'N Averaged Waveform',
         'Amplitude (mV)': '50.000000', 'Auto set timebase': 'TRUE', 'Averages': '16', 'BeamAngleTest': 'FALSE',
         'Burst count': '50', 'Data directory': '', 'Data storage': 'Do not store', 'Element': 'Element 1',
         'ElementPositionTest': 'FALSE', 'Frequency (MHz)': '4.400000', 'Frequency settings': 'Avg. Low frequency',
         'Max angle variation (deg)': '2.000000', 'Max. position error (+/- mm)': '0.200000',
         'Scope channel': 'Channel 1', 'Storage location': 'UA results directory', 'Task type': 'Find element',
         'Theta #Pts.': '41', 'Theta Incr. (deg)': '-0.400000', 'X #Pts.': '21', 'X Incr. (mm)': '0.250000'}

    def loop_over_elements_dict(self):
        return {'Element 1': 'TRUE', 'Element 10': 'TRUE', 'Element 2': 'TRUE', 'Element 3': 'TRUE', 'Element 4': 'TRUE',
         'Element 5': 'TRUE', 'Element 6': 'TRUE', 'Element 7': 'TRUE', 'Element 8': 'TRUE', 'Element 9': 'TRUE',
         'Task type': 'Loop over elements'}

    def home_system_dict(self):
        return {'Axis to home': 'Theta', 'Task type': 'Home system'}

    def end_loop_dict(self):
        return {'Task type': 'End loop'}

    def dict_to_tree_item(self, task_dict):
        item = QTreeWidgetItem([task_dict["Task type"]])

        arg_list = list()
        for key in task_dict:
            if not key == "Task type":
                arg_list.append([key, task_dict[key]])

        #Add parameters as child items
        print(task_dict)

        for parameter in arg_list:
            child = QTreeWidgetItem(parameter)
            item.addChild(child)

        return  item

    def updateTree(self):
        task_dict = {}
        for i in range(len(self.arg_dicts)):
            if not '# of Tasks' in self.arg_dicts[i].keys():
                arg_list = list()
                for key in self.arg_dicts[i]:
                    if not key == "Task type":
                        arg_list.append([key, self.arg_dicts[i][key]])

                task_dict[self.arg_dicts[i]["Task type"]] = arg_list

        self.tree_items = []
        for key, values in task_dict.items():
            item = QTreeWidgetItem([key])
            for value in values:
                child = QTreeWidgetItem(value)
                item.addChild(child)

            self.tree_items.append(item)

        self.script_step_view.insertTopLevelItems(0, self.tree_items)

    def configure_signals(self):
        self.add_cmd_to_script_button.clicked.connect(self.add_cmd_to_script_clicked)
        self.move_cmd_down_button.clicked.connect(self.move_selection_down)
        self.move_cmd_up_button.clicked.connect(self.move_selection_up)

    def move_selection_down(self):
        index = self.treeWidget.currentIndex()
        self.treeWidget.setCurrentIndex(index.sibling(index.row()+1, index.column()))

    def move_selection_up(self):
        index = self.treeWidget.currentIndex()
        self.treeWidget.setCurrentIndex(index.sibling(index.row()-1, index.column()))

    def add_cmd_to_script_clicked(self):
        row = self.treeWidget.currentIndex().row()
        task_name = self.script_cmd_dropdown.currentText()

        # no selection
        if row == -1:
            index = 0
            #Insert at beginning
        else:
            index = row
            # Insert @ selection, shifting items down

        if task_name == 'Measure element efficiency (RFB)':
            new_arg_dict = self.measure_effeciency_dict()
        elif task_name == 'Pre-test initialisation':
            new_arg_dict = self.pre_test_dict()
        elif task_name == 'Find element "n"':
            new_arg_dict = self.find_element_dict()
        elif task_name == 'Loop over elements':
            new_arg_dict = self.loop_over_elements_dict()

        #add the new dictionary to arg_dicts at the correct index
        self.arg_dicts.insert(row, new_arg_dict)

        self.treeWidget.insertTopLevelItems(index, [self.dict_to_tree_item(new_arg_dict)])

        print(self.arg_dicts)

if __name__ == '__main__':
    editor = ScriptEditor()

    editor.script_

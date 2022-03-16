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

    def updateTree(self):
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        self.script_step_view.clear()

        [{'# of Tasks': '14', 'Createdby': 'PSM', 'Createdon': '25/08/2016',
          'Description': 'Script runs through finding elements (Beam angle test), HF and LF efficiency only. Manual setting of frequency at start of test.'},
         {'Task type': 'Pre-test initialisation'},
         {'#Cycles.Capture': '10', '#Cycles.Delay': '0', 'Acquisition type': 'N Averaged Waveform',
          'Amplitude (mV)': '50.000000', 'Auto set timebase': 'TRUE', 'Averages': '16', 'BeamAngleTest': 'FALSE',
          'Burst count': '50', 'Data directory': '', 'Data storage': 'Do not store', 'Element': 'Element 1',
          'ElementPositionTest': 'FALSE', 'Frequency (MHz)': '4.400000', 'Frequency settings': 'Avg. Low frequency',
          'Max angle variation (deg)': '2.000000', 'Max. position error (+/- mm)': '0.200000',
          'Scope channel': 'Channel 1', 'Storage location': 'UA results directory', 'Task type': 'Find element n',
          'Theta #Pts.': '41', 'Theta Incr. (deg)': '-0.400000', 'X #Pts.': '21', 'X Incr. (mm)': '0.250000'},
         {'Element 1': 'TRUE', 'Element 10': 'TRUE', 'Element 2': 'TRUE', 'Element 3': 'TRUE', 'Element 4': 'TRUE',
          'Element 5': 'TRUE', 'Element 6': 'TRUE', 'Element 7': 'TRUE', 'Element 8': 'TRUE', 'Element 9': 'TRUE',
          'Task type': 'Loop over elements'},
         {'#Cycles.Capture': '10', '#Cycles.Delay': '5', 'Acquisition type': 'N Averaged Waveform',
          'Amplitude (mV)': '50.000000', 'Auto set timebase': 'TRUE', 'Averages': '16', 'BeamAngleTest': 'TRUE',
          'Burst count': '50', 'Data directory': '', 'Data storage': 'Store profiles only', 'Element': 'Current',
          'ElementPositionTest': 'FALSE', 'Frequency (MHz)': '4.400000', 'Frequency settings': 'Avg. Low frequency',
          'Max angle variation (deg)': '2.000000', 'Max. position error (+/- mm)': '0.400000',
          'Scope channel': 'Channel 1', 'Storage location': 'UA results directory', 'Task type': 'Find element n_1',
          'Theta #Pts.': '41', 'Theta Incr. (deg)': '-0.400000', 'X #Pts.': '21', 'X Incr. (mm)': '0.200000'},
         {'Task type': 'End loop'},
         {'Element 1': 'TRUE', 'Element 10': 'TRUE', 'Element 2': 'TRUE', 'Element 3': 'TRUE', 'Element 4': 'TRUE',
          'Element 5': 'TRUE', 'Element 6': 'TRUE', 'Element 7': 'TRUE', 'Element 8': 'TRUE', 'Element 9': 'TRUE',
          'Task type': 'Loop over elements_1'},
         {'Amplitude (mVpp)': '100.000000', 'Data directory': '', 'EfficiencyTest': 'TRUE', 'Element': 'Current',
          'Frequency (MHz)': '4.200000', 'Frequency range': 'Low frequency', 'Pa max (target, W)': '4.000000',
          'Pf max (limit, W)': '12.000000', 'RFB target angle': '-90.000000',
          'RFB target position': 'Average UA RFB position', 'RFB.#on/off cycles': '3', 'RFB.Off time (s)': '10.000000',
          'RFB.Offset': '0.500000', 'RFB.On time (s)': '10.000000', 'RFB.Threshold': '0.050000',
          'Reflection limit (%)': '70.000000', 'Set frequency options': 'Common peak frequency',
          'Storage location': 'UA results directory', 'Task type': 'Measure element efficiency (RFB)'},
         {'Amplitude (mVpp)': '175.000000', 'Data directory': '', 'EfficiencyTest': 'TRUE', 'Element': 'Current',
          'Frequency (MHz)': '4.200000', 'Frequency range': 'High frequency', 'Pa max (target, W)': '2.000000',
          'Pf max (limit, W)': '12.000000', 'RFB target angle': '-90.000000',
          'RFB target position': 'Average UA RFB position', 'RFB.#on/off cycles': '3', 'RFB.Off time (s)': '10.000000',
          'RFB.Offset': '0.500000', 'RFB.On time (s)': '10.000000', 'RFB.Threshold': '0.050000',
          'Reflection limit (%)': '70.000000', 'Set frequency options': 'Common peak frequency',
          'Storage location': 'UA results directory', 'Task type': 'Measure element efficiency (RFB)_1'},
         {'Amplitude (mVpp)': '100.000000', 'Data directory': '', 'EfficiencyTest': 'TRUE', 'Element': 'Current',
          'Frequency (MHz)': '4.200000', 'Frequency range': 'Low frequency', 'Pa max (target, W)': '4.000000',
          'Pf max (limit, W)': '12.000000', 'RFB target angle': '-90.000000',
          'RFB target position': 'Average UA RFB position', 'RFB.#on/off cycles': '3', 'RFB.Off time (s)': '10.000000',
          'RFB.Offset': '0.500000', 'RFB.On time (s)': '10.000000', 'RFB.Threshold': '0.050000',
          'Reflection limit (%)': '70.000000', 'Set frequency options': 'Common peak frequency',
          'Storage location': 'UA results directory', 'Task type': 'Measure element efficiency (RFB)_2'},
         {'Task type': 'End loop_1'},
         {'PromptForCalWrite': 'FALSE', 'Save summary file': 'TRUE', 'Task type': 'Save results',
          'Write UA Calibration': 'TRUE'}, {'Prompt type': 'Disable UA pump', 'Task type': 'Prompt user for action'},
         {'Axis to home': 'Theta', 'Task type': 'Home system'}, {'Axis to home': 'X', 'Task type': 'Home system_1'}]

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

    def add_cmd_to_script_clicked(self):
        self.treeWidget.insertTopLevelItems(0, [QTreeWidgetItem([self.script_cmd_dropdown.currentText()])])
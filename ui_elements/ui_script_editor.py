from ui_elements.my_qwidget import MyQWidget
from PyQt5.QtWidgets import QInputDialog, QTreeWidgetItem, QFileDialog, QWidget
from Widget_Library.widget_script_editor import Ui_Form
from collections import OrderedDict
from ui_elements.script_editor.ui_find_element import FindElement
from ui_elements.script_editor.ui_home_system import HomeSystem
from ui_elements.script_editor.ui_prompt_user_for_action import PromptUserForAction
from ui_elements.script_editor.ui_loop_over_elements import LoopOverElements
from ui_elements.script_editor.ui_measure_element_efficiency_rfb import MeasureElementEffeciency
#from ui_elements.script_editor. import
#from ui_elements.script_editor. import

#Todo: add the rest of the methods to the dropdown
class ScriptEditor(MyQWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.list_of_arg_dicts = list()
        self.setupUi(self)
        self.configure_signals()

    def set_tree_widget(self, treeWidget):
        self.treeWidget = treeWidget
        self.treeWidget.itemClicked.connect(self.on_item_clicked)

    def configure_signals(self):
        self.script_cmd_dropdown.currentIndexChanged.connect(self.show_task_type_widget)
        self.add_cmd_to_script_button.clicked.connect(self.add_cmd_to_script_clicked)
        self.move_cmd_down_button.clicked.connect(self.move_selection_down)
        self.move_cmd_up_button.clicked.connect(self.move_selection_up)
        self.update_tree_button.clicked.connect(self.updateTree)
        self.save_script_button.clicked.connect(self.save_script)
        self.delete_step_button.clicked.connect(self.delete_step)
        self.delete_all_button.clicked.connect(self.delete_all)

    def show_task_type_widget(self):
        #clear layout
        for i in reversed(range(self.action_widget_layout.count())):
            self.action_widget_layout.itemAt(i).widget().setParent(None)

        task_type = self.script_cmd_dropdown.currentText()

        widget = None
        if task_type == "Find element \"n\"":
            widget = FindElement()
        elif task_type == "Loop over elements":
            widget = LoopOverElements()
        #elif task_type == "End loop"
        elif task_type == "Measure element efficiency (RFB)":
            widget = MeasureElementEffeciency()
        #elif task_type == "Save results"
        elif task_type == "Prompt user for action":
            widget = PromptUserForAction()
        elif task_type == "Home system":
            widget = HomeSystem()
        #elif task_type == ""
        #elif task_type == ""
        #elif task_type == ""
        #elif task_type == ""
        else:
            widget = QWidget()

        self.action_widget_layout.addWidget(widget, 0,0)

    """Delete the step at the given index"""
    def delete_step(self):
        index = self.treeWidget.currentIndex().row()
        self.treeWidget.takeTopLevelItem(index)
        self.list_of_arg_dicts.pop(index + 1) #account for header
        pass

    """Clear the ui script visual and clear the internal arg_dicts variable"""
    def delete_all(self):
        self.treeWidget.clear()
        self.list_of_arg_dicts = list()
        pass

    def on_item_clicked(self):
        index = self.treeWidget.currentIndex()
        if not index.column() == 1:
            return
        #Click is in the variable column
        item = self.treeWidget.currentItem()
        value = item.text(1)

        is_task = item.parent() is self.treeWidget.invisibleRootItem() or item.parent() is None
        if is_task:
            return

        #Clicked cell contains a variable value
        #Prompt user to edit value
        value = QInputDialog.getText(self, "Change Variable", f"Previous value: {value}")[0]
        if value is not None and value != '':
            item.setText(1, value)

    # Display the task names and arguments from the script parser with a QTreeView
    def visualize_script(self, arg_dicts: list):
        self.list_of_arg_dicts = arg_dicts
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        self.treeWidget.clear()

        task_dict = {}
        for i in range(len(self.list_of_arg_dicts)):
            if not '# of Tasks' in self.list_of_arg_dicts[i].keys():
                arg_list = list()
                for key in self.list_of_arg_dicts[i]:
                    if not key == "Task type":
                        arg_list.append([key, self.list_of_arg_dicts[i][key]])

                task_dict[self.list_of_arg_dicts[i]["Task type"]] = arg_list

        #Add an item for each task and child items for all of its variables
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

        # self.script_editor.treeWidget.insertTopLevelItems(0, tre)

    def header_dict(self):
        return OrderedDict([('# of Tasks', '14'), ('Createdon', '25/08/2016'), ('Createdby', 'PSM'),
                            ('Description', 'Script runs through finding elements (Beam angle test), '
                                    'HF and LF efficiency only. Manual setting of frequency at start of test.')])

    def measure_effeciency_dict(self):
        return OrderedDict([('Task type', 'Measure element efficiency (RFB)'), ('Element', 'Current'),
                            ('Frequency range', 'Low frequency'), ('RFB.#on/off cycles', '3'),
                            ('RFB.On time (s)', '10.000000'), ('RFB.Off time (s)', '10.000000'),
                            ('RFB.Threshold', '0.050000'), ('RFB.Offset', '0.500000'),
                            ('Set frequency options', 'Common peak frequency'), ('Frequency (MHz)', '4.200000'),
                            ('Amplitude (mVpp)', '100.000000'), ('Storage location', 'UA results directory'),
                            ('Data directory', ''), ('RFB target position', 'Average UA RFB position'),
                            ('RFB target angle', '-90.000000'), ('EfficiencyTest', 'TRUE'),
                            ('Pa max (target, W)', '4.000000'), ('Pf max (limit, W)', '12.000000'),
                            ('Reflection limit (%)', '70.000000')])

    def pre_test_dict(self):
        return  OrderedDict([('Task type', 'Pre-test initialisation')])

    def find_element_dict(self):
        return OrderedDict([('Task type', 'Find element \"n\"'), ('Element', 'Element 1'), ('X Incr. (mm)', '0.250000'),
                            ('X #Pts.', '21'), ('Theta Incr. (deg)', '-0.400000'), ('Theta #Pts.', '41'),
                            ('Scope channel', 'Channel 1'), ('Acquisition type', 'N Averaged Waveform'),
                            ('Averages', '16'), ('Data storage', 'Do not store'),
                            ('Storage location', 'UA results directory'), ('Data directory', ''),
                            ('Max. position error (+/- mm)', '0.200000'), ('ElementPositionTest', 'FALSE'),
                            ('Max angle variation (deg)', '2.000000'), ('BeamAngleTest', 'FALSE'),
                            ('Frequency settings', 'Avg. Low frequency'), ('Auto set timebase', 'TRUE'),
                            ('#Cycles.Capture', '10'), ('#Cycles.Delay', '0'), ('Frequency (MHz)', '4.400000'),
                            ('Amplitude (mV)', '50.000000'), ('Burst count', '50')])

    def loop_over_elements_dict(self):
        return OrderedDict([('Task type', 'Loop over elements'), ('Element 1', 'TRUE'), ('Element 2', 'TRUE'),
                            ('Element 3', 'TRUE'), ('Element 4', 'TRUE'), ('Element 5', 'TRUE'), ('Element 6', 'TRUE'),
                            ('Element 7', 'TRUE'), ('Element 8', 'TRUE'), ('Element 9', 'TRUE'),
                            ('Element 10', 'TRUE')])

    def home_system_dict(self):
        return

    def end_loop_dict(self):
        return OrderedDict([('Task type', 'End loop_1')])

    def dict_to_tree_item(self, task_dict):
        item = QTreeWidgetItem([task_dict["Task type"]])

        arg_list = list()
        for key in task_dict:
            if not key == "Task type":
                arg_list.append([key, task_dict[key]])

        #Add parameters as child items
        for parameter in arg_list:
            child = QTreeWidgetItem(parameter)
            item.addChild(child)

        return  item

    def updateTree(self):
        arg_dict_copy = list(self.list_of_arg_dicts)

        task_names = [self.script_cmd_dropdown.itemText(i) for i in range(self.script_cmd_dropdown.count())]

        #For each task name,
        for task_name in task_names:
            #Count the occurrences of that task name,
            counter = 0
            for i in range(len(arg_dict_copy)):
                if "Task type" in arg_dict_copy[i].keys():
                    if task_name in arg_dict_copy[i]["Task type"]:
                        if counter == 0:
                            arg_dict_copy[i]["Task type"] = f"{task_name}"
                        else:
                            #And number each one after the first one
                            arg_dict_copy[i]["Task type"] = f"{task_name}_{counter}"
                        counter = counter + 1

        #Refresh the visualizer
        self.visualize_script(arg_dict_copy)

    def move_selection_down(self):
        # If there is no selection, try to set selection to the first item
        if self.treeWidget.currentItem() is None:
            first_item = self.treeWidget.invisibleRootItem().child(0)
            if first_item is not None:
                self.treeWidget.setCurrentItem(first_item)
                return
            else:
                return

        index = self.treeWidget.currentIndex()
        self.treeWidget.setCurrentIndex(index.sibling(index.row()+1, index.column()))

    def move_selection_up(self):
        # If there is no selection, try to set selection to the last item
        if self.treeWidget.currentItem() is None:
            child_count = self.treeWidget.invisibleRootItem().childCount()
            last_item = self.treeWidget.invisibleRootItem().child(child_count-1)
            if last_item is not None:
                self.treeWidget.setCurrentItem(last_item)
                return
            else:
                return

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
        elif task_name == 'Find element \"n\"':
            new_arg_dict = self.find_element_dict()
        elif task_name == 'Loop over elements':
            new_arg_dict = self.loop_over_elements_dict()
        else:
            new_arg_dict = OrderedDict()

        #add the new dictionary to arg_dicts at the correct index
        self.list_of_arg_dicts.insert(row + 1, new_arg_dict)

        item = self.dict_to_tree_item(new_arg_dict)

        self.treeWidget.insertTopLevelItems(index, [item])

        self.treeWidget.setCurrentItem(item)

    def save_script(self):
        path = QFileDialog.getSaveFileName(parent=self,caption='Save script',filter='Script files (*.wtf)')[0]

        with open(path, 'w') as f:
            #Write header info
            f.write('[Top Level]\n')
            for arg in self.list_of_arg_dicts[0].keys():
                f.write(f"{arg} = \"{self.list_of_arg_dicts[0][arg]}\"\n")
            f.write("\n")

            #Write arguments of each step
            for i in range(len(self.list_of_arg_dicts) - 1):
                f.write(f'[Task{i}]\n')
                task_args = self.list_of_arg_dicts[i + 1]
                for arg in task_args.keys():
                    f.write(f"{arg} = \"{task_args[arg]}\"\n")
                f.write("\n")

if __name__ == '__main__':
    editor = ScriptEditor()

from typing import List
from ui_elements.my_qwidget import MyQWidget
from PyQt5.QtWidgets import QInputDialog, QTreeWidget, QTreeWidgetItem, QFileDialog
from PyQt5.QtCore import pyqtSignal
from Widget_Library.widget_script_editor import Ui_Form
from ui_elements.script_editor_menus.ui_find_element import FindElement
from ui_elements.script_editor_menus.ui_home_system import HomeSystem
from ui_elements.script_editor_menus.ui_prompt_user_for_action import PromptUserForAction
from ui_elements.script_editor_menus.ui_loop_over_elements import LoopOverElements
from ui_elements.script_editor_menus.ui_measure_element_efficiency import MeasureElementEfficiency
from ui_elements.script_editor_menus.ui_save_results import SaveResults
from ui_elements.script_editor_menus.ui_frequency_sweep import FrequencySweep
from ui_elements.script_editor_menus.ui_oscilloscope_channel import OscilloscopeChannels
from ui_elements.script_editor_menus.ui_oscilloscope_timebase import OscilloscopeTimebase
from ui_elements.script_editor_menus.ui_move_system import MoveSystem
from ui_elements.script_editor_menus.ui_function_generator import FunctionGenerator
from ui_elements.script_editor_menus.ui_script_edit_template import AbstractEditMenu
from ui_elements.script_editor_menus.ui_select_ua_channel import SelectUAChannel
from ui_elements.script_editor_menus.no_menu_dicts import *
from datetime import date


class ScriptEditor(MyQWidget, Ui_Form):
    # This will be the menu for changing parameters of the current task type
    edit_menu: AbstractEditMenu
    script_changed_signal = pyqtSignal()
    treeWidget: QTreeWidget
    list_of_var_dicts: List[dict]

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.edit_menu = AbstractEditMenu()
        self.list_of_var_dicts = list()
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
        # clear layout
        for i in reversed(range(self.action_widget_layout.count())):
            self.action_widget_layout.itemAt(i).widget().setParent(None)

        task_type = self.script_cmd_dropdown.currentText()

        if task_type == "Find element \"n\"":
            self.edit_menu = FindElement()
        elif task_type == "Loop over elements":
            self.edit_menu = LoopOverElements()
        elif task_type == "Measure element efficiency (RFB)":
            self.edit_menu = MeasureElementEfficiency()
        elif task_type == "Save results":
            self.edit_menu = SaveResults()
        elif task_type == "Prompt user for action":
            self.edit_menu = PromptUserForAction()
        elif task_type == "Home system":
            self.edit_menu = HomeSystem()
        elif task_type == "Frequency sweep":
            self.edit_menu = FrequencySweep()
        elif task_type == "Configure oscilloscope channels":
            self.edit_menu = OscilloscopeChannels()
        elif task_type == "Configure oscilloscope timebase":
            self.edit_menu = OscilloscopeTimebase()
        elif task_type == "Move system":
            self.edit_menu = MoveSystem()
        elif task_type == "Configure function generator":
            self.edit_menu = FunctionGenerator()
        elif task_type == "Select UA channel":
            self.edit_menu = SelectUAChannel()
        # elif task_type == ""
        # elif task_type == ""
        # elif task_type == ""
        # elif task_type == ""
        else:
            self.edit_menu = AbstractEditMenu()

        self.action_widget_layout.addWidget(self.edit_menu, 0, 0)

    """Delete the step at the given index"""

    def delete_step(self):
        if len(self.list_of_var_dicts) == 0:
            return

        # Prevent user from running the script until it is saved and reloaded
        self.script_changed_signal.emit()

        index = self.treeWidget.currentIndex().row()
        if not self.treeWidget.currentItem().text(1) == 0:
            self.treeWidget.takeTopLevelItem(index)

        if not index+1 > len(self.list_of_var_dicts):
            self.list_of_var_dicts.pop(index + 1)  # account for header

    """Clear the ui script visual and clear the internal var_dicts variable"""

    def delete_all(self):
        # Prevent user from running the script until it is saved and reloaded
        self.script_changed_signal.emit()

        self.treeWidget.clear()
        self.list_of_var_dicts = list()

        tree_items = [QTreeWidgetItem([])]
        # Add invisible item to allow inserting at the end
        self.treeWidget.invisibleRootItem().addChildren(tree_items)

    def on_item_clicked(self):
        index = self.treeWidget.currentIndex()
        if 1 != index.column():
            return
        # Click is in the variable column
        item = self.treeWidget.currentItem()
        parameter_key = item.text(0)
        value = item.text(1)

        is_task = item.parent() is self.treeWidget.invisibleRootItem() or item.parent() is None
        if is_task:
            return

        # Clicked cell contains a variable value
        # Prompt user to edit value
        value = QInputDialog.getText(self, "Change Variable", f"Previous value: {value}")[0]
        if value is not None and value != '':
            # Prevent user from running the script until it is saved and reloaded
            self.script_changed_signal.emit()

            # Update the parameter in the treewidget
            item.setText(1, value)

            #  Get the task index
            task_index = self.get_parent_item_index(item) + 1

            # Update the parameter in the dictionary
            self.list_of_var_dicts[task_index][parameter_key] = value

    def get_parent_item_index(self, item):
        try:
            parent = item.parent()
        except Exception:
            return -1

        # Temporarily switch to the parent item, get the index row, and switch back
        self.treeWidget.setCurrentItem(parent)
        parent_index = self.treeWidget.currentIndex()
        parent_row = parent_index.row()
        self.treeWidget.setCurrentItem(item)

        return parent_row

    # Display the task names and arguments from the script parser with a QTreeView
    def visualize_script(self, var_dicts: list):
        self.list_of_var_dicts = var_dicts
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        self.treeWidget.clear()

        task_dict = {}
        for i in range(len(self.list_of_var_dicts)):
            if '# of Tasks' not in self.list_of_var_dicts[i].keys():
                arg_list = list()
                for key in self.list_of_var_dicts[i]:
                    if not key == "Task type":
                        arg_list.append([key, self.list_of_var_dicts[i][key]])

                task_dict[self.list_of_var_dicts[i]["Task type"]] = arg_list

        # Add an item for each task and child items for all of its variables
        tree_items = []
        for key, values in task_dict.items():
            item = QTreeWidgetItem([key])
            for value in values:
                child = QTreeWidgetItem(value)
                item.addChild(child)

            tree_items.append(item)

        # Add invisible item to allow inserting at the end
        tree_items.append(QTreeWidgetItem([]))

        self.treeWidget.invisibleRootItem().addChildren(tree_items)

        # self.script_editor.treeWidget.insertTopLevelItems(0, tre)

    def dict_to_tree_item(self, task_dict):
        # Prevent user from running the script until it is saved and reloaded
        self.script_changed_signal.emit()

        item = QTreeWidgetItem([task_dict["Task type"]])

        arg_list = list()
        for key in task_dict:
            if not key == "Task type":
                arg_list.append([key, task_dict[key]])

        # Add parameters as child items
        for parameter in arg_list:
            child = QTreeWidgetItem(parameter)
            item.addChild(child)

        return item

    def updateTree(self):
        # Prevent user from running the script until it is saved and reloaded
        self.script_changed_signal.emit()

        var_dict_copy = list(self.list_of_var_dicts)

        # remove quotes
        task_names = [self.script_cmd_dropdown.itemText(i).replace('\"', '') for i in
                      range(self.script_cmd_dropdown.count())]

        # For each task name,
        for task_name in task_names:
            # Count the occurrences of that task name,
            counter = 0
            for i in range(len(var_dict_copy)):
                if "Task type" in var_dict_copy[i].keys():
                    if task_name in var_dict_copy[i]["Task type"]:
                        if counter == 0:
                            var_dict_copy[i]["Task type"] = f"{task_name}"
                        else:
                            # And number each one after the first one
                            var_dict_copy[i]["Task type"] = f"{task_name}_{counter}"
                        counter = counter + 1

        # Refresh the visualizer
        self.visualize_script(var_dict_copy)

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
        self.treeWidget.setCurrentIndex(index.sibling(index.row() + 1, index.column()))

    def move_selection_up(self):
        # If there is no selection, try to set selection to the last item
        if self.treeWidget.currentItem() is None:
            child_count = self.treeWidget.invisibleRootItem().childCount()
            last_item = self.treeWidget.invisibleRootItem().child(child_count - 1)
            if last_item is not None:
                self.treeWidget.setCurrentItem(last_item)
                return
            else:
                return

        index = self.treeWidget.currentIndex()
        self.treeWidget.setCurrentIndex(index.sibling(index.row() - 1, index.column()))

    def add_cmd_to_script_clicked(self):
        self.script_changed_signal.emit()

        row = self.treeWidget.currentIndex().row()
        task_name = self.script_cmd_dropdown.currentText()

        # no selection
        if row == -1:
            index = 0
            # Insert at beginning
        else:
            index = row
            # Insert @ selection, shifting items down

        # if the widget has a ui_to_orderedDict method
        new_var_dict = self.edit_menu.ui_to_orderedDict()

        if new_var_dict is not None:
            pass
        elif task_name == 'Measure element efficiency (RFB)':
            new_var_dict = self.measure_efficiency_dict()
        elif task_name == 'Pre-test initialisation':
            new_var_dict = pre_test_dict()
        elif task_name == 'Find element \"n\"':
            new_var_dict = self.find_element_dict()
        elif task_name == 'Loop over elements':
            new_var_dict = self.loop_over_elements_dict()
        elif task_name == 'End loop':
            new_var_dict = end_loop_dict()
        elif task_name == 'Frequency sweep':
            new_var_dict = frequency_sweep_dict()
        elif task_name == 'Configure oscilloscope channels':
            new_var_dict = oscilloscope_channel_dict()
        elif task_name == 'Configure oscilloscope timebase':
            new_var_dict = oscilloscope_timebase_dict()
        elif task_name == 'Move system':
            new_var_dict = move_system_dict()
        elif task_name == 'Configure function generator':
            new_var_dict = function_generator_dict()
        elif task_name == 'Select UA channel':
            new_var_dict = select_UA_channel_dict()
        elif task_name == 'Run "Auto Gain Control"':
            new_var_dict = auto_gain_control_dict()
        elif task_name == 'Autoset timebase':
            new_var_dict = autoset_timebase_dict()
        # todo: add more methods
        else:
            new_var_dict = OrderedDict()

        # add the new dictionary to var_dicts at the correct index
        self.list_of_var_dicts.insert(row + 1, new_var_dict)
        item = self.dict_to_tree_item(new_var_dict)
        self.treeWidget.insertTopLevelItems(index, [item])
        self.treeWidget.setCurrentItem(item)
        self.move_selection_down()

    def save_script(self):
        path = QFileDialog.getSaveFileName(parent=self, caption='Save script', filter='Script files (*.wtf)')[0]

        # remove existing header(s) if there is one
        for i in range(len(self.list_of_var_dicts)):
            try:
                if "# of Tasks" in self.list_of_var_dicts[i].keys():
                    self.list_of_var_dicts.pop(i)
            except IndexError:
                pass

        with open(path, 'w') as f:
            num_tasks = len(self.list_of_var_dicts)
            # Customize header dict
            self.list_of_var_dicts.insert(0, header_dict())
            self.list_of_var_dicts[0]["# of Tasks"] = num_tasks
            today = date.today()
            self.list_of_var_dicts[0]["Createdon"] = today.strftime("%d/%m/%Y")
            Createdby = QInputDialog.getText(self, "Save script metadata", f"Enter operator name:")[0]
            self.list_of_var_dicts[0]["Createdby"] = Createdby
            Description = QInputDialog.getText(self, "Save script metadata", f"Enter script description:")[0]
            self.list_of_var_dicts[0]["Description"] = Description

            # Write header info
            f.write('[Top Level]\n')

            for arg in self.list_of_var_dicts[0].keys():
                f.write(f"{arg} = \"{self.list_of_var_dicts[0][arg]}\"\n")
            f.write("\n")

            # Write arguments of each step
            for i in range(len(self.list_of_var_dicts) - 1):
                f.write(f'[Task{i}]\n')
                task_args = self.list_of_var_dicts[i + 1]
                for arg in task_args.keys():
                    f.write(f"{arg} = \"{task_args[arg]}\"\n")
                f.write("\n")


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    edit_widget = ScriptEditor()

    edit_widget.show()
    sys.exit(app.exec_())

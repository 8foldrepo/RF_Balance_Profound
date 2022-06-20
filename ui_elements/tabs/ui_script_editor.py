import typing
from datetime import date
# from pprint import pprint
from typing import List

# import PyQt5
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication as QApp
# from PyQt5.QtGui import QFocusEvent
from PyQt5.QtWidgets import QInputDialog, QTreeWidget, QTreeWidgetItem, QFileDialog

from Utilities.useful_methods import in_range
from Widget_Library.widget_script_editor import Ui_Form
from definitions import ROOT_DIR
from ui_elements.my_qwidget import MyQWidget
from ui_elements.script_editor_menus.no_menu_dicts import *
from ui_elements.script_editor_menus.ui_find_element import FindElement
from ui_elements.script_editor_menus.ui_frequency_sweep import FrequencySweep
from ui_elements.script_editor_menus.ui_function_generator import FunctionGenerator
from ui_elements.script_editor_menus.ui_home_system import HomeSystem
from ui_elements.script_editor_menus.ui_loop_over_elements import LoopOverElements
from ui_elements.script_editor_menus.ui_measure_element_efficiency import MeasureElementEfficiency
from ui_elements.script_editor_menus.ui_move_system import MoveSystem
from ui_elements.script_editor_menus.ui_oscilloscope_channel import OscilloscopeChannels
from ui_elements.script_editor_menus.ui_oscilloscope_timebase import OscilloscopeTimebase
from ui_elements.script_editor_menus.ui_prompt_user_for_action import PromptUserForAction
from ui_elements.script_editor_menus.ui_save_results import SaveResults
from ui_elements.script_editor_menus.ui_script_edit_template import AbstractEditMenu
from ui_elements.script_editor_menus.ui_select_ua_channel import SelectUAChannel


class ScriptEditor(MyQWidget, Ui_Form):
    # This will be the menu for changing parameters of the current task type
    edit_menu: AbstractEditMenu
    script_changed_signal = QtCore.pyqtSignal()
    load_script_signal = QtCore.pyqtSignal(str)  # str is the path to the script file
    treeWidget: QTreeWidget
    list_of_var_dicts: List[dict]

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.edit_menu = AbstractEditMenu()
        self.list_of_var_dicts = list()
        self.setupUi(self)
        self.configure_signals()
        self.app = QApp.instance()
        self.manager = None

    def set_manager(self, manager):
        self.manager = manager
        self.load_script_signal.connect(self.manager.load_script)

    def set_tree_widget(self, tree_widget: QTreeWidget) -> None:
        """
        Method to be used by the MainWindow class so that the instantiation
        of this class in it can have access to its tree widget
        """
        self.treeWidget = tree_widget
        self.treeWidget.itemClicked.connect(self.on_item_clicked)
        if self.treeWidget.invisibleRootItem().childCount() > 0:
            self.delete_all()

    @pyqtSlot(bool)
    def set_buttons_enabled(self, enabled):
        """
        Simple method to either enable or disable all the appropriate buttons in this
        widget with signal capabilities
        """
        self.script_cmd_dropdown.setEnabled(enabled)
        self.add_cmd_to_script_button.setEnabled(enabled)
        self.update_tree_button.setEnabled(enabled)
        self.save_script_button.setEnabled(enabled)
        self.move_cmd_up_button.setEnabled(enabled)
        self.move_cmd_down_button.setEnabled(enabled)
        self.delete_step_button.setEnabled(enabled)
        self.delete_all_button.setEnabled(enabled)

    def configure_signals(self):
        """
        Method to connect various buttons in this to backend methods so that they
        may have actual functionality
        """
        self.script_cmd_dropdown.currentIndexChanged.connect(self.show_task_type_widget)
        self.add_cmd_to_script_button.clicked.connect(self.add_cmd_to_script_clicked)
        self.move_cmd_down_button.clicked.connect(self.move_selected_item_down)
        self.move_cmd_up_button.clicked.connect(self.move_selected_item_up)
        self.update_tree_button.clicked.connect(self.update_tree)
        self.save_script_button.clicked.connect(self.save_script)
        self.delete_step_button.clicked.connect(self.delete_step)
        self.delete_all_button.clicked.connect(self.delete_all)

    def show_task_type_widget(self):
        # clear layout
        for i in reversed(range(self.action_widget_layout.count())):
            self.action_widget_layout.itemAt(i).widget().setParent(None)

        task_type = self.script_cmd_dropdown.currentText()

        if 'Find element "n"' in task_type:
            self.edit_menu = FindElement()
        elif "Loop over elements" in task_type:
            self.edit_menu = LoopOverElements()
        elif "Measure element efficiency (RFB)" in task_type:
            self.edit_menu = MeasureElementEfficiency()
        elif "Save results".upper() in task_type.upper():
            self.edit_menu = SaveResults()
        elif "Prompt user for action" in task_type:
            self.edit_menu = PromptUserForAction()
        elif "Home system" in task_type:
            self.edit_menu = HomeSystem()
        elif "Frequency sweep" in task_type:
            self.edit_menu = FrequencySweep()
        elif "Configure oscilloscope channels" in task_type:
            self.edit_menu = OscilloscopeChannels()
        elif "Configure oscilloscope timebase" in task_type:
            self.edit_menu = OscilloscopeTimebase()
        elif "Move system" in task_type:
            self.edit_menu = MoveSystem()
        elif "Configure function generator" in task_type:
            self.edit_menu = FunctionGenerator()
        elif "Select UA channel" in task_type:
            self.edit_menu = SelectUAChannel()
        # elif task_type == ""  # todo: fill these in
        # elif task_type == ""
        # elif task_type == ""
        # elif task_type == ""
        else:
            self.edit_menu = AbstractEditMenu()

        self.action_widget_layout.addWidget(self.edit_menu, 0, 0)

    def delete_step(self) -> None:
        """Delete the step at the given index"""
        if len(self.list_of_var_dicts) == 0:
            return

        if self.treeWidget.currentItem().text(0) == "":
            return

        # Prevent user from running the script until it is saved and reloaded
        self.script_changed_signal.emit()

        index = self.treeWidget.currentIndex().row()
        if self.treeWidget.currentItem().text(1) != 0:
            self.treeWidget.takeTopLevelItem(index)

        if index + 1 < len(self.list_of_var_dicts):
            self.list_of_var_dicts.pop(index + 1)  # account for header

    def delete_all(self) -> None:
        """Clear the ui script visual and clear the internal var_dicts variable"""
        # Prevent user from running the script until it is saved and reloaded
        self.script_changed_signal.emit()

        self.treeWidget.clear()  # clears the treeWidget of all nodes
        self.list_of_var_dicts = list()

        self.add_empty_item_at_end()

    def on_item_clicked(self) -> None:
        """
        If the value of an item in the task tree view is clicked, gives the user an
        opportunity to change the value of that individual variable for the task
        """
        index = self.treeWidget.currentIndex()  # set index variable to currently selected index
        if index.column() != 1:  # if the user clicked on the variable name
            return  # do not do anything
        # Click is in the variable column
        item = self.treeWidget.currentItem()  # set the local item variable to the currently selected item
        parameter_key = item.text(0)  # get the variable name for the task
        value = item.text(1)  # get the variable value for the task

        # QUESTION: shouldn't this check happen before the variable assignment statements above?
        is_task = (  # check to see if selected item is a top-level task node
                item.parent() is self.treeWidget.invisibleRootItem()
                or item.parent() is None
        )
        if is_task:  # if it is a top-level task node
            return  # don't do anything

        # Clicked cell contains a variable value
        # Prompt user to edit value
        value = QInputDialog.getText(self, "Change Variable", f"Previous value: {value}")[0]
        if value is not None and value != "":  # ensures user entered a variable value
            # Prevent user from running the script until it is saved and reloaded
            self.script_changed_signal.emit()

            # Update the parameter in the tree widget
            item.setText(1, value)

            #  Get the task index
            task_index = self.get_parent_item_index(item)

            # Update the parameter in the dictionary

            # add the new dictionary to var_dicts at the correct index
            if len(self.list_of_var_dicts) > 0 and "Task type" not in self.list_of_var_dicts[0]:
                try:
                    self.list_of_var_dicts[task_index + 1][parameter_key] = value
                except IndexError:
                    pass
            else:
                try:
                    self.list_of_var_dicts[task_index][parameter_key] = value
                except IndexError:
                    pass

    def get_parent_item_index(self, item: QTreeWidgetItem) -> typing.Union[int, QTreeWidgetItem]:
        """
        Simple helper method to retrieve the item's parent index or return -1 if there is no parent
        """
        try:
            parent = item.parent()
        except Exception:  # todo: try to figure out what specific exception names could be
            return -1

        # Temporarily switch to the parent item, get the index row, and switch back
        self.treeWidget.setCurrentItem(parent)
        parent_index = self.treeWidget.currentIndex()
        parent_row = parent_index.row()
        self.treeWidget.setCurrentItem(item)

        return parent_row

    def visualize_script(self, var_dicts: list) -> None:
        """
        Display the task names and arguments from the script parser with a QTreeView
        """
        # initialize the variable to None, as it will be (un)changed appropriately via the following lines of codes
        item = None
        self.list_of_var_dicts = var_dicts
        # Create a dictionary with a key for each task, and a list of tuples containing the name and value of each arg
        self.treeWidget.clear()

        task_list = []
        for i in range(len(self.list_of_var_dicts)):
            if "# of Tasks" not in self.list_of_var_dicts[i].keys():
                arg_list = list()
                for key in self.list_of_var_dicts[i]:
                    arg_list.append([key, self.list_of_var_dicts[i][key]])

                task_list.append(arg_list)

        # Add an item for each task and child items for all of its variables
        tree_items = []
        for parameter_pairs in task_list:
            children = []
            for parameter_pair in parameter_pairs:
                if parameter_pair[0].upper() == "Task Type".upper():
                    # Discard the task type label and only show the task type itself
                    item = QTreeWidgetItem([parameter_pair[1]])
                else:
                    parameter_pair[0] = str(parameter_pair[0])
                    parameter_pair[1] = str(parameter_pair[1])
                    children.append(QTreeWidgetItem(parameter_pair))

            if item is None:
                item = QTreeWidgetItem()

            item.addChildren(children)

            tree_items.append(item)

        self.treeWidget.invisibleRootItem().addChildren(tree_items)
        self.add_empty_item_at_end()

    def add_empty_item_at_end(self) -> None:
        """
        Add invisible item to allow inserting at the end
        """
        empty_item = QTreeWidgetItem([])
        empty_item.setFlags(
            empty_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable)  # should prevent user from selecting this item
        self.treeWidget.invisibleRootItem().addChild(empty_item)
        self.treeWidget.setCurrentItem(empty_item)

    def dict_to_tree_item(self, task_dict: dict) -> typing.Union[QTreeWidgetItem, None]:
        """
        Reads the task dictionary entry and imports the task name (parent node) all of its
        variables (children nodes), and turns them into a QTreeWidgetItem to be added to
        the tree view
        """
        # Prevent user from running the script until it is saved and reloaded
        self.script_changed_signal.emit()

        if not task_dict:  # if the dictionary is empty
            self.log("task does not have any values in its dictionary variable, cannot add", "error")
            return
        item = QTreeWidgetItem([task_dict["Task type"]])

        arg_list = list()
        for key in task_dict:
            if key != "Task type":
                arg_list.append([key, task_dict[key]])

        # Add parameters as child items
        for parameter in arg_list:
            child = QTreeWidgetItem(parameter)
            item.addChild(child)

        return item

    def update_tree(self):
        """
        Refreshes the tree view to account for the naming convention of duplicate task names
        """
        # Prevent user from running the script until it is saved and reloaded
        self.script_changed_signal.emit()

        list_of_var_dicts_copy = list(self.list_of_var_dicts)

        # remove quotes
        task_names = [self.script_cmd_dropdown.itemText(i).replace('\"', '') for i in
                      range(self.script_cmd_dropdown.count())]

        # For each task name,
        for task_name in task_names:
            # Count the occurrences of that task name,
            counter = 0
            for i in range(len(list_of_var_dicts_copy)):
                if "Task type" in list_of_var_dicts_copy[i].keys():
                    if task_name in list_of_var_dicts_copy[i]["Task type"]:
                        if counter == 0:
                            list_of_var_dicts_copy[i]["Task type"] = f"{task_name}"
                        else:
                            # And number each one after the first one
                            list_of_var_dicts_copy[i]["Task type"] = f"{task_name}_{counter}"
                        counter += 1

        # Refresh the visualizer
        self.visualize_script(list_of_var_dicts_copy)

    def move_selected_down(self):
        """Moves the highlight cursor in the tree view down"""
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

    def move_selected_item_down(self):
        """
        Moves the actual task itself downwards in the tree so that it runs after the task
        that was previously below it. User must save and reload script for this chang to
        take effect
        """
        try:
            if self.treeWidget.currentItem().parent():  # if selected element is a child
                self.treeWidget.setCurrentItem(
                    self.treeWidget.currentItem().parent())  # set the currently selected item to its parent
        except AttributeError:
            return

        current_index = self.treeWidget.currentIndex()  # QModelIndex object
        current_index_row = current_index.row()  # index of the selected item in tree
        number_of_items_in_tree = self.treeWidget.invisibleRootItem().childCount() - 2  # total number of items in tree

        # error/exception prevention measures
        if self.treeWidget.currentItem() is None:  # if nothing is selected  #todo check to see what this does exactly
            return  # exit this method, nothing will happen, an item needs to be selected
        elif current_index_row >= number_of_items_in_tree:  # if the selected item is at the end of the list
            self.log("you are trying to move an item that is at the end of the list downwards, that is not possible")
            return

        # if an item is selected
        list_of_var_dicts_copy = list(
            self.list_of_var_dicts)  # create a copy by value of the list of variable dictionaries

        if self.check_if_script_has_header(list_of_var_dicts_copy):  # if script has a header
            current_index_row += 1  # offset to account for header
            # since moving item "down," it's actually moving up in the list, save the next item
            temporary_item_to_save = list_of_var_dicts_copy[current_index_row + 1]
            # set next item in list to previous item
            try:
                list_of_var_dicts_copy[current_index_row + 1] = list_of_var_dicts_copy[current_index_row]
            except IndexError:
                return
            # restore previous contents of next item to current index (swapping)
            list_of_var_dicts_copy[current_index_row] = temporary_item_to_save
        else:  # if script does not have a header, no offset is needed
            temporary_item_to_save = list_of_var_dicts_copy[current_index_row + 1]
            list_of_var_dicts_copy[current_index_row + 1] = list_of_var_dicts_copy[current_index_row]
            list_of_var_dicts_copy[current_index_row] = temporary_item_to_save

        self.list_of_var_dicts = list(
            list_of_var_dicts_copy)  # the changes applied to the copy will now be reflected onto the real list
        self.update_tree()  # update the tree
        if self.check_if_script_has_header(list_of_var_dicts_copy):
            a = self.treeWidget.invisibleRootItem().child(current_index_row)
        else:
            a = self.treeWidget.invisibleRootItem().child(current_index_row + 1)

        self.treeWidget.setCurrentItem(a)

    def move_selection_up(self):
        """
        Moves the highlight cursor in the tree view up, takes into no current selection into consideration
        """
        # if there is no selection, try to set selection to the last item
        if self.treeWidget.currentItem() is None:
            # attain how many nodes there are in the tree
            child_count = self.treeWidget.invisibleRootItem().childCount()
            # attain the last item of the tree widget
            last_item = self.treeWidget.invisibleRootItem().child(child_count - 1)
            # checks to make sure the last item actually exists (tree is not empty)
            if last_item is not None:
                # sets the selected item to the last node in tree
                self.treeWidget.setCurrentItem(last_item)
                return  # exit function
            else:  # tree is empty
                return  # exit function

        # if there is a currently selected item in the tree, copy its index
        index = self.treeWidget.currentIndex()
        # move the selection based on the previously attained index position
        self.treeWidget.setCurrentIndex(index.sibling(index.row() - 1, index.column()))

    def move_selected_item_up(self):
        """
        Moves the actual task itself upwards, so the task will actually run before the task that
        was previously ahead of it. User will have to save and reload script for this change to
        take effect
        """
        try:
            if self.treeWidget.currentItem().parent():  # if selected element is a child
                # set the currently selected item to its parent
                self.treeWidget.setCurrentItem(self.treeWidget.currentItem().parent())
        except AttributeError:
            return

        current_index_row = self.treeWidget.currentIndex().row()  # index of the selected item in tree
        # index of the blank item that can be selected at end of tree list
        last_invisible_item_index = self.treeWidget.invisibleRootItem().childCount()

        # error/exception prevention measures
        if self.treeWidget.currentItem() is None:  # if nothing is selected  #todo check to see what this does exactly
            return  # exit this method, nothing will happen, an item needs to be selected
        elif current_index_row <= 0:  # if the selected item is at the beginning of the list
            self.log(
                "you are trying to move an item that is at the beginning of the list upwards, that is not possible")
            return
        elif current_index_row == last_invisible_item_index - 1:
            self.log("you are trying to move a non-item in the list upwards, this is not possible")

        if current_index_row == 0:
            self.log("you are trying to move the zeroth item in the list upwards, this is not possible")
            return

        # if an item is selected
        # create a copy by value of the list of variable dictionaries
        list_of_var_dicts_copy = list(self.list_of_var_dicts)

        if self.check_if_script_has_header(list_of_var_dicts_copy):  # if script has a header
            current_index_row += 1  # offset to account for header
            # since moving item "up," it's actually moving down in the list, save the previous item
            temporary_item_to_save = list_of_var_dicts_copy[current_index_row - 1]
            # set next item in list to previous item
            try:
                list_of_var_dicts_copy[current_index_row - 1] = list_of_var_dicts_copy[current_index_row]
            except IndexError:
                return
            # restore previous contents of previous item to current index (swapping)
            list_of_var_dicts_copy[current_index_row] = temporary_item_to_save

        else:  # if script does not have a header, no offset is needed
            temporary_item_to_save = list_of_var_dicts_copy[current_index_row - 1]
            list_of_var_dicts_copy[current_index_row - 1] = list_of_var_dicts_copy[current_index_row]
            list_of_var_dicts_copy[current_index_row] = temporary_item_to_save

        # the changes applied to the copy will now be reflected onto the real list
        self.list_of_var_dicts = list(list_of_var_dicts_copy)
        self.update_tree()  # update the tree

        if self.check_if_script_has_header(list_of_var_dicts_copy):
            a = self.treeWidget.invisibleRootItem().child(current_index_row - 2)
        else:
            a = self.treeWidget.invisibleRootItem().child(current_index_row - 1)

        self.treeWidget.setCurrentItem(a)

    @staticmethod
    def check_if_script_has_header(list_of_var_dicts: list) -> bool:
        """Checks to see if script has a header when passed a list of variable dictionaries.
        Returns true if there is a header and false if otherwise"""
        if '# of Tasks' in list_of_var_dicts[0]:
            return True  # this script has a header
        else:
            return False

    def add_cmd_to_script_clicked(self):
        """
        Function to allow a user to add a selected task in the script editor into the treeview,
        the user must manually click the save script button to keep the changes and reload the
        script.
        """
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

        # if the widget has an ui_to_orderedDict method
        new_var_dict = self.edit_menu.ui_to_orderedDict()

        if new_var_dict is None:
            if task_name == 'Pre-test initialisation':
                new_var_dict = pre_test_dict()
            elif task_name == 'Find element n':
                new_var_dict = find_element_dict()
            elif task_name == "Loop over elements":
                new_var_dict = loop_over_elements_dict()
            elif task_name == "End loop":
                new_var_dict = end_loop_dict()
            elif task_name == "Frequency sweep":
                new_var_dict = frequency_sweep_dict()
            elif task_name == "Configure oscilloscope channels":
                new_var_dict = oscilloscope_channel_dict()
            elif task_name == "Configure oscilloscope timebase":
                new_var_dict = oscilloscope_timebase_dict()
            elif task_name == "Move system":
                new_var_dict = move_system_dict()
            elif task_name == "Configure function generator":
                new_var_dict = function_generator_dict()
            elif task_name == "Select UA channel":
                new_var_dict = select_UA_channel_dict()
            elif task_name == 'Run "Auto Gain Control"':
                new_var_dict = auto_gain_control_dict()
            elif task_name == "Autoset timebase":
                new_var_dict = autoset_timebase_dict()
            else:
                new_var_dict = OrderedDict()

        # add the new dictionary to var_dicts at the correct index
        if len(self.list_of_var_dicts) > 0 and "Task type" not in self.list_of_var_dicts[0]:
            self.list_of_var_dicts.insert(row + 1, new_var_dict)
        else:
            self.list_of_var_dicts.insert(row, new_var_dict)

        item = self.dict_to_tree_item(new_var_dict)
        self.treeWidget.insertTopLevelItems(index, [item])
        self.treeWidget.setCurrentItem(item)
        self.move_selected_down()

        # If the item we added was the first item
        if self.treeWidget.invisibleRootItem().childCount() == 1:
            self.add_empty_item_at_end()

    def save_script(self):
        self.update_tree()
        self.app.processEvents()

        path = QFileDialog.getSaveFileName(
            parent=self, caption="Save script", directory=ROOT_DIR + "/Scripts", filter="Script files (*.wtf)"
        )[0]

        if path == "":
            return

        # remove existing header(s) if there is one
        for i in range(len(self.list_of_var_dicts)):
            try:
                if "# of Tasks" in self.list_of_var_dicts[i].keys():
                    self.list_of_var_dicts.pop(i)
            except IndexError:
                pass

        with open(path, "w") as f:
            num_tasks = len(self.list_of_var_dicts)
            # Customize header dict
            self.list_of_var_dicts.insert(0, header_dict())
            self.list_of_var_dicts[0]["# of Tasks"] = num_tasks
            today = date.today()
            self.list_of_var_dicts[0]["Createdon"] = today.strftime("%d/%m/%Y")

            created_by = QInputDialog.getText(self, "Save script metadata", f"Enter operator name:")[0]
            self.list_of_var_dicts[0]["Createdby"] = created_by

            description = QInputDialog.getText(self, "Save script metadata", f"Enter script description:")[0]
            self.list_of_var_dicts[0]["Description"] = description

            # Write header info
            f.write("[Top Level]\n")

            for arg in self.list_of_var_dicts[0].keys():
                f.write(f'{arg} = "{self.list_of_var_dicts[0][arg]}"\n')
            f.write("\n")

            # Write arguments of each step
            for i in range(len(self.list_of_var_dicts) - 1):
                f.write(f"[Task{i}]\n")
                task_args = self.list_of_var_dicts[i + 1]
                for arg in task_args.keys():
                    f.write(f'{arg} = "{task_args[arg]}"\n')
                f.write("\n")

        self.load_script_signal.emit(path)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    edit_widget = ScriptEditor()

    edit_widget.show()
    sys.exit(app.exec_())

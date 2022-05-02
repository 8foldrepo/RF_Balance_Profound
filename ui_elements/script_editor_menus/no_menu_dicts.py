from collections import OrderedDict


def autoset_timebase_dict():
    return OrderedDict([("Task type", "Autoset timebase")])


def header_dict():
    return OrderedDict(
        [("# of Tasks", ""), ("Createdon", ""), ("Createdby", ""), ("Description", "")]
    )


def end_loop_dict():
    return OrderedDict([("Task type", "End loop")])


def pre_test_dict():
    return OrderedDict([("Task type", "Pre-test initialisation")])


def home_system_dict():
    return OrderedDict([("Task type", "Home system")])


def frequency_sweep_dict():
    return OrderedDict([("Task type", "Frequency sweep")])


def oscilloscope_channel_dict():
    return OrderedDict([("Task type", "Configure oscilloscope channels")])


def oscilloscope_timebase_dict():
    return OrderedDict([("Task type", "Configure oscilloscope timebase")])


def move_system_dict():
    return OrderedDict([("Task type", "Move system")])


def function_generator_dict():
    return OrderedDict([("Task type", "Configure function generator")])


def select_UA_channel_dict():
    return OrderedDict([("Task type", "Select UA channel")])


def auto_gain_control_dict():
    return OrderedDict([("Task type", 'Run "Auto Gain Control"')])

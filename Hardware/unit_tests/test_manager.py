import unittest
from Utilities.load_config import load_configuration
from data_structures.test_data import TestData
from manager import Manager
from random import randrange, choice, uniform


class MyTestCase(unittest.TestCase):

    config = None
    manager = None

    @classmethod
    def setUpClass(cls):
        cls.config = load_configuration()
        cls.manager = Manager(config=cls.config, parent=None, system_info=None, access_level='Administrator')
        cls.manager.add_devices()
        test_data = TestData()
        cls.manager.begin_script_slot(test_data=test_data)

    def test_scan_axis(self):
        self.manager.test_data.set_blank_values()

        element = randrange(1, 10)

        self.manager.element_r_coordinates[element] = 0
        self.manager.element_x_coordinates[element] = 0

        axis = choice(self.manager.Motors.ax_letters)
        self.manager.scan_axis(element=element, axis=axis, num_points=randrange(2, 100), increment=uniform(.04, 2),
                               ref_position=-90, data_storage='Store entire waveform', go_to_peak=True, storage_location='', update_element_position=True)

        if axis == 'R':
            self.assertNotEqual(self.manager.element_r_coordinates[element], 0)
        elif axis == 'X':
            self.assertNotEqual(self.manager.element_x_coordinates[element], 0)


if __name__ == '__main__':
    unittest.main()

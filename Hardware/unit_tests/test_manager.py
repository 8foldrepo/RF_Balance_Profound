import os
import random
import unittest

from Utilities.load_config import load_configuration
from data_structures.test_data import TestData
from manager import Manager
from random import randrange, choice, uniform
from unittest.mock import patch


class MyTestCase(unittest.TestCase):
    config = None
    manager = None

    @classmethod
    def setUpClass(cls):
        cls.config = load_configuration()
        cls.manager = Manager(config=cls.config, parent=None, system_info=None, access_level='Administrator')
        cls.manager.add_devices()
        test_data = TestData()
        cls.manager.test_metadata_slot(test_data=test_data)
        cls.manager.connect_hardware()

    def test_scan_axis(self):
        self.manager.test_data.set_blank_values()

        element = randrange(1, 10)

        self.manager.element_r_coordinates[element] = 0
        self.manager.element_x_coordinates[element] = 0

        axis = choice(self.manager.Motors.ax_letters)
        self.manager.scan_axis(element=element, axis=axis, num_points=randrange(2, 10), increment=uniform(.04, 2),
                               ref_position=-90, data_storage='Store entire waveform', go_to_peak=True,
                               storage_location='', update_element_position=True)

        if axis == 'R':
            self.assertNotEqual(self.manager.element_r_coordinates[element], 0)
        elif axis == 'X':
            self.assertNotEqual(self.manager.element_x_coordinates[element], 0)

    def test_save_log_and_results_summary(self):
        from os.path import exists
        import platform

        if platform.system() != 'Windows':
            self.fail("This application is meant to be ran on Windows machines only, "
                      "directory specifications in program will not work")
        try:
            var_dict: dict = {"Save summary file": "True", "Write UA Calibration": "False",
                              "PromptForCalWrite": "False"}
            self.manager.save_results(
                var_dict=var_dict)  # INFO: results_summary should be default values specified in test_data.py
        except Exception as e:
            self.fail(f"save_results method ran into an exception when it shouldn't have: {e}")

        self.manager.config['Paths']['UA results root directory'] = "C:\\Users\\Public\\Documents\\UA results"
        results_summary = (
                    "C:\\Users\\Public\\Documents\\UA results\\" + self.manager.file_saver.folder_name + '\\Results Summary.txt')
        script_results = (
                    "C:\\Users\\Public\\Documents\\UA results\\" + self.manager.file_saver.folder_name + '\\Log files\\ScriptResults.log')
        self.assertTrue(exists(results_summary))  # TEST: tests if files exist
        self.assertTrue(exists(script_results))
        self.assertTrue(
            os.stat(results_summary).st_size != 0)  # TEST: this file should have default information within it
        # INFO: cannot check whether script results should be empty since tests are ran in random order

    def test_configure_function_generator(self):
        mVpp = randrange(1000, 10000)
        mode = 'Toneburst'
        frequency_mhz = randrange(1, 10)

        var_dict = {"Amplitude (mVpp)": mVpp, "Mode": mode, 'Enable output': True,
                    'Set frequency options': 'From config cluster', 'Frequency (MHz)': frequency_mhz, '#Cycles': '3'}

        self.manager.configure_function_generator(var_dict=var_dict)
        self.assertEqual(frequency_mhz * 1000000, self.manager.AWG.get_frequency_hz())
        self.assertTrue(self.manager.AWG.get_output())

        self.assertTrue(
            ["", "Configure FGen+PwrMeters", f"Frequency set to {self.manager.AWG.get_frequency_hz() / 1000000} MHz",
             "", ]
            in self.manager.test_data.script_log)

        self.assertEqual(mVpp, self.manager.AWG.get_amplitude_v() * 1000)
        self.assertTrue(self.manager.AWG.get_burst()[0])

        self.assertTrue(["", "Config FGen", f"{mVpp}mVpp;{self.manager.AWG.get_frequency_hz() / 1000000}MHz,{mode}"]
                        in self.manager.test_data.script_log)

    def test_configure_oscilloscope_timebase(self):
        timebase_us = round(random.uniform(1, 10), 3)
        delay_us = round(random.uniform(1, 10), 3)
        var_dict = {'Timebase': timebase_us, 'Delay': delay_us}
        try:
            self.manager.configure_oscilloscope_timebase(var_dict=var_dict)
        except Exception as e:

            self.fail(f"manager's configure_oscilloscope_timebase() method "
                      f"raised exception when it shouldn't have: {e}")

        self.assertEqual(timebase_us / 1000000 * 8, self.manager.Oscilloscope.get_horizontal_scale_sec())
        self.assertEqual(delay_us / 1000000, self.manager.Oscilloscope.get_horizontal_offset_sec())

    def test_autoset_timebase(self):
        self.manager.autoset_timebase()
        oscilloscope = self.manager.Oscilloscope
        self.assertEqual(self.manager.config['Oscilloscope_timebase']["time_window_maximum"],
                         oscilloscope.max_time_of_flight)
        self.assertEqual(self.manager.config['Oscilloscope_timebase']["time_window_minimum"],
                         oscilloscope.min_time_of_flight)
        self.assertEqual(self.manager.config['Oscilloscope_timebase']["Horizontal scale (us)"] * 10 ** -6,
                         oscilloscope.get_horizontal_range_sec())
        time_of_flight_window = (oscilloscope.max_time_of_flight - oscilloscope.min_time_of_flight) / 1000000
        self.assertEqual(oscilloscope.get_horizontal_offset_sec(),
                         oscilloscope.min_time_of_flight / 1000000 + time_of_flight_window / 2)

    def test_disconnect_hardware(self):
        try:
            self.manager.disconnect_hardware()
        except Exception as e:
            self.fail(f"Exception encountered in manager's disconnect_hardware method when it shouldn't have: {e}")
        for device in self.manager.devices:
            self.assertFalse(device.connected)
        self.manager.connect_hardware()

    # WARNING: do not remove the import statements in method below, contrary to the IDE linting
    # WARNING: scanner, these imports are needed. If you notice missing imports, please restore
    # WARNING: them via GitHub's commit history
    def test_update_sensors(self):
        if self.manager.config['Debugging']['simulate_thermocouple']:
            from Hardware.Simulated.simulated_thermocouple import SimulatedThermocouple
            with_clause_thermocouple = 'Hardware.Simulated.simulated_thermocouple.SimulatedThermocouple.get_reading'
        else:
            from Hardware.ni_thermocouple import NIThermocouple
            with_clause_thermocouple = 'Hardware.ni_thermocouple.NIThermocouple.get_water_level'

        if self.manager.config['Debugging']['simulate_io_board']:
            from Hardware.Simulated.simulated_io_board import SimulatedIOBoard
            with_clause_water_level = 'Hardware.Simulated.simulated_io_board.SimulatedIOBoard.get_water_level'
            with_clause_ua_pump = 'Hardware.Simulated.simulated_io_board.SimulatedIOBoard.get_ua_pump_reading'
        else:
            from Hardware.dio_board import DIOBoard
            with_clause_water_level = 'Hardware.dio_board.DIOBoard.get_water_level'
            with_clause_ua_pump = 'Hardware.dio_board.DIOBoard.get_ua_pump_reading'

        with patch(with_clause_water_level) as mock_get_water_level, \
                patch(with_clause_ua_pump) as mock_get_pump_reading, \
                patch(with_clause_thermocouple) as mock_get_reading:
            try:
                self.manager.update_sensors()
            except Exception as e:
                self.fail(f"test_update_sensors method in manager raised exception when it shouldn't have: {e}")
            self.assertTrue(self.manager.IO_Board.connected)
            self.assertTrue(self.manager.thermocouple.connected)
            mock_get_water_level.assert_called()
            mock_get_pump_reading.assert_called()
            mock_get_reading.assert_called()

    def test_capture_scope(self):
        try:
            time, voltage = self.manager.capture_scope(plot=False)
        except Exception as e:
            self.fail(f"manager's capture scope failed when it shouldn't have: {e}")
        self.assertIsNotNone(time)
        self.assertIsNotNone(voltage)

        self.manager.Oscilloscope.disconnect_hardware()
        self.assertRaises(TypeError, self.manager.capture_scope(plot=False))
        self.manager.Oscilloscope.connect_hardware()


if __name__ == '__main__':
    unittest.main()

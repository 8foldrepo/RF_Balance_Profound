import time as t
import unittest

import serial.serialutil
from termcolor import colored

from Hardware.mt_balance import MT_balance


class TestBalance(unittest.TestCase):
    balance = None

    @classmethod
    def setUpClass(cls):
        cls.balance = MT_balance(config=None)
        cls.balance.connect_hardware()

    def test_fields_setup(self):
        print(colored("Testing fields setup", 'cyan'))
        self.assertIsNotNone(self.balance.config)
        self.assertEqual(self.balance.timeout_s, self.balance.config[self.balance.device_key]['timeout_s'])
        self.assertEqual(self.balance.port, self.balance.config[self.balance.device_key]['port'])

    def test_config_loading(self):
        print(colored("Testing config is not None", 'cyan'))
        self.assertIsNotNone(self.balance.config)

    def test_connected(self):
        print(colored("Testing connected", 'cyan'))
        self.assertEqual(self.balance.connected, True)

    def test_reconnect(self):
        print(colored("Testing reconnect", 'cyan'))
        self.balance.disconnect_hardware()
        self.assertEqual(self.balance.connected, False)
        self.assertIsNone(self.balance.get_reading())  # should print log error
        self.balance.connect_hardware()
        self.assertEqual(self.balance.connected, True)
        self.assertIsNotNone(self.balance.get_reading())

    def test_disconnect_hardware(self):
        print(colored("Testing disconnect_hardware", 'cyan'))

        self.balance.disconnect_hardware()
        self.assertFalse(self.balance.connected)
        self.assertIsNone(self.balance.get_reading())
        self.balance.connect_hardware()
        self.assertTrue(self.balance.connected)
        self.assertIsNotNone(self.balance.get_reading())

    def test_connect_hardware(self):
        print(colored("testing connect hardware method", 'cyan'))
        self.balance.disconnect_hardware()
        connected, feedback = self.balance.connect_hardware()
        self.assertIsNotNone(self.balance.ser)
        self.assertTrue(self.balance.connected)
        self.assertEqual(self.balance.connected, connected)
        self.assertEqual(feedback, "")

    def test_get_continuous_readings(self):
        print(colored("Testing read continuously", 'cyan'))
        self.balance.start_continuous_reading()

        start_time = t.time()
        num_captures = 100
        for _ in range(num_captures):
            self.assertIsInstance(self.balance.get_reading(), float)

        capture_time = (t.time() - start_time) / num_captures
        self.assertLessEqual(capture_time, 4)

    def test_stable_reading(self):
        print(colored("Testing stable reading", 'cyan'))
        reading = self.balance.get_stable_reading()
        self.assertIsInstance(reading, float)

    def test_reset(self):
        print(colored('testing reset method', 'cyan'))
        try:
            self.balance.reset()
        except Exception as e:
            self.fail(f"reset method in mt_balance raised exception when it shouldn't have: {e}")

    def test_get_serial_number(self):
        print(colored("Testing get serial number", 'cyan'))
        sn = self.balance.get_serial_number()
        self.assertIsInstance(sn, str)
        self.assertNotEqual(sn, '')

    def test_zero_instantly(self):
        print(colored("Testing zero instantly", 'cyan'))
        self.balance.zero_balance_instantly()
        self.assertAlmostEqual(self.balance.get_reading(), 0, 4)

    def test_zero_stable(self):
        print(colored("Testing zero stable", 'cyan'))
        self.balance.zero_balance_stable()
        self.assertAlmostEqual(self.balance.get_reading(), 0, 4)

    def test_connect_hardware_not_found(self):
        print(colored("Testing connect hardware's exception throwing ability", 'cyan'))
        previous_value = self.balance.port
        self.balance.disconnect_hardware()
        self.balance.port = '0'
        connected, feedback = self.balance.connect_hardware()
        self.assertFalse(connected)
        assert (f"{self.balance.device_key} not connected. Check that it is plugged in and look at Device manager"
                f" to determine which COM port to use and enter it into local.yaml:" in feedback)
        self.balance.port = previous_value
        try:
            self.balance.connect_hardware()
        except serial.serialutil.SerialException:
            self.fail(
                "connect_hardware threw an exception in test_connect_hardware_except_handling even though port was corrected")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.balance.wrap_up()


if __name__ == '__main__':
    unittest.main()

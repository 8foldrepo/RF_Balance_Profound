import unittest
from Hardware.mt_balance import MT_balance
import time as t

class TestBalance(unittest.TestCase):
    def setUp(self):
        self.balance = MT_balance(config=None)
        self.balance.connect_hardware()

    def test_config_loading(self):
        print("Testing loading")
        self.assertIsNotNone(self.balance.config)

    def test_connected(self):
        print("Testing connected")
        self.assertEqual(self.balance.connected, True)

    def test_reconnect(self):
        print("Testing reconnect")
        self.balance.disconnect_hardware()
        self.assertEqual(self.balance.connected, False)
        self.assertIsNone(self.balance.get_reading())
        self.balance.connect_hardware()
        self.assertEqual(self.balance.connected, True)
        self.assertIsNotNone(self.balance.get_reading())

    def test_get_continuous_readings(self):
        print("Testing read continuously")
        self.balance.start_continuous_reading()

        starttime = t.time()
        num_captures = 100
        for i in range(num_captures):
            self.assertIsInstance(self.balance.get_reading(), float)

        capture_time = (t.time() - starttime) / num_captures
        self.assertLessEqual(capture_time, 4)

    def test_stable_reading(self):
        print("Testing stable reading")
        reading = self.balance.get_stable_reading()
        self.assertIsInstance(reading, float)

    def test_get_serial_number(self):
        print("Testing get serial number")
        sn = self.balance.get_serial_number()
        self.assertIsInstance(sn, str)
        self.assertNotEqual(sn, '')

    def test_zero_instantly(self):
        print("Testing zero instantly")
        self.balance.zero_balance_instantly()
        self.assertAlmostEqual(self.balance.get_reading(), 0, 4)

    def test_zero_stable(self):
        print("Testing zero stable")
        self.balance.zero_balance_stable()
        self.assertAlmostEqual(self.balance.get_reading(), 0, 4)


if __name__ == '__main__':
    unittest.main()
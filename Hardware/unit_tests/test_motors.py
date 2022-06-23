import random
import time as t
import unittest

from Hardware.galil_motor_controller import GalilMotorController
from Utilities.load_config import load_configuration


class TestMotors(unittest.TestCase):
    """
    Warning, if connected to the motors this program will move the motors around randomly.
    Tests all core functionality of the motion controller
    """

    @classmethod
    def setUpClass(self):
        self.Motors = GalilMotorController(config=None, lock=None)
        self.Motors.connect_hardware()
        self.config = load_configuration()

    def test_connected(self):
        self.assertTrue(self.Motors.connected)
        self.assertIsNotNone(self.Motors.config)

        self.assertEqual(self.Motors.ax_letters, self.Motors.config[self.Motors.device_key]['axes'])
        self.assertEqual(self.Motors.increment_ray, self.Motors.config[self.Motors.device_key]['increment_ray'])

    def test_set_origin(self):
        self.Motors.set_origin_here()
        self.Motors.get_position()

        margin_of_error = .4
        for i in range(len(self.Motors.coords_mm)):
            self.assertLessEqual(abs(self.Motors.coords_mm[i] - 0), margin_of_error)

    def test_begin_motion(self):
        axis = random.choice(self.Motors.ax_letters)
        ax_index = self.Motors.ax_letters.index(axis)
        current_pos = self.Motors.coords_mm[ax_index]

        self.Motors.begin_motion(axis, 1)
        margin_of_error = .4  # mm or degrees
        actual_pos = self.Motors.coords_mm[ax_index]
        target_pos = self.Motors.increment_ray[ax_index] + current_pos
        self.assertLessEqual(abs(actual_pos - target_pos), margin_of_error)

    def test_go_to_position(self):
        # test go to position
        x = random.randrange(-263, 50)
        r = random.randrange(-180, -80)
        successful = self.Motors.go_to_position(self.Motors.ax_letters, [x, r])
        self.assertTrue(successful)
        margin_of_error = .4  # mm or degrees
        self.assertLessEqual(abs(self.Motors.coords_mm[0] - x), margin_of_error)
        self.assertLessEqual(abs(self.Motors.coords_mm[1] - r), margin_of_error)

    def test_reconnect(self):
        # test disconnecting and reconnecting
        self.Motors.disconnect_hardware()
        self.assertFalse(self.Motors.moving)
        successful = self.Motors.go_to_position(self.Motors.ax_letters, [0] * len(self.Motors.ax_letters))
        self.assertFalse(successful)
        self.Motors.connect_hardware()
        self.assertTrue(self.Motors.connected)
        self.Motors.set_origin_here()
        successful = self.Motors.go_to_position(self.Motors.ax_letters, [0] * len(self.Motors.ax_letters))
        self.assertTrue(successful)
        margin_of_error = .4
        for j in range(len(self.Motors.coords_mm)):
            self.assertLessEqual(abs(self.Motors.coords_mm[j] - 263), margin_of_error)

    def test_stop_motion(self):
        # test stop_motion
        for j in range(2):
            self.Motors.command('DP 0')
            self.Motors.get_position()
            self.Motors.command('PA 5000')
            self.Motors.command('BG A')
            t.sleep(.1)
            self.Motors.get_position()
            self.assertTrue(self.Motors.moving)
            t.sleep(.1)
            self.Motors.stop_motion()

    def test_go_home_1d(self):
        self.Motors.set_origin_here()
        self.Motors.get_position()
        coords = self.Motors.coords_mm
        self.assertAlmostEqual(coords[1],0,1)
        self.Motors.go_to_position(['R'],
                              [self.Motors.coords_mm[1] + self.Motors.config["WTF_PositionParameters"]["ThetaPreHomeMove"]],
                              enable_ui=False)
        coords = self.Motors.coords_mm
        self.assertAlmostEqual(coords[1], self.Motors.config["WTF_PositionParameters"]["ThetaPreHomeMove"],2)
        self.Motors.command("HM B")
        self.Motors.command("BG B")
        self.Motors.wait_for_motion_to_complete()
        self.Motors.get_position()
        self.Motors.set_origin_1d('R', self.Motors.coords_mm[1] - (self.Motors.config['WTF_PositionParameters']['ThetaHomeCoord'] +
                                                         self.Motors.config['WTF_PositionParameters'][
                                                             'ThetaHomeEdgeOffset']))
        self.Motors.get_position()
        coords = self.Motors.coords_mm
        self.assertAlmostEqual(coords[1], (self.Motors.config['WTF_PositionParameters']['ThetaHomeCoord'] +
                                           self.Motors.config['WTF_PositionParameters'][
                                               'ThetaHomeEdgeOffset']),2)
        self.Motors.go_to_position(['R'], [self.Motors.coords_mm[1] + self.Motors.config["WTF_PositionParameters"]["ThetaHomeCoord"]],
                              enable_ui=False)
        self.assertAlmostEqual(coords[1], (self.Motors.config['WTF_PositionParameters']['ThetaHomeCoord']),2)

    def test_go_home(self):
        if True not in self.Motors.config[self.Motors.device_key]['enable_homing_ray']:
            return

        start_time = t.time()
        successful = self.Motors.go_home()
        # make sure it did not take much longer than the cooldown
        # assumes that there is no home switch

        # Flip this check to True when limit switches are installed
        self.assertLessEqual(t.time() - start_time,
                             self.Motors.config[self.Motors.device_key]['move_timeout_s'] * 3 + 3)


if __name__ == '__main__':
    unittest.main()

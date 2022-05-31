# Script/example code for testing out hardware class
import unittest
from termcolor import colored
from Hardware.keysight_oscilloscope import KeysightOscilloscope
import random


class TestOscilloscope(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.osc = KeysightOscilloscope()
        self.osc.connect_hardware()

    def test_config_loading(self):
        self.assertIsNotNone(self.osc.config)

    def test_set_to_defaults(self):
        print(colored("running set to default test", 'cyan'))
        self.osc.set_to_defaults()
        self.assertAlmostEqual(self.osc.channel, self.osc.config[self.osc.device_key]['channel'],1)
        self.assertAlmostEqual(self.osc.max_time_of_flight,
                                self.osc.config['Autoset timebase']["Max time of flight (us)"],1)
        assert self.osc.min_time_of_flight == self.osc.config['Autoset timebase']["Min time of flight (us)"]
        self.assertAlmostEqual(self.osc.range_s, self.osc.config['Autoset timebase']["Horizontal scale (us)"] * 10 ** -6,1)
        self.assertAlmostEqual(self.osc.time_of_flight_window,
                                (self.osc.max_time_of_flight - self.osc.min_time_of_flight) / 1000000)
        self.assertAlmostEqual(self.osc.offset_s, self.osc.min_time_of_flight / 1000000 + self.osc.time_of_flight_window / 2,1)
        assert self.osc.autorange_v == bool(self.osc.config[self.osc.device_key]["autorange_v_startup"])
        self.assertAlmostEqual(self.osc.range_mV, self.osc.config[self.osc.device_key]["range_mV"])
        self.assertAlmostEqual(self.osc.average_count, self.osc.config[self.osc.device_key]["averages"],1)
        assert self.osc.external_trigger == self.osc.config[self.osc.device_key]["ext_trigger"]
        self.assertAlmostEqual(self.osc.timeout_s, self.osc.config[self.osc.device_key]["timeout_s"],1)

    def test_disconnect_hardware(self):
        print(colored("running disconnect hardware test", 'cyan'))
        self.osc.disconnect_hardware()
        assert not self.osc.connected
        self.osc.connect_hardware()
    
    def test_set_averaging(self):
        print(colored("running set averaging test", 'cyan'))
        averages = random.randrange(1, 10)
        self.osc.set_averaging(averages=averages)
        self.assertAlmostEqual(self.osc.averages, averages,1)
        if averages > 1:
            type1 = self.osc.ask(":ACQ:TYPE?")
            assert type1 == "AVER\n"
            self.assertAlmostEqual(int(self.osc.ask(":ACQ:COUN?")), int(averages),1)
        else:
            type2 = self.osc.ask(":ACQ:TYPE?")
            assert type2 == "HRES\n"
    
    def test_set_trigger(self):
        print(colored("running set trigger test", 'cyan'))
        external = bool(random.getrandbits(1))
        self.osc.set_trigger(external=external)
        trig_mode = self.osc.ask(":TRIG:MODE?")
        mode = self.osc.ask(":TRIG:MODE?")
        assert mode == "EDGE\n"
        assert self.osc.ask(":TRIG:EDGE:SLOP?") == "POS\n"
        if external:
            assert self.osc.ask(":TRIG:EDGE:SOUR?") == "EXT\n"
        else:
            assert self.osc.ask(":TRIG:EDGE:SOUR?") == "CHAN1\n"
    
    def test_horizontal_scale(self):
        print(colored("running horizontal scale test", 'cyan'))
        seconds = random.uniform(0, .0005)
        self.osc.set_horizontal_scale_sec(seconds=seconds)
        self.assertAlmostEqual(self.osc.get_horizontal_scale_sec(), seconds,1)
        
    def test_horizontal_range(self):
        print(colored("running horizontal range test", 'cyan'))
        seconds = random.randrange(1, 30)  # set range between 1 and 30 seconds
        self.osc.set_horizontal_range_sec(seconds=float(seconds))
        self.assertAlmostEqual(self.osc.get_horizontal_range_sec(), float(seconds),1)
        self.assertAlmostEqual(self.osc.range_s, float(seconds),1)
        
    def test_horizontal_offset(self):
        print(colored("running horizontal offset test", 'cyan'))
        offset_seconds = random.uniform(-1, 1)
        in_range = self.osc.set_horizontal_offset_sec(offset=offset_seconds)
        if in_range:
            self.assertAlmostEqual(self.osc.get_horizontal_offset_sec(), offset_seconds,1)
        self.assertAlmostEqual(self.osc.offset_s, offset_seconds,1)
        
    def test_vertical_scale(self):
        print(colored("running vertical scale test", 'cyan'))
        scale1 = random.uniform(0.1, 50)
        self.osc.set_vertical_scale_V(channel=1, volts_per_div=scale1)
        scale2 = self.osc.get_vertical_scale_V(channel=1)
        self.assertAlmostEqual(scale1, scale2,1)
        self.assertAlmostEqual(self.osc.range_mV / 1000, 8 * scale1,1)
        
    def test_vertical_range(self):
        print(colored("running vertical range test", 'cyan'))
        range_V = random.uniform(.01, 50)
        self.osc.set_vertical_range_V(channel=1, volts=range_V)
        self.assertAlmostEqual(self.osc.get_vertical_range_V(channel=1), range_V,1)
        self.assertAlmostEqual(self.osc.range_mV, range_V * 1000,1)
    
    def test_vertical_offset(self):
        print(colored("running vertical offset test", 'cyan'))
        offset_V = random.uniform(-20, 20)
        self.osc.set_vertical_offset_V(channel=1, offset=offset_V)
        self.assertAlmostEqual(self.osc.get_vertical_offset_V(channel=1), offset_V,1)
        
    def test_set_timebase(self):
        print(colored("running autoset timebase test", 'cyan'))
        self.osc.autoset_oscilloscope_timebase()
        self.assertAlmostEqual(self.osc.max_time_of_flight,
                                self.osc.config['Autoset timebase']["Max time of flight (us)"],1)
        self.assertAlmostEqual(self.osc.min_time_of_flight,
                                self.osc.config['Autoset timebase']["Min time of flight (us)"],1)
        self.assertAlmostEqual(self.osc.range_s, self.osc.config['Autoset timebase']["Horizontal scale (us)"] * 10 ** -6,1)
        self.assertAlmostEqual(self.osc.time_of_flight_window,
                                (self.osc.max_time_of_flight - self.osc.min_time_of_flight) / 1000000,1)
        self.assertAlmostEqual(self.osc.offset_s, self.osc.min_time_of_flight / 1000000 + self.osc.time_of_flight_window / 2,1)
        self.osc.set_horizontal_range_sec(self.osc.range_s)
        self.osc.set_horizontal_offset_sec(self.osc.offset_s)
        self.assertAlmostEqual(self.osc.get_horizontal_range_sec(), self.osc.range_s,1)
        self.assertAlmostEqual(self.osc.get_horizontal_offset_sec(), self.osc.offset_s,1)

    def test_set_capture(self):
        for i in range(5):
            time, voltage = self.osc.capture(1)
            for j in range(len(time)):
                self.assertIsInstance(time[j], float)
                self.assertIsInstance(voltage[j], float)
            self.assertEqual(len(time), len(voltage))
            time, voltage = self.osc.capture(2)
            self.assertEqual(len(time), len(voltage))
            for j in range(len(time)):
                self.assertIsInstance(voltage[j], float)

    @classmethod
    def tearDownClass(self) -> None:
        self.osc.wrap_up()


if __name__ == '__main__':
    unittest.main()
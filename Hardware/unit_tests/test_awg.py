from Hardware.keysight_awg import KeysightAWG
from Utilities.useful_methods import error_acceptable


# todo: refactor into the standard unit_test library format

def unit_test():
    """
    Tests all key features of the waveform generator in a random order with random parameters 10 times.
    Run in debug mode with a breakpoint on any exception to search for bugs.
    If the test passes the test will print "test passed :)"
    """
    import random

    awg = KeysightAWG()
    awg.connect_hardware()

    # test a random sequence of operations 10 times
    for i in range(10):
        step_sequence = list(range(10))
        random.shuffle(step_sequence)

        for step_number in step_sequence:
            if step_number == 0:  # TEST: output
                on = bool(random.getrandbits(1))
                awg.set_output(on=on)
                if on:
                    assert awg.get_output() is True
                else:
                    assert awg.get_output() is False
            if step_number == 1:  # TEST: frequency (Hz)
                frequency = round(random.uniform(.0001, 19999999), 2)
                successful = awg.set_frequency_hz(frequency=frequency)
                freq = awg.get_frequency_hz()
                assert error_acceptable(freq, frequency, 2) or not successful
            if step_number == 2:  # TEST: offset (V)
                offset = random.uniform(-5, 5)
                awg.set_offset_v(offset=offset)
                assert error_acceptable(offset, awg.get_offset_v())
            if step_number == 3:  # TEST: function
                possible_funcs = ['SIN', 'SQU', 'RAMP', 'TRI', 'NOIS', 'PRBS']
                func = random.choice(possible_funcs)
                awg.set_function(func=func)
                func2 = awg.get_function()
                assert func2 == func
            if step_number == 4:  # TEST: check connected
                awg.disconnect_hardware()
                assert not awg.check_connected()
                awg.connect_hardware()
                assert awg.check_connected()
            if step_number == 5:  # TEST: wrap up
                awg.wrap_up()
                assert not awg.check_connected()
                awg.connect_hardware()
                assert awg.check_connected()
            if step_number == 6:  # TEST: amplitude (V)
                amplitude = round(random.uniform(1, 9.9999), 2)
                awg.set_amplitude_v(amplitude=amplitude)
                assert amplitude == awg.get_amplitude_v()
            if step_number == 7:  # TEST: burst
                on = bool(random.getrandbits(1))
                awg.set_burst(on=on)
                response = awg.get_burst()[0]
                if on:
                    assert response
                else:
                    assert not response
            if step_number == 8:  # TEST: number of cycles
                cycles = random.randint(1, 99)
                awg.set_cycles(cycles=cycles)
                cycles2 = awg.get_cycles()
                assert cycles2 == cycles
            if step_number == 9:  # TEST: phase degrees
                phase_degrees = random.randint(0, 180)
                awg.set_phase_degrees(phase_degrees=phase_degrees)
                phase = awg.get_phase_degrees()
                assert error_acceptable(phase, phase_degrees, 2)
            # if step_number == 10:  # TEST: output impedance
            #     ...
    print("Test passed :)")


if __name__ == "__main__":
    unit_test()

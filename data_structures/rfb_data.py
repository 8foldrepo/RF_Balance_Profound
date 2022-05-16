from statistics import mean
from typing import List, Tuple

from Utilities.formulas import calculate_total_uncertainty_percent, calculate_random_uncertainty_percent, \
    calculate_standard_deviation
from definitions import FrequencyRange


class RFBData:
    element: int
    frequency_range: FrequencyRange
    water_temperature_c: float

    # Test criteria
    Pf_max: float
    Pa_max: float
    ref_limit: float

    times_s: List[float]
    # The indices of these lists match the times array 1 for 1 and each entry is a capture that occurred at that time
    f_meter_readings_w: List[float]
    r_meter_readings_w: List[float]
    acoustic_powers_w: List[float]
    balance_readings_g: List[float]
    #   Record of whether the AWG was off or on for each sample
    awg_on_ray: List[bool]

    # Instantaneous readings to be shown in the UI
    grams: float
    forward_power_w: float
    reflected_power_w: float

    # Analysis metrics of the graph as a whole
    p_on_rand_unc: float
    p_off_rand_unc: float
    p_on_total_unc: float
    p_off_total_unc: float
    p_com_rand_unc: float
    p_com_total_unc: float
    acoustic_power_off_mean: float
    acoustic_power_on_mean: float
    acoustic_power_mean: float
    forward_power_on_mean: float
    reflected_power_on_mean: float
    efficiency_percent: float
    reflected_power_percent: float
    forward_power_max_extrapolated: float

    on_indices: List[Tuple[int, int]]
    off_indices: List[Tuple[int, int]]

    on_time_intervals_s = List[Tuple[float, float]]
    off_time_intervals_s = List[Tuple[float, float]]

    acoustic_power_on_means: list
    acoustic_power_off_means: list

    std_too_high: bool

    def __init__(self, element: int, frequency_range: FrequencyRange, water_temperature_c: float, Pf_max: float,
                 Pa_max: float, ref_limit: float, config):
        self.config = config
        self.element = element
        self.frequency_range = frequency_range
        self.water_temperature_c = water_temperature_c
        self.Pf_max = float(Pf_max)
        self.Pa_max = float(Pa_max)
        self.ref_limit = float(ref_limit)
        self.std_too_high = False

    def update_realtime_data(self):
        """Perform data analysis necessary to populate the RFB tab in the UI"""

        self.on_indices = self.get_on_interval_indices()
        self.off_indices = self.get_off_interval_indices()

        # List containing an average during each of the intervals while the UA was on
        self.acoustic_power_on_means, self.p_on_rand_unc, self.p_on_total_unc, std_too_high = (
            self.analyze_intervals(self.acoustic_powers_w, self.on_indices)
        )
        # Mean acoustic power while on
        if len(self.acoustic_power_on_means) > 0:
            self.acoustic_power_on_mean = mean(self.acoustic_power_on_means)
        else:
            self.acoustic_power_on_mean = float('nan')

        # List containing an average during each of the intervals while the UA was off
        self.acoustic_power_off_means, self.p_off_rand_unc, self.p_off_total_unc, a_std_too_high = (
            self.analyze_intervals(self.acoustic_powers_w, self.off_indices)
        )

        if len(self.acoustic_powers_w) > 0:
            self.acoustic_power_mean = mean(self.acoustic_powers_w)
        else:
            self.acoustic_power_mean = float('nan')

        # Mean acoustic power while off
        if len(self.acoustic_power_off_means) > 0:
            self.acoustic_power_off_mean = mean(self.acoustic_power_off_means)
        else:
            self.acoustic_power_off_mean = float('nan')

        # List containing all readings while AWG was on
        forward_power_on_means, _, _, f_std_too_high = self.analyze_intervals(self.f_meter_readings_w,
                                                                              self.on_indices)
        # Mean acoustic power while on
        if len(forward_power_on_means) > 0:
            self.forward_power_on_mean = mean(forward_power_on_means)
        else:
            self.forward_power_on_mean = float('nan')

        # List containing all readings while AWG was on
        reflected_power_on_means, _, _, r_std_too_high = self.analyze_intervals(self.r_meter_readings_w,
                                                                                self.on_indices)
        # Mean reflected power while on
        if len(reflected_power_on_means) > 0:
            self.reflected_power_on_mean = mean(reflected_power_on_means)
        else:
            self.reflected_power_on_mean = float('nan')

        if len(self.balance_readings_g) != 0:
            self.grams = self.balance_readings_g[len(self.balance_readings_g) - 1]
        else:
            self.grams = float('nan')
        if len(self.f_meter_readings_w) != 0:
            self.forward_power_w = self.f_meter_readings_w[len(self.f_meter_readings_w) - 1]
        else:
            self.forward_power_w = float("nan")
        if len(self.r_meter_readings_w) != 0:
            self.reflected_power_w = self.r_meter_readings_w[len(self.r_meter_readings_w) - 1]
        else:
            self.reflected_power_w = float("nan")

        self.p_com_rand_unc = calculate_random_uncertainty_percent(self.acoustic_powers_w)
        self.p_com_total_unc = calculate_total_uncertainty_percent(self.acoustic_powers_w)
        self.std_too_high = a_std_too_high or f_std_too_high or r_std_too_high

    # Do not call this method while a rfb_data_logger is capturing readings
    def trim_data(self):
        """Trim list attributes to the length of the smallest one"""

        from Utilities.useful_methods import trim
        self.times_s, self.acoustic_powers_w, self.awg_on_ray, self.f_meter_readings_w, self.r_meter_readings_w, \
            self.balance_readings_g = trim(
                [self.times_s, self.acoustic_powers_w, self.awg_on_ray,
                 self.f_meter_readings_w, self.r_meter_readings_w, self.balance_readings_g]
                )

    def end_of_test_data_analysis(self):
        self.trim_data()
        self.update_realtime_data()

        self.on_time_intervals_s = self.convert_interval_indices_to_times(self.on_indices)
        self.off_time_intervals_s = self.convert_interval_indices_to_times(self.off_indices)

        if self.forward_power_on_mean != 0:
            self.efficiency_percent = self.acoustic_power_on_mean / (
                    self.forward_power_on_mean - self.reflected_power_on_mean) * 100
        else:
            self.efficiency_percent = 0

        if self.forward_power_on_mean != 0:
            self.reflected_power_percent = self.reflected_power_on_mean / self.forward_power_on_mean * 100
        else:
            self.reflected_power_percent = 1

        # todo: test

        # Extrapolate the forward power that would be necessary to produce the target clinical acoustic power.
        # If this exceeds a limit the test will fail
        max_f_power = max(self.f_meter_readings_w)
        max_a_power = max(self.acoustic_powers_w)
        self.forward_power_max_extrapolated = max_f_power * (self.Pa_max / max_a_power)

    def get_on_interval_indices(self) -> List[Tuple[int, int]]:
        """
        Examines the awg_on_ray for the intervals while the AWG was on,
        and excludes a fixed settling time from the beginning of the interval.
        Returns a list of pairs of integers corresponding to the indices of this class' list attributes where
        the AWG was on and the sensors have had time to settle.
        """
        buffer = self.config["Analysis"]["samples_to_remove_at_end"]
        if len(self.awg_on_ray) == 0:
            return []

        if len(self.awg_on_ray) == 1:
            if self.awg_on_ray[0]:
                return [(0, 1)]
            else:
                return []

        start_indices = []
        stop_indices = []

        for i in range(1, len(self.awg_on_ray)):
            if i == 1 and self.awg_on_ray[i - 1] and self.awg_on_ray[i]:
                start_indices.append(self.add_delay_to_index(i, self.config["Analysis"]["settling_time_s"]))
            elif not self.awg_on_ray[i - 1] and self.awg_on_ray[i]:
                start_indices.append(self.add_delay_to_index(i, self.config["Analysis"]["settling_time_s"]))
            elif self.awg_on_ray[i - 1] and not self.awg_on_ray[i]:
                stop_indices.append(i - buffer)

            if i == len(self.awg_on_ray) - 1 and self.awg_on_ray[i]:
                stop_indices.append(i+1-buffer)

        assert len(start_indices) <= len(stop_indices)

        output = []
        for i in range(len(start_indices)):
            output.append((start_indices[i], stop_indices[i]))

        return output

    def convert_interval_indices_to_times(self, indices: List[Tuple[int, int]]) -> List[Tuple[float, float]]:
        """Returns the given list of intervals, containing list indices, to
        the corresponding time from the time array"""

        copy = list(indices)

        for i in range(len(copy)):
            copy[i] = list(copy[i])

            copy[i][0] = self.times_s[copy[i][0]]
            copy[i][1] = self.times_s[copy[i][1] - 1]

            copy[i] = tuple(copy[i])

        return copy

    def get_off_interval_indices(self) -> List[Tuple[int, int]]:
        """
        Examines the awg_on_ray for the intervals while the AWG was on,
        and excludes a fixed settling time from the beginning of the interval.
        Returns a list of pairs of integers corresponding to the indices of this class' list attributes where
        the AWG was on and the sensors have had time to settle.
        """
        buffer = self.config["Analysis"]["samples_to_remove_at_end"]
        if len(self.awg_on_ray) == 0:
            return []

        if len(self.awg_on_ray) == 1:
            if not self.awg_on_ray[0]:
                return [(0, 1)]
            else:
                return []

        start_indices = []
        stop_indices = []

        for i in range(1, len(self.awg_on_ray)):
            if i == 1 and not self.awg_on_ray[i - 1] and not self.awg_on_ray[i]:
                start_indices.append(self.add_delay_to_index(i, self.config["Analysis"]["settling_time_s"]))
            elif self.awg_on_ray[i - 1] and not self.awg_on_ray[i]:
                start_indices.append(self.add_delay_to_index(i, self.config["Analysis"]["settling_time_s"]))
            elif not self.awg_on_ray[i - 1] and self.awg_on_ray[i]:
                stop_indices.append(i - buffer)

            if i == len(self.awg_on_ray) - 1 and not self.awg_on_ray[i]:
                stop_indices.append(i+1 - buffer)

        # Remove the first interval since it is not considered an off interval
        try:
            start_indices.pop(0)
            stop_indices.pop(0)
        except IndexError:
            pass

        assert len(start_indices) <= len(stop_indices)

        output = []
        for i in range(len(start_indices)):
            output.append((start_indices[i], stop_indices[i]))

        return output

    def add_delay_to_index(self, index: int, delay: float) -> int:
        """Returns the index where the corresponding time is closest to the time of the original index plus a
        given delay"""
        assert index < len(self.awg_on_ray)
        assert len(self.times_s) >= len(self.awg_on_ray)

        target_time = self.times_s[index] + delay

        smallest_time_deviation = abs(delay)
        closest_index = index

        for i in range(0, len(self.times_s)):
            time_deviation = abs(self.times_s[i] - target_time)
            if time_deviation < smallest_time_deviation:
                closest_index = i
                smallest_time_deviation = time_deviation

        return closest_index

    # TODO: UPDATE THE TEST RESULTS SUMMARY IN MANAGER WITH THIS
    def get_pass_result(self) -> Tuple[str, str]:
        if self.forward_power_max_extrapolated > self.Pf_max:
            return "FAIL", f"Extrapolated forward power exceeds {self.Pf_max}W"

        if self.reflected_power_percent > self.ref_limit:
            return "FAIL", f"Reflected power exceeds {self.ref_limit} percent"

        return "Pass", ""

    def get_result_log_entry(self):
        test_result, _ = self.get_pass_result()
        return ['', "Pass/Fail test",
                f"Element_{self.element};Pf (W)={self.forward_power_on_mean};Pr (W)="
                f"{self.reflected_power_on_mean};Pa (W)={self.acoustic_power_on_mean};Efficiency (%)"
                f"={self.efficiency_percent};RF_Reflection (%)={self.reflected_power_percent};"
                f"Pf Max (W)={self.forward_power_max_extrapolated};WaterTemp (C)={self.water_temperature_c};"
                f"Test result={test_result};Pf Max limit (W)={self.Pf_max}",
                '']

    def data_is_valid(self) -> Tuple[bool, str]:
        """Returns whether the data contains missing values or the uncertainty is too high, along with a feedback
        message"""

        if None in self.balance_readings_g:
            return False, "Invalid test due to missing RFB data"

        if None in self.r_meter_readings_w:
            return False, "Invalid test due to missing reflected power data"

        if None in self.f_meter_readings_w:
            return False, "Invalid test due to missing forward power data"

        if self.std_too_high:
            return False, f"Invalid test due to a possible disturbance. The standard deviation within an interval " \
                          f"was greater than {self.config['Analysis']['max_standard_deviation_w']} Watts"

        return True, ""

    def analyze_intervals(self, data: List[float], intervals: List[Tuple[int, int]]) \
            -> Tuple[List[float], float, float, bool]:
        """
        Takes a  list of integer pairs, each represents an interval of data to return, including the first index and
        not including the last. For example if the interval is (0,3)  this method will analyze indices 0,1,
        and 2 for the first interval and so on for the remaining intervals.

        Returns: A list containing the average of the data in each interval, the average random uncertainty within
        all intervals, the average total uncertainty in all intervals, and a boolean indicating if any interval's
        uncertainty exceeds the threshold in the yaml file
        """

        if len(data) == 0 or len(intervals) == 0 or len(intervals[0]) == 0:
            return [], float('nan'), float('nan'), False

        averages = []
        random_uncertainties = []
        total_uncertainties = []
        standard_deviations = []

        for i in range(len(intervals)):
            data_in_interval = []
            try:
                for j in range(intervals[i][0], intervals[i][1]):
                    data_in_interval.append(data[j])
            except TypeError:
                raise Exception

            if len(data_in_interval) > 0:
                averages.append(mean(data_in_interval))
            else:
                averages.append(float('nan'))
            random_uncertainties.append(calculate_random_uncertainty_percent(data_in_interval))
            total_uncertainties.append(calculate_total_uncertainty_percent(data_in_interval))
            standard_deviations.append(calculate_standard_deviation(data_in_interval))

        if len(random_uncertainties) > 0:
            random_uncertainty = mean(random_uncertainties)
        else:
            random_uncertainty = float('nan')

        if len(total_uncertainties) > 0:
            total_uncertainty = mean(total_uncertainties)
        else:
            total_uncertainty = float('nan')

        std_too_high = False

        for standard_deviation in standard_deviations:
            if standard_deviation > self.config["Analysis"]["max_standard_deviation_w"]:
                std_too_high = True
                break

        return averages, random_uncertainty, total_uncertainty, std_too_high,

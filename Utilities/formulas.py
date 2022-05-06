def calculate_power_from_balance_reading(
        balance_reading_g: float, Temperature_c: float = 20
):
    balance_reading_kg = balance_reading_g / 1000
    g_m_per_s_per_s = 9.80665  # Source: [1] in the documentation

    force_N = balance_reading_kg * g_m_per_s_per_s
    c_water = calculate_speed_of_sound_in_water(Temperature_c)
    acoustic_power_w = force_N * c_water
    return acoustic_power_w


def calculate_speed_of_sound_in_water(temperature_c: float):
    from numpy import poly1d, polyfit

    temp_c_scatter = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, ]  # Source: [2] in documentation
    c_water_m_per_s_scatter = [1403, 1427, 1447, 1481, 1507, 1526, 1541, 1552, 1555, 1555, 1550, 1543, ]

    polyfit = poly1d(polyfit(temp_c_scatter, c_water_m_per_s_scatter, 4))

    return polyfit(temperature_c)


# returns the random uncertainty of a data set as a percentage
# Todo: double check this formula
def calculate_total_uncertainty_percent(data_set: list):
    return calculate_random_uncertainty_percent(data_set) * 2


# returns the random uncertainty of a data set as a percentage
# Todo: double check this formula
def calculate_random_uncertainty_percent(data_set: list):
    if len(data_set) == 0:
        return float("nan")
    from numpy import mean, std

    mean = mean(data_set)
    if mean == 0:
        return float("nan")
    return max(data_set) - min(data_set) / mean * 100


# Test script
if __name__ == "__main__":
    print(calculate_power_from_balance_reading(0.053))
    print(calculate_speed_of_sound_in_water(20))

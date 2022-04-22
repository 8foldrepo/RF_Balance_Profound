#placeholder formula
#todo: fill in with  the correct formula
def calculate_power_from_balance_reading(balance_reading_g:float):
    acoustic_power_w = balance_reading_g #placeholder, not correct
    return acoustic_power_w * 17

#returns the random uncertainty of a data set as a percentage
#Todo: double check this formula
def calculate_total_unceratainty_percent(data_set: list):
    if len(data_set) == 0:
        return float('nan')
    from numpy import mean, std
    mean = mean(data_set)
    if mean == 0:
        return float('nan')
    return std(data_set)/mean*100

#returns the random uncertainty of a data set as a percentage
#Todo: double check this formula
def calculate_random_unceratainty_percent(data_set: list):
    if len(data_set) == 0:
        return float('nan')
    from numpy import mean, std
    mean = mean(data_set)
    if mean == 0:
        return float('nan')
    return std(data_set)/mean * 100
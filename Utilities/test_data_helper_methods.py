from typing import List
from data_structures.test_data import TestData


def create_test_results_summary_file(test_data: TestData, path):
    """Saves the dictionary containing test info to a specified path, formatted as a results summary"""
    f = open(path, "w")

    f.write(test_data.serial_number + "-" + test_data.test_date_time + "\n")
    f.write("Test operator\t" + test_data.operator_name + "\n")
    f.write("Comment\t" + test_data.test_comment + "\n")
    f.write("Software Version\t" + test_data.software_version + "\n")
    f.write("Script\t" + test_data.script_name + "\n")
    if test_data.skip_write_to_ua:
        f.write("UA Write\tN/A\t")
    elif test_data.write_result:
        f.write("UA Write\tOK\n")
    else:
        f.write("UA Write\tFAIL\n")
    f.write("UA hardware code\t" + test_data.hardware_code + "\n")
    f.write("\n")  # empty line
    f.write(
        "\tX\tTheta\tLF (MHz)\tLF.VSI (V^2s)\tHF (MHz)\tHF.VSI (V^2s)\tLF.Eff (%)\tLF.Rfl (%)\tLF.Pf(max) (W)\t"
        "LF.WTemp (degC)\tHF.Eff (%)\tHF.Rfl (%)\tHF.Pf(max) (W)\tHF.WTemp (degC)\tElement result\t"
        "Failure description\n"
    )

    element_data_list = test_data.results_summary
    for x in range(len(element_data_list)):
        if 0 <= x <= 10:  # for all the element lines and the UA Common line
            if x == 10:
                f.write("\n")  # there are empty lines around "UA Common" row
            f.write("\t".join(element_data_list[x]))
            f.write("\n")
        if x == 11:  # for the elements with manual LF...
            f.write("\n")
            f.write("Elements with manual LF\t" + ",".join(element_data_list[x]))
            f.write("\n")
        if x == 12:  # for the elements with manual HF...
            f.write("Elements with manual HF\t" + ",".join(element_data_list[x]))
    f.close()


def generate_calibration_data(test_data: TestData) -> List[str]:
    """Create UA calibration data compatible with the UA_Interface_Box class given test_data from the manager class"""
    output = [''] * 27
    output[0] = str(test_data.schema)
    output[1] = str(test_data.serial_number)
    date_str = test_data.test_date_time[0:4] + test_data.test_date_time[5:7] + test_data.test_date_time[8:10]
    output[2] = date_str
    output[3] = str(test_data.hardware_code)
    output[4] = str(test_data.low_frequency_MHz)
    output[5] = str(test_data.high_frequency_MHz)
    output[6] = str(test_data.results_summary[10][2])  # angle average
    for i in range(10):
        output[i + 7] = test_data.results_summary[i][7]  # LF efficiency percent
    for i in range(10):
        output[i + 17] = test_data.results_summary[i][11]  # LF efficiency percent

    return output

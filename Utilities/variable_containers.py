class TestData:
    def __init__(self):
        from datetime import datetime
        # add formatted date
        now = datetime.now()
        formatted_date = now.strftime("%Y.%m.%d-%H.%M")
        self.test_date_time = formatted_date
        self.software_version = ""
        self.test_comment = ""
        self.serial_number = ""
        self.operator_name = ""
        self.script_name = ""
        self.script_log = list()
        self.low_frequency_MHz = float('nan')
        self.high_frequency_MHz = float('nan')
        self.hardware_code = ""
        self.results_summary = list()
        self.write_result = False
        self.script_name = ''
        self.low_frequency_MHz = float('nan')
        self.high_frequency_MHz = float('nan')
        hf = str(self.low_frequency_MHz)
        lf = str(self.low_frequency_MHz)

        # Create reults_summary table
        table = list([None] * 13)

        # Default values, will be updated during test
        table[0] = ['Element_01', '0', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[1] = ['Element_02', '5', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[2] = ['Element_03', '10', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[3] = ['Element_04', '15', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[4] = ['Element_05', '20', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[5] = ['Element_06', '25', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[6] = ['Element_07', '30', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[7] = ['Element_08', '35', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[8] = ['Element_09', '40', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']
        table[9] = ['Element_10', '45', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                    'NaN',
                    'Pass', '']

        table[10] = ['UA Common', 'NaN', '-90', lf, 'NaN', hf, 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN', 'NaN',
                     'NaN', 'Pass', '']

        elements_with_manual_lf = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
        elements_with_manual_hf = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']

        # Todo: add ability to set manual frequencies per element
        table[11] = elements_with_manual_lf
        table[12] = elements_with_manual_hf

        self.results_summary = table


class FileMetadata:
    element_number: int
    X: float
    Theta: float
    frequency_MHz: float
    amplitude_mVpp: float
    source_signal_type: str
    num_cycles: int
    axis: str
    waveform_number: int

from Utilities.useful_methods import log_msg, check_directory, create_test_results_summary_file
from definitions import  ROOT_DIR
from Utilities.load_config import ROOT_LOGGER_NAME, LOGGER_FORMAT, load_configuration
import logging
import shutil
import os

log_formatter = logging.Formatter(LOGGER_FORMAT)
wtf_logger = logging.getLogger('wtf_log')
file_handler = logging.FileHandler(os.path.join(ROOT_DIR, "./logs/wtf.log"), mode='w')
file_handler.setFormatter(log_formatter)
wtf_logger.addHandler(file_handler)
wtf_logger.setLevel(logging.INFO)
root_logger = logging.getLogger(ROOT_LOGGER_NAME)
log_formatter = logging.Formatter(LOGGER_FORMAT)

class OutputDirectory:
    folder_name = None
    results_dir = None
    log_files_dir = None
    power_data_path = None
    waveform_data_path = None

    def __init__(self, test_data, config):
        if config is not None:
            self.config = config
        else:
            self.config = load_configuration()

        self.test_data = test_data
        self.create_results_folder()
        self.create_subfolders()
        self.copy_system_info()

    def create_results_folder(self):
        self.folder_name = self.test_data["serial_number"] + "-" + self.test_data["test_date_time"]
        results_path = os.path.join(self.config['Paths']['UA results root directory'], self.folder_name)
        #Retrieve the path of the results directory from the yaml file and create it if it does not exist
        self.results_dir = check_directory(results_path)


    def create_subfolders(self):
        log_files_path = os.path.join(self.results_dir,'Log files')
        self.log_files_dir = check_directory(log_files_path)

        power_data_path = os.path.join(self.results_dir, 'Power data')
        self.power_data_path = check_directory(power_data_path)

        waveform_data_path = os.path.join(self.results_dir, 'Waveform data')
        self.waveform_data_path = check_directory(waveform_data_path)


    '''Copies the system info file into the results directory'''
    def copy_system_info(self):
        system_info_file = os.path.join(ROOT_DIR,'systeminfo.ini')
        if not os.path.exists(system_info_file):
            self.log(level='Error', message='Could not store system info to results folder')
            self.log(level='Error', message=f'systeminfo.ini was not found in {ROOT_DIR}')
            return

        destination_path = os.path.join(self.log_files_dir,'SystemHardware.log')
        shutil.copyfile(src=system_info_file,dst=destination_path)

    '''Save the test data (shared with the manager) to the results folder in the form of a  results summary'''
    def save_test_results_summary_and_log(self, test_data):
        if not test_data:  # if dictionary is empty return
            self.log(level='error',message='No results to save')
            return

        self.test_data = test_data

        path = os.path.join(self.results_dir,"Results Summary.txt")

        self.log(f"Saving results summary to: {path}")

        create_test_results_summary_file(self.test_data, path)

        self.save_log_file(self.test_data['script_log'])

    # turn a 2d list into a .log file (a text file with a different extension
    '''saves the 2d list called log_table to a .log file. defaults to self.test_data if none is provided'''

    def save_log_file(self, log_table=None):
        if log_table is None:
            log_table = self.test_data["script_log"]

        try:
            path = os.path.join(self.log_files_dir, "ScriptResults.log")
        except TypeError:
            self.log("config has not been loaded and therefore the log path cannot be pulled from there, defaulting log path")
            path = "../logs2/ScriptResults.log"

        self.log(f"Saving results summary to: {path}")

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        f = open(path, 'w')
        for x in range(len(log_table)):
            f.write('\t'.join(log_table[x]))
            f.write('\n')

    #todo
    def save_frequency_sweep(self):
        pass

    # todo
    def save_find_element_waveform(self):
        pass

    # todo
    def save_find_element_profile(self):
        pass

    # todo
    def save_rfb_traces(self):
        pass

    def log(self, message, level='info'):
        log_msg(self, root_logger, message=message, level=level)

if __name__ == '__main__':
    test_data = dict()
    test_data['serial_number'] = 'GH1214'
    test_data['test_date_time'] = '2020.10.01-15.47'
    results_saver = OutputDirectory(test_data=test_data)
    results_saver.save_test_results_summary_and_log()
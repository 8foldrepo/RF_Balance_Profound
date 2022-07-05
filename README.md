# Wet Test Fixture Python Edition

Application for operation of the wet test fixture using python

(intended to recreate the functionality of existing labview code)

## SETUP INSTRUCTIONS

### Setup script
1. Double click the provided setup.bat file in the root of the repository and folllow the prompts. Reboot your computer afterwards. 
If a desktop shortcut is created and launches the application, skip ahead to hardware setup notes. 
If not, follow the pycharm setup instructions to invesigate what dependancies if any failed to install and install them using the commands in the conda environment setup section.

### SOFTWARE INSTALLATION

1. Clone the github repository at https://github.com/Isaiah7579/RF_Balance_Profound
   (email Isaiah@8foldmfg.com if permissions are required)

The default path is C:\Users\<username>\Documents\GitHub\RF_Balance_Profound

2. Install the following applications:

Anaconda navigator (environment setup)
https://www.anaconda.com/products/individual
*Make sure to add anaconda to the PATH environment variable during setup

Pycharm (python ide)
https://www.jetbrains.com/pycharm/download/

NI Visa (signal generator programming dependancy)
https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#346210

VNC Server (remote support)
https://www.realvnc.com/en/connect/download/vnc/

NI-DAQmx base (NI digital io board programming dependancy)
https://www.ni.com/en-us/support/downloads/drivers/download.ni-daqmx-base.html#326059
(Note: the autoextractor will extract it to C:\National Instruments Downloads\NI-DAQmx Base\15.0. From here,
run setup.exe)

3. Install the power meter dll file

the dll file is located in /Hardware/power_meter_dlls

copy and paste it to C:/Windows/SysWOW64 (assuming a 64 bit windows install)

### CONDA ENVIRONMENT SETUP

Method 1: creating environment manually

create a new conda envirionment with python 3.8

In the anaconda command prompt make sure the environment is activated

ex: conda activate RF_Balance_Profound

run the following commands

> pip install pythonnet\
> pip install pyqtgraph\
> pip install pyqt5\
> pip install pyvisa\
> pip install pyyaml\
> pip install scipy\
> pip install termcolor\
> pip install pyserial\
> python -m pip install nidaqmx


Method 2: Create automatically from environment.yml

launch cmd.exe from anaconda navigator.

run the following commands:
> cd %USERPROFILE%\documents\github\RF_Balance_Profound \
> conda env create -f environment.yml \
> conda activate RF_Balance_Profound \
> setup.bat \
> conda list

The output should resemble this:

> packages in environment at C:\Users\8Fold\Anaconda3\envs\Scantry_Ultra:  \
> \
> Name Version Build Channel \
> ca-certificates 2021.10.26 haa95532_2 \
> certifi 2021.10.8 py38haa95532_0 \
> console_shortcut 0.1.1 4 \
> cycler 0.11.0 pypi_0 pypi \
> fonttools 4.28.2 pypi_0 pypi \
> gclib 1.0 pypi_0 pypi \
> h5py 3.6.0 pypi_0 pypi \
> kiwisolver 1.3.2 pypi_0 pypi \
> matplotlib 3.5.0 pypi_0 pypi \
> numpy 1.21.4 pypi_0 pypi \
> openssl 1.1.1l h2bbff1b_0 \
> packaging 21.3 pypi_0 pypi \
> picosdk 1.0 pypi_0 pypi \
> pillow 8.4.0 pypi_0 pypi \
> pip 21.2.2 py38haa95532_0 \
> pyparsing 3.0.6 pypi_0 pypi \
> pyqt5 5.15.6 pypi_0 pypi \
> pyqt5-qt5 5.15.2 pypi_0 pypi \
> pyqt5-sip 12.9.0 pypi_0 pypi \
> pyqtgraph 0.12.3 pypi_0 pypi \
> python 3.8.12 h6244533_0 \
> python-dateutil 2.8.2 pypi_0 pypi \
> pyvisa 1.11.3 pypi_0 pypi \
> pyyaml 6.0 pypi_0 pypi \
> setuptools 58.0.4 py38haa95532_0 \
> setuptools-scm 6.3.2 pypi_0 pypi \
> six 1.16.0 pypi_0 pypi \
> sqlite 3.36.0 h2bbff1b_0 \
> tomli 1.2.2 pypi_0 pypi \
> typing-extensions 4.0.1 pypi_0 pypi
> vc 14.2 h21ff451_1 \
> vs2015_runtime 14.27.29016 h5e58377_2 \
> wheel 0.37.0 pyhd3eb1b0_1 \
> wincertstore 0.2 py38haa95532_2

### PYCHARM SETUP (optional)

1. Launch pycharm

2. Click "New Project", and set the location to the github repository folder (C:\Users\<username>
   \Documents\GitHub\Scantry_Ultra)

3. Select "Previously configured interpreter" > ... > Conda Environment

4. Set interpreter to C:\Users\<username>\Anaconda3\envs\Scantry_Ultra\python.exe

5. Set Conda executable to C:\Users\<username>\Anaconda3\Scripts\conda.exe

6. Click OK>Create>Create from Existing Sources

7. When the progress bar at the bottom completes, right click main.py and click "run 'main'". The application should
   launch.

### CREATE APPLICATION SHORTCUT

1. Navigate to the github repository in file explorer
2. Right click run.bat
3. Click send to>desktop (create shortcut)
4. Rename the shortcut to Scantry Ultra
5. (optional) Right click it, click properties > shortcut > change icon > and select logo.png

### Hardware setup notes:

Use NI Max to look at connected devices.

1. There should be 3 com ports (the motor controller, the RF switcher power relay, and the balance).
2. The thermocouple shows up as NI-TC01 (rename it to TankTemp in NI-MAX, confirm local.yaml matches)
3. The digital IO board (located in the power module box) shows up as NI-USB 6501. Rename it to WTF4 (or whatever name
   you choose), confirm its name in local.yaml matches.
4. The waveform generator should show up as a VISA identifier containing the model code 0x2507 ex: USB0::0x0957::
   0x2507::MY59001263::INSTR
5. The oscilloscope should show up as a VISA identifier containing the model code 0x179B ex: USB0::0x0957::0x2507::
   MY59001263::INSTR
6. Finally, to configure the UA interface box, go to Network and Sharing center in control panel, look for an unknown
   network corresponding to the network adapter the UA iterface box is plugged into. Click on the ethernet number link
   next to it (EX: ethernet 3), go to properties, uncheck all except ipv4, click on ipv4, click on properties, click
   "Use a specific address", type 192.168.3.1, and use the default subnet mask: 255.255.255.0. To confirm the device is
   connected, go to command prompt and type ping 192.168.3.3. All 4 bytes should be received. Note that the ip address
   of the device in the code differs from the ip address in control panel. I am not sure why this works, but it does.

### Tools for troubleshooting/testing hardware

1. "Test panels" in NI MAX: control the digital IO board and thermocouple with a GUI

2. NI-VISA interactive control suite: Terminal to send commands to Oscilloscope and function generator

3. Wet test fixture EXE file (located in hardware/interface box executable). Use it with the command line, refer to the
   email in the same folder for syntax

4. Test com devices, including the balance, motor controller, and RF switcher on/off relay, using arduino serial
   monitor (works for more than just arduinos)
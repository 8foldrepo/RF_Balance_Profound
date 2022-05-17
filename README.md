# Wet Test Fixture Python Edition

Application for operation of the wet test fixture using python

(intended to recreate the functionality of existing labview code)

## SETUP INSTRUCTIONS

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

### PYCHARM SETUP

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

## USAGE INSTRUCTIONS

0. Make sure signal chain is connected properly, hardware is turned on, UA is free of bubbles, and limit switches are in
   place to prevent hardware damage.
1. Ensure desired settings are selected in the configuration file called default.yaml
2. Ensure desired awg settings are entered into Rigol settings.csv (only if multiple waveform generators are being used)
3. Run main.py
4. Click list connected devices in the output manager
5. Select the AWG you wish to use (make sure it is turned on and plugged in via USB)
6. Click open selected devices
7. Click the dropdown and click the name of the AWG to open its widget.
8. Enter desired AWG settings (make sure trigger out is turned on and the output is turned on)
9. Click on signal inputs, enter oscilloscope settings, and toggle capture on
10. Click on the toggle switch in the Gantry widget to activate the gantry. Set the jog speed to 5.
11. Use X forwards/X backwards buttons to position hydrophone 6.7mm away from the UA. Adjust limit switches if needed.
    Click "set home".
12. Use Y left/ Y right buttons to visually center the hydrophone to the UA. Click "set home"
13. Use the Z up/ Z down buttons to find the location of highest amplitude of the element you wish to scan. Click "set
    home".
14. Click "Launch scan widget" under "cartesian". Enter the frequency being used.
15. Click the checkboxes of the Y and Z axes. Default settings of -3mm to 3mm in 0.5mm steps are good for a preliminary
    scan.
16. Click start. Title the scan test_yz_1 or similar, ensuring it is a unique filename.
17. Click "Image view" and Wait for the scan to complete. If all went according to plan you should see a bright spot in
    the center of the scan.
18. If the spot is not perfectly centered, click on it using the middle mouse button. When prompted if you would like to
    set the origin, click "ok".
19. Click "go home".
20. The scan should now be aligned. If it is not, Repeat from step 11 until it is. Do more test scans with different
    settings if needed.
21. Perform scans with desired dimensions and settings using the cartesian scan widget.
22. By default, scans will be stored in <your_username>/documents/scantry , in a subfolder called "transverse scans", "
    longitudinal scans", or "other scans".

### Data analysis using existing matlab scripts

1. Launch matlab
2. Create a project within the folder __Matlab analysis code
3. Run startup.m (it should run itself when you start matlab in the future)
4. Run a file in the folder "runners". For example run "Display_scan.m" to display a scan.
5. Click on the .hdf5 file containing the desired scan data.
6. Enter the sensitivity of the hydrophone in mV/MPa.
7. Enter 1 if a 50 ohm load was used in paralell to the oscilloscope. Enter 2 otherwise.
8. You should see a visualization of the scan (and other data depending on what file you ran)

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
@echo off
@setlocal enabledelayedexpansion
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

ECHO [92mWelcome to the RF_Balance_Profound setup script for Users![0m

:: Install dependancies :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

SET /P AREYOUSURE="Do you want to download and install NI-VISA drivers (Y/[N]): "
IF /I "!AREYOUSURE!" == "Y" (
	IF EXIST C:\Users\%username%\Downloads\ni-visa_20.0_online_repack3.exe (
		ECHO [92mNI-VISA downloader already exists, skipping download step[0m
	) ELSE (
		CD C:\Users\%username%\Downloads
		curl -LO https://download.ni.com/support/nipkg/products/ni-v/ni-visa/20.0/online/ni-visa_20.0_online_repack3.exe
	)
	ECHO [92mcheck "NI-VISA interactive control" and uncheck everything else. Close the window when done. Do not reboot yet. [0m
	C:\Users\%username%\Downloads\ni-visa_20.0_online_repack3.exe
	CD ..
)

IF EXIST "C:\Windows\System32\nicaiu.dll" (
	SET /P AREYOUSURE="NIDAQ setup exists, re-install? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		CD C:\Users\%username%\Downloads
		ECHO [92mNI-DAQ setup doesn't exist, downloading and launching setup[0m
		IF EXIST "C:\Users\%username%\Downloads\ni-daqmx_21.8_online.exe" (
			ECHO [92mNIDAQ installer already exists, skipping download step[0m 
		) ELSE (
			curl -LO https://download.ni.com/support/nipkg/products/ni-d/ni-daqmx/21.8/online/ni-daqmx_21.8_online.exe
		)
	
		ECHO [92mGo through installer, unselect all packages. Close the window when done. Do not reboot yet. [0m
		C:\Users\%username%\Downloads\ni-daqmx_21.8_online.exe
	)
) ELSE (
	CD C:\Users\%username%\Downloads
	ECHO [92mNI-DAQ setup doesn't exist, downloading and launching setup[0m
	IF EXIST "C:\Users\%username%\Downloads\ni-daqmx_21.8_online.exe" (
		ECHO [92mNIDAQ installer already exists, skipping download step[0m 
	) ELSE (
		curl -LO https://download.ni.com/support/nipkg/products/ni-d/ni-daqmx/21.8/online/ni-daqmx_21.8_online.exe
	)
	
	ECHO [92mGo through installer, unselect all packages. Close the application afterwards, do not reboot yet. [0m
	C:\Users\%username%\Downloads\ni-daqmx_21.8_online.exe
)

IF EXIST "C:\Program Files (x86)\Galil\gclib\source\wrappers\python\gclib.py" (
	SET /P AREYOUSURE="gclib GDK already installed on computer, re-install? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		GOTO :InstallGDK
	) ELSE (
		GOTO :ENDGDK
	)
) ELSE (
	SET /P AREYOUSURE="gclib not found on computer, install gclib? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		:InstallGDK
		IF EXIST C:\Users\%username%\Downloads\galil_gclib_1_34_15.exe (
			ECHO [92mSetup already downloaded, skipping download phase[0m
		) ELSE (
			CD C:\Users\%username%\Downloads\
			curl -LO https://www.galil.com/sw/pub/win/gclib/galil_gclib_1_34_15.exe
		)
		ECHO [92mmake sure to install PCI driver and 32-bit binaries during setup. Close the application afterwards, do not reboot yet.[0m
		C:\Users\%username%\Downloads\galil_gclib_1_34_15.exe
	)
)
:ENDGDK

SET /P AREYOUSURE="Install NI system config and NI max? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		CD C:\Users\%username%\Downloads
		curl -LO https://download.ni.com/support/nipkg/products/ni-s/ni-system-configuration/21.5/online/ni-system-configuration_21.5_online.exe
		ECHO [92mClick through installer. Check only NI automation and measurement explorer. When installation is complete, reboot and launch the RF Balance Profound Executable. [0m
		C:\Users\%username%\Downloads\ni-system-configuration_21.5_online.exe
	)


ECHO Setup complete, Make Sure to Reboot, then right click the exe and click send-to > desktop to create a desktop shortcut. Double click the EXE or its shortcut to run.

:end
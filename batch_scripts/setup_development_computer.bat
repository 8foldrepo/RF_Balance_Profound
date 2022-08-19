@echo off
@setlocal enabledelayedexpansion
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

ECHO [92mWelcome to the RF_Balance_Profound setup script for developers![0m
ECHO [92mBefore continuing, obtain permission to access the repository from the developers (isaiah@8foldmfg.com)[0m


mkdir C:\Users\%username%\Documents\GitHub
mkdir C:\Users\%username%\Documents\GitHub\Dependency_Downloads

:: Ensure repository exists :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
SET /P AREYOUSURE="Is repository already downloaded? (y/[n]): "
IF /I "!AREYOUSURE!" == "y" (
    GOTO repoexists
)

ECHO Setting up github repository
:checkghdt
:: Check for GitHub Desktop
IF EXIST "C:\Users\%username%\AppData\Local\GitHubDesktop\GitHubDesktop.exe" (
	ECHO Sign into Github Desktop, and, click "clone a repository from the internet" and clone the repository RF_Balance_Profound to the default location
	ECHO The default location should be C:\Users\%username%\Documents\GitHub\RF_Balance_Profound
	ECHO Remember to pull from the main brach for updates
	"C:\Users\%username%\AppData\Local\GitHubDesktop\GitHubDesktop.exe"
) ELSE (
	mkdir C:\Users\%username%\Documents\GitHub\Dependency_Downloads
	CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads\
	IF EXIST GitHubDesktopSetup-x64.exe (
		ECHO Github Desktop installer found, skipping download
	) ELSE (
		ECHO downloading installer
		ECHO Downloading Gitub Desktop Installer
		curl -o GitHubDesktopSetup-x64.exe -LO https://central.github.com/deployments/desktop/desktop/latest/win32
      )
	ECHO click through the installer with default settings
	GitHubDesktopSetup-x64.exe
      IF EXIST "C:\Users\%username%\AppData\Local\GitHubDesktop\GitHubDesktop.exe" (
		ECHO Sign into Github Desktop, and, click "clone a repository from the internet" and clone the repository RF_Balance_Profound to the default location
		ECHO (The default location should be C:\Users\%username%\Documents\GitHub\RF_Balance_Profound)
		ECHO Remember to pull from the main brach routinely for updates
		"C:\Users\%username%\AppData\Local\GitHubDesktop\GitHubDesktop.exe"
	)
)

SET /P AREYOUSURE="Enter y if the repository has finished downloading (y/[n]): "
IF /I "!AREYOUSURE!" == "y" (
    GOTO repoexists
) ELSE (
    ECHO Please rerun the script when it is
    GOTO:end
)

:repoexists

:: Ensure Anaconda is installed :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
IF EXIST "C:\ProgramData\Anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF EXIST "C:\Users\%username%\anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF EXIST "C:\Users\Public\anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF DEFINED CONDAEXISTS (
	SET /P AREYOUSURE="Conda found, do you wish to re-install Conda? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\Anaconda3-2022.05-Windows-x86_64.exe (
			ECHO [92mConda installer already downloaded, skipping download step[0m
		) ELSE (
			cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
			curl -LO https://repo.anaconda.com/archive/Anaconda3-2022.05-Windows-x86_64.exe
		)
		ECHO [92mmuntick set as python 3.9 for system and tick add to PATH if possible[0m
		C:\Users\%username%\Documents\GitHub\Dependency_Downloads\Anaconda3-2022.05-Windows-x86_64.exe
	)
) ELSE (
	ECHO [92mConda not detected in computer, downloading and installing[0m
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\Anaconda3-2022.05-Windows-x86_64.exe (
		ECHO [92mConda installer already downloaded, skipping download step[0m
	) ELSE (
		ECHO [92mConda installer not found, downloading[0m
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://repo.anaconda.com/archive/Anaconda3-2022.05-Windows-x86_64.exe
	)
	ECHO [92muntick set as python 3.9 for system and tick add to PATH if possible[0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\Anaconda3-2022.05-Windows-x86_64.exe
)

:: Install dependancies :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

SET /P AREYOUSURE="Do you want to download and install NI-VISA drivers (Y/[N]): "
IF /I "!AREYOUSURE!" == "Y" (
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-visa_20.0_online_repack3.exe (
		ECHO [92mNI-VISA downloader already exists, skipping download step[0m
	) ELSE (
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://download.ni.com/support/nipkg/products/ni-v/ni-visa/20.0/online/ni-visa_20.0_online_repack3.exe
	)
	ECHO [92mcheck "NI-VISA interactive control" and uncheck everything else. Do not reboot yet. [0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-visa_20.0_online_repack3.exe
	CD ..
)

IF EXIST "C:\Windows\System32\nicaiu.dll" (
	SET /P AREYOUSURE="NIDAQ setup exists, re-install? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		IF EXIST "C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-daqmx_21.8_online.exe" (
			ECHO [92mNI-DAQ installer already exists, skipping download step[0m
		) ELSE (
			CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
			curl -LO https://download.ni.com/support/nipkg/products/ni-d/ni-daqmx/21.8/online/ni-daqmx_21.8_online.exe
		)
		IF EXIST "C:\Program Files\National Instruments\NI Package Manager\NIPackageManager.exe" (
		ECHO [92mGo to "Drivers" tab on left column, select "NI-DAQmx", select "Remove", exit out of reboot prompt, then re-install from same package manager[0m
		ECHO [92mselect all packages EXCEPT for "NI I/O Trace", "NI Linux RT System Image", and "NI Web-Based Configuration and Monitoring when installing[0m
		ECHO [92mPress Ctrl and C keys together to go to next step if stuck[0m
			"C:\Program Files\National Instruments\NI Package Manager\NIPackageManager.exe"
		) ELSE (
			C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-daqmx_21.8_online.exe
		)
	)
) ELSE (
	CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
	ECHO [92mNI-DAQ setup doesn't exist, downloading and launching setup[0m
	IF EXIST "C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-daqmx_21.8_online.exe" (
		ECHO [92mNIDAQ installer already exists, skipping download step[0m 
	) ELSE (
		curl -LO https://download.ni.com/support/nipkg/products/ni-d/ni-daqmx/21.8/online/ni-daqmx_21.8_online.exe
	)
	
	ECHO [92mGo through installer, unselect all packages. Do not reboot yet. [0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-daqmx_21.8_online.exe
)


SET /P AREYOUSURE="Do you want to setup the Conda environment for RF_Balance_Profound? (Y/[N]): "
IF /I "!AREYOUSURE!" == "Y" (
	CD C:\Users\%username%\Documents\GitHub\RF_Balance_Profound
	SET PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
	SET PATH=!PATH!;"C:\ProgramData\Anaconda3\condabin\"
    SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\condabin\"
	SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\Scripts\"
	call conda.bat update conda
	call conda.bat env create -f C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\environment.yml -v -v -v
)

IF EXIST "C:\Program Files (x86)\Galil\gclib\source\wrappers\python\gclib.py" (
	SET /P AREYOUSURE="gclib GDK already installed on computer, re-install? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		GOTO :InstallGDK
	) ELSE (
		GOTO :ENDGDK
	)
)
SET /P AREYOUSURE="gclib GDK not found on computer, install gclib? (Y/[N]): "
IF /I "!AREYOUSURE!" == "Y" (
	:InstallGDK
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\galil_gclib_1_34_15.exe (
		ECHO [92mSetup already downloaded, skipping download phase[0m
	) ELSE (
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads\
		curl -LO https://www.galil.com/sw/pub/win/gclib/galil_gclib_1_34_15.exe
	)
	ECHO [92mmake sure to install PCI driver and 32-bit binaries during setup[0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\galil_gclib_1_34_15.exe
)
:ENDGDK

SET /P AREYOUSURE="Add gclib to RF_Balance_Profound environment? (Y/[N]): "
IF /I "!AREYOUSURE!" == "Y" (
	CALL conda.bat activate RF_Balance_Profound
	ECHO [92msetting up gclib python wrapper[0m
	CD %temp%
	mkdir py
	CD py
	copy "c:\Program Files (x86)\Galil\gclib\source\wrappers\python"
	copy "c:\Program Files (x86)\Galil\gclib\examples\python"
	python setup.py install
	copy gclib.py  C:\ProgramData\Anaconda3\envs\RF_Balanace_Profound\Lib\site-packages
)

SET /P AREYOUSURE="Install power meter DLL (to Windows\SysWOW64)? (Y/[N]): "
IF /I "!AREYOUSURE!" == "Y" (
	copy C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\Hardware\power_meter_dlls\mcl_pm_NET45.dll C:\Windows\SysWOW64
)

SET /P AREYOUSURE="Install pycharm community (Optional, for code development)? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://download.jetbrains.com/python/pycharm-community-2022.1.3.exe
		ECHO [92mClick through installer. Once installed, create a new project from existing sources in the repository folder.[0m
		C:\Users\%username%\Documents\GitHub\Dependency_Downloads\pycharm-community-2022.1.3.exe
	)

SET /P AREYOUSURE="Install NI system config and NI max? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://download.ni.com/support/nipkg/products/ni-s/ni-system-configuration/21.5/online/ni-system-configuration_21.5_online.exe
		ECHO [92mClick through installer. Check only NI automation and measurement explorer. [0m
		C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-system-configuration_21.5_online.exe
	)

IF EXIST "%userprofile%\Documents\GitHub\RF_Balance_Profound\local.yaml" (
	echo "local.yaml exists, contiuing"
) ELSE (
	cd /d %userprofile%\Documents\GitHub\RF_Balance_Profound\
	fsutil file createnew local.yaml 0
)

ECHO Setup complete, run the application like so with the following commands:
ECHO You can also create a shortcut to the program by right clicking click_to_run.bat in the repository folder and clicking send to> desktop (create shortcut).
@echo on
cd C:\Users\%username%\Documents\GitHub\RF_Balance_Profound
click_to_run.bat
:end
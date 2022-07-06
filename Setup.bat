@echo off
@setlocal enabledelayedexpansion

:: BatchGotAdmin
:-------------------------------------
REM  --> Check for permissions
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------  

mkdir C:\Users\%username%\Documents\GitHub
mkdir C:\Users\%username%\Documents\GitHub\Dependency_Downloads

SET /P AREYOUSURE="Install portable git for windows? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		mkdir "C:\Program Files\PortableGit\bin\"
		IF EXIST "C:\Program Files\PortableGit\bin\git.exe" (
			echo [92mGit for windows is already installed[0m
		) ELSE (
			cd C:\Program Files
			curl -LO https://github.com/git-for-windows/git/releases/download/v2.37.0.windows.1/PortableGit-2.37.0-64-bit.7z.exe
			echo [92mClick ok, do not change the unzip path"[0m
			PortableGit-2.37.0-64-bit.7z.exe
		)
	)

set PATH=!PATH!;"C:\Program Files\PortableGit\bin"

IF EXIST "C:\Program Files\GitHub CLI\gh.exe" (
	SET AREYOUSURE=N
	:PROMPT
	SET /P AREYOUSURE="You already have gh CLI installed, install again? (Y/N): "
	IF /I "!AREYOUSURE!" NEQ "Y" (GOTO END) ELSE (winget install --id GitHub.cli)
) ELSE (
	echo [92mgh CLI does not exist[0m
	IF EXIST C:\Users\%username%\AppData\Local\Microsoft\WindowsApps\winget.exe (
	winget install --id GitHub.cli
	) ELSE (
	cd Dependency_Downloads
	curl -LO https://github.com/cli/cli/releases/download/v2.13.0/gh_2.13.0_windows_amd64.msi
	gh_2.13.0_windows_amd64.msi
	cd ..
	)
)
:END

set PATH=!PATH!;"C:\Program Files\GitHub CLI\"

SET /P AREYOUSURE="Install github desktop interface? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://central.github.com/deployments/desktop/desktop/latest/win32
		echo [92mClick through installer. Once installed, click add repository on disk, then navigate to C:\Users\%username%\Documents\GitHub. Add an exception if prompted[0m
		GitHubDesktopSetup-x64.exe
	)


IF EXIST "C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\main.py" (
	SET AREYOUSURE=N
	SET /P AREYOUSURE="repo already exists, download again? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		echo [92mSelect manager-core if prompted for a credential helper[0m
		gh auth login
		cd C:\Users\%username%\Documents\GitHub
		gh repo clone 8foldrepo/RF_Balance_Profound
	)
) ELSE (
	echo [92mrepo not found, cloning [0m
	echo [92mSelect manager-core if prompted for a credential helper [0m
	gh auth login
	cd C:\Users\%username%\Documents\GitHub
	gh repo clone 8foldrepo/RF_Balance_Profound
)

IF EXIST "C:\ProgramData\Anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF EXIST "C:\Users\%username%\anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF EXIST "C:\Users\Public\anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF DEFINED CONDAEXISTS (
	echo [92mConda found[0m
	SET /P AREYOUSURE="Do you wish to re-install Conda? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\Anaconda3-2022.05-Windows-x86_64.exe (
			ECHO [92mConda installer already downloaded, skipping download step[0m
		) ELSE (
			cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
			curl -LO https://repo.anaconda.com/archive/Anaconda3-2022.05-Windows-x86_64.exe
		)
		ECHO [93muntick set as python 3.9 for system and tick add to PATH if possible[0m
		C:\Users\%username%\Documents\GitHub\Dependency_Downloads\Anaconda3-2022.05-Windows-x86_64.exe
	)
) ELSE (
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\Anaconda3-2022.05-Windows-x86_64.exe (
		ECHO [92mConda installer already downloaded, skipping download step[0m
	) ELSE (
		cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://repo.anaconda.com/archive/Anaconda3-2022.05-Windows-x86_64.exe
	)
	ECHO [93muntick set as python 3.9 for system and tick add to PATH if possible[0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\Anaconda3-2022.05-Windows-x86_64.exe
)

IF EXIST C:\Users\%username%\AppData\Local\Programs\Python\Python38\python.exe (
	ECHO [92mpython found[0m
	SET /P AREYOUSURE="Do you wish to re-install Python? (Y/[N])"
	IF /I "!AREYOUSURE!" == "Y" (
		IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\python-3.8.10-amd64.exe (
			ECHO [92mpython installer found, skipping download step[0m
		) ELSE (
			CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
			curl -LO https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
		)
		ECHO [93mmake sure to tick install to PATH[0m
		C:\Users\%username%\Documents\GitHub\Dependency_Downloads\python-3.8.10-amd64.exe
	)
) ELSE (
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\python-3.8.10-amd64.exe (
		ECHO [92mpython installer found, skipping download step[0m
	) ELSE (
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
	)
	ECHO [93mmake sure to tick install to PATH[0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\python-3.8.10-amd64.exe
)

SET /P AREYOUSURE="Do you want to download and install NI-VISA drivers (Y/N): "
IF /I "!AREYOUSURE!" == "Y" (
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-visa_20.0_online_repack3.exe (
		ECHO [92mNI VISA downloader already exists, skipping download step[0m
	) ELSE (
		cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://download.ni.com/support/nipkg/products/ni-v/ni-visa/20.0/online/ni-visa_20.0_online_repack3.exe
	)
	ECHO [92mcheck "NI VISA interactive control" and uncheck everything else [0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-visa_20.0_online_repack3.exe
	CD ..
)

IF EXIST "C:\Windows\System32\nicaiu.dll" (
	SET /P AREYOUSURE="NIDAQ setup exists, re-install? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		IF EXIST "C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-daqmx_21.8_online.exe" (
			ECHO [92mNI-DAQ installer already exists, skipping download step[0m
		) ELSE (
			cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
			curl -LO https://download.ni.com/support/nipkg/products/ni-d/ni-daqmx/21.8/online/ni-daqmx_21.8_online.exe
		)
		IF EXIST "C:\Program Files\National Instruments\NI Package Manager\NIPackageManager.exe" (
		ECHO [93mGo to "Drivers" tab on left column, select "NI-DAQmx", select "Remove", exit out of reboot prompt, then re-install from same package manager[0m
		ECHO [93mselect all packages EXCEPT for "NI I/O Trace", "NI Linux RT System Image", and "NI Web-Based Configuration and Monitoring when installing[0m
		ECHO [93mPress Ctrl and C keys together to go to next step if stuck[0m
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
	
	ECHO [92m Go through installer, select all packages EXCEPT for "NI I/O Trace", "NI Linux RT System Image", and "NI Web-Based Configuration and Monitoring"[0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-daqmx_21.8_online.exe
)


SET /P AREYOUSURE="Do you want to setup the anaconda environment RF_Balance_Profound? (Y/N): "
IF /I "!AREYOUSURE!" == "Y" (
	CD C:\Users\%username%\Documents\GitHub\RF_Balance_Profound
	SET PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
	conda update conda
	conda env create -f environment.yml -v -v -v
)


SET /P AREYOUSURE="Install gclib? (Y/N): "
IF /I "!AREYOUSURE!" == "Y" (
	CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads\
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\galil_gclib_1_34_15.exe (
		ECHO [92mSetup already downloaded, skipping download phase[0m
	) ELSE (
		curl -LO https://www.galil.com/sw/pub/win/gclib/galil_gclib_1_34_15.exe
	)
	ECHO [93m make sure to install PCI driver and 32-bit binaries during setup[0m
	galil_gclib_1_34_15.exe
)

SET /P AREYOUSURE="Add gclib to RF_Balance_Profound environment? (Y/N): "
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

SET /P AREYOUSURE="Install power meter DLL (to Windows\SysWOW64)? (Y/N): "
IF /I "!AREYOUSURE!" == "Y" (
	copy C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\Hardware\power_meter_dlls\mcl_pm_NET45.dll C:\Windows\SysWOW64
)

SET /P AREYOUSURE="Install pycharm community (Optional, for code development)? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://download.jetbrains.com/python/pycharm-community-2022.1.3.exe
		ECHO [92mClick through installer. Once installed, create a new project from existing sources in the repository folder. [0m
		pycharm-community-2022.1.3.exe
	)

SET /P AREYOUSURE="Install NI system config and NI max? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://download.ni.com/support/nipkg/products/ni-s/ni-system-configuration/21.5/online/ni-system-configuration_21.5_online.exe
		echo [92mClick through installer. Check only NI automation and measurement explorer. [0m
		ni-system-configuration_21.5_online.exe
	)

SET /P AREYOUSURE="Create desktop shortcut? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		CD "C:\Users\%username%\Desktop\"
		copy "C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\RF Balance Profound.lnk"

ECHO [92mRestart your PC and double click the desktop shortcut for the applcation[0m
pause

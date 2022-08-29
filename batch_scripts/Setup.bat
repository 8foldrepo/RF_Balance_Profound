@echo off
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

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

IF EXIST "C:\Program Files\Git\cmd\git.exe" (
	ECHO [92mNon-portable Git for windows is already installed[0m
	SET /P AREYOUSURE="Would you like to install Git as portable edition? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		GOTO :InstallPortGit
	)
) ELSE (
	ECHO [92mPortable Git for Windows not detected[0m
	SET /P AREYOUSURE="Install portable git for windows? (Y/N): "
		IF /I "!AREYOUSURE!" == "Y" (
			:InstallPortGit
			mkdir "C:\Program Files\PortableGit\bin\"
			IF EXIST "C:\Program Files\PortableGit\bin\git.exe" (
				ECHO [92mPortable Git for Windows is already installed[0m
				SET PATH=!PATH!;"C:\Program Files\PortableGit\bin"
			) ELSE (
				ECHO [92mPortable Git for Windows not detected[0m
				IF EXIST "C:\Program Files\PortableGit-2.37.0-64-bit.7z.exe" (
					ECHO [92mInstaller for portable Git already downloaded, skipping download step[0m
				) ELSE (
					ECHO [92mInstaller for portable Git not detected, downloading[0m
					CD "C:\Program Files"
					curl -LO https://github.com/git-for-windows/git/releases/download/v2.37.0.windows.1/PortableGit-2.37.0-64-bit.7z.exe
				)
				
				ECHO [92mClick ok, do not change the unzip path[0m
				"C:\Program Files\PortableGit-2.37.0-64-bit.7z.exe"
				SET PATH=!PATH!;"C:\Program Files\PortableGit\bin"
			)
		)
)

IF EXIST "C:\Program Files\GitHub CLI\gh.exe" (
	SET /P AREYOUSURE="You already have gh CLI installed, install again? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		GOTO :InstallGHCLI
	)
) ELSE (
	ECHO [92mgh CLI does not exist, installing[0m
	:InstallGHCLI
	IF EXIST C:\Users\%username%\AppData\Local\Microsoft\WindowsApps\winget.exe (
		ECHO [92mwinget detected on computer, using winget to install gh CLI[0m
		winget install --id GitHub.cli
	) ELSE (
		IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\gh_2.13.0_windows_amd64.msi (
			ECHO [92mInstaller for gh CLI detected, skipping download step[0m
		) ELSE (
			ECHO [92mInstaller for gh CLI not detected, downloading[0m
			CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
			curl -LO https://github.com/cli/cli/releases/download/v2.13.0/gh_2.13.0_windows_amd64.msi
		)
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\gh_2.13.0_windows_amd64.msi
	CD ..
	)
)

set PATH=!PATH!;"C:\Program Files\GitHub CLI\"

IF EXIST C:\Users\%username%\AppData\Local\GitHubDesktop\GitHubDesktop.exe (
	SET /P AREYOUSURE="GitHub Desktop already exists, re-install? (Y/[N]): "
	IF "!AREYOUSURE!" == "Y" (
		GOTO :InstallGitDesk
	)
) ELSE (
	ECHO 
	SET /P AREYOUSURE="Install github desktop interface? (Y/N): "
		IF /I "!AREYOUSURE!" == "Y" (
			:InstallGitDesk
			IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\GitHubDesktopSetup-x64.exe (
				ECHO [92mDownloader already exists, skipping download phase[0m
			) ELSE (
				ECHO [92mDownloader for Python 3.8 not detected, downloading[0m
				CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads\
				curl -LO https://central.github.com/deployments/desktop/desktop/latest/win32
			)
			ECHO [92mClick through installer. Once installed, click add repository on disk, then navigate to C:\Users\%username%\Documents\GitHub. Add an exception if prompted[0m
			C:\Users\%username%\Documents\GitHub\Dependency_Downloads\GitHubDesktopSetup-x64.exe
		)
)

IF EXIST "C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\main.py" (
	SET AREYOUSURE=N
	SET /P AREYOUSURE="RF_Balance_Profound repository already exists, download again? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		echo [92mSelect HTTPS for your preferred protocol for git operations and Select manager-core if prompted for a credential helper[0m
		gh auth login
		cd C:\Users\%username%\Documents\GitHub
		gh repo clone 8foldrepo/RF_Balance_Profound
	)
) ELSE (
	echo [92mRF_Balance_Profound repository not found, cloning[0m
	echo [92mSelect manager-core if prompted for a credential helper[0m
	gh auth login
	cd C:\Users\%username%\Documents\GitHub
	gh repo clone 8foldrepo/RF_Balance_Profound
)

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

IF EXIST C:\Users\%username%\AppData\Local\Programs\Python\Python38\python.exe (
	SET /P AREYOUSURE="Python 3.8 found, do you wish to re-install Python? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\python-3.8.10-amd64.exe (
			ECHO [92mpython installer found, skipping download step[0m
		) ELSE (
			CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
			curl -LO https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
		)
		ECHO [92mmake sure to tick install to PATH[0m
		C:\Users\%username%\Documents\GitHub\Dependency_Downloads\python-3.8.10-amd64.exe
	)
) ELSE (
	ECHO [92mPython 3.8 not found on computer, downloading and installing[0m
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\python-3.8.10-amd64.exe (
		ECHO [92mPython 3.8 installer found, skipping download step[0m
	) ELSE (
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
	)
	ECHO [92mmake sure to tick install to PATH[0m
	C:\Users\%username%\Documents\GitHub\Dependency_Downloads\python-3.8.10-amd64.exe
)

SET /P AREYOUSURE="Do you want to download and install NI-VISA drivers (Y/[N]): "
IF /I "!AREYOUSURE!" == "Y" (
	IF EXIST C:\Users\%username%\Documents\GitHub\Dependency_Downloads\ni-visa_20.0_online_repack3.exe (
		ECHO [92mNI-VISA downloader already exists, skipping download step[0m
	) ELSE (
		CD C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://download.ni.com/support/nipkg/products/ni-v/ni-visa/20.0/online/ni-visa_20.0_online_repack3.exe
	)
	ECHO [92mcheck "NI-VISA interactive control" and uncheck everything else [0m
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

SET /P AREYOUSURE="Create desktop shortcut? (Y/[N]): "
	IF /I "!AREYOUSURE!" == "Y" (
		cd /d %userprofile%/Desktop
		copy "%userprofile%\Documents\GitHub\RF_Balance_Profound\RF Balance Profound.lnk"

IF EXIST "%userprofile%\Documents\GitHub\RF_Balance_Profound\Logs\wtf.log" (
	echo "wtf.log exists, contiuing"
) ELSE (
	echo making dir
	mkdir C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\Logs
	cd /d %userprofile%\Documents\GitHub\RF_Balance_Profound\Logs
	fsutil file createnew wtf.log 0
)

IF EXIST "%userprofile%\Documents\GitHub\RF_Balance_Profound\local.yaml" (
	echo "local.yaml exists, contiuing"
) ELSE (
	cd /d %userprofile%\Documents\GitHub\RF_Balance_Profound\
	fsutil file createnew local.yaml 0
)

ECHO [92mRestart your PC and double click the desktop shortcut for the applcation[0m
pause
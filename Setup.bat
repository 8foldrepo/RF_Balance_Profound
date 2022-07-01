@echo on
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
    echo [92Requesting administrative privileges...[0m
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"[0m
    set params= %*
    echo [92UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%temp%\getadmin.vbs"[0m

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
			echo [92Git for windows is already installed[0m
		) else (
			cd C:\Program Files
			curl -LO https://github.com/git-for-windows/git/releases/download/v2.37.0.windows.1/PortableGit-2.37.0-64-bit.7z.exe[0m
			echo [92mClick ok, do not change the unzip path"[0m
			PortableGit-2.37.0-64-bit.7z.exe
		)
	)

set PATH=!PATH!;"C:\Program Files\PortableGit\bin"

IF EXIST "C:\Program Files\GitHub CLI\gh.exe" (
	SET AREYOUSURE=N
	:PROMPT
	SET /P AREYOUSURE="You already have gh CLI installed, install again (Y/N): "
	IF /I "!AREYOUSURE!" NEQ "Y" (GOTO END) ELSE (winget install --id GitHub.cli)
) ELSE (
	echo [92"gh CLI does not exist"[0m
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
		echo [92Click through installer. Once installed, click add repository on disk, then navigate to C:\Users\%username%\Documents\GitHub. Add an exception if prompted[0m
		GitHubDesktopSetup-x64.exe
	)


IF EXIST "C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\main.py" (
	SET AREYOUSURE=N
	SET /P AREYOUSURE="repo already exists, download again? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		echo [92 Select manager-core if prompted for a credential helper [0m
		gh auth login
		cd C:\Users\%username%\Documents\GitHub
		gh repo clone 8foldrepo/RF_Balance_Profound
	)
) ELSE (
	echo [92repo not found, cloning [0m
	echo [92Select manager-core if prompted for a credential helper [0m
	gh auth login
	cd C:\Users\%username%\Documents\GitHub
	gh repo clone 8foldrepo/RF_Balance_Profound
)

IF EXIST "C:\ProgramData\Anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF EXIST "C:\Users\%username%\anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF EXIST "C:\Users\Public\anaconda3\Scripts\conda.exe" set CONDAEXISTS=1
IF DEFINED CONDAEXISTS (
	echo [92mConda found, skipping[0m
) ELSE (
	echo [92mConda not found, downloading and installing"[0m
	cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
	curl -LO https://repo.anaconda.com/archive/Anaconda3-2022.05-Windows-x86_64.exe
	echo [92"untick set as python 3.9 for system and tick add to PATH if possible"
	Anaconda3-2022.05-Windows-x86_64.exe
	cd ..
)

IF EXIST C:\Users\%username%\AppData\Local\Programs\Python\Python38\python.exe (
	echo [92mpython found, skipping[0m
) ELSE (
	cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
	curl -LO https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
	echo [92mmake sure to tick install to PATH[0m
	python-3.8.10-amd64.exe
	cd ..
)

:PROMPT
SET /P AREYOUSURE="Do you want to download and install NI-VISA drivers (Y/N): "
IF /I "!AREYOUSURE!" == "Y" (
	cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
	curl -LO https://download.ni.com/support/nipkg/products/ni-v/ni-visa/20.0/online/ni-visa_20.0_online_repack3.exe
	echo [92check "NI VISA interactive control" and uncheck everything else [0m
	ni-visa_20.0_online_repack3.exe
	cd ..
)

IF EXIST "C:\National Instruments Downloads\NI-DAQmx Base\15.0\setup.exe" (
	echo [92mNIDAQ setup exists, skipping download and install[0m
) ELSE (
	cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
	echo [92mNI DAQ setup doesn't exist, downloading and launching setup[0m
	curl -LO https://download.ni.com/support/nipkg/products/ni-d/ni-daqmx/21.8/online/ni-daqmx_21.8_online.exe
	echo [92Click through installer, uncheck everything.[0m
	ni-daqmx_21.8_online.exe
)


SET /P AREYOUSURE="Do you want to setup the anaconda environment RF_Balance_Profound?: "
IF /I "!AREYOUSURE!" == "Y" (
	cd C:\Users\%username%\Documents\GitHub\RF_Balance_Profound
	set PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
	conda update conda
	cd 
	conda env create -f environment.yml -v -v -v
)


SET /P AREYOUSURE="Install gclib?"
IF /I "!AREYOUSURE!" == "Y" (
	cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
	curl -LO https://www.galil.com/sw/pub/win/gclib/galil_gclib_1_34_15.exe
	echo [92install PCI driver and 32-bit binaries[0m
	galil_gclib_1_34_15.exe
)

SET /P AREYOUSURE="Add gclib to RF_Balance_Profound environment?"
IF /I "!AREYOUSURE!" == "Y" (
	CALL conda.bat activate RF_Balance_Profound
	echo [92setting up gclib python wrapper[0m
	cd %temp%
	mkdir py
	cd py
	copy "c:\Program Files (x86)\Galil\gclib\source\wrappers\python"
	copy "c:\Program Files (x86)\Galil\gclib\examples\python"
	python setup.py install
	copy gclib.py  C:\ProgramData\Anaconda3\envs\RF_Balanace_Profound\Lib\site-packages
)

SET /P AREYOUSURE="Install power meter DLL (to Windows\SysWOW64)?"
IF /I "!AREYOUSURE!" == "Y" (
	copy C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\Hardware\power_meter_dlls\mcl_pm_NET45.dll C:\Windows\SysWOW64
)

SET /P AREYOUSURE="Install pycharm community? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		cd C:\Users\%username%\Documents\GitHub\Dependency_Downloads
		curl -LO https://download.jetbrains.com/python/pycharm-community-2022.1.3.exe?_gl=1*19flnj1*_ga*MTAxOTYyNDQ5Ny4xNjU2Njk3NTQ3*_ga_9J976DJZ68*MTY1NjY5NzU0Ny4xLjEuMTY1NjY5NzU1MC4w&_ga=2.187974888.1324129483.1656697547-1019624497.1656697547
		echo [92Click through installer. Once installed, create a new project from existing sources in the repository folder. [0m
		pycharm-community-2022.1.3.exe
	)

SET /P AREYOUSURE="Create desktop shortcut? (Y/N): "
	IF /I "!AREYOUSURE!" == "Y" (
		cd "C:\Users\%username%\Desktop\"
		copy "C:\Users\Profound_Medical\Documents\GitHub\RF_Balance_Profound\run.bat"
		
pause
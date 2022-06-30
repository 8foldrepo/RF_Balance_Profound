@echo off
@setlocal enabledelayedexpansion

mkdir C:\Users\%username%\Documents\GitHub
cd C:\Users\%username%\Documents\GitHub


IF EXIST "C:\Program Files\GitHub CLI\gh.exe" (
	:PROMPT
	SET /P AREYOUSURE="You already have gh CLI installed, install again Y/[N]: "
	IF /I "!AREYOUSURE!" NEQ "Y" (GOTO END) ELSE (winget install --id GitHub.cli)
) ELSE (
	echo "gh CLI does not exist"
	IF EXIST C:\Users\%username%\AppData\Local\Microsoft\WindowsApps\winget.exe (
	winget install --id GitHub.cli
	) ELSE (
	curl -LO https://github.com/cli/cli/releases/download/v2.13.0/gh_2.13.0_windows_amd64.msi
	gh_2.13.0_windows_amd64.msi
	)
)
:END


set PATH=%PATH%;"C:\Program Files\GitHub CLI\"


IF EXIST "C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\main.py" (
	SET /P AREYOUSURE="repo already exists, download again? Y/N: "
	IF /I "!AREYOUSURE!"=="Y" (
		echo about to delete
		rmdir "C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\" /s
		gh auth login
		gh repo clone 8foldrepo/RF_Balance_Profound
	)
) ELSE (
	echo "repo not found, cloning"
	gh auth login
	gh repo clone 8foldrepo/RF_Balance_Profound
)


IF EXIST "C:\ProgramData\Anaconda3\Scripts\conda.exe" (
	echo [92mconda found, skipping[0m
) ELSE (
	echo [93mconda not found, downloading and installing"[0m
	curl -LO https://repo.anaconda.com/archive/Anaconda3-2022.05-Windows-x86_64.exe
	echo "untick set as python 3.9 for system and tick add to PATH if possible"
	Anaconda3-2022.05-Windows-x86_64.exe
)

IF EXIST C:\Users\%username%\AppData\Local\Programs\Python\Python38\python.exe (
	echo [92mpython found, skipping[0m
) ELSE (
	curl -LO https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
	echo [93mmake sure to tick install to PATH[0m
	python-3.8.10-amd64.exe
)

IF EXIST "C:\Program Files (x86)\Galil\gclib\source\wrappers\python\setup.py" (
	echo [92mgalil software and drivers found, skipping download and installation[0m
) ELSE (
	curl -LO https://www.galil.com/sw/pub/win/gclib/galil_gclib_1_34_15.exe
	start "" cmd /c "echo install PCI driver and 32-bit binaries&echo(&pause"
	galil_gclib_1_34_15.exe 
)

:PROMPT
SET /P AREYOUSURE="Do you want to download and install NI-VISA drivers Y/N: "
IF /I "!AREYOUSURE!" == "Y" (
	curl -LO https://download.ni.com/support/nipkg/products/ni-v/ni-visa/20.0/online/ni-visa_20.0_online_repack3.exe
	ni-visa_20.0_online_repack3.exe
)

IF EXIST "C:\National Instruments Downloads\NI-DAQmx Base\15.0\setup.exe" (
	echo [92mNIDAQ setup exists, skipping download and install[0m
) ELSE (
	echo [93mNI DAQ setup doesn't exist, downloading and launching setup[0m
	curl -LO https://download.ni.com/support/softlib/multifunction_daq/nidaqmxbase/15.0/windows/NIDAQmxBase1500.exe
	NIDAQmxBase1500.exe
)

cd %temp%
mkdir py
cd py
copy "c:\Program Files (x86)\Galil\gclib\source\wrappers\python"
copy "c:\Program Files (x86)\Galil\gclib\examples\python"
python setup.py install
copy gclib.py  C:\ProgramData\Anaconda3\envs\RF_Balanace_Profound\Lib\site-packages

cd C:\Users\%username%\Documents\GitHub\RF_Balance_Profound

set PATH=%PATH%;C:\ProgramData\Anaconda3\Scripts\

copy C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\Hardware\power_meter_dlls\mcl_pm_NET45.dll C:\Windows\SysWOW64

conda env create -f environment.yml -v
conda activate RF_Balance_Profound
cd %temp%
mkdir py
cd py
copy "c:\Program Files (x86)\Galil\gclib\source\wrappers\python"
copy "c:\Program Files (x86)\Galil\gclib\examples\python"
python setup.py install

mkdir C:\Users\%username%\Documents\GitHub
cd C:\Users\%username%\Documents\GitHub

if exist C:\Users\%username%\AppData\Local\Microsoft\WindowsApps\winget.exe(
	winget install --id GitHub.cli
) else(
	curl -LO https://github.com/cli/cli/releases/download/v2.13.0/gh_2.13.0_windows_amd64.msi
	gh_2.13.0_windows_amd64.msi
)

set PATH=%PATH%;"C:\Program Files\GitHub CLI\"

start "" cmd /c "echo repo is private so please complete the login process, one way is via GitHub.com > HTTPS > Yes > Login with a web browser&echo(&pause"
gh auth login

gh repo clone 8foldrepo/RF_Balance_Profound
:: you should now see "RF_Balance_Profound" in your Documents\GitHub folder

:: download gclib, conda, application, and python 3.8.10
if exist C:\ProgramData\Anaconda3\Scripts\conda.exe(
) else(
	curl -LO https://repo.anaconda.com/archive/Anaconda3-2022.05-Windows-x86_64.exe
	start "" cmd /c "echo untick set as python 3.9 for system and tick add to PATH if possible&echo(&pause"
	Anaconda3-2022.05-Windows-x86_64.exe
)

if exist C:\Users\%username%\AppData\Local\Programs\Python\Python38\python.exe(
) else(
	curl -LO https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
	start "" cmd /c "echo make sure to tick install to PATH&echo(&pause"
	python-3.8.10-amd64.exe
)

if exist "C:\Program Files (x86)\Galil\gclib\source\wrappers\python\setup.py"(
) else(
	curl -LO https://www.galil.com/sw/pub/win/gclib/galil_gclib_1_34_15.exe
	start "" cmd /c "echo additionally select install PCI driver and 32-bit binaries during setup&echo(&pause"
	galil_gclib_1_34_15.exe 
)

python "C:\Program Files (x86)\Galil\gclib\source\wrappers\python\setup.py" install

set PATH=%PATH%;C:\ProgramData\Anaconda3\Scripts\

copy C:\Users\%username%\Documents\GitHub\RF_Balance_Profound\Hardware\power_meter_dlls\mcl_pm_NET45.dll C:\Windows\SysWOW64

conda config --add channels conda-forge
conda config --add channels bioconda
conda update conda
conda env create -f environment.yml -v
conda activate RF_Balance_Profound

pip install pyqt5 pyqtgraph pyqt5-qt5 pyqt5-sip


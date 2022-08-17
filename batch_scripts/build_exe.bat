@setlocal enabledelayedexpansion

SET PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
SET PATH=!PATH!;"C:\ProgramData\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\Scripts\"

CALL conda.bat activate RF_Balance_Profound

cd ..
pyinstaller --icon="images\8foldlogo.ico" --noconfirm  --onefile --name="Profound WTF" main.py

mkdir dist
cd dist

ECHO Make sure that the version number of the config file editor is up to date
copy "..\Config File Editor 1.2.exe"
copy ..\local.yaml
copy ..\default.yaml
copy ..\8foldlogo.ico
copy ..\systeminfo.ini
copy ..\FrequencyExclusions.txt
copy ..\mcl_pm_NET45.dll
copy "..\UA serial number and frequency data.txt"
mkdir config_validation_data
cd config_validation_data
copy ..\..\config_validation_data
cd ..
mkdir resources
cd resources
copy ..\..\resources
cd ..
mkdir images
cd images
copy "..\..\images"
cd ..



mkdir scripts
cd scripts
copy "..\..\Scripts"
cd ..

mkdir logs
cd logs

fsutil file createnew wtf.log 0

cd ..
cd ..
cd ..
del build
del "Profound WTF.spec"

pause
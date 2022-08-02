@setlocal enabledelayedexpansion

SET PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
SET PATH=!PATH!;"C:\ProgramData\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\Scripts\"

CALL conda.bat activate RF_Balance_Profound

pyinstaller --icon="images\8foldlogo.ico" --noconfirm  --onefile --name="Profound WTF" main.py


mkdir dist
cd dist

copy ..\local.yaml
copy ..\default.yaml
copy ..\8foldlogo.ico
copy ..\systeminfo.ini
copy ..\FrequencyExclusions.txt
copy ..\mcl_pm_NET45.dll
copy "..\UA serial number and frequency data.txt"
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
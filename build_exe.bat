@setlocal enabledelayedexpansion

SET PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
SET PATH=!PATH!;"C:\ProgramData\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\Scripts\"

CALL conda.bat activate RF_Balance_Profound

cd %USERPROFILE%\documents\github\RF_Balance_Profound
pyinstaller --icon="%USERPROFILE%\documents\github\RF_Balance_Profound\program_data\8foldlogo.ico" --noconfirm --name="App" main.py

mkdir dist
cd dist
mkdir "App"
cd "App"

mkdir ui_elements
cd ui_elements
mkdir images
cd images
copy "%USERPROFILE%\documents\github\RF_Balance_Profound\ui_elements\images"
cd ..
cd ..

mkdir scripts
cd scripts
copy "%USERPROFILE%\documents\github\RF_Balance_Profound\scripts"
cd ..

mkdir Program_Data
cd Program_Data

copy "%USERPROFILE%\documents\github\RF_Balance_Profound\program_data"

mkdir logs
cd logs

fsutil file createnew wtf.log 0

pause
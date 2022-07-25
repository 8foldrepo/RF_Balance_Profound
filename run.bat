SET PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
SET PATH=!PATH!;"C:\ProgramData\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\Scripts\"

CALL conda.bat activate RF_Balance_Profound

cd %USERPROFILE%\documents\github\RF_Balance_Profound
python main.py
pause

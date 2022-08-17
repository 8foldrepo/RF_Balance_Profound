@echo off
@setlocal enabledelayedexpansion

SET PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
SET PATH=!PATH!;"C:\ProgramData\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\condabin\"
SET PATH=!PATH!;"C:\USERS\%username%\Anaconda3\Scripts\"

ECHO activating conda environment, if this fails run setup.bat in the batch scripts folder
CALL conda.bat activate RF_Balance_Profound

python main.py
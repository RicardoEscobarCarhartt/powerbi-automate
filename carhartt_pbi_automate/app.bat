@echo off
@REM Get the user's home directory
set "USERPROFILE = %USERPROFILE%"

@REM Change the directory to the user's home directory
set "DIR=%USERPROFILE%\OneDrive - Carhartt Inc\Documents\git\powerbi-automate"

@REM Change the directory to the project directory
cd /d "%DIR%"

@REM Activate the virtual environment, run the script, and deactivate the virtual environment
call venv\Scripts\activate

@REM Run the script
python "%DIR%\carhartt_pbi_automate\app.py"

@REM Deactivate the virtual environment
call venv\Scripts\deactivate

@REM Write the timestamp to the log file
echo "Ran automagically at: %date% %time%" >> "%USERPROFILE%\OneDrive - Carhartt Inc\Documents\git\powerbi-automate\carhartt_pbi_automate\log.txt"
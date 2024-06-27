@echo off
@REM Get the user's home directory
set "USERPROFILE = %USERPROFILE%"

@REM Get first argument
set "ARG1=%1"

@REM Get second argument
set "ARG2=%2"

@REM Change the directory to the user's home directory
set "DIR=%USERPROFILE%\OneDrive - Carhartt Inc\Documents\git\powerbi-automate"

@REM Change the directory to the project directory
cd /d "%DIR%"

@REM Activate the virtual environment, run the script, and deactivate the virtual environment
call venv\Scripts\activate

@REM Run the script, passing the arguments --daxfile and --sqlfile
python "%DIR%\carhartt_pbi_automate\run_supply.py" --daxfile %ARG1% --sqlfile %ARG2%

@REM Print the command that was run
echo python "%DIR%\carhartt_pbi_automate\run_supply.py" --daxfile %ARG1% --sqlfile %ARG2%

@REM Deactivate the virtual environment
call venv\Scripts\deactivate
exit
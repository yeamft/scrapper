@echo off
REM Start Airflow scheduler (run in a separate terminal after start_airflow.bat)
cd /d "%~dp0"
set PYTHON_PATH=C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe
set AIRFLOW_HOME=%~dp0airflow_home

echo Starting Airflow scheduler...
echo AIRFLOW_HOME=%AIRFLOW_HOME%
echo.
"%PYTHON_PATH%" -m airflow scheduler
pause

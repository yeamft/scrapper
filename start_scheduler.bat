@echo off
REM Start Airflow scheduler (use Python 3.10 or 3.11)
cd /d "%~dp0"
set PYTHON_PATH=C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe
set AIRFLOW_HOME=%~dp0airflow_home
echo Starting Airflow scheduler...
"%PYTHON_PATH%" -m airflow scheduler
pause

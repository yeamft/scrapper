@echo off
REM Start Airflow webserver (use Python 3.10 or 3.11)
cd /d "%~dp0"
set PYTHON_PATH=C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe
set AIRFLOW_HOME=%~dp0airflow_home

echo Starting Airflow webserver...
echo AIRFLOW_HOME=%AIRFLOW_HOME%
echo Open http://localhost:8080 (admin / admin)
echo.
"%PYTHON_PATH%" -m airflow webserver --port 8080
pause

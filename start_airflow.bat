@echo off
REM Start Airflow webserver (use Python 3.10 or 3.11)
cd /d "%~dp0"
set PYTHON_PATH=C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe
set AIRFLOW_HOME=%~dp0airflow_home
if not exist "%AIRFLOW_HOME%\dags" mkdir "%AIRFLOW_HOME%\dags"
if exist "dags\olx_scraper_dag.py" copy /Y "dags\olx_scraper_dag.py" "%AIRFLOW_HOME%\dags\"
echo Starting Airflow webserver at http://localhost:8080
"%PYTHON_PATH%" -m airflow webserver --port 8080
pause

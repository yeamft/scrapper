@echo off
REM Start the API server (uses Python 3.14 at the path below)
cd /d "%~dp0"
set PYTHON_PATH=C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe

echo Starting OLX Scraper API...
echo Using: %PYTHON_PATH%
echo.
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

"%PYTHON_PATH%" api.py

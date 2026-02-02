@echo off
REM Clear the accommodations database
cd /d "%~dp0"
set PYTHON_PATH=C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe

"%PYTHON_PATH%" clear_db.py
pause

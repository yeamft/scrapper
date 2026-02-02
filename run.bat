@echo off
REM Run any Python command using the project's Python location.
REM Usage: run.bat <script.py> [args]   or   run.bat -m pip install ...
cd /d "%~dp0"
set PY=C:\Users\fkt21\AppData\Local\Programs\Python\Python314\python.exe
"%PY%" %*

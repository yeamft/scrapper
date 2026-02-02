@echo off
REM Create .env from .env.example (edit .env with your real values)
cd /d "%~dp0"
if exist .env (
    echo .env already exists. Edit it to change values.
    pause
    exit /b 0
)
copy .env.example .env
echo Created .env from .env.example.
echo Edit .env and set your PostgreSQL and Redis values.
pause

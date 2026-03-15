@echo off
echo Setting up project...

:: Check Python exists
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install it from https://www.python.org
    pause
    exit /b
)

:: Create venv and install requirements only on first run
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    echo Installing requirements...
    echo This might take ~2 minutes
    pip install -r requirements.txt --quiet
) else (
    call .venv\Scripts\activate
)

:: Run the app
echo Starting app...
python main.py
pause
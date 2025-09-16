@echo off
echo Starting Career Advisor App...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\activate
    echo And install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment and start app
call venv\Scripts\activate.bat
python start_app.py

pause

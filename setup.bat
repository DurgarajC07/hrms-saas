@echo off
REM HRMS Development Setup Script for Windows

echo Setting up HRMS development environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env file with your configuration before running the application.
)

REM Initialize database
echo Setting up database...
python setup.py

echo.
echo ✅ Development setup complete!
echo.
echo To start the development server:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Start the server: uvicorn main:app --reload
echo.
echo API Documentation will be available at:
echo - Swagger UI: http://localhost:8000/api/docs
echo - ReDoc: http://localhost:8000/api/redoc
echo.
echo Default credentials:
echo - Super Admin: admin@hrms.com / SuperAdmin123!
echo - HR Manager: hr@techcorp.com / HRManager123!
echo - Employee: john.doe@techcorp.com / Employee123!

pause

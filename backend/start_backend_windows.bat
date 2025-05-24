@echo off
echo Starting PricePulse Backend for Windows...

REM Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Check if virtual environment exists
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start the Flask application
echo Starting Flask application...
python -m flask run --host=0.0.0.0

REM Deactivate virtual environment on exit
call .venv\Scripts\deactivate
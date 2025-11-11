@echo off
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
echo Starting AY HR Backend...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

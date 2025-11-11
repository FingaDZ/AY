cd "F:\Code\AY HR\backend"
.\venv\Scripts\Activate.ps1
Write-Host "Starting AY HR Backend..." -ForegroundColor Green
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

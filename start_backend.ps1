Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AY HR Management - Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$env:PYTHONIOENCODING = "utf-8"
cd "F:\Code\AY HR\backend"

Write-Host "Starting Backend Server..." -ForegroundColor Green
Write-Host "URL: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

& "F:\Code\AY HR\.venv\Scripts\uvicorn.exe" main:app --host 0.0.0.0 --port 8000 --reload

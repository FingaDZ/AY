# Script de démarrage complet pour AY HR
Write-Host "==================================" -ForegroundColor Yellow
Write-Host "   AY HR - Démarrage Complet" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow
Write-Host ""

# Démarrer le backend
Write-Host "[1/2] Démarrage du Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-File", ".\start_backend.ps1"
Start-Sleep -Seconds 3

# Démarrer le frontend
Write-Host "[2/2] Démarrage du Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-File", ".\start_frontend.ps1"

Write-Host ""
Write-Host "✅ Application démarrée !" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur une touche pour fermer cette fenêtre..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# ============================================================================
# Script de Démarrage - AY HR Management
# Pour Windows
# ============================================================================

Write-Host ""
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host " Démarrage AIRBAND HR" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Vérifier si les services sont installés
$backendService = Get-Service -Name "AYHR-Backend" -ErrorAction SilentlyContinue
$frontendService = Get-Service -Name "AYHR-Frontend" -ErrorAction SilentlyContinue

if ($backendService -and $frontendService) {
    Write-Host "Services Windows détectés" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  → Démarrage du service Backend..." -NoNewline
    Start-Service -Name "AYHR-Backend"
    Write-Host " OK" -ForegroundColor Green
    
    Write-Host "  → Démarrage du service Frontend..." -NoNewline
    Start-Service -Name "AYHR-Frontend"
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host "Démarrage manuel" -ForegroundColor Yellow
    Write-Host ""
    
    # Vérifier si les processus existent déjà
    $existingBackend = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*AY HR*"}
    $existingFrontend = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*AY HR*"}
    
    if ($existingBackend -or $existingFrontend) {
        Write-Host "  ⚠️  Des processus existent déjà. Arrêt..." -ForegroundColor Yellow
        .\stop-windows.ps1
        Start-Sleep -Seconds 2
    }
    
    # Démarrer le backend
    Write-Host "  → Démarrage du Backend..." -NoNewline
    $backendPath = Join-Path $PWD "backend"
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$backendPath'; .\.venv\Scripts\Activate.ps1; python -m uvicorn main:app --host 0.0.0.0 --port 8000"
    ) -WindowStyle Normal
    Start-Sleep -Seconds 3
    Write-Host " OK" -ForegroundColor Green
    
    # Démarrer le frontend
    Write-Host "  → Démarrage du Frontend..." -NoNewline
    $frontendPath = Join-Path $PWD "frontend"
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$frontendPath'; npm run dev"
    ) -WindowStyle Normal
    Start-Sleep -Seconds 3
    Write-Host " OK" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Application Démarrée!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Accès à l'application:" -ForegroundColor Cyan
Write-Host "  Interface Web    : http://localhost:3000" -ForegroundColor White
Write-Host "  API Backend      : http://localhost:8000" -ForegroundColor White
Write-Host "  Documentation API: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Pour arrêter l'application:" -ForegroundColor Cyan
Write-Host "  .\stop-windows.ps1" -ForegroundColor White
Write-Host ""

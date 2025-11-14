# ============================================================================
# Script d'Arrêt - AY HR Management
# Pour Windows
# ============================================================================

Write-Host ""
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host " Arrêt AIRBAND HR" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si les services sont installés
$backendService = Get-Service -Name "AYHR-Backend" -ErrorAction SilentlyContinue
$frontendService = Get-Service -Name "AYHR-Frontend" -ErrorAction SilentlyContinue

if ($backendService -and $frontendService) {
    Write-Host "  → Arrêt du service Backend..." -NoNewline
    Stop-Service -Name "AYHR-Backend" -Force
    Write-Host " OK" -ForegroundColor Green
    
    Write-Host "  → Arrêt du service Frontend..." -NoNewline
    Stop-Service -Name "AYHR-Frontend" -Force
    Write-Host " OK" -ForegroundColor Green
} else {
    # Arrêter les processus Python (backend)
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*AY HR*"}
    if ($pythonProcesses) {
        Write-Host "  → Arrêt du Backend..." -NoNewline
        $pythonProcesses | Stop-Process -Force
        Write-Host " OK" -ForegroundColor Green
    }
    
    # Arrêter les processus Node (frontend)
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*AY HR*"}
    if ($nodeProcesses) {
        Write-Host "  → Arrêt du Frontend..." -NoNewline
        $nodeProcesses | Stop-Process -Force
        Write-Host " OK" -ForegroundColor Green
    }
    
    if (-not $pythonProcesses -and -not $nodeProcesses) {
        Write-Host "  Aucun processus en cours d'exécution" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Application arrêtée" -ForegroundColor Green
Write-Host ""

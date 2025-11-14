# ============================================================================
# Installation des Services Windows - AY HR Management
# Nécessite NSSM (Non-Sucking Service Manager)
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Installation Services Windows" -ForegroundColor White
Write-Host " AIRBAND HR v1.1.4" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les droits administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ Ce script nécessite des droits administrateur" -ForegroundColor Red
    Write-Host ""
    Write-Host "Clic droit sur PowerShell → 'Exécuter en tant qu'administrateur'" -ForegroundColor Yellow
    exit 1
}

# Chemins
$installPath = $PWD.Path
$nssmPath = Join-Path $installPath "nssm.exe"
$pythonExe = Join-Path $installPath "backend\.venv\Scripts\python.exe"
$uvicornModule = "uvicorn"
$backendPath = Join-Path $installPath "backend"
$frontendPath = Join-Path $installPath "frontend"
$nodeExe = (Get-Command node).Source
$npmCmd = Join-Path (Split-Path $nodeExe) "npm.cmd"

# Télécharger NSSM si nécessaire
if (-not (Test-Path $nssmPath)) {
    Write-Host "[1/5] Téléchargement de NSSM..." -ForegroundColor Yellow
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = Join-Path $env:TEMP "nssm.zip"
    $nssmExtract = Join-Path $env:TEMP "nssm"
    
    Write-Host "  → Téléchargement..." -NoNewline
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing
    Write-Host " OK" -ForegroundColor Green
    
    Write-Host "  → Extraction..." -NoNewline
    Expand-Archive -Path $nssmZip -DestinationPath $nssmExtract -Force
    
    # Copier la version appropriée (64-bit)
    $nssmExe = Join-Path $nssmExtract "nssm-2.24\win64\nssm.exe"
    Copy-Item $nssmExe -Destination $nssmPath
    Write-Host " OK" -ForegroundColor Green
    
    Remove-Item $nssmZip -Force
    Remove-Item $nssmExtract -Recurse -Force
} else {
    Write-Host "[1/5] NSSM déjà présent" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/5] Arrêt des services existants..." -ForegroundColor Yellow
# Arrêter et supprimer les services existants
$services = @("AYHR-Backend", "AYHR-Frontend")
foreach ($serviceName in $services) {
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "  → Arrêt de $serviceName..." -NoNewline
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        & $nssmPath remove $serviceName confirm
        Write-Host " OK" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[3/5] Installation du service Backend..." -ForegroundColor Yellow

# Créer un script batch pour le backend
$backendBat = Join-Path $installPath "start-backend-service.bat"
$backendBatContent = @"
@echo off
cd /d "$backendPath"
call .venv\Scripts\activate.bat
python -m uvicorn main:app --host 0.0.0.0 --port 8000
"@
Set-Content -Path $backendBat -Value $backendBatContent -Encoding ASCII

Write-Host "  → Configuration du service..." -NoNewline
& $nssmPath install AYHR-Backend $backendBat
& $nssmPath set AYHR-Backend AppDirectory $backendPath
& $nssmPath set AYHR-Backend DisplayName "AY HR Management - Backend"
& $nssmPath set AYHR-Backend Description "Backend API pour AY HR Management (FastAPI)"
& $nssmPath set AYHR-Backend Start SERVICE_AUTO_START
& $nssmPath set AYHR-Backend AppStdout (Join-Path $installPath "logs\backend-service.log")
& $nssmPath set AYHR-Backend AppStderr (Join-Path $installPath "logs\backend-service-error.log")
& $nssmPath set AYHR-Backend AppRotateFiles 1
& $nssmPath set AYHR-Backend AppRotateBytes 1048576
Write-Host " OK" -ForegroundColor Green

Write-Host "  → Démarrage du service..." -NoNewline
Start-Service -Name "AYHR-Backend"
Start-Sleep -Seconds 3
Write-Host " OK" -ForegroundColor Green

Write-Host ""
Write-Host "[4/5] Installation du service Frontend..." -ForegroundColor Yellow

# Créer un script batch pour le frontend
$frontendBat = Join-Path $installPath "start-frontend-service.bat"
$frontendBatContent = @"
@echo off
cd /d "$frontendPath"
call npm run dev
"@
Set-Content -Path $frontendBat -Value $frontendBatContent -Encoding ASCII

Write-Host "  → Configuration du service..." -NoNewline
& $nssmPath install AYHR-Frontend $frontendBat
& $nssmPath set AYHR-Frontend AppDirectory $frontendPath
& $nssmm set AYHR-Frontend DisplayName "AY HR Management - Frontend"
& $nssmPath set AYHR-Frontend Description "Interface Web pour AY HR Management (React + Vite)"
& $nssmPath set AYHR-Frontend Start SERVICE_AUTO_START
& $nssmPath set AYHR-Frontend DependOnService AYHR-Backend
& $nssmPath set AYHR-Frontend AppStdout (Join-Path $installPath "logs\frontend-service.log")
& $nssmPath set AYHR-Frontend AppStderr (Join-Path $installPath "logs\frontend-service-error.log")
& $nssmPath set AYHR-Frontend AppRotateFiles 1
& $nssmPath set AYHR-Frontend AppRotateBytes 1048576
Write-Host " OK" -ForegroundColor Green

Write-Host "  → Démarrage du service..." -NoNewline
Start-Service -Name "AYHR-Frontend"
Start-Sleep -Seconds 3
Write-Host " OK" -ForegroundColor Green

Write-Host ""
Write-Host "[5/5] Vérification des services..." -ForegroundColor Yellow
Write-Host ""

$backendStatus = (Get-Service -Name "AYHR-Backend").Status
$frontendStatus = (Get-Service -Name "AYHR-Frontend").Status

Write-Host "  AYHR-Backend  : $backendStatus" -ForegroundColor $(if($backendStatus -eq 'Running'){'Green'}else{'Red'})
Write-Host "  AYHR-Frontend : $frontendStatus" -ForegroundColor $(if($frontendStatus -eq 'Running'){'Green'}else{'Red'})

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Services Windows Installés!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Les services démarreront automatiquement avec Windows" -ForegroundColor Cyan
Write-Host ""
Write-Host "Gestion des services:" -ForegroundColor Cyan
Write-Host "  Démarrer  : Start-Service AYHR-Backend, AYHR-Frontend" -ForegroundColor White
Write-Host "  Arrêter   : Stop-Service AYHR-Backend, AYHR-Frontend" -ForegroundColor White
Write-Host "  Redémarrer: Restart-Service AYHR-Backend, AYHR-Frontend" -ForegroundColor White
Write-Host "  Statut    : Get-Service AYHR-Backend, AYHR-Frontend" -ForegroundColor White
Write-Host ""
Write-Host "Accès à l'application:" -ForegroundColor Cyan
Write-Host "  Interface Web: http://localhost:3000" -ForegroundColor White
Write-Host ""

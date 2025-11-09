# Script de démarrage de l'application AY HR Management
# Utilisation : .\start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AY HR Management - Démarrage" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est installé
Write-Host "[1/5] Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "   Téléchargez Python depuis https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Se déplacer dans le dossier backend
Write-Host ""
Write-Host "[2/5] Navigation vers le dossier backend..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
if (Test-Path $backendPath) {
    Set-Location $backendPath
    Write-Host "✓ Dossier backend trouvé" -ForegroundColor Green
} else {
    Write-Host "✗ Dossier backend non trouvé" -ForegroundColor Red
    exit 1
}

# Vérifier si l'environnement virtuel existe
Write-Host ""
Write-Host "[3/5] Vérification de l'environnement virtuel..." -ForegroundColor Yellow
$venvPath = Join-Path $backendPath "venv"
if (Test-Path $venvPath) {
    Write-Host "✓ Environnement virtuel trouvé" -ForegroundColor Green
} else {
    Write-Host "! Environnement virtuel non trouvé" -ForegroundColor Yellow
    Write-Host "  Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Environnement virtuel créé" -ForegroundColor Green
    } else {
        Write-Host "✗ Erreur lors de la création de l'environnement virtuel" -ForegroundColor Red
        exit 1
    }
}

# Activer l'environnement virtuel
Write-Host ""
Write-Host "[4/5] Activation de l'environnement virtuel..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "✓ Environnement virtuel activé" -ForegroundColor Green
} else {
    Write-Host "✗ Script d'activation non trouvé" -ForegroundColor Red
    exit 1
}

# Vérifier si les dépendances sont installées
Write-Host ""
Write-Host "[5/5] Vérification des dépendances..." -ForegroundColor Yellow
$requirementsPath = Join-Path $backendPath "requirements.txt"
if (Test-Path $requirementsPath) {
    # Vérifier si fastapi est installé
    $fastapiInstalled = pip show fastapi 2>&1 | Select-String "Name: fastapi"
    if ($fastapiInstalled) {
        Write-Host "✓ Dépendances installées" -ForegroundColor Green
    } else {
        Write-Host "! Installation des dépendances..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dépendances installées avec succès" -ForegroundColor Green
        } else {
            Write-Host "✗ Erreur lors de l'installation des dépendances" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "✗ Fichier requirements.txt non trouvé" -ForegroundColor Red
    exit 1
}

# Vérifier si le fichier IRG existe
Write-Host ""
Write-Host "Vérification du fichier IRG..." -ForegroundColor Yellow
$irgPath = Join-Path $backendPath "data\irg.xlsx"
if (Test-Path $irgPath) {
    Write-Host "✓ Fichier IRG trouvé" -ForegroundColor Green
} else {
    Write-Host "! Fichier IRG non trouvé" -ForegroundColor Yellow
    Write-Host "  Création du fichier IRG..." -ForegroundColor Yellow
    $createIrgScript = Join-Path $backendPath "data\create_irg.py"
    if (Test-Path $createIrgScript) {
        python $createIrgScript
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Fichier IRG créé" -ForegroundColor Green
            Write-Host "⚠  IMPORTANT: Vérifiez et ajustez le barème dans data\irg.xlsx" -ForegroundColor Yellow
        } else {
            Write-Host "✗ Erreur lors de la création du fichier IRG" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Script de création IRG non trouvé" -ForegroundColor Red
    }
}

# Démarrer l'application
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage de l'application..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "L'API sera accessible sur:" -ForegroundColor Green
Write-Host "  • API: http://localhost:8000" -ForegroundColor White
Write-Host "  • Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

# Lancer le serveur
python main.py

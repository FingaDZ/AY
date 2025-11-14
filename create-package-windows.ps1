# ============================================================================
# Script de Création du Package Windows
# AIRBAND HR v1.1.4
# ============================================================================

param(
    [string]$Version = "1.1.4"
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Création du Package Windows v$Version" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Dossiers et fichiers à exclure
$excludePatterns = @(
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".git",
    ".gitignore",
    ".vscode",
    ".idea",
    "*.log",
    "logs",
    "backups",
    "uploads",
    "test_*.py",
    "check_*.py",
    "*.zip"
)

# Créer le dossier temporaire
$tempDir = "temp_package"
$packageName = "ay-hr-v$Version-windows"
$packageDir = Join-Path $tempDir $packageName

Write-Host "[1/6] Nettoyage des anciens packages..." -ForegroundColor Yellow
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}
if (Test-Path "$packageName.zip") {
    Remove-Item -Path "$packageName.zip" -Force
}

Write-Host "[2/6] Création de la structure du package..." -ForegroundColor Yellow
New-Item -Path $packageDir -ItemType Directory -Force | Out-Null

# Fonction pour copier un dossier en excluant certains fichiers
function Copy-FilteredFolder {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    Get-ChildItem -Path $Source -Recurse | ForEach-Object {
        $shouldExclude = $false
        foreach ($pattern in $excludePatterns) {
            if ($_.FullName -like "*$pattern*") {
                $shouldExclude = $true
                break
            }
        }
        
        if (-not $shouldExclude) {
            $relativePath = $_.FullName.Substring($Source.Length)
            $destPath = Join-Path $Destination $relativePath
            
            if ($_.PSIsContainer) {
                New-Item -Path $destPath -ItemType Directory -Force | Out-Null
            } else {
                Copy-Item -Path $_.FullName -Destination $destPath -Force
            }
        }
    }
}

Write-Host "[3/6] Copie du backend..." -ForegroundColor Yellow
Copy-FilteredFolder -Source "backend" -Destination (Join-Path $packageDir "backend")

Write-Host "[4/6] Copie du frontend..." -ForegroundColor Yellow
Copy-FilteredFolder -Source "frontend" -Destination (Join-Path $packageDir "frontend")

Write-Host "[5/6] Copie des fichiers d'installation..." -ForegroundColor Yellow
$filesToCopy = @(
    "database\create_database.sql",
    "install-windows.ps1",
    "start-windows.ps1",
    "stop-windows.ps1",
    "install-service-windows.ps1",
    "INSTALLATION_GUIDE.md",
    "README.md"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        $destPath = Join-Path $packageDir $file
        $destDir = Split-Path $destPath -Parent
        
        if (-not (Test-Path $destDir)) {
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
        }
        
        Copy-Item -Path $file -Destination $destPath -Force
    }
}

# Créer un README simplifié pour le package
Write-Host "[6/6] Création du README du package..." -ForegroundColor Yellow
$packageReadme = @"
# AY HR Management v$Version - Package Windows

## Installation Rapide

1. Extraire ce fichier ZIP dans un dossier de votre choix
2. Ouvrir PowerShell en tant qu'Administrateur
3. Naviguer vers le dossier extrait:
   ``````
   cd "C:\chemin\vers\$packageName"
   ``````
4. Exécuter le script d'installation:
   ``````
   .\install-windows.ps1
   ``````

## Contenu du Package

- **backend/** - Code source du serveur API
- **frontend/** - Code source de l'interface web
- **database/** - Scripts SQL de création de la base de données
- **install-windows.ps1** - Script d'installation automatique
- **start-windows.ps1** - Script de démarrage manuel
- **stop-windows.ps1** - Script d'arrêt
- **install-service-windows.ps1** - Installation en tant que service Windows
- **INSTALLATION_GUIDE.md** - Guide d'installation complet

## Prérequis

- Windows 10/11 ou Windows Server 2016+
- Python 3.11 ou supérieur
- Node.js 18 ou supérieur
- MariaDB 10.11 ou supérieur

## Documentation

Consultez le fichier **INSTALLATION_GUIDE.md** pour:
- Instructions d'installation détaillées
- Configuration de la base de données
- Dépannage
- Configuration réseau
- Procédures de sauvegarde

## Support

Pour toute question ou problème:
- Consultez INSTALLATION_GUIDE.md section "Dépannage"
- Vérifiez les logs dans le dossier logs/
- Contactez votre administrateur système

## Version

Version: $Version
Date: $(Get-Date -Format "dd/MM/yyyy")
"@

Set-Content -Path (Join-Path $packageDir "README_PACKAGE.md") -Value $packageReadme -Encoding UTF8

Write-Host "`n[Compression] Création de l'archive ZIP..." -ForegroundColor Yellow
Compress-Archive -Path "$tempDir\*" -DestinationPath "$packageName.zip" -Force

Write-Host "`n[Nettoyage] Suppression des fichiers temporaires..." -ForegroundColor Yellow
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "`n========================================" -ForegroundColor Green
Write-Host " Package créé avec succès!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nFichier: $packageName.zip" -ForegroundColor White
Write-Host "Taille: $((Get-Item "$packageName.zip").Length / 1MB | ForEach-Object { '{0:N2}' -f $_ }) MB" -ForegroundColor White
Write-Host "`nLe package est prêt pour la distribution!" -ForegroundColor Cyan

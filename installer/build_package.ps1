# ====================================
# Script de Préparation du Package
# AY HR System v3.6.0
# ====================================

param(
    [switch]$SkipDownloads,
    [switch]$SkipBuild,
    [switch]$CompileNow
)

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AY HR System - Build Package" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$InstallerDir = $PSScriptRoot
$PackageDir = Join-Path $InstallerDir "package"
$ProjectRoot = Split-Path $InstallerDir -Parent

# Fonctions utilitaires
function Write-Step {
    param($Message)
    Write-Host "`n[STEP] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param($Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-ErrorMsg {
    param($Message)
    Write-Host "[ERREUR] $Message" -ForegroundColor Red
}

# Créer la structure
Write-Step "Création de la structure du package..."
$Folders = @(
    "$PackageDir\python",
    "$PackageDir\nodejs",
    "$PackageDir\mariadb",
    "$PackageDir\nginx",
    "$PackageDir\nssm",
    "$PackageDir\nginx-config",
    "$PackageDir\resources"
)

foreach ($Folder in $Folders) {
    if (-not (Test-Path $Folder)) {
        New-Item -ItemType Directory -Force -Path $Folder | Out-Null
    }
}
Write-Success "Structure créée"

# ÉTAPE 1: Python Embedded
if (-not $SkipDownloads) {
    Write-Step "Téléchargement de Python 3.11 Embedded..."
    $PythonDir = "$PackageDir\python"
    $PythonZip = "$PythonDir\python-embed.zip"
    
    if (-not (Test-Path "$PythonDir\python.exe")) {
        Write-Info "Téléchargement depuis python.org..."
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip" `
            -OutFile $PythonZip
        
        Write-Info "Extraction..."
        Expand-Archive -Path $PythonZip -DestinationPath $PythonDir -Force
        Remove-Item $PythonZip
        
        Write-Info "Installation de pip..."
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" `
            -OutFile "$PythonDir\get-pip.py"
        
        & "$PythonDir\python.exe" "$PythonDir\get-pip.py"
        
        Write-Info "Configuration de Python..."
        $PthFile = Get-Content "$PythonDir\python311._pth"
        $PthFile = $PthFile -replace "#import site", "import site"
        Set-Content "$PythonDir\python311._pth" $PthFile
        
        Write-Success "Python configuré"
    } else {
        Write-Info "Python déjà téléchargé"
    }
    
    # Télécharger les packages Python
    Write-Step "Téléchargement des packages Python..."
    $PackagesDir = "$PythonDir\packages"
    if (-not (Test-Path $PackagesDir)) {
        New-Item -ItemType Directory -Force -Path $PackagesDir | Out-Null
    }
    
    if ((Get-ChildItem $PackagesDir).Count -lt 10) {
        Write-Info "Téléchargement des dépendances..."
        & "$PythonDir\python.exe" -m pip download `
            -r "$ProjectRoot\backend\requirements.txt" `
            -d $PackagesDir
        Write-Success "Packages téléchargés: $((Get-ChildItem $PackagesDir).Count) fichiers"
    } else {
        Write-Info "Packages déjà téléchargés"
    }
}

# ÉTAPE 2: Node.js Portable
if (-not $SkipDownloads) {
    Write-Step "Téléchargement de Node.js..."
    $NodeDir = "$PackageDir\nodejs"
    
    if (-not (Test-Path "$NodeDir\node.exe")) {
        Write-Info "Téléchargement depuis nodejs.org..."
        $NodeZip = "$NodeDir\nodejs.zip"
        Invoke-WebRequest -Uri "https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip" `
            -OutFile $NodeZip
        
        Write-Info "Extraction..."
        Expand-Archive -Path $NodeZip -DestinationPath $NodeDir -Force
        
        Get-ChildItem "$NodeDir\node-v*\*" | Move-Item -Destination $NodeDir -Force
        Remove-Item "$NodeDir\node-v*" -Recurse -Force
        Remove-Item $NodeZip
        
        Write-Success "Node.js installé"
    } else {
        Write-Info "Node.js déjà téléchargé"
    }
}

# ÉTAPE 3: Compiler le Frontend
if (-not $SkipBuild) {
    Write-Step "Compilation du frontend..."
    $FrontendDir = "$ProjectRoot\frontend"
    $FrontendDist = "$PackageDir\frontend-dist"
    
    Push-Location $FrontendDir
    
    if (-not (Test-Path "node_modules")) {
        Write-Info "Installation des dépendances npm..."
        npm install
    }
    
    Write-Info "Build du frontend..."
    npm run build
    
    Pop-Location
    
    Write-Info "Copie du build..."
    if (Test-Path $FrontendDist) {
        Remove-Item $FrontendDist -Recurse -Force
    }
    Copy-Item -Recurse "$FrontendDir\dist" $FrontendDist -Force
    
    Write-Success "Frontend compilé"
}

# ÉTAPE 4: MariaDB
if (-not $SkipDownloads) {
    Write-Step "Téléchargement de MariaDB..."
    $MariaDir = "$PackageDir\mariadb"
    
    if (-not (Test-Path "$MariaDir\bin\mysqld.exe")) {
        Write-Info "Téléchargement depuis mariadb.org..."
        $MariaZip = "$MariaDir\mariadb.zip"
        $MariaUrl = "https://archive.mariadb.org/mariadb-10.11.6/winx64-packages/mariadb-10.11.6-winx64.zip"
        
        Invoke-WebRequest -Uri $MariaUrl -OutFile $MariaZip
        
        Write-Info "Extraction..."
        Expand-Archive -Path $MariaZip -DestinationPath $MariaDir -Force
        
        Get-ChildItem "$MariaDir\mariadb-*\*" | Move-Item -Destination $MariaDir -Force
        Remove-Item "$MariaDir\mariadb-*" -Recurse -Force
        Remove-Item $MariaZip
        
        Write-Info "Création de my.ini..."
        @"
[mysqld]
port=3307
datadir=../../data/mysql
socket=/tmp/mysql.sock
key_buffer_size=16M
max_allowed_packet=128M
table_open_cache=256
sort_buffer_size=512K
net_buffer_length=8K
read_buffer_size=256K
read_rnd_buffer_size=512K
myisam_sort_buffer_size=8M
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
default-storage-engine=InnoDB
max_connections=200

[client]
port=3307
socket=/tmp/mysql.sock
"@ | Out-File -FilePath "$MariaDir\my.ini" -Encoding UTF8
        
        Write-Success "MariaDB installé"
    } else {
        Write-Info "MariaDB déjà téléchargé"
    }
}

# ÉTAPE 5: Nginx
if (-not $SkipDownloads) {
    Write-Step "Téléchargement de Nginx..."
    $NginxDir = "$PackageDir\nginx"
    
    if (-not (Test-Path "$NginxDir\nginx.exe")) {
        Write-Info "Téléchargement depuis nginx.org..."
        $NginxZip = "$NginxDir\nginx.zip"
        Invoke-WebRequest -Uri "http://nginx.org/download/nginx-1.24.0.zip" `
            -OutFile $NginxZip
        
        Write-Info "Extraction..."
        Expand-Archive -Path $NginxZip -DestinationPath $NginxDir -Force
        
        Get-ChildItem "$NginxDir\nginx-*\*" | Move-Item -Destination $NginxDir -Force
        Remove-Item "$NginxDir\nginx-*" -Recurse -Force
        Remove-Item $NginxZip
        
        Write-Success "Nginx installé"
    } else {
        Write-Info "Nginx déjà téléchargé"
    }
    
    # Configuration Nginx
    Write-Info "Création de la configuration Nginx..."
    @"
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;

    server {
        listen 80;
        server_name localhost;

        location / {
            root ../../frontend/dist;
            index index.html;
            try_files `$uri `$uri/ /index.html;
        }

        location /api {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }

        location /docs {
            proxy_pass http://127.0.0.1:8000;
        }

        location /redoc {
            proxy_pass http://127.0.0.1:8000;
        }

        location /static {
            proxy_pass http://127.0.0.1:8000;
        }
    }
}
"@ | Out-File -FilePath "$PackageDir\nginx-config\nginx.conf" -Encoding UTF8
}

# ÉTAPE 6: NSSM
if (-not $SkipDownloads) {
    Write-Step "Téléchargement de NSSM..."
    $NssmDir = "$PackageDir\nssm"
    
    if (-not (Test-Path "$NssmDir\nssm.exe")) {
        Write-Info "Téléchargement depuis nssm.cc..."
        $NssmZip = "$NssmDir\nssm.zip"
        Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" `
            -OutFile $NssmZip
        
        Write-Info "Extraction..."
        Expand-Archive -Path $NssmZip -DestinationPath $NssmDir -Force
        
        Copy-Item "$NssmDir\nssm-2.24\win64\nssm.exe" "$NssmDir\nssm.exe" -Force
        Remove-Item "$NssmDir\nssm-2.24" -Recurse -Force
        Remove-Item $NssmZip
        
        Write-Success "NSSM installé"
    } else {
        Write-Info "NSSM déjà téléchargé"
    }
}

# ÉTAPE 7: Copier le code source
Write-Step "Copie du code source..."

Write-Info "Copie du backend..."
$BackendDest = "$PackageDir\backend"
if (Test-Path $BackendDest) {
    Remove-Item $BackendDest -Recurse -Force
}
Copy-Item -Recurse "$ProjectRoot\backend" $BackendDest -Force
Remove-Item "$BackendDest\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$BackendDest\.env" -Force -ErrorAction SilentlyContinue
Remove-Item "$BackendDest\data" -Recurse -Force -ErrorAction SilentlyContinue

Write-Info "Copie du frontend source..."
$FrontendSrc = "$PackageDir\frontend"
if (Test-Path $FrontendSrc) {
    Remove-Item $FrontendSrc -Recurse -Force
}
Copy-Item -Recurse "$ProjectRoot\frontend" $FrontendSrc -Force
Remove-Item "$FrontendSrc\node_modules" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$FrontendSrc\dist" -Recurse -Force -ErrorAction SilentlyContinue

Write-Info "Copie de la base de données..."
Copy-Item -Recurse "$ProjectRoot\database" "$PackageDir\database" -Force

Write-Info "Copie des fichiers racine..."
Copy-Item "$ProjectRoot\*.md" $PackageDir -Force -ErrorAction SilentlyContinue
Copy-Item "$ProjectRoot\backend\.env.example" "$PackageDir\.env.example" -Force

Write-Success "Code source copié"

# ÉTAPE 8: Créer les ressources
Write-Step "Création des ressources..."
$ResourcesDir = "$PackageDir\resources"

if (-not (Test-Path "$ResourcesDir\LICENSE.txt")) {
    @"
AY HR SYSTEM - CONTRAT DE LICENCE

Copyright (c) 2025 AY Company

Ce logiciel est fourni "tel quel", sans garantie d'aucune sorte.
L'utilisation de ce logiciel est soumise aux termes et conditions suivants:

1. Le logiciel est destiné à un usage interne uniquement.
2. Aucune redistribution n'est autorisée sans autorisation écrite.
3. Le support technique est fourni selon les termes du contrat de service.

Pour plus d'informations, contactez: support@aycompany.dz
"@ | Out-File -FilePath "$ResourcesDir\LICENSE.txt" -Encoding UTF8
}

Write-Info "NOTE: Ajoutez les icônes manuellement dans $ResourcesDir"
Write-Info "Fichiers nécessaires: app.ico, header.bmp, wizard.bmp"

Write-Success "Ressources créées"

# ÉTAPE 9: Rapport
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PRÉPARATION TERMINÉE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nTaille du package:" -ForegroundColor Yellow
$TotalSize = (Get-ChildItem $PackageDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host ("  {0:N2} MB" -f $TotalSize) -ForegroundColor White

Write-Host "`nContenu du package:" -ForegroundColor Yellow
Get-ChildItem $PackageDir -Directory | ForEach-Object {
    $Size = (Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host ("  {0,-20} : {1,8:N2} MB" -f $_.Name, $Size) -ForegroundColor White
}

# Compilation NSIS
if ($CompileNow) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  COMPILATION NSIS" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $NsisExe = "C:\Program Files (x86)\NSIS\makensis.exe"
    if (Test-Path $NsisExe) {
        Write-Info "Compilation de l'installateur..."
        & $NsisExe "$InstallerDir\ayhr_installer.nsi"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Installateur créé avec succès !"
            $InstallerPath = "$InstallerDir\AY_HR_Setup_v3.6.0.exe"
            if (Test-Path $InstallerPath) {
                $InstallerSize = (Get-Item $InstallerPath).Length / 1MB
                Write-Host ("`nTaille de l'installateur: {0:N2} MB" -f $InstallerSize) -ForegroundColor Green
            }
        } else {
            Write-ErrorMsg "Erreur lors de la compilation"
        }
    } else {
        Write-Info "NSIS n'est pas installé. Installez-le depuis:"
        Write-Info "https://nsis.sourceforge.io/Download"
    }
}

Write-Host "`nProchaines étapes:" -ForegroundColor Yellow
Write-Host "  1. Ajoutez les icônes dans $ResourcesDir" -ForegroundColor White
Write-Host "  2. Vérifiez le contenu du package" -ForegroundColor White
Write-Host "  3. Compilez avec: .\build_package.ps1 -CompileNow" -ForegroundColor White
Write-Host "  4. Testez sur une VM Windows propre" -ForegroundColor White
Write-Host ""

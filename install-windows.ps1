# ============================================================================
# Script d'Installation Automatique - AY HR Management v1.1.4
# Pour Windows 10/11
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AIRBAND HR v1.1.4" -ForegroundColor White
Write-Host " Installation Automatique Windows" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérification des prérequis
Write-Host "[1/8] Vérification des prérequis..." -ForegroundColor Yellow
Write-Host ""

# Vérifier Python
Write-Host "  → Vérification de Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK ($pythonVersion)" -ForegroundColor Green
    } else {
        throw "Python non trouvé"
    }
} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python n'est pas installé ou n'est pas dans le PATH." -ForegroundColor Red
    Write-Host "Téléchargez Python 3.11+ depuis: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "IMPORTANT: Cochez 'Add Python to PATH' lors de l'installation" -ForegroundColor Yellow
    exit 1
}

# Vérifier Node.js
Write-Host "  → Vérification de Node.js..." -NoNewline
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK ($nodeVersion)" -ForegroundColor Green
    } else {
        throw "Node.js non trouvé"
    }
} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    Write-Host ""
    Write-Host "Node.js n'est pas installé." -ForegroundColor Red
    Write-Host "Téléchargez Node.js 18+ depuis: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Vérifier MariaDB/MySQL
Write-Host "  → Vérification de MariaDB..." -NoNewline
$mariadbService = Get-Service -Name "MariaDB*","MySQL*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($mariadbService) {
    Write-Host " OK" -ForegroundColor Green
    if ($mariadbService.Status -ne "Running") {
        Write-Host "    Démarrage du service..." -NoNewline
        Start-Service $mariadbService.Name
        Write-Host " OK" -ForegroundColor Green
    }
} else {
    Write-Host " ERREUR" -ForegroundColor Red
    Write-Host ""
    Write-Host "MariaDB n'est pas installé." -ForegroundColor Red
    Write-Host "Téléchargez MariaDB depuis: https://mariadb.org/download/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[2/8] Création de l'environnement Python..." -ForegroundColor Yellow
Write-Host ""

# Créer l'environnement virtuel
if (Test-Path "backend\.venv") {
    Write-Host "  → Environnement virtuel existant trouvé" -ForegroundColor Gray
} else {
    Write-Host "  → Création de l'environnement virtuel..." -NoNewline
    cd backend
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " ERREUR" -ForegroundColor Red
        exit 1
    }
    cd ..
}

Write-Host ""
Write-Host "[3/8] Installation des dépendances Python..." -ForegroundColor Yellow
Write-Host ""

cd backend
& .\.venv\Scripts\Activate.ps1
Write-Host "  → Mise à jour de pip..." -NoNewline
python -m pip install --upgrade pip --quiet
Write-Host " OK" -ForegroundColor Green

Write-Host "  → Installation des packages Python..." -NoNewline
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " ERREUR" -ForegroundColor Red
    deactivate
    cd ..
    exit 1
}
deactivate
cd ..

Write-Host ""
Write-Host "[4/8] Installation des dépendances Node.js..." -ForegroundColor Yellow
Write-Host ""

cd frontend
Write-Host "  → Installation des packages Node.js..." -NoNewline
npm install --silent 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " ERREUR" -ForegroundColor Red
    cd ..
    exit 1
}
cd ..

Write-Host ""
Write-Host "[5/8] Configuration de la base de données..." -ForegroundColor Yellow
Write-Host ""

# Demander les informations de connexion
Write-Host "  Veuillez fournir les informations de connexion MariaDB:" -ForegroundColor Cyan
Write-Host ""

$dbHost = Read-Host "  Hôte [localhost]"
if ([string]::IsNullOrWhiteSpace($dbHost)) { $dbHost = "localhost" }

$dbPort = Read-Host "  Port [3306]"
if ([string]::IsNullOrWhiteSpace($dbPort)) { $dbPort = "3306" }

$dbUser = Read-Host "  Utilisateur [root]"
if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = "root" }

$dbPassword = Read-Host "  Mot de passe" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
)

Write-Host ""
Write-Host "  → Test de connexion..." -NoNewline
try {
    mysql -h $dbHost -P $dbPort -u $dbUser -p"$dbPasswordPlain" -e "SELECT 1;" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        throw "Connexion échouée"
    }
} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    Write-Host "  Impossible de se connecter à la base de données." -ForegroundColor Red
    Write-Host "  Vérifiez vos identifiants et réessayez." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[6/8] Création des fichiers de configuration..." -ForegroundColor Yellow
Write-Host ""

# Générer une clé secrète
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Créer le fichier .env backend
Write-Host "  → Création de backend/.env..." -NoNewline
$envContent = @"
# Configuration Base de Données
DB_HOST=$dbHost
DB_PORT=$dbPort
DB_USER=$dbUser
DB_PASSWORD=$dbPasswordPlain
DB_NAME=ay_hr

# Configuration Sécurité
SECRET_KEY=$secretKey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Configuration Serveur
HOST=0.0.0.0
PORT=8000
"@
Set-Content -Path "backend\.env" -Value $envContent -Encoding UTF8
Write-Host " OK" -ForegroundColor Green

# Créer le fichier .env frontend
Write-Host "  → Création de frontend/.env..." -NoNewline
$frontendEnv = "VITE_API_URL=http://localhost:8000"
Set-Content -Path "frontend\.env" -Value $frontendEnv -Encoding UTF8
Write-Host " OK" -ForegroundColor Green

Write-Host ""
Write-Host "[7/8] Initialisation de la base de données..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  → Création de la base de données ay_hr..." -NoNewline
$sqlScript = Get-Content "database\create_database.sql" -Raw -Encoding UTF8
try {
    $sqlScript | mysql -h $dbHost -P $dbPort -u $dbUser -p"$dbPasswordPlain" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        throw "Erreur SQL"
    }
} catch {
    Write-Host " ERREUR" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Erreur lors de la création de la base de données." -ForegroundColor Red
    Write-Host "  Vérifiez que MariaDB est démarré et que les permissions sont correctes." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[8/8] Création des dossiers nécessaires..." -ForegroundColor Yellow
Write-Host ""

# Créer les dossiers
$folders = @("logs", "backups", "uploads")
foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        Write-Host "  → Création de $folder..." -NoNewline
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host " OK" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Installation Terminée avec Succès!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour démarrer l'application:" -ForegroundColor Cyan
Write-Host "  .\start-windows.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Pour installer comme service Windows:" -ForegroundColor Cyan
Write-Host "  .\install-service-windows.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Accès à l'application:" -ForegroundColor Cyan
Write-Host "  Interface Web    : http://localhost:3000" -ForegroundColor White
Write-Host "  API Backend      : http://localhost:8000" -ForegroundColor White
Write-Host "  Documentation API: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Identifiants par défaut:" -ForegroundColor Cyan
Write-Host "  Nom d'utilisateur: admin" -ForegroundColor White
Write-Host "  Mot de passe     : admin123" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANT: Changez le mot de passe admin dès la première connexion!" -ForegroundColor Yellow
Write-Host ""

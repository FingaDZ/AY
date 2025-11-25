# AY HR - Guide de Déploiement Windows 10/11

## Prérequis

- Windows 10/11 (64-bit)
- Droits administrateur
- Connexion Internet

## Installation des Dépendances

### 1. Python 3.11

**Télécharger et installer:**
1. Aller sur https://www.python.org/downloads/
2. Télécharger Python 3.11.x (dernière version)
3. **IMPORTANT**: Cocher "Add Python to PATH" pendant l'installation
4. Cliquer sur "Install Now"

**Vérifier l'installation:**
```powershell
python --version
# Devrait afficher: Python 3.11.x
```

### 2. Node.js 20.x

**Télécharger et installer:**
1. Aller sur https://nodejs.org/
2. Télécharger la version LTS (20.x)
3. Exécuter l'installateur avec les options par défaut

**Vérifier l'installation:**
```powershell
node --version
npm --version
```

### 3. MariaDB / MySQL

**Option A: MariaDB (Recommandé)**
1. Télécharger depuis https://mariadb.org/download/
2. Installer avec les options par défaut
3. Définir un mot de passe root pendant l'installation

**Option B: MySQL**
1. Télécharger depuis https://dev.mysql.com/downloads/installer/
2. Choisir "MySQL Installer for Windows"
3. Installer MySQL Server avec les options par défaut

**Vérifier l'installation:**
```powershell
mysql --version
```

## Installation de l'Application

### 1. Cloner le Repository

```powershell
# Installer Git si nécessaire
winget install Git.Git

# Cloner le projet
cd C:\
git clone https://github.com/FingaDZ/AY.git
cd AY
```

### 2. Configuration de la Base de Données

**Créer la base de données:**
```powershell
# Se connecter à MySQL/MariaDB
mysql -u root -p

# Dans MySQL:
CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ayhr_user'@'localhost' IDENTIFIED BY 'VotreMotDePasse';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Importer le schéma:**
```powershell
mysql -u ayhr_user -p ay_hr < database\create_database.sql
```

### 3. Configuration du Backend

```powershell
cd backend

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
@"
DATABASE_URL=mysql+pymysql://ayhr_user:VotreMotDePasse@localhost/ay_hr
SECRET_KEY=votre-cle-secrete-changez-moi
CORS_ORIGINS=http://localhost:3000
DEBUG=False
"@ | Out-File -FilePath .env -Encoding UTF8
```

### 4. Configuration du Frontend

```powershell
cd ..\frontend

# Installer les dépendances
npm install

# Créer le fichier .env (optionnel)
@"
VITE_API_URL=http://localhost:8000
"@ | Out-File -FilePath .env -Encoding UTF8
```

## Démarrage de l'Application

### Démarrage Manuel

**Terminal 1 - Backend:**
```powershell
cd C:\AY\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd C:\AY\frontend
npm run dev
```

### Démarrage Automatique (Script)

**Créer `start.ps1` à la racine:**
```powershell
@"
# Démarrer le backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Attendre 3 secondes
Start-Sleep -Seconds 3

# Démarrer le frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
"@ | Out-File -FilePath start.ps1 -Encoding UTF8
```

**Utilisation:**
```powershell
.\start.ps1
```

## Accès à l'Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

## Configuration en tant que Service Windows

### Utiliser NSSM (Non-Sucking Service Manager)

**1. Installer NSSM:**
```powershell
winget install NSSM.NSSM
```

**2. Créer le service Backend:**
```powershell
nssm install AY-HR-Backend "C:\AY\backend\venv\Scripts\python.exe" "-m uvicorn main:app --host 0.0.0.0 --port 8000"
nssm set AY-HR-Backend AppDirectory "C:\AY\backend"
nssm set AY-HR-Backend DisplayName "AY HR Backend API"
nssm set AY-HR-Backend Description "AY HR Management System - Backend API"
nssm set AY-HR-Backend Start SERVICE_AUTO_START
nssm start AY-HR-Backend
```

**3. Créer le service Frontend:**

Créer `frontend-service.js`:
```javascript
const { spawn } = require('child_process');
const http = require('http');

// Démarrer Vite en mode preview
const vite = spawn('npm', ['run', 'preview', '--', '--host', '0.0.0.0', '--port', '3000'], {
  cwd: 'C:\\AY\\frontend',
  shell: true
});

vite.stdout.on('data', (data) => console.log(data.toString()));
vite.stderr.on('data', (data) => console.error(data.toString()));

// Garder le processus actif
setInterval(() => {}, 1000);
```

```powershell
nssm install AY-HR-Frontend "C:\Program Files\nodejs\node.exe" "C:\AY\frontend-service.js"
nssm set AY-HR-Frontend AppDirectory "C:\AY\frontend"
nssm set AY-HR-Frontend DisplayName "AY HR Frontend"
nssm set AY-HR-Frontend Description "AY HR Management System - Frontend Web Interface"
nssm set AY-HR-Frontend Start SERVICE_AUTO_START
nssm start AY-HR-Frontend
```

## Gestion des Services

```powershell
# Démarrer
nssm start AY-HR-Backend
nssm start AY-HR-Frontend

# Arrêter
nssm stop AY-HR-Backend
nssm stop AY-HR-Frontend

# Redémarrer
nssm restart AY-HR-Backend
nssm restart AY-HR-Frontend

# Voir le statut
nssm status AY-HR-Backend
nssm status AY-HR-Frontend
```

## Mise à Jour de l'Application

```powershell
# Arrêter les services
nssm stop AY-HR-Backend
nssm stop AY-HR-Frontend

# Mettre à jour le code
cd C:\AY
git pull origin main

# Mettre à jour le backend
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Mettre à jour le frontend
cd ..\frontend
npm install
npm run build

# Redémarrer les services
nssm start AY-HR-Backend
nssm start AY-HR-Frontend
```

## Dépannage

### Port déjà utilisé
```powershell
# Trouver le processus utilisant le port 8000
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Erreur de connexion à la base de données
- Vérifier que MariaDB/MySQL est démarré
- Vérifier les credentials dans `.env`
- Tester la connexion: `mysql -u ayhr_user -p ay_hr`

### Module Python manquant
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Sauvegarde

### Base de Données
```powershell
# Créer un backup
mysqldump -u ayhr_user -p ay_hr > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Restaurer un backup
mysql -u ayhr_user -p ay_hr < backup_20251125_120000.sql
```

### Fichiers Application
```powershell
# Créer une archive
Compress-Archive -Path C:\AY -DestinationPath C:\Backups\AY_backup_$(Get-Date -Format 'yyyyMMdd').zip
```

---

**Version**: 1.1.5  
**Dernière mise à jour**: 25 novembre 2025  
**Support**: Documentation complète dans README.md

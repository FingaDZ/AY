# 🪟 Guide d'Installation Windows - AY HR System v3.6.0

## 📋 Table des Matières
1. [Prérequis](#prérequis)
2. [Installation Manuelle](#installation-manuelle)
3. [Configuration](#configuration)
4. [Démarrage](#démarrage)
5. [Dépannage](#dépannage)

---

## 🔧 Prérequis

### Logiciels Requis
- **Windows 10/11** (64-bit)
- **Python 3.11+** - [Télécharger](https://www.python.org/downloads/)
- **Node.js 20 LTS** - [Télécharger](https://nodejs.org/)
- **MySQL 8.0** ou **MariaDB 11.x** - [MySQL](https://dev.mysql.com/downloads/installer/) | [MariaDB](https://mariadb.org/download/)
- **Git** (optionnel) - [Télécharger](https://git-scm.com/download/win)

### Vérification des Versions
```powershell
python --version  # Doit afficher Python 3.11.x ou supérieur
node --version    # Doit afficher v20.x.x
npm --version     # Doit afficher 10.x.x ou supérieur
mysql --version   # Doit afficher 8.0.x ou MariaDB 11.x
```

---

## 📦 Installation Manuelle

### Étape 1: Préparation du Répertoire

```powershell
# Créer le répertoire d'installation
New-Item -ItemType Directory -Path "C:\AY-HR" -Force
Set-Location "C:\AY-HR"
```

### Étape 2: Téléchargement des Sources

**Option A: Depuis GitHub**
```powershell
git clone https://github.com/VotreOrg/ay-hr.git .
```

**Option B: Depuis Archive ZIP**
1. Télécharger le fichier ZIP depuis GitHub
2. Extraire dans `C:\AY-HR`

### Étape 3: Configuration MySQL

Ouvrir **MySQL Workbench** ou **MySQL Command Line**:

```sql
-- Créer la base de données
CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur
CREATE USER 'ayhr_user'@'localhost' IDENTIFIED BY 'VotreMotDePasse!2024';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';
FLUSH PRIVILEGES;
```

### Étape 4: Import du Schéma

```powershell
# Depuis PowerShell
cd C:\AY-HR\database
mysql -u ayhr_user -p ay_hr < schema.sql
```

### Étape 5: Configuration Backend

```powershell
cd C:\AY-HR\backend

# Créer environnement virtuel Python
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

**Créer le fichier `.env` dans `C:\AY-HR\backend\.env`:**

```env
DATABASE_URL=mysql+pymysql://ayhr_user:VotreMotDePasse!2024@localhost/ay_hr
SECRET_KEY=votre-cle-secrete-tres-longue-et-aleatoire
DEBUG=False
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ATTENDANCE_API_URL=http://localhost:8000/api
ATTENDANCE_API_TIMEOUT=30
```

**Générer une clé secrète:**
```powershell
# Depuis Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Étape 6: Création Utilisateur Admin

Créer `C:\AY-HR\backend\create_admin.py`:

```python
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from models.user import User
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Vérifier si admin existe
    admin = db.query(User).filter(User.email == "admin@ay-hr.com").first()
    
    if not admin:
        hashed_password = pwd_context.hash("Admin@2024!")
        admin = User(
            email="admin@ay-hr.com",
            nom="Admin",
            prenom="System",
            password_hash=hashed_password,
            role="Admin",
            actif=True
        )
        db.add(admin)
        db.commit()
        print("✅ Utilisateur admin créé: admin@ay-hr.com / Admin@2024!")
    else:
        print("ℹ️  L'utilisateur admin existe déjà")
    
    db.close()

if __name__ == "__main__":
    create_admin()
```

Exécuter:
```powershell
python create_admin.py
```

### Étape 7: Configuration Frontend

```powershell
cd C:\AY-HR\frontend

# Installer les dépendances
npm install

# Créer .env
New-Item -ItemType File -Path ".env" -Value "VITE_API_URL=http://localhost:8000"

# Build de production
npm run build
```

---

## 🚀 Démarrage

### Démarrage Manuel

**Terminal 1 - Backend:**
```powershell
cd C:\AY-HR\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend (Mode Dev):**
```powershell
cd C:\AY-HR\frontend
npm run dev
```

**OU Frontend (Mode Production avec Nginx):**
- Installer [Nginx for Windows](https://nginx.org/en/download.html)
- Configurer `nginx.conf` (voir section Nginx)
- Copier `C:\AY-HR\frontend\dist\*` vers `C:\nginx\html\`

### Démarrage Automatique (Windows Service)

**Option 1: NSSM (Recommandé)**

1. Télécharger [NSSM](https://nssm.cc/download)
2. Installer le service backend:

```powershell
# Installer NSSM
choco install nssm

# Créer le service backend
nssm install AYHRBackend "C:\AY-HR\backend\venv\Scripts\python.exe" `
  "-m uvicorn main:app --host 0.0.0.0 --port 8000"

nssm set AYHRBackend AppDirectory "C:\AY-HR\backend"
nssm set AYHRBackend DisplayName "AY HR Backend API"
nssm set AYHRBackend Description "AY HR Management System - Backend Service"
nssm set AYHRBackend Start SERVICE_AUTO_START

# Démarrer le service
nssm start AYHRBackend

# Vérifier le statut
nssm status AYHRBackend
```

**Option 2: Task Scheduler**

Créer une tâche planifiée:
```powershell
$action = New-ScheduledTaskAction -Execute "C:\AY-HR\backend\venv\Scripts\python.exe" `
  -Argument "-m uvicorn main:app --host 0.0.0.0 --port 8000" `
  -WorkingDirectory "C:\AY-HR\backend"

$trigger = New-ScheduledTaskTrigger -AtStartup

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount

Register-ScheduledTask -TaskName "AYHRBackend" -Action $action -Trigger $trigger `
  -Principal $principal -Description "AY HR Backend Service"
```

---

## 🌐 Configuration Nginx (Production)

Télécharger [Nginx for Windows](https://nginx.org/en/download.html)

**Éditer `C:\nginx\conf\nginx.conf`:**

```nginx
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;

    server {
        listen       80;
        server_name  localhost;

        # Frontend
        location / {
            root   C:/AY-HR/frontend/dist;
            index  index.html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api {
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

Démarrer Nginx:
```powershell
cd C:\nginx
start nginx
```

---

## 🔧 Dépannage

### Problème: Port déjà utilisé

**Backend (Port 8000):**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Frontend (Port 5173/3000):**
```powershell
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Problème: Erreur MySQL Connection

Vérifier:
1. MySQL/MariaDB est démarré:
   ```powershell
   Get-Service MySQL* | Start-Service
   ```

2. Credentials dans `.env`:
   ```powershell
   cat C:\AY-HR\backend\.env
   ```

3. Tester la connexion:
   ```powershell
   mysql -u ayhr_user -p ay_hr
   ```

### Problème: Module Python manquant

```powershell
cd C:\AY-HR\backend
.\venv\Scripts\Activate.ps1
pip install <nom-du-module>
```

### Problème: npm install échoue

```powershell
# Nettoyer le cache
npm cache clean --force

# Supprimer node_modules
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json

# Réinstaller
npm install
```

---

## 📊 Commandes Utiles

### Backend
```powershell
# Activer environnement
cd C:\AY-HR\backend
.\venv\Scripts\Activate.ps1

# Lancer en développement
uvicorn main:app --reload

# Lancer en production
uvicorn main:app --host 0.0.0.0 --port 8000

# Logs
# Vérifier C:\AY-HR\backend\logs\
```

### Frontend
```powershell
cd C:\AY-HR\frontend

# Mode développement
npm run dev

# Build production
npm run build

# Preview build
npm run preview
```

### Base de données
```powershell
# Backup
mysqldump -u ayhr_user -p ay_hr > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Restore
mysql -u ayhr_user -p ay_hr < backup_20241216_143000.sql

# Accès MySQL
mysql -u ayhr_user -p ay_hr
```

---

## 🔒 Sécurité

### Pare-feu Windows

```powershell
# Autoriser ports
New-NetFirewallRule -DisplayName "AY HR Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

### SSL/TLS (Optionnel)

1. Générer certificat auto-signé:
```powershell
$cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My"
```

2. Configurer Nginx avec HTTPS (voir documentation Nginx)

---

## 📝 Remarques

- **Antivirus**: Ajouter `C:\AY-HR` aux exclusions pour éviter les faux positifs
- **Windows Defender**: Autoriser Python, Node.js, et MySQL
- **Mises à jour**: Exécuter `git pull` régulièrement pour obtenir les dernières versions

---

## 🆘 Support

En cas de problème:
1. Vérifier les logs: `C:\AY-HR\backend\logs\`
2. Consulter la documentation: [INDEX_DOCUMENTATION.md](INDEX_DOCUMENTATION.md)
3. Contacter le support technique


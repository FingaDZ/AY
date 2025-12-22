# Guide de Préparation de l'Installateur NSIS
## AY HR System v3.6.0

Ce guide explique comment préparer et compiler l'installateur NSIS pour déployer AY HR System sur Windows.

---

## 📋 Prérequis

### 1. Installer NSIS
- Télécharger NSIS 3.x depuis: https://nsis.sourceforge.io/Download
- Installer avec les plugins par défaut
- Vérifier que `makensis.exe` est dans le PATH

### 2. Outils Nécessaires
- Python 3.11 (pour télécharger les packages)
- Node.js 18+ (pour compiler le frontend)
- Git Bash ou PowerShell
- 7-Zip pour la compression
- Connexion Internet (uniquement pour la préparation)

---

## 📦 Structure du Package

Créer la structure suivante dans `installer/package/` :

```
installer/
├── package/
│   ├── python/              # Python embarqué + packages
│   ├── nodejs/              # Node.js portable
│   ├── mariadb/             # MariaDB serveur
│   ├── nginx/               # Nginx serveur web
│   ├── nssm/                # NSSM service manager
│   ├── backend/             # Code backend
│   ├── frontend/            # Code frontend (source)
│   ├── frontend-dist/       # Frontend compilé
│   ├── database/            # Scripts SQL
│   ├── nginx-config/        # Configuration Nginx
│   └── resources/           # Icônes et images
├── scripts/                 # Scripts d'installation (déjà créés)
├── ayhr_installer.nsi       # Script NSIS principal (déjà créé)
└── build_package.ps1        # Script de préparation (à créer)
```

---

## 🔧 Étapes de Préparation

### ÉTAPE 1: Télécharger Python Embedded

```powershell
# Créer le dossier
New-Item -ItemType Directory -Force -Path "installer\package\python"
cd installer\package\python

# Télécharger Python 3.11 Embedded (Windows x64)
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip" -OutFile "python-embed.zip"

# Extraire
Expand-Archive -Path "python-embed.zip" -DestinationPath "." -Force
Remove-Item "python-embed.zip"

# Télécharger get-pip.py
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "get-pip.py"

# Installer pip
.\python.exe get-pip.py

# Modifier python311._pth pour activer site-packages
$pthFile = Get-Content "python311._pth"
$pthFile = $pthFile -replace "#import site", "import site"
Set-Content "python311._pth" $pthFile
```

### ÉTAPE 2: Télécharger les Packages Python

```powershell
# Créer le dossier packages
New-Item -ItemType Directory -Force -Path "packages"

# Télécharger tous les packages avec leurs dépendances
.\python.exe -m pip download -r ..\..\..\backend\requirements.txt -d packages

# Les packages seront installés offline pendant l'installation
```

### ÉTAPE 3: Télécharger Node.js Portable

```powershell
# Retour à installer/package
cd ..

# Télécharger Node.js portable
New-Item -ItemType Directory -Force -Path "nodejs"
cd nodejs

Invoke-WebRequest -Uri "https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip" -OutFile "nodejs.zip"
Expand-Archive -Path "nodejs.zip" -DestinationPath "." -Force

# Déplacer les fichiers à la racine
Move-Item "node-v20.11.0-win-x64\*" "." -Force
Remove-Item "node-v20.11.0-win-x64" -Recurse
Remove-Item "nodejs.zip"
```

### ÉTAPE 4: Compiler le Frontend

```powershell
cd ..\..\..\frontend

# Installer les dépendances
npm install

# Compiler pour la production
npm run build

# Copier le build dans le package
Copy-Item -Recurse "dist\*" "..\installer\package\frontend-dist\" -Force
```

### ÉTAPE 5: Télécharger MariaDB

```powershell
cd ..\installer\package

# Télécharger MariaDB 10.11 (version portable)
New-Item -ItemType Directory -Force -Path "mariadb"
cd mariadb

# URL: https://mariadb.org/download/?t=mariadb&p=mariadb&r=10.11.6&os=windows&cpu=x86_64&pkg=zip
$mariadbUrl = "https://archive.mariadb.org/mariadb-10.11.6/winx64-packages/mariadb-10.11.6-winx64.zip"
Invoke-WebRequest -Uri $mariadbUrl -OutFile "mariadb.zip"

# Extraire
Expand-Archive -Path "mariadb.zip" -DestinationPath "." -Force
Move-Item "mariadb-10.11.6-winx64\*" "." -Force
Remove-Item "mariadb-10.11.6-winx64" -Recurse
Remove-Item "mariadb.zip"

# Créer le fichier de configuration my.ini
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
"@ | Out-File -FilePath "my.ini" -Encoding UTF8
```

### ÉTAPE 6: Télécharger Nginx

```powershell
cd ..

# Télécharger Nginx pour Windows
New-Item -ItemType Directory -Force -Path "nginx"
cd nginx

Invoke-WebRequest -Uri "http://nginx.org/download/nginx-1.24.0.zip" -OutFile "nginx.zip"
Expand-Archive -Path "nginx.zip" -DestinationPath "." -Force
Move-Item "nginx-1.24.0\*" "." -Force
Remove-Item "nginx-1.24.0" -Recurse
Remove-Item "nginx.zip"
```

### ÉTAPE 7: Créer la Configuration Nginx

```powershell
cd ..
New-Item -ItemType Directory -Force -Path "nginx-config"

# Créer nginx.conf
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

        # Frontend
        location / {
            root ../../frontend/dist;
            index index.html;
            try_files `$uri `$uri/ /index.html;
        }

        # Backend API
        location /api {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }

        # Documentation API
        location /docs {
            proxy_pass http://127.0.0.1:8000;
        }

        location /redoc {
            proxy_pass http://127.0.0.1:8000;
        }

        # Static files
        location /static {
            proxy_pass http://127.0.0.1:8000;
        }
    }
}
"@ | Out-File -FilePath "nginx-config\nginx.conf" -Encoding UTF8
```

### ÉTAPE 8: Télécharger NSSM

```powershell
cd package

# Télécharger NSSM (Non-Sucking Service Manager)
New-Item -ItemType Directory -Force -Path "nssm"
cd nssm

Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "nssm.zip"
Expand-Archive -Path "nssm.zip" -DestinationPath "." -Force

# Copier l'exécutable 64-bit
Copy-Item "nssm-2.24\win64\nssm.exe" "." -Force
Remove-Item "nssm-2.24" -Recurse
Remove-Item "nssm.zip"
```

### ÉTAPE 9: Copier le Code Source

```powershell
cd ..

# Copier le backend
Copy-Item -Recurse "..\..\backend" "backend" -Force -Exclude @("__pycache__", "*.pyc", ".env", "venv", "data")

# Copier le frontend source
Copy-Item -Recurse "..\..\frontend" "frontend" -Force -Exclude @("node_modules", "dist", ".env")

# Copier la base de données
Copy-Item -Recurse "..\..\database" "database" -Force

# Copier les scripts
Copy-Item "..\..\*.bat" "." -Force
Copy-Item "..\..\*.ps1" "." -Force
Copy-Item "..\..\*.md" "." -Force
Copy-Item "..\..\docker-compose.yml" "." -Force
Copy-Item "..\..\ecosystem.config.js" "." -Force

# Copier .env.example
Copy-Item "..\..\backend\.env.example" ".env.example" -Force
```

### ÉTAPE 10: Créer les Ressources (Icônes)

```powershell
cd ..
New-Item -ItemType Directory -Force -Path "resources"

# Vous devez créer ou copier les icônes suivantes:
# - app.ico (icône principale)
# - header.bmp (150x57 pixels)
# - wizard.bmp (164x314 pixels)
# - start.ico
# - stop.ico
# - logs.ico
# - config.ico
# - uninstall.ico
```

**Note**: Vous pouvez créer des icônes simples avec des outils en ligne ou utiliser des icônes par défaut.

### ÉTAPE 11: Créer LICENSE.txt

```powershell
@"
AY HR SYSTEM - CONTRAT DE LICENCE

Copyright (c) 2025 AY Company

Ce logiciel est fourni "tel quel", sans garantie d'aucune sorte.
L'utilisation de ce logiciel est soumise aux termes et conditions suivants:

1. Le logiciel est destiné à un usage interne uniquement.
2. Aucune redistribution n'est autorisée sans autorisation écrite.
3. Le support technique est fourni selon les termes du contrat de service.

Pour plus d'informations, contactez: support@aycompany.dz
"@ | Out-File -FilePath "resources\LICENSE.txt" -Encoding UTF8
```

---

## 🏗️ Compilation de l'Installateur

### Option 1: Compiler avec l'IDE NSIS

1. Ouvrir NSIS (HM NIS Edit ou NSIS Menu)
2. Compiler `ayhr_installer.nsi`
3. L'exécutable sera créé: `AY_HR_Setup_v3.6.0.exe`

### Option 2: Compiler en ligne de commande

```powershell
# Depuis le dossier installer/
& "C:\Program Files (x86)\NSIS\makensis.exe" ayhr_installer.nsi
```

---

## 📏 Taille Estimée du Package

- Python Embedded + Packages: ~150 MB
- Node.js Portable: ~50 MB
- MariaDB: ~200 MB
- Nginx: ~15 MB
- NSSM: ~1 MB
- Code source: ~10 MB
- Frontend compilé: ~5 MB

**TOTAL: ~430 MB (package non compressé)**
**Installateur final (avec compression NSIS): ~200-250 MB**

---

## ✅ Checklist Avant Compilation

- [ ] Python 3.11 embarqué téléchargé
- [ ] Tous les packages Python téléchargés (offline)
- [ ] Node.js portable téléchargé
- [ ] Frontend compilé (npm run build)
- [ ] MariaDB téléchargé et configuré
- [ ] Nginx téléchargé
- [ ] Configuration Nginx créée
- [ ] NSSM téléchargé
- [ ] Code backend copié (sans __pycache__)
- [ ] Scripts SQL copiés
- [ ] Icônes créées (ou par défaut)
- [ ] LICENSE.txt créé
- [ ] .env.example copié
- [ ] NSIS installé sur la machine de build

---

## 🚀 Test de l'Installateur

1. **Tester sur une VM Windows propre** (sans Python, Node, MySQL)
2. **Exécuter l'installateur** en tant qu'administrateur
3. **Vérifier les services**:
   ```cmd
   sc query AYHR_MySQL
   sc query AYHR_Backend
   sc query AYHR_Nginx
   ```
4. **Tester l'application**: http://localhost
5. **Vérifier la désinstallation**

---

## 🔧 Dépannage

### Problème: Python ne trouve pas les modules
**Solution**: Vérifier que `python311._pth` contient `import site` (sans #)

### Problème: MariaDB ne démarre pas
**Solution**: Vérifier les permissions sur `data/mysql` et le port 3307

### Problème: Backend ne démarre pas
**Solution**: Vérifier les logs dans `logs/backend_error.log`

### Problème: Nginx erreur 502
**Solution**: Vérifier que le backend est bien démarré sur le port 8000

---

## 📝 Notes Importantes

1. **Tous les téléchargements doivent être faits AVANT la compilation**
2. **Testez l'installateur sur une machine propre** (VM recommandée)
3. **La compilation nécessite ~1 GB d'espace disque**
4. **Le processus de préparation prend environ 30-45 minutes**
5. **Gardez une copie du package pour les futures versions**

---

## 📧 Support

Pour toute question sur la préparation de l'installateur:
- Documentation: README.md
- Email: support@aycompany.dz

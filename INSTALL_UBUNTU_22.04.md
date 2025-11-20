# Installation AY HR sur Ubuntu 22.04 - Guide Complet

## 📋 Vue d'ensemble

Ce guide vous accompagne dans l'installation complète d'AY HR Management sur Ubuntu 22.04, avec configuration du démarrage automatique au boot.

**Durée estimée** : 30-45 minutes  
**Niveau** : Intermédiaire

---

## ✅ Prérequis

- Ubuntu 22.04 LTS fraîchement installé
- Accès root ou sudo
- Connexion Internet stable
- 2 GB RAM minimum, 4 GB recommandé
- 10 GB d'espace disque

---

## 🚀 Installation Rapide (Recommandée)

### Étape 1 : Télécharger et Extraire le Package

```bash
# Télécharger le package depuis GitHub
wget https://github.com/FingaDZ/AY/releases/download/v1.1.4/ay-hr-v1.1.4-linux.tar.gz

# Extraire dans /opt (recommandé pour les applications)
sudo mkdir -p /opt/ay-hr
sudo tar -xzf ay-hr-v1.1.4-linux.tar.gz -C /opt/ay-hr --strip-components=1

# Naviguer vers le dossier
cd /opt/ay-hr
```

### Étape 2 : Lancer l'Installation Automatique

```bash
# Rendre le script exécutable
sudo chmod +x install-linux.sh

# Lancer l'installation
sudo ./install-linux.sh
```

Le script va automatiquement :
- ✓ Installer Python 3.11, Node.js 18, MariaDB
- ✓ Créer l'environnement virtuel Python
- ✓ Installer toutes les dépendances
- ✓ Configurer la base de données
- ✓ Créer les fichiers .env

### Étape 3 : Installer comme Service (Auto-démarrage)

```bash
# Installer les services systemd
sudo chmod +x install-service-linux.sh
sudo ./install-service-linux.sh
```

Les services seront automatiquement démarrés au boot du système.

### Étape 4 : Vérifier l'Installation

```bash
# Vérifier les services
sudo systemctl status ayhr-backend
sudo systemctl status ayhr-frontend

# Accéder à l'application
# Frontend : http://localhost:3000
# Backend API : http://localhost:8000/docs
# Login : admin / admin123
```

---

## 📦 Installation Manuelle (Étape par Étape)

Si vous préférez comprendre chaque étape ou personnaliser l'installation.

### 1. Mise à Jour du Système

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y software-properties-common apt-transport-https ca-certificates curl wget git
```

### 2. Installation de Python 3.11

```bash
# Ajouter le PPA deadsnakes
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Installer Python 3.11 et outils
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Vérifier
python3 --version  # Doit afficher Python 3.11.x
```

### 3. Installation de Node.js 20 LTS

```bash
# Corriger l'erreur apt_pkg si nécessaire
sudo apt install --reinstall python3-apt -y

# Télécharger et installer NodeSource repository (Node.js 20 LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Installer Node.js
sudo apt install -y nodejs

# Vérifier
node --version  # Doit afficher v20.x.x
npm --version   # Doit afficher 10.x.x
```

**Note** : Node.js 18 n'est plus supporté. Nous utilisons Node.js 20 LTS.

### 4. Installation de MariaDB 10.11

```bash
# Installer MariaDB
sudo apt install -y mariadb-server mariadb-client

# Démarrer MariaDB
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Sécuriser l'installation
sudo mysql_secure_installation
```

**Configuration mysql_secure_installation** :
- Switch to unix_socket authentication? **N**
- Change root password? **Y** → Entrer un mot de passe fort
- Remove anonymous users? **Y**
- Disallow root login remotely? **Y**
- Remove test database? **Y**
- Reload privilege tables? **Y**

### 5. Créer l'Utilisateur de Base de Données

```bash
sudo mysql -u root -p
```

Dans le prompt MySQL :

```sql
-- Créer la base de données
CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur dédié
CREATE USER 'ayhr_user'@'localhost' IDENTIFIED BY 'VotreMotDePasseSecurise';

-- Donner tous les privilèges
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Quitter
EXIT;
```

### 6. Configuration du Projet

```bash
# Créer le dossier d'installation
sudo mkdir -p /opt/ay-hr
cd /opt/ay-hr

# Si vous avez le package, extraire ici
# Sinon, cloner depuis Git
sudo git clone https://github.com/FingaDZ/AY.git .

# Rendre les scripts exécutables
sudo chmod +x *.sh

# Corriger les permissions (important !)
sudo chown -R $USER:$USER /opt/ay-hr

# Créer l'environnement virtuel Python
cd /opt/ay-hr/backend
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances Python
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

### 7. Installer les Dépendances Frontend

```bash
cd /opt/ay-hr/frontend
npm install
```

### 8. Configuration des Variables d'Environnement

**Backend (.env)** :

```bash
cd /opt/ay-hr/backend
nano .env
```

Contenu :

```env
# Base de données
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=ay_hr
DATABASE_USER=ayhr_user
DATABASE_PASSWORD=VotreMotDePasseSecurise

# Sécurité (générer une clé aléatoire)
SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire_minimum_32_caracteres

# Server
HOST=0.0.0.0
PORT=8000

# CORS
FRONTEND_URL=http://localhost:3000
```

**Générer un SECRET_KEY** :

```bash
openssl rand -hex 32
```

**Frontend (.env)** :

```bash
cd /opt/ay-hr/frontend
nano .env
```

Contenu :

```env
VITE_API_URL=http://localhost:8000
```

### 9. Initialiser la Base de Données

```bash
cd /opt/ay-hr
mysql -u ayhr_user -p ay_hr < database/create_database.sql
```

Entrer le mot de passe de `ayhr_user`.

### 10. Créer les Dossiers Nécessaires

```bash
cd /opt/ay-hr
mkdir -p logs backups uploads

# Corriger toutes les permissions
sudo chown -R $USER:$USER /opt/ay-hr
chmod +x /opt/ay-hr/*.sh

# Vérifier les permissions
ls -la /opt/ay-hr/*.sh
```

---

## 🔧 Configuration des Services Systemd

### Créer le Service Backend

```bash
sudo nano /etc/systemd/system/ayhr-backend.service
```

Contenu :

```ini
[Unit]
Description=AY HR Management - Backend API
After=network.target mariadb.service
Wants=mariadb.service

[Service]
Type=simple
User=votreuser
WorkingDirectory=/opt/ay-hr/backend
Environment="PATH=/opt/ay-hr/backend/.venv/bin"
ExecStart=/opt/ay-hr/backend/.venv/bin/python start_clean.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/ay-hr/logs/backend.log
StandardError=append:/opt/ay-hr/logs/backend.log

# Limites de ressources
LimitNOFILE=65535
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

**Remplacer** `votreuser` par votre nom d'utilisateur (obtenir avec `whoami`).

### Créer le Service Frontend

```bash
sudo nano /etc/systemd/system/ayhr-frontend.service
```

Contenu :

```ini
[Unit]
Description=AY HR Management - Frontend Web Interface
After=network.target ayhr-backend.service
Wants=ayhr-backend.service

[Service]
Type=simple
User=votreuser
WorkingDirectory=/opt/ay-hr/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=10
StandardOutput=append:/opt/ay-hr/logs/frontend.log
StandardError=append:/opt/ay-hr/logs/frontend.log

# Limites de ressources
LimitNOFILE=65535
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### Activer et Démarrer les Services

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer les services (démarrage automatique)
sudo systemctl enable ayhr-backend
sudo systemctl enable ayhr-frontend

# Démarrer les services
sudo systemctl start ayhr-backend
sudo systemctl start ayhr-frontend

# Vérifier le statut
sudo systemctl status ayhr-backend
sudo systemctl status ayhr-frontend
```

---

## 🔥 Configuration du Pare-feu

```bash
# Installer UFW si non installé
sudo apt install -y ufw

# Autoriser SSH (important !)
sudo ufw allow 22/tcp

# Autoriser les ports de l'application
sudo ufw allow 8000/tcp  # Backend
sudo ufw allow 3000/tcp  # Frontend

# Activer le pare-feu
sudo ufw enable

# Vérifier
sudo ufw status
```

---

## 🌐 Accès Réseau (Depuis d'Autres Machines)

### Option 1 : Accès Direct (Développement)

Si vous voulez accéder depuis d'autres machines du réseau local :

**Backend** : Déjà configuré (HOST=0.0.0.0)

**Frontend** : Modifier vite.config.js

```bash
nano /opt/ay-hr/frontend/vite.config.js
```

Ajouter dans `server` :

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Écouter sur toutes les interfaces
    port: 3000,
    strictPort: true,
  }
})
```

Redémarrer :

```bash
sudo systemctl restart ayhr-frontend
```

### Option 2 : Nginx Reverse Proxy (Production)

**Installer Nginx** :

```bash
sudo apt install -y nginx
```

**Configurer** :

```bash
sudo nano /etc/nginx/sites-available/ayhr
```

Contenu :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;  # ou adresse IP

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Activer** :

```bash
sudo ln -s /etc/nginx/sites-available/ayhr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Autoriser HTTP** :

```bash
sudo ufw allow 'Nginx Full'
```

---

## 📊 Sauvegardes Automatiques

### Script de Sauvegarde

```bash
sudo nano /opt/ay-hr/backup.sh
```

Contenu :

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/opt/ay-hr/backups"
DB_USER="ayhr_user"
DB_PASS="VotreMotDePasseSecurise"
DB_NAME="ay_hr"

# Créer la sauvegarde
mysqldump -u $DB_USER -p$DB_PASS \
    --single-transaction \
    --routines \
    --triggers \
    $DB_NAME | gzip > "$BACKUP_DIR/ay_hr_$TIMESTAMP.sql.gz"

# Nettoyer les anciennes sauvegardes (garder 30 jours)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Sauvegarde créée : ay_hr_$TIMESTAMP.sql.gz"
```

**Rendre exécutable** :

```bash
sudo chmod +x /opt/ay-hr/backup.sh
```

### Planifier avec Cron

```bash
sudo crontab -e
```

Ajouter :

```bash
# Sauvegarde quotidienne à 2h du matin
0 2 * * * /opt/ay-hr/backup.sh >> /opt/ay-hr/logs/backup.log 2>&1
```

---

## 📝 Commandes Utiles

### Gestion des Services

```bash
# Démarrer
sudo systemctl start ayhr-backend ayhr-frontend

# Arrêter
sudo systemctl stop ayhr-backend ayhr-frontend

# Redémarrer
sudo systemctl restart ayhr-backend ayhr-frontend

# Statut
sudo systemctl status ayhr-backend ayhr-frontend

# Voir les logs en temps réel
sudo journalctl -u ayhr-backend -f
sudo journalctl -u ayhr-frontend -f

# Logs sauvegardés
tail -f /opt/ay-hr/logs/backend.log
tail -f /opt/ay-hr/logs/frontend.log
```

### Tests de Connexion

```bash
# Tester le backend
curl http://localhost:8000/docs

# Tester la base de données
mysql -u ayhr_user -p ay_hr -e "SELECT COUNT(*) FROM users;"
```

---

## 🔍 Dépannage

### Problème apt_pkg (ModuleNotFoundError)

```bash
# Solution 1 : Réinstaller python3-apt
sudo apt install --reinstall python3-apt -y

# Solution 2 : Si la solution 1 ne fonctionne pas
sudo apt remove --purge python3-apt -y
sudo apt install python3-apt -y

# Vérifier
python3 -c "import apt_pkg; print('OK')"
```

### Scripts Non Exécutables (Permission Denied)

```bash
# Rendre tous les scripts exécutables
cd /opt/ay-hr
chmod +x *.sh

# Vérifier
ls -la *.sh
```

### Script Refuse de S'exécuter en Root

```bash
# NE PAS utiliser sudo pour install-linux.sh
# Le script détecte automatiquement s'il est en root

# Si vous êtes connecté en tant que root, créer un utilisateur
adduser ayhr
usermod -aG sudo ayhr

# Changer de propriétaire
chown -R ayhr:ayhr /opt/ay-hr

# Se connecter avec le nouvel utilisateur
su - ayhr
cd /opt/ay-hr
./install-linux.sh
```

### Service ne Démarre Pas

```bash
# Voir les erreurs détaillées
sudo journalctl -u ayhr-backend -n 50 --no-pager
sudo journalctl -u ayhr-frontend -n 50 --no-pager

# Tester manuellement
cd /opt/ay-hr/backend
source .venv/bin/activate
python start_clean.py
```

### Erreur de Connexion Base de Données

```bash
# Tester la connexion
mysql -u ayhr_user -p ay_hr

# Vérifier que MariaDB est démarré
sudo systemctl status mariadb

# Redémarrer MariaDB
sudo systemctl restart mariadb
```

### Port Déjà Utilisé

```bash
# Trouver le processus
sudo lsof -i :8000
sudo lsof -i :3000

# Tuer le processus
sudo kill -9 <PID>
```

### Erreur de Permissions

```bash
# Corriger les permissions
sudo chown -R $USER:$USER /opt/ay-hr
chmod +x /opt/ay-hr/*.sh
```

---

## 🔐 Sécurité Post-Installation

### 1. Changer le Mot de Passe Admin

Première connexion :
- Login : **admin**
- Mot de passe : **admin123**

**IMPORTANT** : Changer immédiatement ce mot de passe !

### 2. Configurer SSH (si accès distant)

```bash
sudo nano /etc/ssh/sshd_configroot@AIRBAND-HR:/opt/ay-hr# journalctl -u ayhr-backend -f


```

Recommandations :
- `PermitRootLogin no`
- `PasswordAuthentication no` (utiliser des clés SSH)
- `Port 2222` (changer le port par défaut)

```bash
sudo systemctl restart sshd
```

### 3. Configurer fail2ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📈 Monitoring et Performance

### Installer htop

```bash
sudo apt install -y htop
htop
```

### Vérifier l'Utilisation

```bash
# CPU et mémoire
top

# Espace disque
df -h

# Processus de l'application
ps aux | grep -E "python|node"
```

---

## ✅ Checklist Post-Installation

- [ ] Système à jour (apt update && apt upgrade)
- [ ] Python 3.11 installé
- [ ] Node.js 18 installé
- [ ] MariaDB configuré et sécurisé
- [ ] Base de données `ay_hr` créée
- [ ] Utilisateur `ayhr_user` créé avec privilèges
- [ ] Dépendances backend installées
- [ ] Dépendances frontend installées
- [ ] Fichiers .env configurés (backend et frontend)
- [ ] SECRET_KEY généré (32+ caractères)
- [ ] Base de données initialisée (SQL importé)
- [ ] Services systemd créés et activés
- [ ] Services démarrés avec succès
- [ ] Pare-feu configuré (UFW)
- [ ] Application accessible (http://localhost:3000)
- [ ] Mot de passe admin changé
- [ ] Sauvegardes automatiques configurées
- [ ] Documentation lue

---

## 🎉 Installation Terminée !

Votre système AY HR Management est maintenant installé et configuré pour démarrer automatiquement au boot.

**Accès** :
- Frontend : http://localhost:3000 (ou http://votre-ip:3000)
- Backend API : http://localhost:8000/docs
- Login : admin / admin123 (à changer !)

**Support** :
- Documentation : `/opt/ay-hr/INSTALLATION_GUIDE.md`
- Guide Admin : `/opt/ay-hr/ADMIN_GUIDE.md`
- Logs : `/opt/ay-hr/logs/`

---

**Version** : 1.1.4  
**Date** : Novembre 2025  
**Plateforme** : Ubuntu 22.04 LTS

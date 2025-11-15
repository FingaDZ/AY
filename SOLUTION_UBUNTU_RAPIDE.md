# 🔧 Solution Rapide - Votre Installation Ubuntu

## ⚠️ Problèmes Identifiés

1. **Erreur apt_pkg** - Module Python manquant
2. **Node.js 12** - Version obsolète (besoin de 18+ ou 20 LTS)
3. **Scripts non exécutables** - Permissions manquantes
4. **Connexion root** - Le script refuse root

---

## ✅ Solution Immédiate

### Étape 1 : Corriger apt_pkg et Node.js

```bash
# Corriger apt_pkg
sudo apt install --reinstall python3-apt -y

# Supprimer l'ancien Node.js
sudo apt remove nodejs nodejs-doc libnode72 -y
sudo apt autoremove -y

# Installer Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Vérifier
node --version   # v20.x.x
npm --version    # 10.x.x
```

### Étape 2 : Corriger les Permissions

```bash
# Aller dans le dossier du projet
cd /opt/ay-hr

# Rendre TOUS les scripts exécutables
chmod +x *.sh

# Vérifier
ls -la *.sh
```

### Étape 3 : Créer un Utilisateur (Si vous êtes root)

**Le script install-linux.sh refuse de s'exécuter en tant que root !**

```bash
# Créer un utilisateur
adduser ayhr
# (Entrer un mot de passe)

# Ajouter aux sudoers
usermod -aG sudo ayhr

# Changer le propriétaire du dossier
chown -R ayhr:ayhr /opt/ay-hr

# Se connecter avec le nouvel utilisateur
su - ayhr

# Aller dans le dossier
cd /opt/ay-hr
```

### Étape 4 : Installation Manuelle Complète

**Option A : Si vous avez créé un utilisateur non-root**

```bash
# Utiliser le script automatique
cd /opt/ay-hr
./install-linux.sh
```

**Option B : Installation manuelle complète**

```bash
# 1. Backend - Environnement virtuel
cd /opt/ay-hr/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 2. Frontend - Dépendances
cd /opt/ay-hr/frontend
npm install

# 3. Configuration Backend (.env)
cd /opt/ay-hr/backend
cat > .env << 'EOF'
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=ay_hr
DATABASE_USER=ayhr_user
DATABASE_PASSWORD=VotreMotDePasse
SECRET_KEY=$(openssl rand -hex 32)
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000
EOF

# Générer et remplacer SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/\$(openssl rand -hex 32)/$SECRET_KEY/" .env

# 4. Configuration Frontend (.env)
cd /opt/ay-hr/frontend
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF

# 5. Créer la base de données (si pas encore fait)
sudo mysql -u root -p << 'EOF'
CREATE DATABASE IF NOT EXISTS ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'ayhr_user'@'localhost' IDENTIFIED BY 'VotreMotDePasse';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
EOF

# 6. Initialiser la base de données
mysql -u ayhr_user -p ay_hr < /opt/ay-hr/database/create_database.sql

# 7. Créer les dossiers
cd /opt/ay-hr
mkdir -p logs backups uploads

# 8. Démarrer l'application
cd /opt/ay-hr
./start-linux.sh
```

---

## 🚀 Démarrage Rapide

### Démarrage Manuel

```bash
# Terminal 1 - Backend
cd /opt/ay-hr/backend
source .venv/bin/activate
python start_clean.py

# Terminal 2 - Frontend
cd /opt/ay-hr/frontend
npm run dev
```

### Accès

- Frontend : http://localhost:3000
- Backend API : http://localhost:8000/docs
- Login : admin / admin123

---

## 🔧 Installation comme Service

Une fois que l'application fonctionne manuellement :

```bash
cd /opt/ay-hr
sudo ./install-service-linux.sh
```

Cela créera les services systemd pour démarrage automatique.

---

## 📋 Checklist de Vérification

Avant de continuer, vérifiez :

```bash
# Python 3.11
python3 --version
# Doit afficher : Python 3.11.x

# Node.js 20
node --version
# Doit afficher : v20.x.x

# npm
npm --version
# Doit afficher : 10.x.x

# MariaDB
sudo systemctl status mariadb
# Doit être : active (running)

# Scripts exécutables
ls -la /opt/ay-hr/*.sh
# Tous doivent avoir -rwxr-xr-x
```

---

## ⚡ Script de Correction Automatique

J'ai créé un script qui corrige automatiquement tout :

```bash
cd /opt/ay-hr

# Rendre le script exécutable
chmod +x fix-ubuntu-install.sh

# Exécuter (PAS en root !)
./fix-ubuntu-install.sh
```

Le script va :
- Corriger apt_pkg
- Installer Node.js 20 LTS
- Corriger les permissions
- Vérifier la structure du projet
- Donner les prochaines étapes

---

## 🆘 Problèmes Persistants ?

### Erreur "command not found" pour npm

```bash
# Vérifier le PATH
echo $PATH

# Ajouter Node.js au PATH si nécessaire
export PATH="/usr/bin:$PATH"

# Vérifier
which npm
```

### apt_pkg toujours problématique

```bash
# Solution radicale
sudo apt remove --purge python3-apt -y
sudo apt install python3-apt -y

# Vérifier
python3 -c "import apt_pkg; print('OK')"
```

### Base de données non créée

```bash
# Tester la connexion
mysql -u root -p

# Dans MySQL, créer manuellement
CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ayhr_user'@'localhost' IDENTIFIED BY 'MotDePasse123!';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Importer le schéma
mysql -u ayhr_user -pMotDePasse123! ay_hr < database/create_database.sql
```

---

## 📞 Commandes Utiles

```bash
# Voir les logs en temps réel
tail -f /opt/ay-hr/logs/backend.log
tail -f /opt/ay-hr/logs/frontend.log

# Tester le backend
curl http://localhost:8000/docs

# Tester la base de données
mysql -u ayhr_user -p ay_hr -e "SELECT COUNT(*) FROM users;"

# Voir les processus
ps aux | grep -E "python|node"

# Arrêter tout
pkill -f "python start_clean.py"
pkill -f "npm run dev"
```

---

**Date** : 15 novembre 2025  
**Version** : 1.1.4

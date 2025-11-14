# 📦 Guide d'Installation - AIRBAND HR v1.1.4

## 🎯 Guide Simple pour Débutants

Ce guide vous permettra d'installer le système de gestion RH AY HR sur votre ordinateur Windows ou Linux, même si vous n'avez jamais installé ce type de logiciel.

---

## 📋 Ce dont vous avez besoin

### Pour Windows
- Un ordinateur Windows 10 ou 11
- Une connexion Internet
- 30 minutes de temps
- Droits administrateur sur votre ordinateur

### Pour Linux (Ubuntu/Debian)
- Un ordinateur Ubuntu 20.04 ou plus récent
- Une connexion Internet
- 30 minutes de temps
- Accès sudo

---

## 🪟 INSTALLATION WINDOWS (Étape par Étape)

### Étape 1 : Télécharger les logiciels nécessaires

1. **Python 3.11** (Le moteur du système)
   - Allez sur : https://www.python.org/downloads/
   - Téléchargez Python 3.11 ou plus récent
   - **IMPORTANT** : Lors de l'installation, cochez "Add Python to PATH"
   - Cliquez sur "Install Now"

2. **Node.js 18** (Pour l'interface web)
   - Allez sur : https://nodejs.org/
   - Téléchargez la version LTS (recommandée)
   - Installez avec les options par défaut

3. **MariaDB 10.11** (La base de données)
   - Allez sur : https://mariadb.org/download/
   - Téléchargez MariaDB 10.11
   - Lors de l'installation :
     - Définissez un mot de passe root (NOTEZ-LE !)
     - Cochez "Enable networking"
     - Port par défaut : 3306

### Étape 2 : Préparer le logiciel AY HR

1. **Extraire le fichier**
   - Double-cliquez sur `ay-hr-v1.1.4-windows.zip`
   - Extrayez dans `C:\AY-HR`

2. **Ouvrir PowerShell en tant qu'Administrateur**
   - Cliquez sur Démarrer
   - Tapez "PowerShell"
   - Clic droit → "Exécuter en tant qu'administrateur"

### Étape 3 : Installer automatiquement

```powershell
# Aller dans le dossier du logiciel
cd C:\AY-HR

# Autoriser l'exécution des scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Lancer l'installation automatique
.\install-windows.ps1
```

Le script va vous demander :
- **Hôte MariaDB** : Appuyez sur Entrée (utilise "localhost")
- **Port** : Appuyez sur Entrée (utilise "3306")
- **Utilisateur** : Appuyez sur Entrée (utilise "root")
- **Mot de passe** : Tapez le mot de passe root de MariaDB

⏳ L'installation prend 5-10 minutes.

### Étape 4 : Installer comme service Windows

```powershell
# Installer le service backend
.\install-service-windows.ps1

# Installer le service frontend
.\install-service-frontend-windows.ps1
```

✅ Le logiciel démarrera automatiquement à chaque démarrage de Windows !

### Étape 5 : Démarrer le logiciel

**Première fois** :
```powershell
.\start-windows.ps1
```

**Ensuite** : Le logiciel démarre automatiquement avec Windows !

### Étape 6 : Accéder au logiciel

Ouvrez votre navigateur (Chrome, Firefox, Edge) et allez sur :
- **http://localhost:3000**

**Identifiants par défaut** :
- Nom d'utilisateur : `admin`
- Mot de passe : `admin123`

🔒 **IMPORTANT** : Changez le mot de passe dès la première connexion !

---

## 🐧 INSTALLATION LINUX (Ubuntu/Debian)

### Étape 1 : Ouvrir le Terminal

Appuyez sur `Ctrl + Alt + T`

### Étape 2 : Installer les logiciels nécessaires

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Installer Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Installer MariaDB
sudo apt install -y mariadb-server

# Sécuriser MariaDB
sudo mysql_secure_installation
```

**Lors de la sécurisation MariaDB** :
- Switch to unix_socket authentication? **N**
- Change root password? **Y** (choisissez un mot de passe fort)
- Remove anonymous users? **Y**
- Disallow root login remotely? **Y**
- Remove test database? **Y**
- Reload privilege tables? **Y**

### Étape 3 : Préparer le logiciel

```bash
# Créer le dossier d'installation
sudo mkdir -p /opt/ay-hr
cd /opt/ay-hr

# Extraire le fichier (remplacez le chemin par votre fichier téléchargé)
sudo tar -xzf ~/Téléchargements/ay-hr-v1.1.4-linux.tar.gz

# Donner les permissions
sudo chown -R $USER:$USER /opt/ay-hr
```

### Étape 4 : Installer automatiquement

```bash
# Rendre le script exécutable
chmod +x install-linux.sh

# Lancer l'installation
./install-linux.sh
```

Le script va vous demander :
- **Hôte MariaDB** : Appuyez sur Entrée (utilise "localhost")
- **Port** : Appuyez sur Entrée (utilise "3306")
- **Utilisateur** : Appuyez sur Entrée (utilise "root")
- **Mot de passe** : Tapez le mot de passe root de MariaDB

⏳ L'installation prend 5-10 minutes.

### Étape 5 : Installer comme service système

```bash
# Installer les services
sudo ./install-service-linux.sh
```

✅ Le logiciel démarrera automatiquement à chaque démarrage de Linux !

### Étape 6 : Démarrer le logiciel

**Première fois** :
```bash
sudo systemctl start ayhr-backend
sudo systemctl start ayhr-frontend
```

**Vérifier le statut** :
```bash
sudo systemctl status ayhr-backend
sudo systemctl status ayhr-frontend
```

### Étape 7 : Accéder au logiciel

Ouvrez votre navigateur et allez sur :
- **http://localhost:3000**

**Identifiants par défaut** :
- Nom d'utilisateur : `admin`
- Mot de passe : `admin123`

---

## 🗄️ Structure de la Base de Données

La base de données `ay_hr` contient 11 tables principales :

1. **utilisateurs** - Comptes utilisateurs du système
2. **employes** - Informations des employés
3. **postes** - Postes de travail disponibles
4. **pointages** - Feuilles de présence mensuelles
5. **clients** - Liste des clients
6. **missions** - Missions et affectations
7. **avances** - Avances sur salaire
8. **credits** - Crédits salariaux
9. **conges** - Gestion des congés
10. **parametres_entreprise** - Configuration de l'entreprise
11. **logs** - Journal d'activité système

---

## ⚙️ Configuration de l'Entreprise

Après la première connexion :

1. Allez dans **Paramètres** → **Entreprise**
2. Remplissez :
   - Raison sociale
   - RC (Registre de Commerce)
   - NIF (Numéro d'Identification Fiscale)
   - N° Sécurité Sociale Employeur
   - Adresse
   - Téléphone
   - Email

Ces informations apparaîtront sur tous les documents PDF générés.

---

## 🔐 Sécurité - Première Configuration

### 1. Changer le mot de passe admin

Après la première connexion :
- Cliquez sur votre nom (en haut à droite)
- Sélectionnez "Profil"
- Cliquez sur "Changer le mot de passe"
- Utilisez un mot de passe fort (12+ caractères, majuscules, chiffres, symboles)

### 2. Créer d'autres utilisateurs

- Allez dans **Administration** → **Utilisateurs**
- Créez des comptes pour vos collaborateurs
- Définissez les rôles appropriés :
  - **Admin** : Accès complet
  - **Manager** : Gestion RH
  - **User** : Consultation uniquement

---

## 🚀 Commandes Utiles

### Windows

**Démarrer manuellement** :
```powershell
cd C:\AY-HR
.\start-windows.ps1
```

**Arrêter** :
```powershell
cd C:\AY-HR
.\stop-windows.ps1
```

**Voir les logs** :
```powershell
cd C:\AY-HR\logs
type backend.log
type frontend.log
```

**Redémarrer les services** :
```powershell
Restart-Service AYHR-Backend
Restart-Service AYHR-Frontend
```

### Linux

**Démarrer** :
```bash
sudo systemctl start ayhr-backend
sudo systemctl start ayhr-frontend
```

**Arrêter** :
```bash
sudo systemctl stop ayhr-backend
sudo systemctl stop ayhr-frontend
```

**Redémarrer** :
```bash
sudo systemctl restart ayhr-backend
sudo systemctl restart ayhr-frontend
```

**Voir les logs** :
```bash
sudo journalctl -u ayhr-backend -f
sudo journalctl -u ayhr-frontend -f
```

**Statut** :
```bash
sudo systemctl status ayhr-backend
sudo systemctl status ayhr-frontend
```

---

## 🔧 Dépannage

### Problème : "Port 3000 déjà utilisé"

**Windows** :
```powershell
netstat -ano | findstr :3000
taskkill /PID [numéro_du_PID] /F
```

**Linux** :
```bash
sudo lsof -i :3000
sudo kill -9 [PID]
```

### Problème : "Impossible de se connecter à la base de données"

1. Vérifier que MariaDB fonctionne :
   - **Windows** : Services → MariaDB → Démarrer
   - **Linux** : `sudo systemctl start mariadb`

2. Tester la connexion :
   ```bash
   mysql -u root -p
   ```

3. Vérifier le fichier `.env` dans `backend/` :
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=votre_mot_de_passe
   DB_NAME=ay_hr
   ```

### Problème : "L'interface ne s'affiche pas"

1. Vérifier que les deux services fonctionnent
2. Effacer le cache du navigateur (Ctrl + Shift + Delete)
3. Essayer un autre navigateur
4. Vérifier les logs : `logs/frontend.log`

### Problème : "Erreur d'authentification"

1. Réinitialiser le mot de passe admin :
   ```sql
   mysql -u root -p ay_hr
   UPDATE utilisateurs SET hashed_password='$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5QK7TJk/bQhau' WHERE username='admin';
   ```
   (Mot de passe réinitialisé à : `admin123`)

---

## 🌐 Accès depuis d'autres ordinateurs (Réseau Local)

### Windows

1. Trouver votre adresse IP :
   ```powershell
   ipconfig
   ```
   Notez l'adresse IPv4 (ex: 192.168.1.100)

2. Configurer le pare-feu :
   - Panneau de configuration → Pare-feu Windows
   - Autoriser les ports 3000 et 8000

3. Modifier `frontend/.env` :
   ```
   VITE_API_URL=http://192.168.1.100:8000
   ```

4. Accès depuis d'autres PC :
   - `http://192.168.1.100:3000`

### Linux

1. Trouver votre adresse IP :
   ```bash
   ip addr show
   ```

2. Configurer le pare-feu :
   ```bash
   sudo ufw allow 3000/tcp
   sudo ufw allow 8000/tcp
   ```

3. Modifier `frontend/.env` :
   ```
   VITE_API_URL=http://192.168.1.100:8000
   ```

---

## 📊 Sauvegarde de la Base de Données

### Sauvegarde Automatique (Recommandé)

**Windows** (Script PowerShell - `backup-daily.ps1`) :
```powershell
$date = Get-Date -Format "yyyy-MM-dd"
$backupPath = "C:\AY-HR\backups\ay_hr_$date.sql"
mysqldump -u root -p[MOT_DE_PASSE] ay_hr > $backupPath
```

Créer une tâche planifiée :
- Ouvrir "Planificateur de tâches"
- Créer une tâche de base
- Déclencheur : Quotidien à 23h00
- Action : Exécuter `backup-daily.ps1`

**Linux** (Cron) :
```bash
# Créer le script de sauvegarde
sudo nano /opt/ay-hr/backup-daily.sh
```

Contenu :
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="/opt/ay-hr/backups"
mkdir -p $BACKUP_DIR
mysqldump -u root -p[MOT_DE_PASSE] ay_hr > $BACKUP_DIR/ay_hr_$DATE.sql
```

```bash
# Rendre exécutable
sudo chmod +x /opt/ay-hr/backup-daily.sh

# Ajouter au cron
sudo crontab -e
```

Ajouter cette ligne :
```
0 23 * * * /opt/ay-hr/backup-daily.sh
```

### Sauvegarde Manuelle

```bash
mysqldump -u root -p ay_hr > ay_hr_backup_$(date +%Y-%m-%d).sql
```

### Restauration

```bash
mysql -u root -p ay_hr < ay_hr_backup_2025-11-14.sql
```

---

## 📞 Support et Aide

### Documentation Intégrée
- Dans l'application : Menu **Aide** → **Documentation**
- API Documentation : http://localhost:8000/docs

### Fichiers Journaux
- Backend : `logs/backend.log`
- Frontend : `logs/frontend.log`
- Base de données : Selon configuration MariaDB

### Contact
- Email : support@ayhr.com
- Téléphone : +213 XXX XXX XXX

---

## 📄 Informations Système

**Version** : 1.1.4
**Date de Release** : Novembre 2025
**Développé par** : AIRBAND HR

**Technologies** :
- Backend : Python 3.11 + FastAPI
- Frontend : React 18 + Vite + Ant Design
- Base de données : MariaDB 10.11+
- PDF : ReportLab + QRCode

**Licence** : Propriétaire - Copyright © 2025 AIRBAND HR

---

## ✅ Liste de Vérification Post-Installation

- [ ] Logiciel installé et démarré
- [ ] Connexion réussie avec admin/admin123
- [ ] Mot de passe admin changé
- [ ] Paramètres de l'entreprise configurés
- [ ] Premiers postes de travail créés
- [ ] Premier employé ajouté (test)
- [ ] Génération d'un bulletin de paie (test)
- [ ] Sauvegarde automatique configurée
- [ ] Accès réseau testé (si nécessaire)
- [ ] Formation des utilisateurs planifiée

---

## 🎓 Premiers Pas Rapides

### 1. Configurer les Postes de Travail
Menu **RH** → **Postes** → **Nouveau Poste**

### 2. Ajouter un Employé
Menu **RH** → **Employés** → **Nouvel Employé**

### 3. Enregistrer les Pointages
Menu **RH** → **Pointages** → Sélectionner le mois

### 4. Calculer les Salaires
Menu **Paie** → **Calcul des Salaires** → Choisir le mois

### 5. Générer les Bulletins
Menu **Paie** → **Bulletins de Paie** → Télécharger PDF

---

Félicitations ! Votre système AY HR Management est maintenant opérationnel ! 🎉

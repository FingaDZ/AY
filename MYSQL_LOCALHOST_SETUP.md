# Guide d'Installation et Configuration MySQL pour Localhost

Ce guide explique comment installer MySQL sur Windows et restaurer la base de données depuis le serveur.

## Option 1: Installation de MySQL sur Windows

### Téléchargement
1. Visitez: https://dev.mysql.com/downloads/installer/
2. Téléchargez **MySQL Installer for Windows** (mysql-installer-community)
3. Choisissez la version **8.0.x** (version complète ~400 MB)

### Installation
1. Exécutez l'installeur MySQL
2. Choisissez **Custom** ou **Developer Default**
3. Composants à installer:
   - MySQL Server 8.0.x
   - MySQL Workbench (optionnel, interface graphique)
   - MySQL Shell (optionnel)
   - Connector/Python (recommandé)

4. Configuration du serveur:
   - **Type**: Development Computer
   - **Port**: 3306 (par défaut)
   - **Root Password**: Choisissez un mot de passe (ex: Lamicro@4000)
   - **Authentication**: Use Strong Password Encryption

5. Terminer l'installation et démarrer le service MySQL

### Vérification de l'installation
```powershell
# Dans PowerShell
mysql --version

# Se connecter à MySQL
mysql -u root -p
# Entrez votre mot de passe root
```

## Option 2: Utiliser MariaDB (Alternative)

### Téléchargement
1. Visitez: https://mariadb.org/download/
2. Téléchargez MariaDB 10.11 ou 11.x pour Windows
3. Exécutez l'installeur MSI

### Configuration
- Port: 3306
- Root password: Votre mot de passe
- Service name: MySQL ou MariaDB

## Restauration de la Base de Données

### Méthode 1: Via Script Python
```powershell
cd "F:\Code\AY HR"
& "F:/Code/AY HR/.venv/Scripts/python.exe" create_db_dump.py
```
Ceci créera un fichier `ay_hr_backup_YYYYMMDD_HHMMSS.sql`

### Méthode 2: Restauration Manuelle

#### 1. Créer la base de données
```sql
mysql -u root -p
# Puis dans MySQL:
CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

#### 2. Créer l'utilisateur (optionnel)
```sql
mysql -u root -p
# Puis dans MySQL:
CREATE USER 'ayhr_user'@'localhost' IDENTIFIED BY 'VotreMotDePasse';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';
FLUSH PRIVILEGES;
exit;
```

#### 3. Restaurer le dump
```powershell
# Remplacez YYYYMMDD_HHMMSS par la date de votre fichier
mysql -u root -p ay_hr < "F:\Code\AY HR\ay_hr_backup_YYYYMMDD_HHMMSS.sql"
```

#### 4. Vérifier la restauration
```powershell
mysql -u root -p ay_hr -e "SELECT COUNT(*) as total_employes FROM employes; SELECT COUNT(*) as total_postes FROM postes_travail;"
```

## Configuration du Backend pour Localhost

### Modifier le fichier .env
Créez ou modifiez `backend/.env`:

```env
# Base de données locale
DATABASE_URL=mysql+pymysql://root:VotreMotDePasse@localhost:3306/ay_hr

# Ou si vous avez créé l'utilisateur ayhr_user:
DATABASE_URL=mysql+pymysql://ayhr_user:VotreMotDePasse@localhost:3306/ay_hr

# Clé secrète (générez-en une nouvelle)
SECRET_KEY=votre-clé-secrète-très-longue-et-complexe

# Autres configurations
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Tester la connexion
```powershell
cd "F:\Code\AY HR\backend"
& "F:/Code/AY HR/.venv/Scripts/python.exe" -c "from database import engine; print('✓ Connexion réussie!')"
```

## Scripts Disponibles

### 1. create_db_dump.py
Crée un dump de la base de données du serveur 192.168.20.53
```powershell
& "F:/Code/AY HR/.venv/Scripts/python.exe" create_db_dump.py
```

### 2. sync_postes_travail.py
Synchronise les postes de travail avec ceux utilisés par les employés
```powershell
& "F:/Code/AY HR/.venv/Scripts/python.exe" sync_postes_travail.py
```

### 3. import_employes_from_excel.py
Importe les employés depuis un fichier Excel
```powershell
& "F:/Code/AY HR/.venv/Scripts/python.exe" import_employes_from_excel.py
```

## Synchronisation Localhost ↔️ Serveur

### Du Serveur vers Localhost
1. Créer un dump du serveur:
```powershell
& "F:/Code/AY HR/.venv/Scripts/python.exe" create_db_dump.py
```

2. Restaurer sur localhost:
```powershell
mysql -u root -p ay_hr < "F:\Code\AY HR\ay_hr_backup_YYYYMMDD_HHMMSS.sql"
```

### De Localhost vers Serveur
1. Créer un dump local:
```powershell
mysqldump -u root -p ay_hr > "F:\Code\AY HR\localhost_backup.sql"
```

2. Transférer au serveur:
```powershell
scp "F:\Code\AY HR\localhost_backup.sql" root@192.168.20.53:/tmp/
```

3. Restaurer sur le serveur:
```powershell
ssh root@192.168.20.53
mysql -u ayhr_user -p'!Yara@2014' ay_hr < /tmp/localhost_backup.sql
rm /tmp/localhost_backup.sql
```

## Dépannage

### Erreur: Access denied
- Vérifiez que le service MySQL est démarré
- Vérifiez le mot de passe root
- Vérifiez que l'utilisateur existe et a les permissions

### Erreur: Can't connect to MySQL server
- Vérifiez que MySQL est installé
- Vérifiez que le service est démarré:
```powershell
Get-Service MySQL* | Start-Service
```

### Erreur: Table doesn't exist
- Assurez-vous d'avoir restauré le dump complet
- Vérifiez que vous êtes dans la bonne base de données

### Démarrer/Arrêter MySQL sur Windows
```powershell
# Démarrer
net start MySQL

# Arrêter
net stop MySQL

# Vérifier le statut
Get-Service MySQL*
```

## Outils Recommandés

### MySQL Workbench
- Interface graphique pour gérer MySQL
- Permet de visualiser les tables, exécuter des requêtes
- Téléchargement: https://dev.mysql.com/downloads/workbench/

### HeidiSQL
- Alternative légère à MySQL Workbench
- Interface simple et rapide
- Téléchargement: https://www.heidisql.com/download.php

### DBeaver
- Outil universel pour bases de données
- Supporte MySQL, MariaDB, PostgreSQL, etc.
- Téléchargement: https://dbeaver.io/download/

## Notes de Sécurité

⚠️ **Important**:
- Ne committez jamais les fichiers `.env` avec vos mots de passe
- Utilisez des mots de passe forts pour MySQL
- Changez le mot de passe root après l'installation
- Créez des utilisateurs spécifiques avec permissions limitées

## Support

Pour toute question:
1. Consultez la documentation MySQL: https://dev.mysql.com/doc/
2. Consultez les logs MySQL: `C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err`
3. Contactez l'administrateur système

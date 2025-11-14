# Guide Administrateur - AY HR Management v1.1.4

## 📋 Table des Matières

1. [Déploiement Initial](#déploiement-initial)
2. [Gestion des Services](#gestion-des-services)
3. [Surveillance et Logs](#surveillance-et-logs)
4. [Sauvegardes](#sauvegardes)
5. [Mises à Jour](#mises-à-jour)
6. [Dépannage Avancé](#dépannage-avancé)
7. [Sécurité](#sécurité)
8. [Performance](#performance)

---

## Déploiement Initial

### Checklist Pré-Déploiement

#### Windows
- [ ] Windows 10/11 ou Server 2016+ installé
- [ ] Mises à jour Windows appliquées
- [ ] Pare-feu configuré (ports 8000, 3000)
- [ ] Python 3.11+ installé (python --version)
- [ ] Node.js 18+ installé (node --version)
- [ ] MariaDB 10.11+ installé et sécurisé
- [ ] Droits administrateur disponibles

#### Linux
- [ ] Ubuntu 20.04+ ou Debian 11+ installé
- [ ] Système à jour (apt update && apt upgrade)
- [ ] Pare-feu configuré (ufw allow 8000,3000)
- [ ] Python 3.11+ installé
- [ ] Node.js 18+ installé
- [ ] MariaDB 10.11+ installé et sécurisé
- [ ] Accès sudo disponible

### Installation Standard

#### Windows
```powershell
# 1. Extraire le package
Expand-Archive -Path ay-hr-v1.1.4-windows.zip -DestinationPath C:\AY-HR
cd C:\AY-HR\ay-hr-v1.1.4-windows

# 2. Exécuter l'installation
.\install-windows.ps1

# 3. Installer comme service
.\install-service-windows.ps1

# 4. Vérifier les services
Get-Service AYHR-*
```

#### Linux
```bash
# 1. Extraire le package
tar -xzf ay-hr-v1.1.4-linux.tar.gz
cd ay-hr-v1.1.4-linux

# 2. Exécuter l'installation
chmod +x install-linux.sh
sudo ./install-linux.sh

# 3. Installer comme service
sudo ./install-service-linux.sh

# 4. Vérifier les services
sudo systemctl status ayhr-backend
sudo systemctl status ayhr-frontend
```

### Configuration Base de Données

#### Créer un Utilisateur Dédié
```sql
-- Se connecter à MariaDB en root
mysql -u root -p

-- Créer un utilisateur pour l'application
CREATE USER 'ayhr_user'@'localhost' IDENTIFIED BY 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Optimiser MariaDB
```ini
# /etc/mysql/mariadb.conf.d/50-server.cnf (Linux)
# C:\Program Files\MariaDB\data\my.ini (Windows)

[mysqld]
max_connections = 100
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
innodb_flush_log_at_trx_commit = 2
query_cache_size = 32M
```

---

## Gestion des Services

### Windows (NSSM)

#### Commandes de Base
```powershell
# Démarrer les services
Start-Service AYHR-Backend
Start-Service AYHR-Frontend

# Arrêter les services
Stop-Service AYHR-Backend
Stop-Service AYHR-Frontend

# Redémarrer les services
Restart-Service AYHR-Backend
Restart-Service AYHR-Frontend

# Vérifier l'état
Get-Service AYHR-* | Format-Table -AutoSize

# Voir les logs de service
Get-EventLog -LogName Application -Source AYHR-Backend -Newest 50
```

#### Configuration Avancée NSSM
```powershell
# Modifier les paramètres de démarrage
nssm set AYHR-Backend Start SERVICE_DELAYED_AUTO_START

# Configurer les actions de récupération
nssm set AYHR-Backend AppExit Default Restart
nssm set AYHR-Backend AppRestartDelay 5000

# Modifier les variables d'environnement
nssm set AYHR-Backend AppEnvironmentExtra "KEY=value"
```

### Linux (systemd)

#### Commandes de Base
```bash
# Démarrer les services
sudo systemctl start ayhr-backend
sudo systemctl start ayhr-frontend

# Arrêter les services
sudo systemctl stop ayhr-backend
sudo systemctl stop ayhr-frontend

# Redémarrer les services
sudo systemctl restart ayhr-backend
sudo systemctl restart ayhr-frontend

# Vérifier l'état
sudo systemctl status ayhr-backend
sudo systemctl status ayhr-frontend

# Voir les logs
sudo journalctl -u ayhr-backend -f
sudo journalctl -u ayhr-frontend -f
```

#### Configuration Avancée systemd
```bash
# Éditer le fichier service
sudo systemctl edit ayhr-backend

# Ajouter:
[Service]
Restart=always
RestartSec=10
StartLimitInterval=200
StartLimitBurst=5
```

---

## Surveillance et Logs

### Emplacements des Logs

#### Windows
```
C:\AY-HR\logs\backend.log
C:\AY-HR\logs\frontend.log
C:\AY-HR\logs\nssm\AYHR-Backend.log
C:\AY-HR\logs\nssm\AYHR-Frontend.log
```

#### Linux
```
/chemin/installation/logs/backend.log
/chemin/installation/logs/frontend.log
sudo journalctl -u ayhr-backend
sudo journalctl -u ayhr-frontend
```

### Rotation des Logs

#### Windows (PowerShell Script)
```powershell
# rotate-logs.ps1
$logPath = "C:\AY-HR\logs"
$maxSize = 10MB
$maxAge = 30 # jours

Get-ChildItem -Path $logPath -Filter *.log | ForEach-Object {
    if ($_.Length -gt $maxSize) {
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $archiveName = "$($_.BaseName)-$timestamp.zip"
        Compress-Archive -Path $_.FullName -DestinationPath "$logPath\archives\$archiveName"
        Clear-Content $_.FullName
    }
}

# Supprimer les anciennes archives
Get-ChildItem -Path "$logPath\archives" -Filter *.zip | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$maxAge) } |
    Remove-Item
```

#### Linux (logrotate)
```bash
# /etc/logrotate.d/ayhr
/chemin/installation/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 ayhr_user ayhr_user
    sharedscripts
    postrotate
        systemctl reload ayhr-backend > /dev/null 2>&1 || true
        systemctl reload ayhr-frontend > /dev/null 2>&1 || true
    endscript
}
```

### Surveillance en Temps Réel

#### Surveiller les Processus
```powershell
# Windows
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"} | 
    Format-Table ProcessName, Id, CPU, WorkingSet -AutoSize

# Linux
ps aux | grep -E "python|node" | grep -v grep
```

#### Surveiller les Ports
```powershell
# Windows
netstat -ano | findstr ":8000 :3000"

# Linux
sudo netstat -tulpn | grep -E ":8000|:3000"
```

---

## Sauvegardes

### Sauvegarde Automatique de la Base de Données

#### Windows (Tâche Planifiée)
```powershell
# backup-db.ps1
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = "C:\AY-HR\backups"
$backupFile = "$backupDir\ay_hr_$timestamp.sql"

& "C:\Program Files\MariaDB 10.11\bin\mysqldump.exe" `
    -u ayhr_user -p'mot_de_passe' `
    --single-transaction `
    --routines `
    --triggers `
    ay_hr > $backupFile

# Compresser
Compress-Archive -Path $backupFile -DestinationPath "$backupFile.zip"
Remove-Item $backupFile

# Nettoyer les anciennes sauvegardes (garder 30 jours)
Get-ChildItem -Path $backupDir -Filter *.zip | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item
```

**Planifier la tâche:**
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\AY-HR\backup-db.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest

Register-ScheduledTask -TaskName "AY-HR Database Backup" `
    -Action $action -Trigger $trigger -Principal $principal
```

#### Linux (Cron)
```bash
# backup-db.sh
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/chemin/installation/backups"
BACKUP_FILE="$BACKUP_DIR/ay_hr_$TIMESTAMP.sql"

mysqldump -u ayhr_user -p'mot_de_passe' \
    --single-transaction \
    --routines \
    --triggers \
    ay_hr > "$BACKUP_FILE"

# Compresser
gzip "$BACKUP_FILE"

# Nettoyer les anciennes sauvegardes (garder 30 jours)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
```

**Ajouter au crontab:**
```bash
chmod +x backup-db.sh
crontab -e
# Ajouter:
0 2 * * * /chemin/installation/backup-db.sh
```

### Restauration

#### Depuis une Sauvegarde
```bash
# Décompresser (si nécessaire)
gunzip ay_hr_20250120-020000.sql.gz  # Linux
Expand-Archive ay_hr_20250120-020000.sql.zip  # Windows

# Restaurer
mysql -u ayhr_user -p ay_hr < ay_hr_20250120-020000.sql
```

---

## Mises à Jour

### Procédure de Mise à Jour

#### 1. Préparation
```bash
# Sauvegarder la base de données
# (voir section Sauvegardes)

# Arrêter les services
# Windows:
Stop-Service AYHR-*
# Linux:
sudo systemctl stop ayhr-backend ayhr-frontend
```

#### 2. Installation de la Nouvelle Version
```bash
# Extraire la nouvelle version
# Exécuter le script d'installation
# Vérifier la configuration (.env)
```

#### 3. Migration Base de Données
```sql
-- Appliquer les scripts de migration si nécessaire
SOURCE migration_v1.1.4.sql;
```

#### 4. Redémarrage
```bash
# Windows:
Start-Service AYHR-*
# Linux:
sudo systemctl start ayhr-backend ayhr-frontend
```

#### 5. Vérification
```bash
# Tester l'accès à l'application
# Vérifier les logs
# Tester les fonctionnalités principales
```

---

## Dépannage Avancé

### Problèmes de Base de Données

#### Connexion Refusée
```bash
# Vérifier que MariaDB est démarré
# Windows:
Get-Service MariaDB
# Linux:
sudo systemctl status mariadb

# Tester la connexion
mysql -u ayhr_user -p ay_hr -e "SELECT 1;"
```

#### Performances Lentes
```sql
-- Analyser les requêtes lentes
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Vérifier les index manquants
SHOW INDEXES FROM employes;

-- Optimiser les tables
OPTIMIZE TABLE employes, pointages, missions;
```

### Problèmes de Service

#### Service ne Démarre Pas
```bash
# Windows - Vérifier les logs NSSM
Get-Content C:\AY-HR\logs\nssm\AYHR-Backend.log -Tail 50

# Linux - Vérifier les logs systemd
sudo journalctl -u ayhr-backend -n 50 --no-pager
```

#### Port Déjà Utilisé
```powershell
# Windows - Trouver le processus
netstat -ano | findstr :8000
Stop-Process -Id <PID> -Force

# Linux - Trouver et tuer le processus
sudo lsof -i :8000
sudo kill -9 <PID>
```

---

## Sécurité

### Checklist de Sécurité

#### Base de Données
- [ ] Mot de passe root MariaDB fort et unique
- [ ] Utilisateur dédié avec privilèges limités
- [ ] Accès réseau restreint (bind-address = 127.0.0.1)
- [ ] SSL/TLS activé pour les connexions distantes
- [ ] Sauvegardes chiffrées

#### Application
- [ ] SECRET_KEY unique et aléatoire (32+ caractères)
- [ ] HTTPS activé en production (reverse proxy)
- [ ] CORS configuré correctement
- [ ] Logs d'audit activés
- [ ] Mots de passe utilisateurs hachés (bcrypt)

#### Système
- [ ] Pare-feu activé et configuré
- [ ] Mises à jour système régulières
- [ ] Accès SSH sécurisé (clés, pas de root)
- [ ] Permissions fichiers correctes (640/750)
- [ ] Surveillance des tentatives d'intrusion

### Configuration HTTPS avec Nginx

```nginx
# /etc/nginx/sites-available/ayhr
server {
    listen 443 ssl http2;
    server_name ayhr.exemple.com;

    ssl_certificate /etc/ssl/certs/ayhr.crt;
    ssl_certificate_key /etc/ssl/private/ayhr.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Redirection HTTP vers HTTPS
server {
    listen 80;
    server_name ayhr.exemple.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Performance

### Optimisations Backend

#### Configuration Uvicorn
```python
# main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Nombre de workers (CPU cores)
        limit_concurrency=100,
        timeout_keep_alive=30,
        access_log=True
    )
```

### Optimisations Frontend

#### Build de Production
```bash
# Au lieu de npm run dev, utiliser:
npm run build
npm run preview  # ou servir avec nginx
```

### Optimisations Base de Données

```sql
-- Index pour améliorer les recherches
CREATE INDEX idx_employes_search ON employes(nom, prenom);
CREATE INDEX idx_pointages_date ON pointages(annee, mois);
CREATE INDEX idx_missions_date ON missions(date_mission);

-- Analyser les tables
ANALYZE TABLE employes, pointages, missions;
```

---

## Contacts Support

- **Documentation**: INSTALLATION_GUIDE.md
- **Logs**: logs/backend.log, logs/frontend.log
- **Base de données**: Logs MariaDB

---

**Version**: 1.1.4  
**Dernière mise à jour**: Janvier 2025

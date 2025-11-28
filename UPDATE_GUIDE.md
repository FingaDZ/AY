# Guide de Mise à Jour - AY HR System

**Version du guide** : 2.0  
**Date** : 28 novembre 2025  
**Compatibilité** : Linux (Ubuntu 22.04+, Debian 11+)

---

## 📋 Table des Matières

1. [Mise à Jour Automatique (Recommandé)](#mise-à-jour-automatique)
2. [Mise à Jour Manuelle](#mise-à-jour-manuelle)
3. [Vérification Post-Mise à Jour](#vérification)
4. [Rollback en Cas de Problème](#rollback)
5. [FAQ](#faq)

---

## 🚀 Mise à Jour Automatique (Recommandé)

### Prérequis

- Accès root (sudo)
- Connexion Internet
- Services AY HR en cours d'exécution

### Procédure

```bash
# 1. Se connecter au serveur
ssh user@192.168.20.53

# 2. Accéder au répertoire de l'application
cd /opt/ay-hr

# 3. Exécuter le script de mise à jour
sudo ./update.sh
```

### Ce que fait le script

Le script `update.sh` v2.0 effectue automatiquement :

1. ✅ **Vérifications préliminaires** (permissions, répertoires)
2. ✅ **Sauvegarde de la base de données** (dump SQL compressé)
3. ✅ **Sauvegarde des fichiers de configuration** (.env, config.py)
4. ✅ **Arrêt des services** (backend, frontend)
5. ✅ **Récupération du code** depuis GitHub (git pull)
6. ✅ **Mise à jour Backend** (pip install, nettoyage cache)
7. ✅ **Mise à jour Frontend** (npm install, build production)
8. ✅ **Correction des permissions** (ownership, exécutables)
9. ✅ **Redémarrage des services** avec vérification
10. ✅ **Nettoyage** (backups >30 jours, logs anciens)

### Durée estimée

- **Petite mise à jour** : 2-3 minutes
- **Mise à jour majeure** : 5-10 minutes

### Logs

Les logs de mise à jour sont stockés dans :
```
/opt/ay-hr/logs/update_YYYYMMDD_HHMMSS.log
```

Pour consulter le dernier log :
```bash
ls -lt /opt/ay-hr/logs/update_*.log | head -1 | xargs cat
```

---

## 🔧 Mise à Jour Manuelle

Si le script automatique échoue ou pour un contrôle total :

### 1. Sauvegarde de la Base de Données

```bash
# Créer le répertoire de backup
sudo mkdir -p /opt/ay-hr/backups

# Extraire les credentials depuis .env
cd /opt/ay-hr/backend
DB_NAME=$(grep DATABASE_URL .env | grep -oP '(?<=/)[\w_]+$')
DB_USER=$(grep DATABASE_URL .env | grep -oP '(?<=://)[^:]+')
DB_PASS=$(grep DATABASE_URL .env | grep -oP '(?<=:)[^@]+(?=@)')

# Dump de la base
mysqldump -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" | gzip > /opt/ay-hr/backups/db_backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### 2. Sauvegarde de la Configuration

```bash
cd /opt/ay-hr
tar -czf backups/config_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    backend/.env \
    backend/config.py
```

### 3. Arrêt des Services

```bash
sudo systemctl stop ayhr-backend
sudo systemctl stop ayhr-frontend
```

### 4. Mise à Jour du Code

```bash
cd /opt/ay-hr
sudo git stash  # Sauvegarder les modifications locales
sudo git pull origin main
```

### 5. Mise à Jour Backend

```bash
cd /opt/ay-hr/backend
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
find . -type d -name "__pycache__" -exec rm -rf {} +
deactivate
```

### 6. Mise à Jour Frontend

```bash
cd /opt/ay-hr/frontend
npm install
npm run build
```

### 7. Permissions

```bash
cd /opt/ay-hr
sudo chown -R root:root .
sudo chmod +x *.sh
```

### 8. Redémarrage des Services

```bash
sudo systemctl start ayhr-backend
sudo systemctl start ayhr-frontend
```

---

## ✅ Vérification Post-Mise à Jour

### 1. Vérifier le Statut des Services

```bash
# Statut complet
sudo systemctl status ayhr-backend ayhr-frontend

# Vérification rapide
sudo systemctl is-active ayhr-backend && echo "Backend OK"
sudo systemctl is-active ayhr-frontend && echo "Frontend OK"
```

### 2. Vérifier la Version

```bash
# Version backend
grep APP_VERSION /opt/ay-hr/backend/config.py

# Version frontend (dans le navigateur)
# Ouvrir http://192.168.20.53:8000
# Vérifier le numéro de version en bas de la sidebar
```

### 3. Vérifier les Logs

```bash
# Logs backend (temps réel)
sudo journalctl -u ayhr-backend -f

# Logs frontend (temps réel)
sudo journalctl -u ayhr-frontend -f

# Dernières erreurs backend
sudo journalctl -u ayhr-backend -p err -n 50
```

### 4. Test Fonctionnel

1. Ouvrir l'application : `http://192.168.20.53:8000`
2. Se connecter (admin / admin123)
3. Vérifier les modules principaux :
   - Dashboard (statistiques)
   - Employés (liste)
   - Pointages (grille)
   - Logs incomplets (si v1.7.0)

### 5. Vérifier la Base de Données

```bash
# Se connecter à MySQL
mysql -u root -p

# Vérifier les tables
USE ay_hr;
SHOW TABLES;

# Vérifier la table des logs incomplets (v1.7.0+)
DESCRIBE incomplete_attendance_logs;

# Quitter
EXIT;
```

---

## 🔄 Rollback en Cas de Problème

Si la mise à jour échoue ou cause des problèmes :

### Option 1 : Restauration Rapide (Code uniquement)

```bash
cd /opt/ay-hr

# Revenir à la version précédente
sudo git log --oneline -10  # Voir les derniers commits
sudo git reset --hard <commit-hash>  # Remplacer <commit-hash>

# Redémarrer les services
sudo systemctl restart ayhr-backend ayhr-frontend
```

### Option 2 : Restauration Complète (Code + DB)

```bash
# 1. Arrêter les services
sudo systemctl stop ayhr-backend ayhr-frontend

# 2. Restaurer le code
cd /opt/ay-hr
sudo git reset --hard <commit-hash>

# 3. Restaurer la base de données
cd /opt/ay-hr/backups
LATEST_BACKUP=$(ls -t db_backup_*.sql.gz | head -1)
gunzip -c "$LATEST_BACKUP" | mysql -u root -p ay_hr

# 4. Restaurer la configuration
LATEST_CONFIG=$(ls -t config_backup_*.tar.gz | head -1)
tar -xzf "$LATEST_CONFIG" -C /opt/ay-hr

# 5. Redémarrer
sudo systemctl start ayhr-backend ayhr-frontend
```

### Option 3 : Restauration depuis Backup Manuel

Si vous avez un backup complet du serveur :

```bash
# Restaurer depuis votre système de backup
# (dépend de votre solution : Veeam, Bacula, rsync, etc.)
```

---

## ❓ FAQ

### Q1 : Combien de temps dure une mise à jour ?

**R** : En moyenne 2-5 minutes. Les mises à jour majeures peuvent prendre jusqu'à 10 minutes.

### Q2 : Dois-je prévenir les utilisateurs ?

**R** : Oui, il est recommandé de :
- Planifier la mise à jour en dehors des heures de travail
- Prévenir les utilisateurs 24h à l'avance
- Afficher un message de maintenance si possible

### Q3 : Que faire si le script update.sh échoue ?

**R** : 
1. Consulter les logs : `/opt/ay-hr/logs/update_*.log`
2. Identifier l'étape qui a échoué
3. Exécuter manuellement cette étape (voir [Mise à Jour Manuelle](#mise-à-jour-manuelle))
4. Contacter le support si nécessaire

### Q4 : Les données sont-elles sauvegardées automatiquement ?

**R** : Oui, le script `update.sh` v2.0 sauvegarde automatiquement :
- La base de données (dump SQL compressé)
- Les fichiers de configuration (.env, config.py)
- Les backups sont conservés 30 jours

### Q5 : Puis-je annuler une mise à jour ?

**R** : Oui, voir la section [Rollback](#rollback).

### Q6 : Comment vérifier la version actuelle ?

**R** :
```bash
# Backend
grep APP_VERSION /opt/ay-hr/backend/config.py

# Frontend (dans l'interface)
# Voir le numéro en bas de la sidebar ou sur la page de login
```

### Q7 : Que faire si les services ne redémarrent pas ?

**R** :
```bash
# Vérifier les logs d'erreur
sudo journalctl -u ayhr-backend -p err -n 50
sudo journalctl -u ayhr-frontend -p err -n 50

# Vérifier les ports
sudo netstat -tlnp | grep 8000

# Redémarrer manuellement
sudo systemctl restart ayhr-backend
sudo systemctl restart ayhr-frontend
```

### Q8 : Comment mettre à jour depuis Windows ?

**R** : Le script `update.sh` est pour Linux uniquement. Sur Windows :
1. Ouvrir Git Bash ou PowerShell
2. `cd F:\Code\AY HR`
3. `git pull origin main`
4. Backend : `cd backend && .venv\Scripts\activate && pip install -r requirements.txt`
5. Frontend : `cd frontend && npm install && npm run build`

### Q9 : Puis-je automatiser les mises à jour ?

**R** : Oui, avec un cron job :
```bash
# Éditer crontab
sudo crontab -e

# Ajouter (mise à jour tous les dimanches à 2h du matin)
0 2 * * 0 /opt/ay-hr/update.sh >> /opt/ay-hr/logs/cron_update.log 2>&1
```

⚠️ **Attention** : Automatiser les mises à jour peut causer des problèmes si une version introduit des bugs. Recommandé uniquement pour les environnements de test.

### Q10 : Comment voir l'historique des mises à jour ?

**R** :
```bash
# Logs de mise à jour
ls -lth /opt/ay-hr/logs/update_*.log

# Historique Git
cd /opt/ay-hr
git log --oneline --graph --all -20
```

---

## 📞 Support

En cas de problème :

1. **Consulter les logs** : `/opt/ay-hr/logs/`
2. **Vérifier le CHANGELOG** : `/opt/ay-hr/CHANGELOG.md`
3. **GitHub Issues** : https://github.com/FingaDZ/AY/issues
4. **Documentation** : `/opt/ay-hr/README.md`

---

## 📝 Changelog du Guide

| Version | Date | Changements |
|---------|------|-------------|
| 2.0 | 28 nov 2025 | Script update.sh v2.0, sauvegarde auto, logs détaillés |
| 1.0 | 25 nov 2025 | Version initiale |

---

**Développé par AIRBAND**  
**Dernière mise à jour** : 28 novembre 2025

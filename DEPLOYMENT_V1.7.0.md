# 🚀 Déploiement v1.7.0 - Hybrid Incomplete Logs

**Date de release** : 28 novembre 2025  
**Version** : 1.7.0  
**Statut** : ✅ Production Ready

---

## 📋 Vue d'Ensemble

Cette version introduit une **gestion robuste des logs de pointage incomplets** (Entrée sans Sortie ou inversement) avec :
- ✅ **Calcul intelligent** : Estimation automatique des heures manquantes
- ✅ **Validation RH** : Interface dédiée pour corriger les estimations
- ✅ **Traçabilité complète** : Historique des validations et corrections
- ✅ **Import sans perte** : Aucune donnée n'est perdue, tout est flaggé pour validation

---

## 🆕 Nouveautés v1.7.0

### 1. Gestion Logs Incomplets

**Problème résolu** :
- Logs biométriques incomplets (ENTRY sans EXIT ou EXIT sans ENTRY)
- Impossibilité de calculer les heures travaillées exactes
- Risque de perte de données lors de l'import

**Solution** :
- **Calcul smart** : Estimation basée sur des règles métier
  - ENTRY seul → assume EXIT à 17h00
  - EXIT seul → assume ENTRY à 08h00
- **Flagging** : Tous les logs incomplets sont marqués pour validation
- **Interface RH** : Page dédiée `/incomplete-logs` pour valider/corriger
- **Notifications** : Badges et alertes pour actions requises

### 2. Nouvelles Tables DB

**`incomplete_attendance_logs`** :
```sql
CREATE TABLE incomplete_attendance_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_log_id INT NOT NULL,
    attendance_sync_log_id INT,
    hr_employee_id INT NOT NULL,
    employee_name VARCHAR(200),
    log_date DATE NOT NULL,
    log_type ENUM('ENTRY', 'EXIT') NOT NULL,
    log_timestamp DATETIME NOT NULL,
    estimated_minutes INT NOT NULL,
    estimation_rule VARCHAR(100),
    status ENUM('pending', 'validated', 'corrected') DEFAULT 'pending',
    validated_minutes INT,
    validated_by VARCHAR(100),
    validated_at DATETIME,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hr_employee (hr_employee_id),
    INDEX idx_status (status),
    INDEX idx_log_date (log_date)
);
```

### 3. Nouveaux Endpoints API

**`/api/incomplete-logs`** :
- `GET /` : Liste des logs incomplets (avec filtres)
- `GET /{id}` : Détails d'un log incomplet
- `PUT /{id}/validate` : Valider une estimation
- `PUT /{id}/correct` : Corriger manuellement
- `DELETE /{id}` : Supprimer (admin uniquement)

### 4. Nouvelle Page Frontend

**`/incomplete-logs`** :
- Liste des logs incomplets avec filtres (statut, employé, date)
- Badges de notification (nombre de logs en attente)
- Modal de validation/correction
- Historique des actions

---

## 📦 Déploiement

### Prérequis

- Version actuelle : v1.3.0 ou supérieure
- Accès root au serveur
- Connexion Internet
- Services AY HR en cours d'exécution

### Procédure Automatique (Recommandé)

```bash
# 1. Se connecter au serveur
ssh user@192.168.20.53

# 2. Accéder au répertoire
cd /opt/ay-hr

# 3. Exécuter la mise à jour
sudo ./update.sh
```

Le script `update.sh` v2.0 effectue automatiquement :
1. Sauvegarde DB et configuration
2. Git pull depuis GitHub
3. Migration DB (nouvelle table)
4. Mise à jour dépendances
5. Build frontend
6. Redémarrage services

**Durée estimée** : 3-5 minutes

### Procédure Manuelle

Si le script automatique échoue :

#### 1. Sauvegarde

```bash
# DB
mysqldump -u root -p ay_hr | gzip > /opt/ay-hr/backups/db_backup_$(date +%Y%m%d).sql.gz

# Config
tar -czf /opt/ay-hr/backups/config_backup_$(date +%Y%m%d).tar.gz \
    /opt/ay-hr/backend/.env \
    /opt/ay-hr/backend/config.py
```

#### 2. Arrêt des services

```bash
sudo systemctl stop ayhr-backend
sudo systemctl stop ayhr-frontend
```

#### 3. Mise à jour du code

```bash
cd /opt/ay-hr
sudo git pull origin main
```

#### 4. Migration DB

```bash
cd /opt/ay-hr/database

# Exécuter le script de migration
mysql -u root -p ay_hr < migrations/001_add_incomplete_logs_table.sql
```

**Script SQL** :
```sql
-- Créer la table incomplete_attendance_logs
CREATE TABLE IF NOT EXISTS incomplete_attendance_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_log_id INT NOT NULL,
    attendance_sync_log_id INT,
    hr_employee_id INT NOT NULL,
    employee_name VARCHAR(200),
    log_date DATE NOT NULL,
    log_type ENUM('ENTRY', 'EXIT') NOT NULL,
    log_timestamp DATETIME NOT NULL,
    estimated_minutes INT NOT NULL,
    estimation_rule VARCHAR(100),
    status ENUM('pending', 'validated', 'corrected') DEFAULT 'pending',
    validated_minutes INT,
    validated_by VARCHAR(100),
    validated_at DATETIME,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hr_employee (hr_employee_id),
    INDEX idx_status (status),
    INDEX idx_log_date (log_date),
    FOREIGN KEY (hr_employee_id) REFERENCES employes(id) ON DELETE CASCADE,
    FOREIGN KEY (attendance_sync_log_id) REFERENCES attendance_sync_log(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 5. Backend

```bash
cd /opt/ay-hr/backend
source .venv/bin/activate
pip install -r requirements.txt
find . -type d -name "__pycache__" -exec rm -rf {} +
deactivate
```

#### 6. Frontend

```bash
cd /opt/ay-hr/frontend
npm install
npm run build
```

#### 7. Redémarrage

```bash
sudo systemctl start ayhr-backend
sudo systemctl start ayhr-frontend
```

---

## ✅ Vérification

### 1. Vérifier les services

```bash
sudo systemctl status ayhr-backend ayhr-frontend
```

### 2. Vérifier la version

```bash
# Backend
grep APP_VERSION /opt/ay-hr/backend/config.py
# Doit afficher: APP_VERSION: str = "1.7.0"

# Frontend (dans le navigateur)
# Ouvrir http://192.168.20.53:8000
# Vérifier le numéro de version en bas du menu : v1.7.0
```

### 3. Vérifier la nouvelle table

```bash
mysql -u root -p ay_hr -e "DESCRIBE incomplete_attendance_logs;"
```

### 4. Vérifier la nouvelle page

1. Se connecter à l'application
2. Vérifier que le lien "Logs Incomplets" apparaît dans la sidebar
3. Cliquer dessus → la page doit s'afficher sans erreur

### 5. Test fonctionnel

1. Importer des logs depuis Attendance
2. Si des logs incomplets sont détectés :
   - Badge de notification sur "Logs Incomplets"
   - Logs apparaissent dans la liste
   - Possibilité de valider/corriger

---

## 🔄 Rollback

Si la mise à jour échoue :

```bash
# 1. Arrêter les services
sudo systemctl stop ayhr-backend ayhr-frontend

# 2. Revenir à la version précédente
cd /opt/ay-hr
sudo git reset --hard v1.3.0

# 3. Restaurer la DB (si migration effectuée)
cd /opt/ay-hr/backups
gunzip -c db_backup_YYYYMMDD.sql.gz | mysql -u root -p ay_hr

# 4. Redémarrer
sudo systemctl start ayhr-backend ayhr-frontend
```

---

## 📝 Notes de Migration

### Changements Backend

**Nouveaux fichiers** :
- `backend/models/incomplete_log.py`
- `backend/schemas/incomplete_log.py`
- `backend/routers/incomplete_logs.py`

**Fichiers modifiés** :
- `backend/services/attendance_service.py` (méthode `import_attendance_logs`)
- `backend/main.py` (ajout router `incomplete_logs`)
- `backend/config.py` (version 1.7.0)

### Changements Frontend

**Nouveaux fichiers** :
- `frontend/src/pages/IncompleteLogs/IncompleteLogsList.jsx`
- `frontend/src/services/incompleteLogs.js`

**Fichiers modifiés** :
- `frontend/src/components/Sidebar.jsx` (ajout lien + version 1.7.0)
- `frontend/src/components/Layout.jsx` (version 1.7.0)
- `frontend/src/pages/Login/LoginPage.jsx` (version 1.7.0)
- `frontend/src/App.jsx` (ajout route `/incomplete-logs`)
- `frontend/package.json` (version 1.7.0)

### Changements Database

**Nouvelle table** :
- `incomplete_attendance_logs` (15 colonnes, 3 index, 2 FK)

**Pas de modification** des tables existantes

---

## 🐛 Problèmes Connus

Aucun problème connu pour cette version.

---

## 📞 Support

En cas de problème :

1. **Consulter les logs** :
   ```bash
   sudo journalctl -u ayhr-backend -f
   ```

2. **Vérifier la DB** :
   ```bash
   mysql -u root -p ay_hr -e "SELECT COUNT(*) FROM incomplete_attendance_logs;"
   ```

3. **Restaurer depuis backup** : Voir section [Rollback](#rollback)

4. **GitHub Issues** : https://github.com/FingaDZ/AY/issues

---

## 📚 Documentation

- [UPDATE_GUIDE.md](UPDATE_GUIDE.md) - Guide de mise à jour complet
- [CHANGELOG.md](CHANGELOG.md) - Historique des versions
- [README.md](README.md) - Documentation générale

---

**Développé par AIRBAND**  
**Date de release** : 28 novembre 2025

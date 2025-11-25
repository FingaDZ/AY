# Déploiement v1.3.0-beta - Intégration Attendance (Backend)

## ⚠️ Important
Cette version inclut **uniquement le backend** de l'intégration Attendance.  
Le frontend sera déployé dans une version ultérieure (v1.3.0 finale).

---

## Prérequis
- Accès SSH au serveur : `192.168.20.53`
- Accès root ou sudo
- Serveur Attendance opérationnel sur `192.168.20.56:8000`

---

## Étapes de Déploiement

### 1. Connexion au Serveur
```bash
ssh root@192.168.20.53
cd /opt/ay-hr
```

### 2. Mise à Jour du Code
```bash
git pull origin main
```

### 3. Migration de la Base de Données
```bash
mysql -u root -p ay_hr < database/migrations/001_attendance_integration.sql
```

**Vérification** :
```bash
mysql -u root -p ay_hr -e "SHOW TABLES LIKE 'attendance%';"
```

Vous devriez voir :
- `attendance_employee_mapping`
- `attendance_import_conflicts`
- `attendance_sync_log`

### 4. Configuration Backend
Ajouter dans `backend/.env` :
```bash
nano backend/.env
```

Ajouter ces lignes :
```env
ATTENDANCE_API_URL=http://192.168.20.56:8000/api
ATTENDANCE_API_TIMEOUT=30
```

### 5. Redémarrer le Backend
```bash
systemctl restart ayhr-backend
```

**Vérification** :
```bash
systemctl status ayhr-backend
```

### 6. Tester l'API
Ouvrir dans le navigateur :
```
http://192.168.20.53:8000/docs
```

Vérifier la présence de la section **"Attendance Integration"** avec les endpoints :
- `POST /api/attendance-integration/sync-employee`
- `POST /api/attendance-integration/sync-all-employees`
- `GET /api/attendance-integration/mappings`
- `POST /api/attendance-integration/import-logs`
- `GET /api/attendance-integration/conflicts`
- `POST /api/attendance-integration/conflicts/{conflict_id}/resolve`

---

## Tests Manuels (via Swagger UI)

### Test 1 : Sync d'un Employé
1. Aller sur `http://192.168.20.53:8000/docs`
2. Trouver `POST /api/attendance-integration/sync-employee`
3. Cliquer "Try it out"
4. Entrer un `employee_id` valide (ex: 1)
5. Exécuter

**Résultat attendu** :
- Si l'employé existe dans Attendance : `success: true` + mapping créé
- Si l'employé n'existe pas : Message demandant de créer manuellement avec photos

### Test 2 : Lister les Mappings
1. Trouver `GET /api/attendance-integration/mappings`
2. Exécuter

**Résultat attendu** : Liste des mappings créés

### Test 3 : Importer des Logs (si logs disponibles)
1. Créer un log de test dans Attendance (employé GHELLAM ABDERREZZAQ)
2. Trouver `POST /api/attendance-integration/import-logs`
3. Entrer :
   ```json
   {
     "start_date": "2025-11-25",
     "end_date": "2025-11-25"
   }
   ```
4. Exécuter

**Résultat attendu** : Summary avec nombre de logs importés

---

## Rollback (si problème)

### Annuler la Migration
```bash
mysql -u root -p ay_hr << EOF
DROP TABLE IF EXISTS attendance_import_conflicts;
DROP TABLE IF EXISTS attendance_sync_log;
DROP TABLE IF EXISTS attendance_employee_mapping;
ALTER TABLE pointages DROP COLUMN IF EXISTS heures_supplementaires;
EOF
```

### Revenir à v1.2.4
```bash
git checkout v1.2.4
systemctl restart ayhr-backend
```

---

## Prochaines Étapes

1. **Tester la sync** : Synchroniser quelques employés manuellement via API
2. **Créer photos** : Uploader photos dans Attendance UI pour les employés synchronisés
3. **Tester import** : Créer des logs de test dans Attendance et les importer
4. **Implémenter Frontend** : Suivre `ATTENDANCE_FRONTEND_GUIDE.md`

---

## Support

En cas de problème :
1. Vérifier les logs backend : `journalctl -u ayhr-backend -f`
2. Vérifier la connexion à Attendance : `curl http://192.168.20.56:8000/api/employees/`
3. Vérifier la base de données : `mysql -u root -p ay_hr`

---

**Déployé le** : 25 Novembre 2025  
**Version** : 1.3.0-beta (Backend Only)

# Guide de Mise à Jour v3.6.1

## 🎯 Objectif
Mise à jour de AY HR System de v3.6.0 vers v3.6.1

## 📦 Changements Principaux

### Backend
- ✅ Modèle Congé: Ajout `mois_deduction` et `annee_deduction`
- ✅ Modèle Crédit: Ajout dates prévisionnelles (`mois_debut`, `annee_debut`, `mois_fin_prevu`, `annee_fin_prevu`)
- ✅ Service employé: Gestion automatique contrats expirés
- ✅ Routes employés: 3 nouveaux endpoints pour contrats expirés
- ✅ Logging amélioré: `user_id`, `user_email`, `ip_address`, `record_id`

### Frontend
- ✅ Version affichée mise à jour: 3.6.1
- ✅ Dashboard: Badge version v3.6.1
- ✅ LoginPage: Footer version 3.6.1

### Base de Données
- ✅ Script migration MySQL pour nouvelles colonnes
- ✅ Index ajoutés pour performances

## 🚀 Instructions de Mise à Jour

### Étape 1: Sauvegarder
```bash
# Sauvegarde base de données MySQL
mysqldump -u root -p ay_hr > backup_v3.6.0_$(date +%Y%m%d).sql

# Sauvegarde fichiers
tar -czf backup_ayhr_v3.6.0.tar.gz /path/to/ay-hr/
```

### Étape 2: Arrêter l'Application
```bash
# Linux/Mac
./stop_ayhr.sh

# Windows
stop_ayhr.bat

# Docker
docker-compose down
```

### Étape 3: Mettre à Jour le Code
```bash
cd /path/to/ay-hr/
git pull origin main
```

### Étape 4: Exécuter la Migration MySQL
```bash
# Connexion MySQL
mysql -u root -p ay_hr < database/migration_v3.6.1_conges_credits_contrats.sql

# OU depuis MySQL shell
mysql> USE ay_hr;
mysql> SOURCE /path/to/database/migration_v3.6.1_conges_credits_contrats.sql;
```

### Étape 5: Mettre à Jour les Dépendances

#### Backend
```bash
cd backend
source .venv/bin/activate  # Linux/Mac
# OU
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
npm run build
```

### Étape 6: Redémarrer l'Application

#### Production (Linux)
```bash
cd /path/to/ay-hr/
./start_ayhr.sh
```

#### Windows
```bash
start_ayhr.bat
```

#### Docker
```bash
docker-compose up -d --build
```

### Étape 7: Vérifier la Mise à Jour
1. Ouvrir le navigateur: `http://localhost` ou votre URL
2. Vérifier version dans Dashboard: doit afficher **v3.6.1**
3. Vérifier version page Login: doit afficher **Version 3.6.1**
4. Tester les nouvelles fonctionnalités:
   - Congés avec mois de déduction
   - Crédits avec échéancier automatique
   - Liste contrats expirés: `GET /employes/contrats-expires`

## 🧪 Tests Recommandés

### Test 1: Congés avec Mois de Déduction
```bash
# Mettre à jour un congé avec mois de déduction différent
curl -X PUT http://localhost:8000/conges/1/consommation \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jours_pris": 2.5,
    "mois_deduction": 12,
    "annee_deduction": 2025
  }'
```

### Test 2: Crédit avec Échéancier
```bash
# Créer un crédit et vérifier calcul auto dates
curl -X POST http://localhost:8000/credits/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employe_id": 1,
    "date_octroi": "2025-12-22",
    "montant_total": 50000,
    "nombre_mensualites": 10
  }'

# Vérifier que mois_debut, annee_debut, etc. sont calculés
```

### Test 3: Contrats Expirés
```bash
# Lister les employés avec contrat expiré
curl -X GET http://localhost:8000/employes/contrats-expires \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Désactiver automatiquement (Admin uniquement)
curl -X POST http://localhost:8000/employes/verifier-contrats-expires \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## 📊 Vérification Base de Données

### Vérifier Nouvelles Colonnes
```sql
-- Congés
DESCRIBE conges;
-- Doit afficher: mois_deduction, annee_deduction

-- Crédits
DESCRIBE credits;
-- Doit afficher: mois_debut, annee_debut, mois_fin_prevu, annee_fin_prevu

-- Index
SHOW INDEX FROM conges WHERE Key_name = 'idx_conges_deduction';
SHOW INDEX FROM credits WHERE Key_name = 'idx_credits_periode';
SHOW INDEX FROM employes WHERE Key_name = 'idx_employes_date_fin_contrat';
```

## ⚠️ Résolution de Problèmes

### Erreur: Column already exists
Si la colonne existe déjà (migration partielle précédente):
```sql
-- Ignorer les erreurs "Column exists" - c'est normal
-- Le script utilise IF NOT EXISTS
```

### Erreur: Permission denied
```bash
# Vérifier permissions fichiers
sudo chown -R www-data:www-data /path/to/ay-hr/

# OU pour votre utilisateur
sudo chown -R $USER:$USER /path/to/ay-hr/
```

### Erreur: Port déjà utilisé
```bash
# Trouver et tuer le processus
sudo netstat -tulpn | grep :8000
sudo kill -9 PID

# OU changer le port dans .env
BACKEND_PORT=8001
```

## 🔄 Rollback (si nécessaire)

### Restaurer Base de Données
```bash
# Restaurer backup
mysql -u root -p ay_hr < backup_v3.6.0_YYYYMMDD.sql
```

### Restaurer Code
```bash
cd /path/to/ay-hr/
git checkout v3.6.0
# OU
tar -xzf backup_ayhr_v3.6.0.tar.gz
```

## 📞 Support

En cas de problème:
1. Vérifier les logs: `backend/logs/` ou `docker logs ayhr-backend`
2. Consulter la documentation: [RELEASE_V3.6.1.md](RELEASE_V3.6.1.md)
3. Contacter le support technique

## ✅ Checklist Post-Migration

- [ ] Version affichée: v3.6.1 (Dashboard et Login)
- [ ] Migration MySQL exécutée sans erreurs
- [ ] Nouvelles colonnes présentes dans la BDD
- [ ] Index créés
- [ ] Backend démarre sans erreurs
- [ ] Frontend build réussi
- [ ] Tests API passent
- [ ] Logs fonctionnent avec user_id/ip_address
- [ ] Nouvelle route contrats-expires accessible
- [ ] Aucune régression détectée

## 🎉 Mise à Jour Réussie !

Félicitations ! AY HR System est maintenant en version 3.6.1.

Profitez des nouvelles fonctionnalités :
- 📅 Gestion flexible des congés
- 💰 Échéancier automatique des crédits
- 🔄 Auto-désactivation contrats expirés
- 🔒 Logging amélioré

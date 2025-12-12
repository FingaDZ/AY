# 🚀 GUIDE DÉPLOIEMENT RAPIDE v3.5.1

**Version** : 3.5.1  
**Date** : 12 décembre 2025  
**Durée estimée** : 10-15 minutes  
**Commits** : 6b2612b, e957b8b, 8aaac70, 2b210e0

---

## ⚡ Commandes Déploiement (Copier-Coller)

```bash
# ÉTAPE 1 : Connexion serveur
ssh root@192.168.20.55

# ÉTAPE 2 : Pull dernières modifications
cd /opt/ay-hr
git pull origin main

# ÉTAPE 3 : Backup base de données (IMPORTANT)
mysqldump -u root -p ay_hr > /tmp/backup_ay_hr_$(date +%Y%m%d_%H%M%S).sql

# ÉTAPE 4 : Migration SQL (si pas déjà fait)
mysql -u root -p ay_hr < database/migration_conges_v3.5.1.sql

# ÉTAPE 5 : Rebuild frontend
cd /opt/ay-hr/frontend
npm run build

# ÉTAPE 6 : Redémarrer services
cd /opt/ay-hr
sudo systemctl restart ayhr-backend
sudo systemctl restart ayhr-frontend

# ÉTAPE 7 : Vérifier services
sudo systemctl status ayhr-backend --no-pager
sudo systemctl status ayhr-frontend --no-pager

# ÉTAPE 8 : Tester version
curl http://localhost:8000/ | grep version
```

---

## ✅ Checklist Validation

### Backend
- [ ] `systemctl status ayhr-backend` → **Active (running)**
- [ ] `journalctl -u ayhr-backend -n 20` → Pas d'erreurs
- [ ] `curl http://localhost:8000/` → `"version": "3.5.1"`

### Frontend
- [ ] `systemctl status ayhr-frontend` → **Active (running)**
- [ ] `ls -lh frontend/dist/` → Fichiers récents (date du jour)
- [ ] Ouvrir navigateur → http://192.168.20.55 → Dashboard affiche **v3.5.1**

### Base de données
- [ ] `mysql -u root -p ay_hr -e "DESCRIBE conges;"` → Colonnes en **INT** (pas DECIMAL)
- [ ] `mysql -u root -p ay_hr -e "SELECT COUNT(*) FROM conges;"` → Données présentes

---

## 🧪 Tests Fonctionnels

### Test 1 : Blocage Congés > Acquis (2 min)

```bash
# Dans navigateur : http://192.168.20.55
1. Login
2. Menu → Congés
3. Sélectionner un employé avec peu de jours acquis (ex: 3j)
4. Cliquer "Modifier" sur un enregistrement
5. Saisir 10 dans "Jours pris"
6. Cliquer "Enregistrer"

✅ ATTENDU : Message erreur "INTERDIT: Congés pris (10j) > Congés acquis (3j)"
❌ SI PROBLÈME : Vérifier logs backend
```

### Test 2 : Notification Bulletins (3 min)

```bash
# Dans navigateur
1. Menu → Salaires → Calcul des Salaires
2. Sélectionner mois actuel (Décembre 2025)
3. Cliquer "Calculer Tous les Salaires"
4. Cliquer "Générer Bulletins de Paie (ZIP)"

✅ ATTENDU : Modal "Attention : Congés non saisis" s'affiche
✅ ATTENDU : Bouton "Oui, aller aux Congés" redirige vers /conges
❌ SI PROBLÈME : Vérifier console navigateur (F12)
```

### Test 3 : Versions Cohérentes (1 min)

```bash
# Vérifier affichages
1. Dashboard → Badge devrait afficher "v3.5.1"
2. Footer bas de page → "v3.5.1"
3. Se déconnecter → Page login → "Version 3.5.1"

✅ ATTENDU : Partout affiche 3.5.1
```

---

## 🐛 Résolution Problèmes

### Problème : Backend ne démarre pas

```bash
# Vérifier logs
sudo journalctl -u ayhr-backend -n 50 --no-pager

# Erreur commune : "Cannot connect to database"
# Solution : Vérifier .env
cat /opt/ay-hr/backend/.env | grep DATABASE_URL

# Restart manuel
cd /opt/ay-hr
source backend/venv/bin/activate
python backend/main.py
# Observer les erreurs
```

### Problème : Frontend pages blanches

```bash
# Vérifier build
ls -lh /opt/ay-hr/frontend/dist/
# Devrait contenir index.html + assets/

# Rebuild forcé
cd /opt/ay-hr/frontend
rm -rf dist
npm run build

# Vérifier Nginx
sudo nginx -t
sudo systemctl status nginx
```

### Problème : Migration SQL échoue

```bash
# Vérifier si déjà appliquée
mysql -u root -p ay_hr -e "DESCRIBE conges;"

# Si colonnes déjà INT → Migration déjà faite
# Si colonnes DECIMAL(5,2) → Appliquer migration

# Forcer migration
mysql -u root -p ay_hr < database/migration_conges_v3.5.1.sql

# Erreur "Duplicate column" → Normal si déjà fait
```

### Problème : Modal notification ne s'affiche pas

```bash
# Vérifier endpoint backend
curl http://localhost:8000/api/conges/verifier-saisie/2025/12

# Devrait retourner JSON avec "a_verifier": true/false

# Si 404 → Backend pas à jour
cd /opt/ay-hr
git pull origin main
sudo systemctl restart ayhr-backend
```

---

## 📊 Monitoring Post-Déploiement

### Premier jour

```bash
# Surveiller logs backend (en direct)
sudo journalctl -u ayhr-backend -f

# Surveiller erreurs uniquement
sudo journalctl -u ayhr-backend -p err -n 50

# Statistiques usage endpoint congés
sudo journalctl -u ayhr-backend | grep "/conges/verifier-saisie" | wc -l
```

### Performance

```bash
# Temps réponse endpoint
time curl http://localhost:8000/api/conges/verifier-saisie/2025/12

# Devrait être < 1 seconde

# Espace disque
df -h /opt/ay-hr
```

---

## 🔄 Rollback (Si Problèmes Majeurs)

```bash
# URGENT : Revenir version précédente

# 1. Rollback code
cd /opt/ay-hr
git checkout e957b8b  # Dernier commit stable avant améliorations

# 2. Restaurer DB depuis backup
mysql -u root -p ay_hr < /tmp/backup_ay_hr_YYYYMMDD_HHMMSS.sql

# 3. Rebuild frontend
cd frontend
npm run build

# 4. Restart
sudo systemctl restart ayhr-backend ayhr-frontend

# 5. Vérifier version
curl http://localhost:8000/ | grep version
# Devrait afficher 3.5.1 (règles congés gardées) ou 3.5.0
```

---

## 📞 Support

### Logs utiles à envoyer si problème

```bash
# Backend
sudo journalctl -u ayhr-backend -n 100 --no-pager > backend_logs.txt

# Frontend
sudo journalctl -u ayhr-frontend -n 50 --no-pager > frontend_logs.txt

# Nginx
sudo tail -100 /var/log/nginx/error.log > nginx_errors.txt

# Database
mysql -u root -p ay_hr -e "SHOW TABLES;" > db_tables.txt
mysql -u root -p ay_hr -e "DESCRIBE conges;" > db_schema_conges.txt
```

### Infos à collecter

- Version OS : `lsb_release -a`
- Version Python : `python3 --version`
- Version Node : `node --version`
- Version MariaDB : `mysql --version`
- Espace disque : `df -h`
- Mémoire RAM : `free -h`

---

## ✅ Succès Déploiement

Si tous les tests passent :

- ✅ Backend démarre proprement
- ✅ Frontend affiche v3.5.1
- ✅ Migration SQL appliquée (colonnes INT)
- ✅ Blocage congés fonctionne
- ✅ Notification bulletins s'affiche
- ✅ Pas d'erreurs dans les logs

**🎉 DÉPLOIEMENT RÉUSSI !**

---

**Document créé le** : 12 décembre 2025  
**Dernière mise à jour** : 12 décembre 2025  
**Version système** : AY HR v3.5.1

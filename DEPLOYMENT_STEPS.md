# 🚀 Guide de Déploiement - Serveur Production 192.168.20.55

**Date**: 9 Décembre 2025  
**Version**: v2.5.0  
**Serveur**: 192.168.20.55

---

## ✅ Prérequis Vérifiés

Le script `update.sh` est **prêt à l'emploi** et configuré correctement :

### Configuration du Script
- ✅ Répertoire application: `/opt/ay-hr`
- ✅ Backend: `/opt/ay-hr/backend`
- ✅ Frontend: `/opt/ay-hr/frontend`
- ✅ Services systemd: `ayhr-backend`, `ayhr-frontend`
- ✅ Support venv ET .venv (flexible)
- ✅ Backup automatique DB + config
- ✅ Git pull depuis `origin main`
- ✅ Migrations DB automatiques
- ✅ Build frontend automatique

---

## 📋 Étapes de Déploiement

### 1. Se connecter au serveur

```bash
ssh root@192.168.20.55
# ou
ssh user@192.168.20.55
sudo su -
```

### 2. Vérifier l'état actuel

```bash
cd /opt/ay-hr
git status
systemctl status ayhr-backend
systemctl status ayhr-frontend
```

### 3. Sauvegarder manuellement (optionnel - le script le fait)

```bash
# Backup manuel si désiré
mysqldump -u ay_hr -p ay_hr > /opt/ay-hr/backups/manual_backup_$(date +%Y%m%d).sql
tar -czf /opt/ay-hr/backups/manual_config_$(date +%Y%m%d).tar.gz /opt/ay-hr/backend/.env
```

### 4. Lancer la mise à jour

```bash
cd /opt/ay-hr
chmod +x update.sh
./update.sh
```

### 5. Suivre les logs en temps réel (autre terminal)

```bash
# Logs de mise à jour
tail -f /opt/ay-hr/logs/update_*.log

# Logs backend après mise à jour
sudo journalctl -u ayhr-backend -f

# Logs frontend après mise à jour
sudo journalctl -u ayhr-frontend -f
```

---

## 🔍 Ce que fait le Script update.sh

### Phase 1: Vérifications (0/8)
- Vérification root
- Vérification répertoires
- Création logs et backups
- Lecture version actuelle

### Phase 2: Backup DB (1/8)
- Extraction credentials depuis `.env`
- Dump MySQL avec mysqldump
- Compression gzip
- Stockage dans `/opt/ay-hr/backups/`

### Phase 3: Backup Config (2/8)
- Sauvegarde `.env` et `config.py`
- Archive tar.gz
- Horodatage automatique

### Phase 4: Arrêt Services (3/8)
- `systemctl stop ayhr-backend`
- `systemctl stop ayhr-frontend`
- Kill process port 8000 (si bloqué)

### Phase 5: Git Pull (4/8)
- Stash changements locaux
- `git pull origin main`
- Lecture nouvelle version

### Phase 6: Backend Update (5/8)
- Activation environnement virtuel
- `pip install --upgrade pip`
- `pip install -r requirements.txt`
- Exécution `fix_db_schema.py` (migrations)
- Nettoyage cache Python

### Phase 7: Frontend Update (6/8)
- `npm install`
- `npm run build`
- Build production dans `dist/`

### Phase 8: Permissions (7/8)
- `chown -R root:root /opt/ay-hr`
- `chmod +x *.sh`
- Permissions logs et backups

### Phase 9: Redémarrage (8/8)
- `systemctl start ayhr-backend`
- `systemctl start ayhr-frontend`
- Vérification statut services
- Nettoyage backups >30 jours

---

## 📊 Résumé de la Mise à Jour v2.5.0

### Nouveautés
```
✅ ANALYSE_PROJET.md
   - Analyse exhaustive: 20+ modèles BD
   - 80+ endpoints API documentés
   - Formule calcul salaire (12 étapes)
   - Relations et contraintes FK

✅ SESSION_RAPPORT.md
   - Récapitulatif session
   - État projet complet
   - Commandes utiles

✅ Serveur Production
   - Ancien: 192.168.20.53
   - Nouveau: 192.168.20.55
   - update.sh prêt

✅ Frontend
   - react-hot-toast v2.6.0
   - Sidebar version v2.5.0

✅ Backend
   - Migration IRG simplifiée
   - Config.py APP_VERSION: 2.5.0
```

---

## 🔧 En Cas de Problème

### Si le script échoue

```bash
# 1. Vérifier les logs
cat /opt/ay-hr/logs/update_*.log | tail -100

# 2. Restaurer backup DB
cd /opt/ay-hr/backups
gunzip -c db_backup_YYYYMMDD_HHMMSS.sql.gz | mysql -u ay_hr -p ay_hr

# 3. Restaurer config
tar -xzf config_backup_YYYYMMDD_HHMMSS.tar.gz -C /

# 4. Redémarrer services manuellement
systemctl restart ayhr-backend
systemctl restart ayhr-frontend
```

### Si les services ne démarrent pas

```bash
# Backend
systemctl status ayhr-backend -l
journalctl -u ayhr-backend -n 100 --no-pager

# Frontend
systemctl status ayhr-frontend -l
journalctl -u ayhr-frontend -n 100 --no-pager

# Vérifier connexion DB
cd /opt/ay-hr/backend
source venv/bin/activate
python -c "from database import engine; print(engine)"
```

### Si Git pull échoue

```bash
cd /opt/ay-hr
git status
git stash
git pull origin main --rebase
```

---

## ✅ Vérifications Post-Déploiement

### 1. Vérifier les services

```bash
systemctl status ayhr-backend
systemctl status ayhr-frontend

# Doivent afficher: active (running)
```

### 2. Tester l'API

```bash
curl http://192.168.20.55:8000/docs
curl http://192.168.20.55:8000/api/parametres/

# Devrait retourner du JSON
```

### 3. Tester le Frontend

```bash
curl http://192.168.20.55:3000

# Devrait retourner du HTML
```

### 4. Vérifier la version

```bash
curl http://192.168.20.55:8000/api/parametres/ | grep version
# ou
grep APP_VERSION /opt/ay-hr/backend/config.py
# Devrait afficher: 2.5.0
```

### 5. Accès navigateur

```
http://192.168.20.55:3000 (frontend)
http://192.168.20.55:8000/docs (API docs)
```

---

## 📝 Logs Importants

### Localisation
```
/opt/ay-hr/logs/update_YYYYMMDD_HHMMSS.log
/opt/ay-hr/backups/db_backup_YYYYMMDD_HHMMSS.sql.gz
/opt/ay-hr/backups/config_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Surveillance
```bash
# Backend en temps réel
sudo journalctl -u ayhr-backend -f

# Frontend en temps réel
sudo journalctl -u ayhr-frontend -f

# Tous les services système
sudo journalctl -f
```

---

## 🎯 Checklist Complète

Avant de lancer `update.sh` :
- [ ] Connexion SSH établie sur 192.168.20.55
- [ ] Accès root (sudo su -)
- [ ] Sauvegarde manuelle optionnelle faite
- [ ] Utilisateurs avertis de la maintenance

Pendant l'exécution :
- [ ] Suivre logs dans terminal secondaire
- [ ] Vérifier aucune erreur rouge
- [ ] Attendre fin complète (8/8)

Après l'exécution :
- [ ] Services actifs (systemctl status)
- [ ] API accessible (curl /docs)
- [ ] Frontend accessible (navigateur)
- [ ] Version correcte (2.5.0)
- [ ] Connexion DB fonctionnelle
- [ ] Aucune erreur dans journalctl

---

## 🚨 Contacts Support

En cas de problème critique :
1. Consulter `ANALYSE_PROJET.md` (architecture complète)
2. Consulter `SESSION_RAPPORT.md` (commandes utiles)
3. Vérifier GitHub: https://github.com/FingaDZ/AY
4. Rollback avec les backups

---

## 📌 Notes Importantes

1. **Backup automatique**: Le script fait backup DB + config automatiquement
2. **Downtime**: ~2-3 minutes pendant la mise à jour
3. **Rollback**: Possible avec backups horodatés
4. **Git stash**: Changements locaux préservés automatiquement
5. **Python venv**: Support venv/ ET .venv/ (flexible)
6. **Nettoyage**: Backups >30 jours supprimés automatiquement

---

**Préparé par**: GitHub Copilot  
**Date**: 9 Décembre 2025  
**Version script**: update.sh v2.2


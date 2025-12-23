# Guide de Déploiement v3.6.1 - Serveur 192.168.20.55

## 📋 Information Serveur

- **Adresse**: 192.168.20.55
- **Utilisateur**: root
- **Version déployée**: 3.6.1
- **Date**: 23 Décembre 2025

---

## 🚀 Méthode 1: Déploiement Automatique (PowerShell)

### Depuis Windows

```powershell
# Exécuter le script de déploiement
.\deploy_v3.6.1_server_55.ps1
```

Le script effectuera automatiquement:
1. ✅ Vérification de la connexion SSH
2. 💾 Sauvegarde de la base de données
3. 📦 Sauvegarde des fichiers actuels
4. 🔄 Mise à jour du code depuis GitHub
5. 🗄️ Application des migrations SQL
6. 📚 Installation des dépendances Python
7. 🔁 Redémarrage des services

---

## 🛠️ Méthode 2: Déploiement Manuel

### 1. Connexion au Serveur

```powershell
ssh root@192.168.20.55
```

### 2. Sauvegarde

```bash
# Créer le répertoire de sauvegarde
mkdir -p /root/backups/ay_hr

# Sauvegarder la base de données
mysqldump -u root -p ay_hr > /root/backups/ay_hr/ay_hr_backup_$(date +%Y%m%d_%H%M%S).sql

# Sauvegarder les fichiers (si le répertoire existe)
if [ -d '/root/AY_HR' ]; then
    cp -r /root/AY_HR /root/backups/ay_hr/ay_hr_files_$(date +%Y%m%d_%H%M%S)
fi
```

### 3. Mise à Jour du Code

```bash
# Si le dépôt existe déjà
cd /root/AY_HR
git fetch origin
git reset --hard origin/main
git pull origin main

# OU si c'est une nouvelle installation
cd /root
rm -rf AY_HR
git clone https://github.com/FingaDZ/AY.git AY_HR
cd AY_HR
```

### 4. Migration Base de Données

```bash
cd /root/AY_HR/database

# Appliquer la migration v3.6.1
mysql -u root -p ay_hr < migration_v3.6.1_conges_credits_contrats.sql
```

**Contenu de la migration v3.6.1:**
- ✅ Table `conges`: Colonnes `mois_deduction`, `annee_deduction`
- ✅ Table `credits`: Colonnes `mois_debut`, `annee_debut`, `mois_fin_prevu`, `annee_fin_prevu`
- ✅ Table `avances`: Colonnes `mois_debut`, `annee_debut`

### 5. Mise à Jour Backend

```bash
cd /root/AY_HR/backend

# Activer/Créer environnement virtuel
if [ -d 'venv' ]; then
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
fi

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Vérifier la Configuration

```bash
# Vérifier le fichier .env
cd /root/AY_HR/backend
cat .env

# S'assurer que ces variables sont définies:
# DATABASE_URL=mysql+pymysql://root:PASSWORD@localhost/ay_hr
# SECRET_KEY=votre_clef_secrete
# CORS_ORIGINS=http://localhost:3000,http://192.168.20.55:3000
```

### 7. Redémarrer les Services

```bash
# Arrêter les processus existants
pkill -f 'uvicorn main:app' || echo 'Aucun processus backend'
pkill -f 'npm.*vite' || echo 'Aucun processus frontend'

# Démarrer le backend
cd /root/AY_HR/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/ay_hr_backend.log 2>&1 &

# Vérifier le démarrage
tail -f /var/log/ay_hr_backend.log
```

### 8. Build Frontend (Optionnel)

```bash
cd /root/AY_HR/frontend

# Installer les dépendances
npm install

# Build de production
npm run build

# Les fichiers sont dans dist/
```

---

## ✅ Vérification du Déploiement

### 1. Vérifier l'API

```bash
# Depuis le serveur
curl http://localhost:8000/docs

# Depuis votre machine
curl http://192.168.20.55:8000/docs
```

### 2. Vérifier les Logs

```bash
# Logs backend
tail -f /var/log/ay_hr_backend.log

# Logs système (si PM2 utilisé)
pm2 logs ay-hr-backend
```

### 3. Tester les Endpoints

```bash
# Test de santé
curl http://192.168.20.55:8000/

# Documentation API
http://192.168.20.55:8000/docs

# Documentation Redoc
http://192.168.20.55:8000/redoc
```

### 4. Vérifier la Version

```bash
cd /root/AY_HR/backend
grep "APP_VERSION" config.py
# Devrait afficher: APP_VERSION: str = "3.6.1"
```

---

## 🎯 Nouvelles Fonctionnalités v3.6.1

### 1. Gestion Avancée des Congés

**Endpoints:**
```
GET    /conges                    # Liste tous les congés
POST   /conges                    # Créer un congé avec mois_deduction
PUT    /conges/{id}               # Modifier un congé
DELETE /conges/{id}               # Supprimer un congé
```

**Test:**
```bash
# Créer un congé avec déduction différée
curl -X POST http://192.168.20.55:8000/conges \
  -H "Content-Type: application/json" \
  -d '{
    "employe_id": 1,
    "mois": 12,
    "annee": 2025,
    "jours_conges_acquis": 2.5,
    "mois_deduction": 1,
    "annee_deduction": 2026
  }'
```

### 2. Échéancier Automatique Crédits

**Endpoints:**
```
GET    /credits                   # Liste tous les crédits
POST   /credits                   # Créer crédit (dates auto)
PUT    /credits/{id}              # Modifier un crédit
```

**Test:**
```bash
# Créer un crédit avec calcul automatique des dates
curl -X POST http://192.168.20.55:8000/credits \
  -H "Content-Type: application/json" \
  -d '{
    "employe_id": 1,
    "montant": 50000,
    "nombre_mensualites": 10,
    "date_credit": "2025-12-15"
  }'
# Les champs mois_debut, annee_debut, mois_fin_prevu, annee_fin_prevu
# sont calculés automatiquement
```

### 3. Auto-Désactivation Contrats Expirés

**Nouveaux Endpoints:**
```
GET    /employes/contrats-expires              # Lister sans désactiver
POST   /employes/verifier-contrats-expires     # Désactiver (Admin)
POST   /employes/mettre-a-jour-dates-fin-contrat  # Calculer dates
```

**Test:**
```bash
# Lister les contrats expirés
curl http://192.168.20.55:8000/employes/contrats-expires

# Désactiver automatiquement (nécessite token admin)
curl -X POST http://192.168.20.55:8000/employes/verifier-contrats-expires \
  -H "Authorization: Bearer <TOKEN_ADMIN>"
```

---

## 🔧 Dépannage

### Problème: API ne démarre pas

```bash
# Vérifier les logs
tail -100 /var/log/ay_hr_backend.log

# Vérifier si le port 8000 est utilisé
lsof -i :8000

# Tuer le processus si nécessaire
kill -9 $(lsof -t -i :8000)
```

### Problème: Erreur de connexion à MySQL

```bash
# Tester la connexion MySQL
mysql -u root -p -e "SHOW DATABASES;"

# Vérifier que ay_hr existe
mysql -u root -p -e "USE ay_hr; SHOW TABLES;"

# Vérifier le .env
cd /root/AY_HR/backend
cat .env | grep DATABASE_URL
```

### Problème: Migration échoue

```bash
# Vérifier si les colonnes existent déjà
mysql -u root -p ay_hr -e "DESCRIBE conges;"
mysql -u root -p ay_hr -e "DESCRIBE credits;"
mysql -u root -p ay_hr -e "DESCRIBE avances;"

# Si les colonnes existent, la migration a déjà été appliquée
```

### Problème: Module Python manquant

```bash
cd /root/AY_HR/backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Surveillance Post-Déploiement

### Vérifications Quotidiennes

```bash
# 1. Logs backend
tail -50 /var/log/ay_hr_backend.log

# 2. Processus en cours
ps aux | grep uvicorn

# 3. Espace disque
df -h

# 4. Mémoire
free -h
```

### Logs à Surveiller

```bash
# Logs des désactivations automatiques
mysql -u root -p ay_hr -e "
  SELECT * FROM logs 
  WHERE action = 'contract_auto_deactivation' 
  ORDER BY timestamp DESC 
  LIMIT 10;
"

# Logs des modifications de congés
mysql -u root -p ay_hr -e "
  SELECT * FROM logs 
  WHERE table_name = 'conges' 
  ORDER BY timestamp DESC 
  LIMIT 10;
"
```

---

## 📞 Support

**En cas de problème:**

1. Vérifier les logs: `/var/log/ay_hr_backend.log`
2. Vérifier l'état du service
3. Consulter la documentation: [INDEX_DOCUMENTATION.md](INDEX_DOCUMENTATION.md)
4. Restaurer depuis la sauvegarde si nécessaire

**Restauration d'urgence:**

```bash
# Trouver la dernière sauvegarde
ls -lt /root/backups/ay_hr/

# Restaurer la base de données
mysql -u root -p ay_hr < /root/backups/ay_hr/ay_hr_backup_YYYYMMDD_HHMMSS.sql

# Restaurer les fichiers
cp -r /root/backups/ay_hr/ay_hr_files_YYYYMMDD_HHMMSS /root/AY_HR
```

---

## 🎉 Succès!

Une fois le déploiement terminé:

✅ Version 3.6.1 déployée
✅ API accessible sur http://192.168.20.55:8000
✅ Documentation sur http://192.168.20.55:8000/docs
✅ Nouvelles fonctionnalités opérationnelles
✅ Sauvegardes créées

**Date de déploiement**: 23 Décembre 2025  
**Version**: 3.6.1  
**Statut**: Production

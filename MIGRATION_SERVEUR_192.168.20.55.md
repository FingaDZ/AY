# Guide Migration v3.5.0 sur Serveur 192.168.20.55

## 🎯 Objectif
Déployer les modifications PDF v3.5.0 sur le serveur de production

**Serveur**: 192.168.20.55  
**Base de données**: ay_hr  
**Version cible**: 3.5.0

---

## 📋 Prérequis

1. Accès SSH au serveur
2. Droits sudo sur le serveur
3. Accès MySQL (root ou utilisateur avec droits ALTER TABLE)
4. Backend AY HR déjà installé sur le serveur

---

## 🚀 ÉTAPE 1: Connexion au Serveur Ubuntu

### Depuis votre machine locale (Windows PowerShell)

```powershell
# Connexion SSH
ssh utilisateur@192.168.20.55

# OU si vous avez une clé SSH
ssh -i chemin\vers\cle.pem utilisateur@192.168.20.55
```

**Remplacez `utilisateur` par votre nom d'utilisateur sur le serveur Ubuntu**

### Note: Le serveur est sous Ubuntu Linux

---

## 📤 ÉTAPE 2: Transfert des Fichiers

### Option A: Via Git (RECOMMANDÉ)

```bash
# Sur le serveur, aller dans le répertoire du projet
cd /chemin/vers/AY_HR

# Récupérer les dernières modifications
git pull origin main

# Vérifier que vous êtes sur la bonne version
git log --oneline -1
```

### Option B: Via SCP (depuis votre machine Windows)

```powershell
# Transférer le fichier de migration
scp "f:\Code\AY HR\database\migrations\add_numero_anem.sql" utilisateur@192.168.20.55:/tmp/

# Transférer le fichier pdf_generator.py
scp "f:\Code\AY HR\backend\services\pdf_generator.py" utilisateur@192.168.20.55:/tmp/

# Transférer le fichier config.py
scp "f:\Code\AY HR\backend\config.py" utilisateur@192.168.20.55:/tmp/
```

Puis sur le serveur:
```bash
# Copier les fichiers au bon endroit
sudo cp /tmp/add_numero_anem.sql /chemin/vers/AY_HR/database/migrations/
sudo cp /tmp/pdf_generator.py /chemin/vers/AY_HR/backend/services/
sudo cp /tmp/config.py /chemin/vers/AY_HR/backend/

# Ajuster les permissions
sudo chown -R ayhr:ayhr /chemin/vers/AY_HR/backend/
```

---

## 🗄️ ÉTAPE 3: Migration Base de Données

### Vérifier l'accès MySQL

```bash
# Tester la connexion
mysql -u root -p -e "SHOW DATABASES;" | grep ay_hr
```

### Exécuter la migration

```bash
# Aller dans le répertoire des migrations
cd /chemin/vers/AY_HR/database/migrations

# Exécuter la migration
mysql -u root -p ay_hr < add_numero_anem.sql
```

**Entrez le mot de passe MySQL quand demandé**

### Vérifier que la migration est réussie

```bash
# Vérifier que la colonne existe
mysql -u root -p ay_hr -e "DESCRIBE employes;" | grep numero_anem
```

**Résultat attendu:**
```
numero_anem | varchar(50) | YES | | NULL |
```

Si vous voyez cette ligne, la migration est réussie ✅

---

## 🐍 ÉTAPE 4: Installer les Dépendances Python

```bash
# Aller dans le répertoire backend
cd /chemin/vers/AY_HR/backend

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les nouvelles dépendances
pip install qrcode[pil] pillow reportlab

# Vérifier l'installation
python -c "import qrcode; from reportlab.lib.utils import ImageReader; print('OK')"
```

**Si vous voyez "OK", les dépendances sont installées ✅**

---

## 🔄 ÉTAPE 5: Redémarrer le Backend

### Option A: Avec systemd

```bash
# Vérifier le nom du service
sudo systemctl list-units | grep ayhr

# Redémarrer le service
sudo systemctl restart ayhr-backend

# Vérifier le statut
sudo systemctl status ayhr-backend
```

### Option B: Avec PM2

```bash
# Lister les processus PM2
pm2 list

# Redémarrer l'application
pm2 restart ayhr-backend

# Vérifier les logs
pm2 logs ayhr-backend --lines 20
```

### Option C: Manuellement (si pas de service)

```bash
# Arrêter l'ancien processus (trouver le PID)
ps aux | grep uvicorn
sudo kill -9 <PID>

# Redémarrer
cd /chemin/vers/AY_HR/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/ayhr-backend.log 2>&1 &
```

---

## ✅ ÉTAPE 6: Tests de Validation

### Test 1: Vérifier que le backend démarre

```bash
# Test API
curl http://192.168.20.55:8000/ | grep "3.5.0"
```

**Résultat attendu:** Vous devriez voir "3.5.0" dans la réponse

### Test 2: Vérifier les logs

```bash
# Voir les derniers logs
tail -f /var/log/ayhr-backend.log

# OU avec systemd
sudo journalctl -u ayhr-backend -n 50 -f
```

**Vérifiez qu'il n'y a pas d'erreurs**

### Test 3: Tester la génération PDF

Depuis votre navigateur, connectez-vous à l'application et testez:
1. **Attestation de travail** → Générer le PDF → Scanner le QR code
2. **Contrat de travail** → Générer le PDF → Vérifier le numéro de contrat
3. **Rapport salaires** → Générer le PDF → Vérifier le footer

---

## 🔍 ÉTAPE 7: Vérification Complète

### Checklist de validation

```bash
# 1. Version backend
curl http://192.168.20.55:8000/ | jq .version

# 2. Colonne numero_anem
mysql -u root -p ay_hr -e "SELECT COUNT(*) FROM employes;"
mysql -u root -p ay_hr -e "SHOW COLUMNS FROM employes LIKE 'numero_anem';"

# 3. Backend actif
sudo systemctl is-active ayhr-backend
# OU
pm2 status ayhr-backend

# 4. Logs sans erreur
sudo journalctl -u ayhr-backend --since "5 minutes ago" | grep -i error
```

---

## 🚨 Dépannage

### Problème: La migration SQL échoue

```bash
# Vérifier que la base existe
mysql -u root -p -e "SHOW DATABASES;" | grep ay_hr

# Vérifier les droits
mysql -u root -p -e "SHOW GRANTS FOR CURRENT_USER();"

# Essayer manuellement
mysql -u root -p
USE ay_hr;
ALTER TABLE employes ADD COLUMN IF NOT EXISTS numero_anem VARCHAR(50);
CREATE INDEX IF NOT EXISTS idx_numero_anem ON employes(numero_anem);
EXIT;
```

### Problème: Module qrcode introuvable

```bash
# Réinstaller avec force
cd /chemin/vers/AY_HR/backend
source venv/bin/activate
pip uninstall qrcode pillow -y
pip install --no-cache-dir qrcode[pil] pillow
```

### Problème: Backend ne démarre pas

```bash
# Vérifier les erreurs Python
cd /chemin/vers/AY_HR/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Regarder les erreurs et corriger
```

### Problème: Port 8000 déjà utilisé

```bash
# Trouver le processus
sudo lsof -i :8000

# Arrêter le processus
sudo kill -9 <PID>

# OU utiliser un autre port
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

## 🔙 Rollback (si nécessaire)

Si quelque chose ne fonctionne pas:

```bash
# 1. Revenir au commit précédent
cd /chemin/vers/AY_HR
git log --oneline -5
git checkout <commit-precedent>

# 2. Supprimer la colonne
mysql -u root -p ay_hr -e "ALTER TABLE employes DROP COLUMN numero_anem;"

# 3. Redémarrer le backend
sudo systemctl restart ayhr-backend
```

---

## 📞 Support

En cas de problème:
1. Vérifier les logs: `/var/log/ayhr-backend.log`
2. Vérifier le statut: `systemctl status ayhr-backend`
3. Tester manuellement: `uvicorn main:app --reload`

---

## 🎉 Finalisation

Une fois tous les tests validés:

```bash
# Créer un backup de la base
mysqldump -u root -p ay_hr > /backup/ay_hr_v3.5.0_$(date +%Y%m%d).sql

# Documenter le déploiement
echo "v3.5.0 déployée le $(date)" >> /var/log/ayhr-deployments.log
```

---

**✅ Migration terminée avec succès !**

*Guide créé le 10 décembre 2025*  
*AY HR Management System v3.5.0*

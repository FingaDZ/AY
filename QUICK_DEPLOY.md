# 🚀 DÉPLOIEMENT RAPIDE v3.5.0 - Serveur Ubuntu 192.168.20.55

## ⚡ Guide Express (3 minutes)

### 1️⃣ Connexion SSH

```powershell
# Depuis votre PC Windows
ssh utilisateur@192.168.20.55
```

---

### 2️⃣ Push vers GitHub (Depuis Windows)

```powershell
# Depuis votre PC Windows (PowerShell)
cd "f:\Code\AY HR"

# Commit et push
git add -A
git commit -m "feat(pdf): v3.5.0 - PDF enhancements + ANEM integration"
git push origin main

# Optionnel: Créer un tag
git tag v3.5.0
git push origin v3.5.0
```

### 3️⃣ Pull sur le Serveur Ubuntu

```bash
# Sur le serveur Ubuntu
cd /chemin/vers/AY_HR

# Récupérer les modifications
git pull origin main

# Vérifier la version
git log --oneline -1
```

---

### 4️⃣ Exécuter la Migration (Sur le serveur Ubuntu)

```bash
# Aller dans le projet
cd /chemin/vers/AY_HR

# 1. Backup
mysqldump -u root -p ay_hr > /tmp/backup_$(date +%Y%m%d).sql

# 2. Migration SQL
mysql -u root -p ay_hr < database/migrations/add_numero_anem.sql

# 3. Vérifier
mysql -u root -p ay_hr -e "DESCRIBE employes;" | grep numero_anem
# ✓ Vous devez voir: numero_anem | varchar(50) | YES

# 4. Installer dépendances Python
cd backend
source venv/bin/activate
pip install qrcode[pil] pillow reportlab
python -c "import qrcode; from reportlab.lib.utils import ImageReader; print('OK')"
deactivate

# 5. Redémarrer backend
sudo systemctl restart ayhr-backend
# OU si PM2:
# pm2 restart ayhr-backend

# 6. Vérifier
curl http://localhost:8000/ | grep "3.5.0"
sudo systemctl status ayhr-backend
```

---

### 5️⃣ Tests

Depuis l'interface web:
- ✅ Générer une **Attestation** → Scanner le QR code
- ✅ Générer un **Contrat** → Vérifier numéro + QR code
- ✅ Générer **Rapport Salaires** → Vérifier footer

---

## 🔧 Chemins Communs sur Ubuntu

Selon votre installation, le projet peut être ici:
- `/opt/ay_hr`
- `/var/www/ay_hr`
- `/home/utilisateur/ay_hr`
- `/srv/ay_hr`

**Adaptez les commandes selon votre chemin !**

---

## 📋 Script Automatique (Optionnel)

Si vous voulez tout automatiser, créez ce script sur le serveur:

```bash
# Sur le serveur Ubuntu, créer le fichier
nano ~/migrate_v3.5.0.sh
```

Collez ce contenu:

```bash
#!/bin/bash
PROJECT="/opt/ay_hr"  # ADAPTER ICI

cd $PROJECT
mysqldump -u root -p ay_hr > /tmp/backup_$(date +%Y%m%d).sql
mysql -u root -p ay_hr < database/migrations/add_numero_anem.sql
cd backend
source venv/bin/activate
pip install qrcode[pil] pillow reportlab --quiet
deactivate
sudo systemctl restart ayhr-backend
sleep 2
curl http://localhost:8000/ | grep "3.5.0" && echo "✓ Migration OK"
```

Exécutez:
```bash
chmod +x ~/migrate_v3.5.0.sh
~/migrate_v3.5.0.sh
```

---

## 🚨 Dépannage Rapide

### Problème: Permission denied

```bash
sudo chown -R $USER:$USER /chemin/vers/AY_HR
```

### Problème: Backend ne redémarre pas

```bash
# Voir les logs
sudo journalctl -u ayhr-backend -n 50

# Redémarrer manuellement
cd /chemin/vers/AY_HR/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Problème: Port 8000 occupé

```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Problème: Module qrcode introuvable

```bash
cd /chemin/vers/AY_HR/backend
source venv/bin/activate
pip install --force-reinstall qrcode[pil] pillow
```

---

## 🔙 Rollback (Si Problème)

```bash
# Restaurer la base
mysql -u root -p ay_hr < /tmp/backup_YYYYMMDD.sql

# Revenir au code précédent
cd /chemin/vers/AY_HR
git checkout v3.0.0  # Ou le tag précédent

# Redémarrer
sudo systemctl restart ayhr-backend
```

---

## ✅ Checklist Finale

- [ ] Connexion SSH fonctionne
- [ ] Fichiers transférés sur le serveur
- [ ] Backup BDD créé
- [ ] Migration SQL exécutée
- [ ] Colonne `numero_anem` existe
- [ ] Dépendances Python installées
- [ ] Backend redémarré sans erreur
- [ ] Version 3.5.0 affichée dans l'API
- [ ] PDF Attestation génère QR code
- [ ] PDF Contrat affiche numéro + QR code

---

## 📞 Besoin d'Aide?

**Logs en temps réel:**
```bash
sudo journalctl -u ayhr-backend -f
```

**Tester l'API:**
```bash
curl http://localhost:8000/
curl http://localhost:8000/docs
```

**Vérifier le service:**
```bash
sudo systemctl status ayhr-backend
```

---

**✨ Bon déploiement !**

*Guide créé le 10 décembre 2025 - AY HR v3.5.0*

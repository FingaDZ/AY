# 🚀 Guide de Déploiement Rapide - AY HR v3.5.0

## 📋 Pré-requis

- Base de données ay_hr existante et accessible
- Serveur avec Python 3.10+ et Node.js 18+
- Accès SSH au serveur
- Droits sudo

---

## ⚡ Déploiement Express (5 minutes)

### 1. Mise à Jour du Code

```bash
# Sur le serveur
cd /path/to/AY_HR
git pull origin main
```

### 2. Migration Base de Données

```bash
# Appliquer la migration numero_anem
mysql -u root -p ay_hr < database/migrations/add_numero_anem.sql

# Vérification
mysql -u root -p ay_hr -e "DESCRIBE employes;" | grep numero_anem
```

**Résultat attendu :**
```
numero_anem | varchar(50) | YES | | NULL |
```

### 3. Backend

```bash
cd backend

# Activer l'environnement virtuel
source venv/bin/activate  # Linux
# OU
.\venv\Scripts\activate  # Windows

# Installer les dépendances (si nouvelles)
pip install -r requirements.txt

# Redémarrer le service
sudo systemctl restart ayhr-backend  # Linux
# OU
pm2 restart ayhr-backend  # PM2
```

**Vérification Backend :**
```bash
curl http://localhost:8000/
# Devrait retourner: {"message": "HR System API", "version": "3.5.0"}
```

### 4. Frontend

```bash
cd ../frontend

# Installer dépendances (si nouvelles)
npm install

# Build production
npm run build

# Copier vers nginx (adapter le chemin)
sudo cp -r dist/* /var/www/html/ay-hr/

# OU redémarrer service Node
sudo systemctl restart ayhr-frontend
```

**Vérification Frontend :**
- Accéder à l'interface web
- Vérifier en bas de page : **Version 3.5.0**

---

## 🧪 Tests de Validation

### 1. Test Backend
```bash
# Tester l'endpoint version
curl http://localhost:8000/ | jq .version
# Sortie: "3.5.0"

# Tester la génération PDF (exemple avec employe_id=1)
curl -X GET "http://localhost:8000/api/employes/1/attestation" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o test_attestation.pdf

# Vérifier le PDF contient un QR code
file test_attestation.pdf
# Sortie: test_attestation.pdf: PDF document, version 1.4
```

### 2. Test Frontend
1. **Connexion** : Se connecter à l'interface
2. **Version** : Vérifier footer = "v3.5.0"
3. **Employé** : Créer/modifier un employé, ajouter un N° ANEM
4. **Documents** :
   - Générer une attestation de travail
   - Vérifier présence du QR code
   - Scanner le QR code (devrait contenir N°ANEM)
5. **Bulletin** :
   - Calculer un salaire
   - Générer le bulletin PDF
   - Vérifier ligne "Jours de congé pris"
   - Vérifier footer "Powered by AIRBAND"
6. **Rapport** :
   - Générer rapport salaires
   - Vérifier footer en pied de page
   - Vérifier marges étroites

---

## 🐛 Dépannage

### Erreur : "Column 'numero_anem' doesn't exist"

```bash
# La migration n'a pas été appliquée
mysql -u root -p ay_hr < database/migrations/add_numero_anem.sql
sudo systemctl restart ayhr-backend
```

### Erreur : "ModuleNotFoundError: No module named 'qrcode'"

```bash
cd backend
source venv/bin/activate
pip install qrcode[pil] pillow
sudo systemctl restart ayhr-backend
```

### PDF ne génère pas de QR code

```bash
# Vérifier l'installation de Pillow
python -c "from PIL import Image; print('OK')"

# Si erreur, réinstaller
pip uninstall pillow
pip install pillow --no-cache-dir
```

### Version affichée est "3.0.0" au lieu de "3.5.0"

```bash
# Vérifier config.py
cat backend/config.py | grep APP_VERSION
# Devrait montrer: APP_VERSION: str = "3.5.0"

# Vérifier package.json
cat frontend/package.json | grep version
# Devrait montrer: "version": "3.5.0"

# Rebuild si nécessaire
cd frontend
npm run build
sudo cp -r dist/* /var/www/html/ay-hr/
```

### Bulletin PDF ne montre pas la ligne congés

```bash
# Vérifier que salaire_data contient jours_conges
# Le calcul doit récupérer les congés du mois
# Si aucun congé pris, la ligne affichera "0 j"
```

---

## 📦 Rollback (si problème)

### Revenir à la version précédente

```bash
# Backend
cd /path/to/AY_HR
git checkout v3.0.0  # ou le tag de la version stable précédente
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ayhr-backend

# Frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/html/ay-hr/

# Base de données (supprimer la colonne si nécessaire)
mysql -u root -p ay_hr -e "ALTER TABLE employes DROP COLUMN numero_anem;"
```

---

## ✅ Checklist Post-Déploiement

- [ ] Backend démarre sans erreur (`systemctl status ayhr-backend`)
- [ ] Frontend accessible (http://your-domain.com)
- [ ] Version affichée = "3.5.0"
- [ ] Colonne `numero_anem` existe dans table `employes`
- [ ] Attestation de travail génère QR code
- [ ] Certificat de travail génère QR code
- [ ] Bulletin de paie contient ligne congés
- [ ] Rapport salaires a footer en pied de page
- [ ] Contrat génère numéro unique (CT-XXXX-YYYY)

---

## 📞 Support

En cas de problème :
1. Consulter les logs : `sudo journalctl -u ayhr-backend -n 100`
2. Vérifier la base de données : `mysql -u root -p ay_hr`
3. Tester l'API : `curl http://localhost:8000/`
4. Ouvrir une issue GitHub : https://github.com/FingaDZ/AY/issues

---

**✨ Déploiement réussi ! Profitez de la version 3.5.0 !**

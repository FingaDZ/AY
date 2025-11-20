# Tests de Déploiement G29 ✅

**Date:** 18 novembre 2025  
**Status:** ✅ DÉPLOYÉ avec succès

## 🎯 Résumé des Déploiements

### ✅ Localhost (Développement)
- **Backend:** http://localhost:8000 ✅ ACTIF
- **Frontend:** http://localhost:3000 ✅ ACTIF
- **Base de données:** 192.168.20.52:3306 (user: n8n)
- **Table salaires:** ✅ Créée

### ✅ Serveur Production (192.168.20.53)
- **Backend:** http://192.168.20.53:8000 ✅ ACTIF (systemd)
- **Frontend:** http://192.168.20.53:3000 ✅ ACTIF (systemd)
- **Base de données:** 192.168.20.53:3306 (local MariaDB)
- **Table salaires:** ✅ Créée

## 📦 Fichiers Déployés

### Backend (Python/FastAPI)
- ✅ `database/add_salaires_table.sql` - Migration DB
- ✅ `backend/models/salaire.py` - Model Salaire
- ✅ `backend/models/employe.py` - Relationship ajoutée
- ✅ `backend/models/__init__.py` - Export Salaire
- ✅ `backend/schemas/salaire.py` - Schemas G29
- ✅ `backend/routers/rapports.py` - Endpoints G29 (corrigé)
- ✅ `backend/services/pdf_generator.py` - Génération PDF G29

### Frontend (React/Vite)
- ✅ `frontend/src/pages/Rapports/index.jsx` - Page Rapports
- ✅ `frontend/src/components/Layout/MainLayout.jsx` - Menu Rapports
- ✅ `frontend/src/App.jsx` - Import corrigé

## 🔧 Corrections Effectuées

### Problème: `require_auth` utilisé comme décorateur
**Erreur:**
```
TypeError: <coroutine object require_auth> is not a callable object
```

**Cause:** 
- `require_auth` est une fonction async avec `Depends(get_current_user)`
- Utilisée incorrectement comme `@require_auth` (décorateur)

**Solution:**
```python
# Avant (INCORRECT)
@router.get("/g29/{annee}")
@require_auth
async def get_g29_data(...):

# Après (CORRECT)
@router.get("/g29/{annee}")
async def get_g29_data(
    current_user: dict = Depends(require_auth)
):
```

**Fichier modifié:** `backend/routers/rapports.py`
- Ligne ~220: `get_g29_data` corrigée
- Ligne ~290: `generate_g29_pdf` corrigée

## 🧪 Plan de Tests

### 1. Test Backend API (localhost)

**Endpoint 1: Récupérer données G29**
```bash
# Test sans authentification (doit échouer 401)
curl http://localhost:8000/api/rapports/g29/2025

# Test avec token (remplacer <TOKEN>)
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/rapports/g29/2025
```

**Endpoint 2: Générer PDF**
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/rapports/g29/2025/pdf \
  -o g29_test_localhost.pdf
```

### 2. Test Backend API (serveur)

```bash
# Récupérer données
curl -H "Authorization: Bearer <TOKEN>" \
  http://192.168.20.53:8000/api/rapports/g29/2025

# Générer PDF
curl -H "Authorization: Bearer <TOKEN>" \
  http://192.168.20.53:8000/api/rapports/g29/2025/pdf \
  -o g29_test_serveur.pdf
```

### 3. Test Frontend (localhost)

1. Ouvrir http://localhost:3000
2. Se connecter avec un compte valide
3. Vérifier menu "Rapports" (entre Calcul Salaires et Paramètres)
4. Cliquer sur "Rapports"
5. Saisir année: 2025
6. Cliquer "Valider"
7. Vérifier affichage:
   - ⚠️ "Aucune donnée trouvée" (normal si table vide)
   - OU ✅ Statistiques + bouton "Générer G29"

### 4. Test Frontend (serveur)

1. Ouvrir http://192.168.20.53:3000
2. Mêmes étapes que localhost

### 5. Création de Données de Test

**Via SQL direct:**
```sql
-- Se connecter à la base
mysql -u root -p'Massi@2024' ay_hr

-- Créer un salaire test pour janvier 2025
INSERT INTO salaires (
  employe_id, annee, mois,
  salaire_base, jours_travailles,
  prime_rendement, prime_fidelite, prime_panier,
  total_primes, salaire_brut,
  cotisation_secu_sociale, irg_retenu, total_deductions,
  salaire_net, statut
) VALUES (
  1, 2025, 1,
  40000.00, 26,
  2000.00, 2000.00, 2600.00,
  6600.00, 46600.00,
  4194.00, 5000.00, 9194.00,
  37406.00, 'validé'
);

-- Vérifier
SELECT * FROM salaires WHERE annee = 2025;
```

**Via Python (depuis localhost):**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connexion (192.168.20.52 pour localhost)
engine = create_engine('mysql+pymysql://n8n:%21Yara%402014@192.168.20.52:3306/ay_hr')
Session = sessionmaker(bind=engine)
session = Session()

# Créer un salaire test
from backend.models.salaire import Salaire
salaire = Salaire(
    employe_id=1,
    annee=2025,
    mois=1,
    salaire_base=40000.00,
    jours_travailles=26,
    prime_rendement=2000.00,
    prime_fidelite=2000.00,
    prime_panier=2600.00,
    total_primes=6600.00,
    salaire_brut=46600.00,
    cotisation_secu_sociale=4194.00,
    irg_retenu=5000.00,
    total_deductions=9194.00,
    salaire_net=37406.00,
    statut='validé'
)
session.add(salaire)
session.commit()
print("Salaire test créé!")
```

### 6. Test Complet avec Données

**Après création de données:**

1. **Frontend localhost:**
   - Rapports → Année 2025 → Valider
   - ✅ Devrait afficher:
     - Nombre d'employés: 1
     - Total salaires bruts: 46,600.00 DA
     - Total IRG retenu: 5,000.00 DA
   - Cliquer "Générer G29"
   - ✅ Téléchargement de `G29_2025.pdf`

2. **Vérifier PDF:**
   - Page 1: Récapitulatif avec Janvier = 46,600 DA brut, 5,000 DA IRG
   - Page 2: 1 employé avec données janvier

3. **Frontend serveur:** Mêmes tests

## 📊 Structure Table Salaires

```sql
DESCRIBE salaires;
```

**Colonnes créées:**
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `employe_id` INT NOT NULL (FK → employes)
- `annee` INT NOT NULL
- `mois` INT NOT NULL (1-12)
- `salaire_base` DECIMAL(10,2)
- `heures_travaillees` DECIMAL(8,2)
- `jours_travailles` INT
- `prime_rendement`, `prime_fidelite`, `prime_experience` DECIMAL(10,2)
- `prime_panier`, `prime_transport`, `prime_nuit`, `autres_primes` DECIMAL(10,2)
- `total_primes`, `salaire_brut` DECIMAL(10,2)
- `cotisation_cnr`, `cotisation_secu_sociale` DECIMAL(10,2)
- `irg_retenu`, `autres_deductions` DECIMAL(10,2)
- `total_deductions`, `salaire_net` DECIMAL(10,2)
- `date_paiement` DATE
- `statut` VARCHAR(20) DEFAULT 'brouillon'
- `notes` TEXT
- `created_at`, `updated_at` TIMESTAMP

**Contraintes:**
- UNIQUE KEY `unique_salaire` (employe_id, annee, mois)
- INDEX `idx_annee` (annee)
- INDEX `idx_mois` (mois)
- INDEX `idx_employe_annee` (employe_id, annee)

## 🎯 Résultat Attendu

### Avec Données
- ✅ Menu "Rapports" visible entre "Calcul Salaires" et "Paramètres"
- ✅ Page Rapports charge avec filtre année
- ✅ Validation année affiche statistiques (employés, totaux)
- ✅ Bouton "Générer G29" télécharge PDF 2 pages
- ✅ PDF page 1: Tableau mensuel avec totaux
- ✅ PDF page 2: Liste employés avec 12 mois de données

### Sans Données
- ✅ Menu "Rapports" visible
- ✅ Page charge normalement
- ⚠️ Message "Aucune donnée trouvée pour cette année"
- ❌ Pas de bouton génération (normal, pas de données)

## 🚀 Services Systemd (Serveur)

### Backend
```bash
# Status
systemctl status ayhr-backend

# Redémarrer
systemctl restart ayhr-backend

# Logs
journalctl -u ayhr-backend -f
```

### Frontend
```bash
# Status
systemctl status ayhr-frontend

# Redémarrer
systemctl restart ayhr-frontend

# Logs
journalctl -u ayhr-frontend -f
```

## 📝 Commandes Utiles

### Vérifier table salaires
```bash
# Localhost (via 192.168.20.52)
mysql -h 192.168.20.52 -u n8n -p'!Yara@2014' ay_hr -e "SELECT COUNT(*) FROM salaires;"

# Serveur
ssh root@192.168.20.53 "mysql -u root -p'Massi@2024' ay_hr -e 'SELECT COUNT(*) FROM salaires;'"
```

### Tester endpoints
```bash
# Health check
curl http://localhost:8000/docs
curl http://192.168.20.53:8000/docs

# Liste des routes
curl http://localhost:8000/openapi.json | grep "g29"
```

## ✅ Checklist Finale

- [x] Table `salaires` créée sur 192.168.20.53
- [x] Backend déployé sur serveur (7 fichiers)
- [x] Backend actif sur serveur (systemd)
- [x] Frontend déployé sur serveur (3 fichiers)
- [x] Frontend actif sur serveur (systemd)
- [x] Backend localhost actif (port 8000)
- [x] Frontend localhost actif (port 3000)
- [x] Correction `require_auth` appliquée partout
- [ ] Données de test créées
- [ ] Test frontend localhost
- [ ] Test frontend serveur
- [ ] PDF généré et validé

## 🎉 Status Final

**DÉPLOIEMENT RÉUSSI** ✅

Les fonctionnalités G29 sont maintenant disponibles sur:
- **Localhost:** Backend actif (8000), Frontend actif (3000)
- **Serveur:** Backend actif (8000), Frontend actif (3000)

**Prochaine étape:** Créer des données de test et valider la génération du PDF G29.

---

**Développé par:** GitHub Copilot  
**Date:** 18 novembre 2025  
**Temps de déploiement:** ~30 minutes  
**Fichiers déployés:** 10 (7 backend + 3 frontend)

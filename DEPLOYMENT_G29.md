# Guide de Déploiement - Fonctionnalité G29

## 📋 Résumé des Modifications

Cette fonctionnalité ajoute la génération de rapports G29 (déclaration annuelle IRG) avec:
- Suivi mensuel des salaires dans une nouvelle table `salaires`
- API backend pour récupérer et générer les données G29
- Génération PDF du G29 (2 pages: récapitulatif + détails employés)
- Interface frontend avec filtre année et téléchargement PDF
- Nouveau menu "Rapports" entre "Calcul Salaires" et "Paramètres"

## 🗄️ Base de Données

### Étape 1: Créer la table salaires

**Sur le serveur 192.168.20.53**, exécuter:

```bash
cd /opt/ayhr
mysql -u ay_hr_user -p'Massi@2024' ay_hr < database/add_salaires_table.sql
```

**Vérification:**
```bash
mysql -u ay_hr_user -p'Massi@2024' ay_hr -e "DESCRIBE salaires;"
```

La table `salaires` contient:
- Colonnes: employe_id, annee, mois
- Salaire: salaire_base, heures_travaillees, jours_travailles
- 7 primes (rendement, fidélité, expérience, panier, transport, nuit, autres)
- Déductions: CNR, sécurité sociale, IRG, autres
- Totaux: total_primes, salaire_brut, total_deductions, salaire_net
- Métadonnées: date_paiement, statut (brouillon/validé/payé), notes
- Contrainte unique: (employe_id, annee, mois)

## 🔧 Backend (Python/FastAPI)

### Fichiers Modifiés

1. **backend/schemas/salaire.py** ✅
   - Ajouté: `G29DataEmploye`, `G29DataRecap`, `G29Response`
   - Schémas pour structurer les données G29

2. **backend/routers/rapports.py** ✅
   - Ajouté: `GET /api/rapports/g29/{annee}` - Récupère données G29
   - Ajouté: `GET /api/rapports/g29/{annee}/pdf` - Génère PDF G29
   - Imports: Salaire, G29 schemas, PDFGenerator

3. **backend/services/pdf_generator.py** ✅
   - Ajouté: `generate_g29()` - Méthode principale
   - Ajouté: `_generate_g29_page1()` - Page récapitulatif mensuel
   - Ajouté: `_generate_g29_page2()` - Page détails par employé (52 lignes)

4. **backend/models/salaire.py** ✅ (nouveau)
   - SQLAlchemy model pour table salaires
   - Relationship avec Employe

5. **backend/models/employe.py** ✅
   - Ajouté relationship: `salaires = relationship("Salaire", ...)`

6. **backend/models/__init__.py** ✅
   - Ajouté import: `from .salaire import Salaire`
   - Ajouté "Salaire" à __all__

### Étape 2: Déployer le Backend

**Sur votre machine Windows:**

```powershell
cd "f:\Code\AY HR"

# Transférer les fichiers modifiés
scp backend/schemas/salaire.py ayhr@192.168.20.53:/opt/ayhr/backend/schemas/
scp backend/routers/rapports.py ayhr@192.168.20.53:/opt/ayhr/backend/routers/
scp backend/services/pdf_generator.py ayhr@192.168.20.53:/opt/ayhr/backend/services/
scp backend/models/salaire.py ayhr@192.168.20.53:/opt/ayhr/backend/models/
scp backend/models/employe.py ayhr@192.168.20.53:/opt/ayhr/backend/models/
scp backend/models/__init__.py ayhr@192.168.20.53:/opt/ayhr/backend/models/
scp database/add_salaires_table.sql ayhr@192.168.20.53:/opt/ayhr/database/
```

**Sur le serveur:**

```bash
# Redémarrer le backend
sudo systemctl restart ayhr-backend

# Vérifier le statut
sudo systemctl status ayhr-backend

# Vérifier les logs
sudo journalctl -u ayhr-backend -f
```

### Étape 3: Tester l'API

**Test 1: Récupérer données G29**
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://192.168.20.53:8000/api/rapports/g29/2025
```

**Test 2: Générer PDF**
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://192.168.20.53:8000/api/rapports/g29/2025/pdf \
  -o g29_test.pdf
```

## 🎨 Frontend (React/Vite)

### Fichiers Modifiés

1. **frontend/src/pages/Rapports/index.jsx** ✅ (nouveau)
   - Page principale Rapports
   - Filtre année (InputNumber 2020-2100)
   - Bouton "Valider" pour charger données
   - Affichage statistiques (nb employés, totaux)
   - Bouton "Générer G29" pour télécharger PDF

2. **frontend/src/components/Layout/MainLayout.jsx** ✅
   - Ajouté menu "Rapports" avec icône FileTextOutlined
   - Position: après "Calcul Salaires", avant "Paramètres"

3. **frontend/src/App.jsx** ✅
   - Route `/rapports` vers composant Rapports
   - Import corrigé: `import Rapports from './pages/Rapports'`

### Étape 4: Build et Déployer Frontend

**Sur votre machine Windows:**

```powershell
cd "f:\Code\AY HR\frontend"

# Build production
npm run build

# Transférer dist vers serveur
scp -r dist/* ayhr@192.168.20.53:/var/www/ayhr/
```

**Alternative - Transférer sources et build sur serveur:**

```powershell
# Transférer fichiers modifiés
scp frontend/src/pages/Rapports/index.jsx ayhr@192.168.20.53:/opt/ayhr/frontend/src/pages/Rapports/
scp frontend/src/components/Layout/MainLayout.jsx ayhr@192.168.20.53:/opt/ayhr/frontend/src/components/Layout/
scp frontend/src/App.jsx ayhr@192.168.20.53:/opt/ayhr/frontend/src/
```

**Sur le serveur:**

```bash
cd /opt/ayhr/frontend
npm run build
sudo cp -r dist/* /var/www/ayhr/
```

## ✅ Tests de Validation

### 1. Créer des données de test

**Via l'application ou API:**

```python
# Exemple: Créer un salaire pour janvier 2025
POST /api/salaires/
{
  "employe_id": 1,
  "annee": 2025,
  "mois": 1,
  "salaire_base": 40000.00,
  "jours_travailles": 26,
  "prime_rendement": 2000.00,
  "prime_fidelite": 2000.00,
  "prime_panier": 2600.00,
  "total_primes": 6600.00,
  "salaire_brut": 46600.00,
  "cotisation_secu_sociale": 4194.00,
  "irg_retenu": 5000.00,
  "total_deductions": 9194.00,
  "salaire_net": 37406.00,
  "statut": "validé"
}
```

**Ou via SQL direct:**

```sql
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
```

### 2. Tester l'interface

1. Se connecter à http://192.168.20.53:3000
2. Cliquer sur "Rapports" dans le menu (entre Calcul Salaires et Paramètres)
3. Saisir une année (ex: 2025)
4. Cliquer "Valider"
5. Vérifier l'affichage des statistiques:
   - Nombre d'employés
   - Total salaires bruts
   - Total IRG retenu
   - Total salaires imposables
6. Cliquer "Générer le G29 (PDF - 2 pages)"
7. Vérifier le téléchargement de `G29_2025.pdf`
8. Ouvrir le PDF et vérifier:
   - Page 1: Récapitulatif mensuel avec totaux
   - Page 2: Liste des employés avec 12 mois de données

### 3. Valider le contenu du PDF

**Page 1 doit contenir:**
- En-tête: ADMINISTRATION DES IMPOTS, série G29
- Informations entreprise (nom, NIF, activité, adresse)
- Tableau 12 lignes (janvier à décembre)
- Colonnes: Mois, Salaires Bruts, IRG Retenu
- Ligne totaux en gras
- Date et signature

**Page 2 doit contenir:**
- Titre: DÉTAIL DES SALAIRES PAR EMPLOYÉ
- En-têtes: Nom/Prénom, SF (situation familiale), 12 mois
- Chaque mois: 2 colonnes (Net, IRG)
- Colonnes totaux: Tot.Net, Tot.IRG
- Une ligne par employé
- Multi-page si plus de ~40 employés

## 🔄 Utilisation Post-Déploiement

### Workflow mensuel

1. **Calcul Salaires** (page existante)
   - Effectuer le calcul mensuel habituel
   - Vérifier les résultats

2. **Enregistrement dans salaires** (nouveau)
   - Après validation, créer/mettre à jour les enregistrements dans `salaires`
   - Statut: brouillon → validé → payé

3. **Génération G29 annuelle**
   - En fin d'année ou au besoin fiscal
   - Menu Rapports → Année → Valider → Générer G29
   - Imprimer et soumettre à l'administration fiscale

### API Endpoints disponibles

```
GET  /api/rapports/g29/{annee}      - Récupérer données G29 (JSON)
GET  /api/rapports/g29/{annee}/pdf  - Télécharger G29 (PDF)
POST /api/salaires/                 - Créer un salaire mensuel
GET  /api/salaires/{id}             - Récupérer un salaire
PUT  /api/salaires/{id}             - Modifier un salaire
DELETE /api/salaires/{id}           - Supprimer un salaire
```

## 📊 Données Requises

Pour générer un G29 complet pour une année, il faut:

- Au moins 1 enregistrement dans `salaires` pour l'année
- Idéalement 12 enregistrements (1 par mois) par employé actif
- Champs critiques:
  - `salaire_brut` (pour page 1 récap)
  - `salaire_net` (pour page 2 montant imposable)
  - `irg_retenu` (pour les deux pages)

## 🚨 Points d'Attention

1. **Migration Base de Données**
   - Exécuter `add_salaires_table.sql` AVANT de redémarrer le backend
   - Vérifier que la table est créée avec succès

2. **Données Historiques**
   - Pour générer un G29 d'années passées, il faut saisir rétroactivement les données
   - Contrainte unique empêche les doublons (employe_id, annee, mois)

3. **Performance**
   - La requête G29 charge tous les employés actifs
   - Pour 50 employés × 12 mois = 600 enregistrements max
   - Index sur (employe_id, annee) pour optimiser

4. **Sécurité**
   - Endpoints G29 protégés par `@require_auth`
   - Token JWT obligatoire dans headers

5. **Format PDF**
   - Page 2 peut s'étendre sur plusieurs pages si >40 employés
   - Police taille 5-6 pour page 2 (compact)
   - Format A4 portrait

## 📝 TODO Futur (Optionnel)

- [ ] CRUD complet pour salaires (interface frontend)
- [ ] Import automatique depuis "Calcul Salaires" vers `salaires`
- [ ] Validation des données avant génération G29
- [ ] Export Excel du G29
- [ ] Autres rapports (états de paie annuels, statistiques)
- [ ] Archivage automatique des G29 générés

## 🆘 Dépannage

**Erreur: Table 'ay_hr.salaires' doesn't exist**
→ Exécuter la migration SQL

**Erreur 404: Aucune donnée trouvée**
→ Créer des enregistrements dans `salaires` pour l'année testée

**PDF vide ou mal formaté**
→ Vérifier les logs backend: `journalctl -u ayhr-backend -f`

**Menu Rapports non visible**
→ Vider le cache navigateur (Ctrl+Shift+R)

**Erreur de connexion API**
→ Vérifier que le backend est démarré: `systemctl status ayhr-backend`

---

**Date de création:** 2025-01-XX  
**Version:** 1.0.0  
**Développeur:** GitHub Copilot  
**Temps estimé d'implémentation:** 6 heures (backend + frontend + tests)

# Système de Gestion des Crédits Salariaux - Version Complète

## Vue d'ensemble

Le système de crédits permet de gérer les prêts accordés aux employés avec un suivi mensuel automatisé des remboursements (mensualités).

## Caractéristiques principales

### 1. **Filtres de Recherche Multicritères**
- Filtre par employé
- Filtre par statut (En cours / Soldé)
- Bouton de réinitialisation des filtres
- Mise à jour automatique des données lors de la modification des filtres

### 2. **Date de Début de Remboursement**
- Format : **Mois/Année** uniquement (pas de jour)
- Sélection via DatePicker avec `picker="month"`
- Format d'affichage : "Janvier 2025", "Février 2025", etc.

### 3. **Échéancier de Paiement Automatisé**
- Génération automatique de toutes les mensualités
- Calcul automatique : `mensualité = montant_total / nombre_mensualites`
- Suivi du statut : **Payé** / **Non payé**
- Affichage chronologique sur 12 mois (ou plus selon la durée)

### 4. **Suivi des Remboursements**
- **Montant retenu** : cumul de toutes les retenues effectuées
- **Montant restant** : calculé en temps réel `montant_total - montant_retenu`
- **Statut automatique** : passe à "Soldé" quand tout est remboursé

### 5. **Détails du Crédit (Drawer)**
- **Informations générales** :
  - Employé
  - Date d'octroi
  - Montant total
  - Nombre de mensualités
  - Montant de chaque mensualité
  - Montant retenu
  - **Montant restant** (en évidence)
  - Statut

- **Tableau de l'échéancier** :
  - Colonne "Période" : Mois et année (ex: Janvier 2025)
  - Colonne "Mensualité" : montant en DA
  - Colonne "Statut" : Tag coloré (Payé/Non payé/Prorogé)
  - Colonne "Remarque" : informations sur les prorogations

### 6. **Prorogations (Reports)**
- Possibilité de reporter une mensualité vers un autre mois
- Mention dans l'échéancier avec le nouveau mois
- Conserve l'historique des reports

## API Backend

### Endpoints principaux

```python
GET    /api/credits/                    # Liste avec filtres
POST   /api/credits/                    # Créer un crédit
GET    /api/credits/{id}                # Détails d'un crédit
PUT    /api/credits/{id}                # Modifier le nombre de mensualités
DELETE /api/credits/{id}                # Supprimer un crédit

GET    /api/credits/{id}/echeancier     # Échéancier complet
POST   /api/credits/{id}/retenue        # Enregistrer une retenue
POST   /api/credits/{id}/prorogation    # Reporter une mensualité
GET    /api/credits/{id}/historique     # Historique complet
```

### Paramètres de filtrage

```python
GET /api/credits/?employe_id=4&statut=En cours
```

### Échéancier (Exemple de réponse)

```json
[
  {
    "mois": 1,
    "annee": 2025,
    "montant": 10000.0,
    "statut": "payé",
    "date_retenue": "2025-01-15",
    "prorogation": null
  },
  {
    "mois": 2,
    "annee": 2025,
    "montant": 10000.0,
    "statut": "non payé",
    "date_retenue": null,
    "prorogation": null
  }
]
```

## Modèle de Données

### Table `credits`
```sql
- id: INT (PK)
- employe_id: INT (FK -> employes.id)
- date_octroi: DATE
- montant_total: DECIMAL(12, 2)
- nombre_mensualites: INT
- montant_mensualite: DECIMAL(12, 2)  -- Calculé automatiquement
- montant_retenu: DECIMAL(12, 2)      -- Cumul des retenues
- statut: ENUM('En cours', 'Soldé')
```

### Table `retenues_credit`
```sql
- id: INT (PK)
- credit_id: INT (FK -> credits.id)
- mois: INT (1-12)
- annee: INT
- montant: DECIMAL(12, 2)
- date_retenue: DATE
```

### Table `prorogations_credit`
```sql
- id: INT (PK)
- credit_id: INT (FK -> credits.id)
- date_prorogation: DATE
- mois_initial: INT
- annee_initiale: INT
- mois_reporte: INT
- annee_reportee: INT
- motif: VARCHAR(500)
```

## Interface Utilisateur (Frontend)

### Composant principal : `CreditsList.jsx`

**États gérés** :
- `credits` : liste des crédits
- `employes` : liste des employés actifs
- `filters` : {employe_id, statut}
- `selectedCredit` : crédit sélectionné pour affichage détails
- `echeancier` : données de l'échéancier du crédit sélectionné
- `detailDrawerVisible` : contrôle l'affichage du drawer

**Fonctionnalités** :
- Filtrage en temps réel
- Modal de création de crédit
- Drawer de détails avec échéancier complet
- Affichage du montant restant dans la table principale

## Intégration avec le Système de Paie

### À noter
1. **Affichage sur le bulletin** : Le crédit apparaît sur le bulletin de salaire
2. **Pas de déduction automatique** : Le crédit **n'entre pas dans le calcul du salaire**
3. **Suivi interne** : Les retenues sont enregistrées manuellement chaque mois via l'API
4. **Vérification** : Le système vérifie si une retenue est déjà enregistrée pour éviter les doublons

## Règles de Gestion

1. **Création** :
   - Montant total obligatoire
   - Nombre de mensualités obligatoire (minimum 1)
   - Mensualité calculée automatiquement : `montant_total / nombre_mensualites`

2. **Retenue mensuelle** :
   - Une seule retenue par mois autorisée
   - Montant ne peut pas dépasser le montant restant
   - Si montant restant < mensualité, retenue = montant restant
   - Mise à jour automatique du `montant_retenu`
   - Passage automatique au statut "Soldé" si totalement remboursé

3. **Prorogation** :
   - Report d'une mensualité vers un autre mois
   - Conserve le montant de la mensualité
   - Trace dans l'échéancier

4. **Suppression** :
   - Suppression en cascade des retenues et prorogations associées

## Exemple d'Utilisation

### Scénario : Crédit de 120,000 DA sur 12 mois

1. **Création** :
   ```json
   {
     "employe_id": 4,
     "date_octroi": "2025-01-01",
     "montant_total": 120000,
     "nombre_mensualites": 12
   }
   ```
   → Mensualité calculée : **10,000 DA/mois**

2. **Échéancier généré** :
   - Janvier 2025 : 10,000 DA
   - Février 2025 : 10,000 DA
   - ... (12 mois)
   - Décembre 2025 : 10,000 DA

3. **Enregistrement des retenues** :
   - Chaque mois, appel API : `POST /credits/{id}/retenue?mois=1&annee=2025`
   - Montant retenu total mis à jour
   - Statut dans l'échéancier passe à "payé"

4. **Suivi** :
   - Montant restant visible en temps réel
   - Échéancier coloré (vert = payé, gris = non payé)
   - Statut global passe à "Soldé" après 12ème retenue

## Tests Réussis ✅

Le système a été testé avec succès :
- ✓ Création de crédit
- ✓ Génération d'échéancier (12 mensualités)
- ✓ Enregistrement de retenue
- ✓ Mise à jour du montant retenu
- ✓ Calcul du montant restant
- ✓ Mise à jour du statut dans l'échéancier

**Résultat** : Tous les tests passent, le système est **opérationnel** ! 🎉

## Fichiers Modifiés

### Backend
- `backend/routers/credits.py` : ajout endpoint `/echeancier`
- `backend/services/index.js` : ajout méthode `getEcheancier()`
- Installation : `python-dateutil==2.9.0.post0`

### Frontend
- `frontend/src/pages/Credits/CreditsList.jsx` : filtres + drawer détails
- `frontend/src/services/index.js` : ajout méthode API

### Tests
- `test_credits.py` : script de test complet du système

## Améliorations Futures Possibles

1. **Automatisation** : Génération automatique des retenues chaque mois
2. **Notifications** : Rappel des mensualités à déduire
3. **Export** : Export Excel de l'échéancier
4. **Dashboard** : Vue statistique des crédits en cours
5. **Multi-crédits** : Gestion de plusieurs crédits simultanés par employé

---

**Statut** : ✅ **Système Opérationnel**  
**Version** : 2.0  
**Date** : 11/11/2025

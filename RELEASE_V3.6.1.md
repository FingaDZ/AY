# Notes de Version v3.6.1 - Améliorations Congés, Crédits et Gestion Contrats

**Date**: 22 Décembre 2025

## 🎯 Nouvelles Fonctionnalités

### 1. **Gestion Avancée des Congés** ✨

#### Mois de Déduction pour Bulletin de Paie
- **Nouveau**: Les congés peuvent maintenant être déduits dans un mois différent de leur acquisition
- **Champs ajoutés**:
  - `mois_deduction` (1-12): Mois où les jours sont déduits du salaire
  - `annee_deduction`: Année de déduction

#### Utilisation
```python
# Lors de la mise à jour d'un congé
PUT /conges/{conge_id}/consommation
{
    "jours_pris": 2.5,
    "mois_deduction": 12,      # Nouveau: Déduire en décembre
    "annee_deduction": 2025     # Nouveau: Année 2025
}
```

#### Intégration Bulletin de Paie
Le système peut maintenant transférer correctement les congés pris dans leur mois de déduction pour une comptabilité précise.

---

### 2. **Calculs Précis Crédits et Avances** 📊

#### Échéancier Automatique pour Crédits
- **Nouveau**: Calcul automatique des dates de début et fin prévues
- **Champs ajoutés aux crédits**:
  - `mois_debut`: Mois de début des retenues (calculé automatiquement)
  - `annee_debut`: Année de début
  - `mois_fin_prevu`: Mois de fin prévu (basé sur nombre de mensualités)
  - `annee_fin_prevu`: Année de fin prévue

#### Calcul Automatique lors de la Création
```python
# Exemple: Crédit de 50,000 DA sur 10 mois, octroyé le 15/12/2025
# Le système calcule automatiquement:
# - mois_debut: 1 (janvier 2026, mois suivant l'octroi)
# - annee_debut: 2026
# - mois_fin_prevu: 10 (octobre 2026)
# - annee_fin_prevu: 2026
```

#### Validation Renforcée
- ✅ Vérification exacte des périodes de retenue
- ✅ Calcul précis des échéances
- ✅ Détection des prorogations et reports

#### Avances - Contrôle 70%
- ✅ Validation stricte: maximum 70% du salaire de base par mois
- ✅ Calcul automatique du cumul des avances du mois
- ✅ Message d'erreur détaillé si limite dépassée

---

### 3. **Gestion Automatique Contrats Expirés** 🔄

#### Désactivation Automatique
**Nouveau service**: Les employés avec contrat expiré sont automatiquement désactivés.

#### Nouvelles Routes API

##### 1. Lister les Contrats Expirés (Sans Désactiver)
```http
GET /employes/contrats-expires
Authorization: Bearer {token}
```

**Réponse**:
```json
{
    "total": 2,
    "employes_contrats_expires": [
        {
            "id": 15,
            "nom": "BENALI",
            "prenom": "Ahmed",
            "poste_travail": "Chauffeur",
            "date_recrutement": "2023-06-01",
            "date_fin_contrat": "2025-06-01",
            "jours_expires": 204,
            "salaire_base": 30000.00
        }
    ]
}
```

##### 2. Désactiver Automatiquement les Contrats Expirés
```http
POST /employes/verifier-contrats-expires
Authorization: Bearer {token} (Admin uniquement)
```

**Réponse**:
```json
{
    "message": "2 employé(s) désactivé(s) automatiquement",
    "employes_desactives": [
        {
            "id": 15,
            "nom": "BENALI",
            "prenom": "Ahmed",
            "date_fin_contrat": "2025-06-01",
            "jours_expires": 204
        }
    ]
}
```

##### 3. Calculer Automatiquement les Dates de Fin de Contrat
```http
POST /employes/mettre-a-jour-dates-fin-contrat
Authorization: Bearer {token} (Admin uniquement)
```

Pour les employés qui ont `duree_contrat` mais pas `date_fin_contrat`, calcule automatiquement la date.

**Exemple**:
- Date recrutement: 01/01/2025
- Durée contrat: 12 mois
- → Date fin calculée: 01/01/2026

#### Service Backend
Nouveau fichier: `backend/services/employe_service.py`

**Fonctions principales**:
```python
verifier_contrats_expires(db)          # Désactive automatiquement
calculer_date_fin_contrat(employe)     # Calcule date de fin
mettre_a_jour_dates_fin_contrat(db)    # Met à jour en masse
```

#### Workflow Recommandé

1. **Vérification quotidienne** (automatisable via cron/scheduler):
   ```python
   # Lister les contrats expirés
   GET /employes/contrats-expires
   ```

2. **Désactivation manuelle ou automatique**:
   ```python
   # L'admin décide de désactiver
   POST /employes/verifier-contrats-expires
   ```

3. **Réactivation manuelle**:
   - L'utilisateur doit mettre à jour `date_fin_contrat`
   - Puis changer `actif` à `True` manuellement

---

## 🗄️ Migration Base de Données

### Script SQL
Fichier: `database/migration_v3.6.1_conges_credits_contrats.sql`

**Commandes**:
```sql
-- Ajouter colonnes congés
ALTER TABLE conges ADD COLUMN mois_deduction INTEGER;
ALTER TABLE conges ADD COLUMN annee_deduction INTEGER;

-- Ajouter colonnes crédits
ALTER TABLE credits ADD COLUMN mois_debut INTEGER;
ALTER TABLE credits ADD COLUMN annee_debut INTEGER;
ALTER TABLE credits ADD COLUMN mois_fin_prevu INTEGER;
ALTER TABLE credits ADD COLUMN annee_fin_prevu INTEGER;

-- Index pour performances
CREATE INDEX idx_conges_deduction ON conges(annee_deduction, mois_deduction);
CREATE INDEX idx_credits_periode ON credits(annee_debut, mois_debut);
CREATE INDEX idx_employes_date_fin_contrat ON employes(date_fin_contrat) WHERE actif = TRUE;
```

**Exécution**:
```bash
# Linux
psql -U postgres -d ayhr_db -f database/migration_v3.6.1_conges_credits_contrats.sql

# Windows
psql -U postgres -d ayhr_db -f "database\migration_v3.6.1_conges_credits_contrats.sql"
```

---

## 📝 Logging et Traçabilité

Toutes les opérations sont maintenant loggées avec:
- ✅ `user_id` et `user_email`
- ✅ `record_id` (ID de l'enregistrement modifié)
- ✅ `ip_address` (adresse IP de la requête)
- ✅ Description détaillée de l'action
- ✅ Données avant/après modification

**Modules concernés**:
- Congés: Mise à jour consommation avec mois déduction
- Crédits: Création avec calcul échéancier
- Employés: Désactivation automatique contrats expirés

---

## 🔧 Modifications Techniques

### Modèles Modifiés

#### `backend/models/conge.py`
```python
mois_deduction = Column(Integer, nullable=True)
annee_deduction = Column(Integer, nullable=True)
```

#### `backend/models/credit.py`
```python
mois_debut = Column(Integer, nullable=True)
annee_debut = Column(Integer, nullable=True)
mois_fin_prevu = Column(Integer, nullable=True)
annee_fin_prevu = Column(Integer, nullable=True)
```

### Routers Modifiés

- `backend/routers/conges.py`: Ajout gestion mois déduction
- `backend/routers/credits.py`: Calcul automatique échéancier
- `backend/routers/employes.py`: 3 nouvelles routes contrats expirés

### Services Créés

- `backend/services/employe_service.py`: Gestion automatique employés

---

## ⚠️ Points d'Attention

### Sécurité
- Les routes de désactivation automatique nécessitent **droits Admin**
- Toutes les opérations sont loggées pour audit
- Validation stricte des dates et montants

### Workflow Utilisateur
1. **Contrat Expiré** → Employé désactivé automatiquement
2. **Réactivation** → L'utilisateur DOIT:
   - Mettre à jour `date_fin_contrat` (nouveau contrat)
   - Changer `actif` à `True` manuellement
   - Cela évite les réactivations accidentelles

### Congés
- Le `mois_deduction` est optionnel
- Si non spécifié, considère le mois d'acquisition par défaut
- Validation: 1-12 pour mois, 2000-2100 pour année

### Crédits
- Calcul automatique lors de création uniquement
- Modification du nombre de mensualités recalcule l'échéancier
- Les prorogations modifient les dates prévues

---

## 🚀 Prochaines Étapes

Pour utiliser ces nouvelles fonctionnalités:

1. **Exécuter la migration SQL**
2. **Redémarrer le backend**
3. **Tester les nouvelles routes**
4. **Configurer une tâche planifiée** pour vérifier les contrats expirés

### Exemple Tâche Planifiée (Windows)
```powershell
# Script PowerShell à exécuter quotidiennement
$headers = @{
    "Authorization" = "Bearer ADMIN_TOKEN"
}

# Vérifier les contrats expirés
$response = Invoke-RestMethod -Uri "http://localhost:8000/employes/contrats-expires" -Headers $headers

# Si des contrats sont expirés, envoyer notification
if ($response.total -gt 0) {
    Write-Host "$($response.total) contrat(s) expiré(s) détecté(s)"
    
    # Désactiver automatiquement (si souhaité)
    Invoke-RestMethod -Uri "http://localhost:8000/employes/verifier-contrats-expires" -Method POST -Headers $headers
}
```

---

## 📞 Support

Pour toute question ou problème:
- Vérifier les logs dans la table `logging`
- Consulter la documentation API
- Tester les endpoints avec Postman/Swagger

# 📦 Release Notes - Version 1.1.3

**Date de Release**: 13 Novembre 2025  
**Version**: 1.1.3  
**Type**: Feature + Bugfix

---

## 🎯 Résumé

Cette version apporte un nouveau module complet de gestion des postes de travail et corrige plusieurs problèmes critiques d'authentification et de validation découverts lors des tests.

---

## ✨ Nouvelles Fonctionnalités

### 1. Module Postes de Travail Complet

**Description**: Nouveau module permettant la gestion dynamique des postes de travail dans l'entreprise.

**Fonctionnalités**:
- ✅ Création de postes personnalisés
- ✅ Modification des postes existants
- ✅ Désactivation/suppression de postes
- ✅ Indicateur "Chauffeur" pour les missions
- ✅ Protection des postes système (non modifiables)
- ✅ Filtrage actifs/inactifs
- ✅ Interface utilisateur complète avec Ant Design

**Interface**:
- Liste des postes avec actions (modifier, supprimer)
- Modal de création/modification
- Validation des champs
- Gestion des statuts (actif/inactif)

**Technique**:
- Table `postes_travail` en base de données
- Router API `/api/postes` complet (CRUD)
- Service frontend `posteService`
- Composants React: `PostesList.jsx`, `PosteForm.jsx`

**Impact**: Les postes ne sont plus hardcodés, permettant une meilleure flexibilité organisationnelle.

---

### 2. Durée de Contrat Automatique

**Description**: Ajout du champ `duree_contrat` avec calcul automatique de la date de fin.

**Fonctionnalités**:
- ✅ Saisie de la durée en mois
- ✅ Calcul automatique de `date_fin_contrat`
- ✅ Affichage dans le formulaire employé
- ✅ Validation des données

**Calcul**: 
```
date_fin_contrat = date_recrutement + (duree_contrat * 30 jours)
```

**Migration**: 
- Colonne `duree_contrat` ajoutée (nullable)
- Migration `migrate_add_duree_contrat.py`

---

## 🐛 Corrections de Bugs

### 1. Erreur 401 - Module Postes (CRITIQUE)

**Problème**: 
- Erreur "401 Unauthorized" lors de l'accès au module Postes
- Impossible de charger la liste des postes
- Création/modification échouaient

**Cause**: Utilisation directe d'`axios` au lieu du service configuré avec authentification

**Fichiers corrigés**:
- `frontend/src/pages/Postes/PostesList.jsx`
- `frontend/src/pages/Postes/PosteForm.jsx`

**Solution**: Utilisation de `posteService` avec intercepteur d'authentification automatique

**Commit**: `069acf4`

---

### 2. Erreur 401 - Formulaire Employé (CRITIQUE)

**Problème**: 
- Erreur "401 Unauthorized" lors de la modification du poste d'un employé
- Liste déroulante des postes ne se chargeait pas

**Cause**: `EmployeForm.jsx` utilisait `axios` directement pour charger les postes

**Fichier corrigé**:
- `frontend/src/pages/Employes/EmployeForm.jsx`

**Solution**: Import et utilisation de `posteService.getAll()`

**Commit**: `75dc44c`

---

### 3. Validation Salaire Incorrect (MAJEUR)

**Problème**: 
- Message "Le salaire minimum légal est de 20 000 DA" affiché même avec salaire valide (ex: 30000 DA)
- Impossible de créer/modifier des employés

**Cause**: Le `parser` de l'InputNumber retournait une **string** au lieu d'un **nombre**
```jsx
// Avant: "30000" (string)
parser={value => value.replace(/\s?/g, '')}

// Après: 30000 (number)
parser={value => {
  const parsed = value.replace(/\s/g, '');
  return parsed ? Number(parsed) : 0;
}}
```

**Impact**: La validation `type: 'number', min: 20000` échouait en comparant string vs number

**Commit**: `d0f1ebd`

---

### 4. Corrections Session v1.1.2

**Corrections précédentes incluses**:
- ✅ Erreur 500 lors de la création d'employé (sérialisation Decimal)
- ✅ Section EMPLOYEUR manquante dans bulletins de paie
- ✅ En-tête entreprise manquant dans rapports salaires
- ✅ Validation salaire minimum 20k DA
- ✅ Nettoyage instructions debug

**Commit**: `1d29c82`

---

## 📊 Modifications Techniques

### Base de Données

**Nouvelles tables**:
- `postes_travail` - Gestion des postes de travail
  - Colonnes: id, libelle, est_chauffeur, modifiable, actif

**Nouvelles colonnes**:
- `employes.duree_contrat` (INT, nullable)
- `employes.date_fin_contrat` (DATE, nullable, calculée automatiquement)

**Migrations**:
- `backend/migrate_add_duree_contrat.py`
- `backend/migrate_add_postes_travail.py`

---

### Backend (FastAPI)

**Nouveaux routers**:
- `/api/postes` - CRUD complet postes de travail
  - GET `/` - Liste postes (filtrage actifs)
  - POST `/` - Créer poste (admin only)
  - PUT `/{id}` - Modifier poste (admin only)
  - DELETE `/{id}` - Supprimer poste (admin only)

**Nouveaux modèles**:
- `models/poste_travail.py` - SQLAlchemy model
- `schemas/poste_travail.py` - Pydantic schemas

**Nouveaux services**:
- `services/postes_service.py` - Logique métier

---

### Frontend (React)

**Nouveaux composants**:
- `pages/Postes/PostesList.jsx` - Liste et gestion
- `pages/Postes/PosteForm.jsx` - Formulaire création/modification

**Services modifiés**:
- `services/index.js` - Ajout `posteService`

**Formulaires modifiés**:
- `pages/Employes/EmployeForm.jsx` 
  - Chargement dynamique des postes
  - Ajout champ durée contrat
  - Fix validation salaire

---

## 🔧 Améliorations Techniques

### Architecture

1. **Service centralisé pour authentification**
   - Tous les modules utilisent les services configurés
   - Intercepteur axios automatique pour le token
   - Gestion centralisée des erreurs 401

2. **Validation robuste**
   - Types corrects dans les formulaires (number vs string)
   - Parser InputNumber retourne des nombres
   - Validation Pydantic côté backend

3. **Code plus maintenable**
   - Suppression du code axios redondant
   - Services réutilisables
   - Séparation des préoccupations

---

## 📝 Documentation

**Nouveaux fichiers**:
- `SESSION_CORRECTIONS_V1.1.3.md` - Documentation complète de la session (519 lignes)
- `RELEASE_NOTES_V1.1.3.md` - Ces notes de release

**Commits de documentation**:
- `b1f8113` - Documentation session
- `e0c2fa3` - Documentation features

---

## 🧪 Tests Recommandés

### Tests Fonctionnels

1. **Module Postes**
   - [ ] Créer un nouveau poste
   - [ ] Modifier un poste existant
   - [ ] Désactiver un poste
   - [ ] Vérifier filtrage actifs/inactifs
   - [ ] Tenter de modifier un poste système (doit être bloqué)

2. **Gestion Employés**
   - [ ] Créer employé avec nouveau poste
   - [ ] Modifier le poste d'un employé existant
   - [ ] Saisir salaire 30000 DA (doit passer)
   - [ ] Tenter salaire 15000 DA (doit échouer)
   - [ ] Saisir durée de contrat et vérifier date_fin_contrat

3. **Authentification**
   - [ ] Accéder à tous les modules (pas d'erreur 401)
   - [ ] Se déconnecter et vérifier redirection
   - [ ] Actions admin uniquement (création postes)

---

## 🚀 Migration depuis v1.1.2

### Étapes de mise à jour

1. **Arrêter les services**
   ```powershell
   # Arrêter backend et frontend
   ```

2. **Récupérer le code**
   ```bash
   git pull origin main
   git checkout v1.1.3
   ```

3. **Mettre à jour les dépendances**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   cd ../frontend
   npm install
   ```

4. **Exécuter les migrations**
   ```bash
   cd backend
   python migrate_add_duree_contrat.py
   python migrate_add_postes_travail.py
   ```

5. **Redémarrer les services**
   ```powershell
   # Backend
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Frontend
   cd frontend
   npm run dev
   ```

---

## 📦 Fichiers Modifiés

### Backend
- ✏️ `main.py` - Ajout router postes
- ✏️ `models/__init__.py` - Export PosteTravail
- ✏️ `routers/__init__.py` - Import postes_travail
- ➕ `routers/postes_travail.py` - Nouveau router
- ➕ `models/poste_travail.py` - Nouveau modèle
- ➕ `schemas/poste_travail.py` - Nouveaux schemas
- ➕ `services/postes_service.py` - Nouveau service
- ➕ `migrate_add_duree_contrat.py` - Migration
- ➕ `migrate_add_postes_travail.py` - Migration

### Frontend
- ✏️ `src/services/index.js` - Ajout posteService
- ✏️ `src/pages/Employes/EmployeForm.jsx` - Fix auth + durée contrat
- ✏️ `src/App.jsx` - Ajout route Postes
- ➕ `src/pages/Postes/PostesList.jsx` - Nouveau composant
- ➕ `src/pages/Postes/PosteForm.jsx` - Nouveau composant

### Documentation
- ➕ `SESSION_CORRECTIONS_V1.1.3.md`
- ➕ `RELEASE_NOTES_V1.1.3.md`

---

## 🔗 Commits

| Commit | Type | Description |
|--------|------|-------------|
| `d0f1ebd` | fix | Correction validation salaire - Parser retourne nombre |
| `75dc44c` | fix | Correction authentification EmployeForm |
| `069acf4` | fix | Correction authentification module Postes |
| `b1f8113` | docs | Documentation session v1.1.3 |
| `e0c2fa3` | feat | Ajout durée contrat + module postes |
| `1d29c82` | fix | Corrections bugs v1.1.2 |

---

## ⚠️ Breaking Changes

**Aucun breaking change** - Cette version est rétrocompatible avec v1.1.2

Les nouvelles colonnes en base de données sont `nullable`, donc les données existantes ne sont pas affectées.

---

## 🐛 Problèmes Connus

1. **Warning Ant Design `addonAfter`**
   - Warning: `[antd: Input] addonAfter is deprecated`
   - Source: Composant `Input.Search` d'Ant Design
   - Impact: **Aucun** - Simple warning de développement
   - Statut: Sera corrigé dans une future version d'Ant Design

2. **Python 3.13 Compatibility**
   - Certains packages (pandas, pydantic) nécessitent compilation Rust
   - Recommandation: Utiliser Python 3.11 ou 3.12 pour faciliter l'installation
   - Contournement: Packages déjà installés dans venv fonctionnent correctement

---

## 📞 Support

Pour toute question ou problème:
- 📧 Issues GitHub: https://github.com/FingaDZ/AY/issues
- 📝 Documentation: Voir fichiers MD dans le repository

---

## 🙏 Contributeurs

- **Session de développement**: 13 Novembre 2025
- **Développeur**: FingaDZ
- **Assistant IA**: GitHub Copilot

---

## 📅 Prochaines Étapes (v1.2.0)

**Fonctionnalités prévues**:
- 📊 Tableau de bord statistiques avancées
- 📧 Notifications par email
- 📱 Export PDF amélioré
- 🔐 Gestion avancée des permissions
- 📈 Rapports personnalisables

---

**Version**: 1.1.3  
**Date**: 13 Novembre 2025  
**Status**: ✅ Production Ready

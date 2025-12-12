# 🚀 Plan d'implémentation v3.5.2

## ✅ FAIT - Task 1: Page Congés
- [x] Groupement par employé
- [x] Colonnes: Employé, Total Travaillés, Total Acquis, Total Pris, Solde, Actions
- [x] Supprimé colonne "Période"
- [x] Bouton "Détails" avec popup montrant périodes détaillées
- [x] Fichier: `frontend/src/pages/Conges/CongesList.jsx`

## 📋 TODO - Task 2: Ligne Congés dans bulletin PDF
**Analyse**: Ligne existe déjà dans `backend/services/pdf_generator.py` ligne 899-902
**Problème possible**: La variable `jours_conges` n'est peut-être pas passée correctement

**Actions**:
1. Vérifier que `jours_conges` est bien récupéré des pointages dans `calculer_salaire()`
2. Vérifier transmission à `generer_bulletin_paie_pdf()`
3. Tester génération PDF

**Fichiers à vérifier**:
- `backend/routers/salaires.py` - fonction `calculer_salaire()`
- `backend/services/salary_calculator.py` - récupération jours_conges
- `backend/services/pdf_generator.py` - ligne 899

## 📋 TODO - Task 3: Pointages - Message dates hors contrat
**Objectif**: Popup quand on essaie de saisir un pointage hors période de contrat

**Actions**:
1. Vérifier si logique déjà implémentée dans backend
2. Ajouter validation frontend avec Modal
3. Afficher dates contrat dans message

**Fichier**: `frontend/src/pages/Pointages/GrillePointage.jsx`

## 📋 TODO - Task 4: Employés - Couleurs contrats
**Objectif**: 
- Rouge: contrat expiré
- Orange: expiration < 30 jours

**Actions**:
1. Calculer état contrat dans composant
2. Ajouter className conditionnelle sur ligne tableau
3. Ajouter légende couleurs

**Fichier**: `frontend/src/pages/Employes/EmployesList.jsx`

## 📋 TODO - Task 5: Page Logs - Colonnes manquantes
**Problème**: Utilisateur et ID Enregistrement non renseignés

**Actions**:
1. Vérifier structure table `logs`
2. S'assurer que `user_id` et `record_id` sont enregistrés
3. Afficher dans colonnes tableau
4. Corriger popup détails

**Fichier**: `frontend/src/pages/Logs/LogsPage.jsx`

## 📋 TODO - Task 6: Vérifier logs inscrits partout
**Actions**:
1. Lister endpoints critiques
2. Vérifier présence `log_action()` dans chaque endpoint
3. Ajouter logs manquants

**Endpoints prioritaires**:
- POST /employes
- PUT /employes/{id}
- POST /pointages
- PUT /pointages/{id}
- POST /salaires
- POST /conges

## 📋 TODO - Task 7: Mise à jour versions v3.5.2
**Fichiers à modifier**:
- backend/config.py
- frontend/package.json  
- frontend/src/components/Layout.jsx
- frontend/src/pages/Dashboard.jsx
- frontend/src/pages/Login/LoginPage.jsx
- README.md

---

**Ordre d'exécution**: Tasks 2-7 séquentiellement

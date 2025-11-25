# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [1.1.6] - 2025-11-25 ✅ ACTUELLE

### 🐛 Corrections
- **Sidebar Scrolling** : Fix sidebar ne défilant pas pour accéder aux éléments en bas
  - Ajout `overflow-y-auto` au conteneur de navigation
  - Tous les liens du menu sont maintenant accessibles
- **Navigation Rapports** : Fix redirection vers Dashboard au lieu de la page Rapports
  - Suppression des imports et routes Rapports (module non implémenté)
  - Suppression du lien Rapports de la sidebar

### 🔍 Audit Logging
- **Audit Complet** : Vérification de l'intégration du logging dans tous les modules
  - ✅ `employes.py` - Logging complet (CREATE, UPDATE, DELETE, SOFT_DELETE, EXPORT)
  - ✅ `postes_travail.py` - Logging complet (CREATE, UPDATE, DELETE)
  - ⚠️ Modules sans logging : pointages, missions, avances, credits, salaires, clients
  - Note : L'ajout du logging aux modules restants sera fait en v1.2.0

### 🎨 Améliorations UI
- **Version Display** : Mise à jour de l'affichage de version partout
  - Sidebar : v2.0 → v1.1.6
  - Layout footer : v1.1.5 → v1.1.6
  - Login page : v1.1.5 → v1.1.6

### 📄 Fichiers Modifiés
- `frontend/src/components/Sidebar.jsx` - Fix scrolling + version + suppression Rapports
- `frontend/src/App.jsx` - Suppression routes Rapports
- `frontend/src/components/Layout.jsx` - Version 1.1.6
- `frontend/src/pages/Login/LoginPage.jsx` - Version 1.1.6
- `frontend/package.json` - Version 1.1.6

---

## [1.1.5] - 2025-11-25

### 🐛 Corrections
- **Validation Salaire Base** : Fix erreur validation lors de l'édition d'un employé
  - Conversion explicite `salaire_base` en nombre lors du chargement des données
  - Résout le problème "Le salaire minimum légal est de 20 000 DA" sur valeurs existantes

### 🧹 Nettoyage
- **Suppression Fichiers Non Essentiels** : Nettoyage complet du repository
  - Suppression de 14 guides obsolètes (ANALYSE_G29, CERTIFICATS_GUIDE, etc.)
  - Suppression fichiers de test (test-mobile.html, test-responsive.html, etc.)
  - Suppression scripts de déploiement temporaires
  - Suppression backups SQL et fichiers Excel de test

### 📚 Documentation
- **README.md** : Nouvelle version complète et concise
  - Structure du projet claire
  - Stack technique détaillée
  - Guide de démarrage rapide
  - Modules principaux documentés
- **DEPLOYMENT_WINDOWS.md** : Nouveau guide complet pour Windows 10/11
  - Installation pas à pas
  - Configuration en tant que service Windows (NSSM)
  - Scripts de démarrage automatique
  - Dépannage et sauvegarde
- **DEPLOYMENT_LINUX.md** : Guide existant conservé et à jour
- **INSTALL_UBUNTU_22.04.md** : Guide existant conservé

### 📄 Fichiers Modifiés
- `frontend/src/pages/Employes/EmployeForm.jsx` - Fix validation salaire
- `frontend/package.json` - Version 1.1.5
- `README.md` - Réécriture complète
- `CHANGELOG.md` - Ajout v1.1.5

### 📄 Fichiers Supprimés
- 14 guides obsolètes (MD)
- 6 scripts de test/déploiement (PS1, PY, SH)
- 3 fichiers de test HTML
- 2 backups SQL
- 1 fichier Excel de test

---

## [1.1.4] - 2025-01-XX 🆕 EN DÉVELOPPEMENT

### ✨ Nouvelles Fonctionnalités
- **Génération Attestation de Travail** : Document PDF pour employés actifs
  - Méthode `PDFGenerator.generate_attestation_travail()`
  - Endpoint API : `GET /api/employes/{employe_id}/attestation-travail`
  - Calcul automatique de l'ancienneté (années et mois)
  - Utilise les paramètres entreprise de la base de données
  - Document avec en-tête entreprise, détails employé, signature
  
- **Génération Certificat de Travail** : Document PDF pour employés ayant quitté l'entreprise
  - Méthode `PDFGenerator.generate_certificat_travail()`
  - Endpoint API : `GET /api/employes/{employe_id}/certificat-travail`
  - Calcul automatique de la durée d'emploi totale
  - Mention "libre de tout engagement"
  - Validation : employé doit avoir date_fin_contrat ou être inactif

### 🔧 Améliorations Techniques
- **Validation logique** : Attestation uniquement pour employés actifs, certificat pour employés inactifs/avec date_fin
- **Logging automatique** : Toutes les générations de documents sont loggées avec ActionType.EXPORT
- **Noms de fichiers descriptifs** : Format `attestation_travail_NOM_PRENOM_DDMMYYYY.pdf`
- **Gestion erreurs robuste** : HTTPException avec messages explicites

### 📄 Fichiers Modifiés
- `backend/services/pdf_generator.py` - Ajout 2 nouvelles méthodes (~300 lignes)
- `backend/routers/employes.py` - Ajout 2 nouveaux endpoints

### 📚 Documentation
- Code documenté avec docstrings détaillées
- Spécification des paramètres attendus dans employe_data dict

## [1.1.3] - 2025-11-13 ✅ ACTUELLE

### ✨ Nouvelles Fonctionnalités
- **Module Postes de Travail** : Gestion complète et dynamique des postes (CRUD, filtrage, protection postes système)
  - Table `postes_travail` avec colonnes : id, libelle, est_chauffeur, modifiable, actif
  - Router API `/api/postes` complet avec authentification admin
  - Interface React : `PostesList.jsx` et `PosteForm.jsx`
  - Service frontend `posteService` avec authentification automatique
  - Les postes ne sont plus hardcodés dans le formulaire employé
- **Durée de Contrat Automatique** : Ajout champ `duree_contrat` (mois) avec calcul automatique de `date_fin_contrat`
  - Migration `migrate_add_duree_contrat.py`
  - Champ affiché dans le formulaire employé

### 🐛 Corrections Critiques
- **Erreur 401 Module Postes** : Correction authentification dans `PostesList.jsx` et `PosteForm.jsx`
  - Remplacement `axios` direct par `posteService` avec intercepteur automatique
- **Erreur 401 Formulaire Employé** : Correction chargement liste postes dans `EmployeForm.jsx`
  - Import et utilisation de `posteService.getAll()`
- **Validation Salaire Incorrect** : Fix parser InputNumber retournant string au lieu de number
  - Ajout conversion explicite : `parser={value => { ... return Number(parsed) }}`
  - La validation `min: 20000` fonctionne maintenant correctement

### 📄 Fichiers Ajoutés
- `backend/routers/postes_travail.py` - Router API postes
- `backend/models/poste_travail.py` - Modèle SQLAlchemy
- `backend/schemas/poste_travail.py` - Schemas Pydantic
- `backend/migrate_add_duree_contrat.py` - Migration durée contrat
- `backend/migrate_add_postes_travail.py` - Migration postes
- `frontend/src/pages/Postes/PostesList.jsx` - Composant liste
- `frontend/src/pages/Postes/PosteForm.jsx` - Composant formulaire
- `SESSION_CORRECTIONS_V1.1.3.md` - Documentation complète (519 lignes)
- `RELEASE_NOTES_V1.1.3.md` - Notes de release détaillées

### 📄 Fichiers Modifiés
- `frontend/src/services/index.js` - Ajout `posteService`
- `frontend/src/pages/Employes/EmployeForm.jsx` - Fix auth + durée contrat + validation salaire
- `frontend/src/App.jsx` - Ajout route `/postes`
- `backend/main.py` - Enregistrement router postes

### 🔧 Améliorations Techniques
- Architecture service centralisé pour authentification (tous modules utilisent services configurés)
- Validation robuste avec types corrects (number vs string)
- Code plus maintenable (suppression axios redondant, services réutilisables)

### 📊 Commits
- `d0f1ebd` - fix(frontend): Correction validation salaire
- `75dc44c` - fix(frontend): Correction authentification EmployeForm
- `069acf4` - fix(frontend): Correction authentification module Postes
- `b1f8113` - docs: Documentation session v1.1.3
- `e0c2fa3` - feat: Ajout durée contrat + module postes
- `1d29c82` - fix: Corrections bugs v1.1.2

---

## [1.1.2] - 2025-11-13

### 🐛 Corrections
- **PDF Bulletins de Paie** : Affichage dynamique des informations entreprise depuis `parametres_entreprise` (raison sociale, adresse, CNAS) au lieu de valeurs codées en dur
- **Footer PDF** : Ajout automatique de "Powered by AIRBAND" sur tous les bulletins de paie
- **Test Connexion DB** : Encodage correct des mots de passe avec caractères spéciaux (!@#$%^&*) via `quote_plus()` dans `DatabaseConfig.connection_string()`
- **Création Employé** : Correction erreur 500 - ajout du champ `actif: bool = True` dans les schémas Pydantic (EmployeBase, EmployeUpdate)
- **React Router** : Suppression des warnings v7 via ajout des future flags `v7_startTransition` et `v7_relativeSplatPath`

### 📄 Fichiers Modifiés
- `backend/services/pdf_generator.py` (12 lignes)
- `backend/models/database_config.py` (3 lignes)
- `backend/schemas/employe.py` (2 lignes)
- `frontend/src/App.jsx` (6 lignes)

### 📝 Documentation
- Ajout de `CORRECTIONS_V1.1.2.md` (374 lignes)

---

## [1.1.1] - 2025-11-12

### 🛡️ Protection des Données (CRITIQUE)
- **Soft Delete** : Les employés avec données liées (pointages, salaires, missions, avances, crédits) ne peuvent plus être supprimés définitivement
- **Vérification Automatique** : Le système vérifie l'existence de données liées avant suppression
- **Désactivation** : Employés avec données → désactivés (`actif=FALSE`) au lieu de supprimés
- **Suppression Définitive** : Autorisée uniquement si aucune donnée liée
- **Filtrage Automatique** : Employés inactifs exclus des listes par défaut (paramètre `inclure_inactifs`)

### 🐛 Corrections
- **Logging Suppressions** : Log enregistré AVANT `db.delete()` au lieu d'après (fix session invalide)
- **CORS Réseau LAN** : `allow_origins=["*"]` pour accepter toutes les machines du réseau local
- **Encodage Password DB** : Ajout `quote_plus()` dans `database_config.py` endpoints `/test` et `/`
- **Frontend Paramètres** : Vérifications null + valeurs par défaut si API ne retourne pas de données

### 🗄️ Base de Données
- **Migration** : Ajout colonne `actif BOOLEAN DEFAULT TRUE` à la table `employes`
- **Index** : `idx_employes_actif` pour optimiser les requêtes
- **Script** : `backend/add_actif_column.py` pour migration automatique

### 📄 Fichiers Modifiés
- `backend/routers/employes.py` (90 lignes) - Soft delete + logging fix
- `backend/models/employe.py` (1 ligne) - Colonne actif
- `backend/main.py` (1 ligne) - CORS ouvert
- `backend/routers/database_config.py` (8 lignes) - Encodage password
- `frontend/src/components/Layout/MainLayout.jsx` (12 lignes) - Null checks

### 📝 Documentation
- Ajout de `CORRECTIONS_V1.1.1.md` (280 lignes)

---

## [1.1.0] - 2025-11-12

### ✨ Nouvelles Fonctionnalités

#### Système de Logging Complet
- **Table `logging`** : 11 colonnes avec 5 index pour performance
- **Capture** : CREATE, UPDATE, DELETE sur tous les modules
- **Données** : `old_data` (JSON), `new_data` (JSON), user, timestamp, IP, module, description
- **Sécurité** : Logs en lecture seule (suppression uniquement via DB directe)
- **API** : 4 endpoints avec filtres avancés (module, action, user, dates, search)

#### Page Logs Frontend
- **Filtres** : Module dropdown, action (CREATE/UPDATE/DELETE), user, date range, recherche texte
- **Affichage** : Table avec tags colorés, pagination 100/page
- **Détail** : Modal avec JSON formatté (old_data, new_data)
- **Export** : Prêt pour export CSV (feature future)

#### Branding Entreprise
- **Logo Dynamique** : Initiales de l'entreprise (3 lettres max) depuis `parametres_entreprise`
- **Footer Global** : "Powered by AIRBAND" sur tous les écrans
- **PDF Personnalisés** : Infrastructure prête (méthodes `_create_company_header()`, `_create_footer()`)

### 📄 Fichiers Créés
**Backend (6 fichiers)**
- `backend/models/logging.py` (47 lignes) - Modèle Logging + ActionType enum
- `backend/services/logging_service.py` (97 lignes) - log_action() + clean_data_for_logging()
- `backend/routers/logs.py` (129 lignes) - 4 endpoints avec filtres
- `backend/middleware/logging_middleware.py` (59 lignes) - Placeholder futur
- `backend/create_logging_table.py` (24 lignes) - Script création table
- `database/add_logging_table.sql` (18 lignes) - SQL table logging

**Frontend (2 fichiers)**
- `frontend/src/services/logs.js` (19 lignes) - API service
- `frontend/src/pages/Logs/LogsPage.jsx` (371 lignes) - Interface logs

**Documentation (2 fichiers)**
- `AMELIORATIONS_V1.1.md` (458 lignes) - Guide complet
- `LOGGING_GUIDE.md` (295 lignes) - Tutoriel intégration

### 🔧 Fichiers Modifiés
- `backend/models/__init__.py` - Export Logging, ActionType
- `backend/routers/__init__.py` - Import logs router
- `backend/routers/employes.py` - Intégration logging (exemple)
- `backend/services/pdf_generator.py` - Méthodes branding
- `backend/main.py` - Inclusion logs router
- `frontend/src/components/Layout/MainLayout.jsx` - Logo initiales + footer

### 📊 Statistiques
- 6 nouveaux fichiers backend
- 2 nouveaux fichiers frontend
- 5 fichiers modifiés
- 1698 lignes de code ajoutées
- 753 lignes de documentation

---

## [1.0.0] - 2025-11-11

### 🎉 Première Version Stable

#### Authentification et Autorisation
- **JWT** : Système d'authentification complet
- **Rôles** : Admin (tous droits) + User (lecture seule)
- **Middleware** : `require_admin`, `require_auth`
- **Sécurité** : Tokens expirables, bcrypt pour passwords

#### Configuration Base de Données
- **Module** : Configuration dynamique de la connexion DB
- **Interface** : Page dédiée avec test de connexion
- **Historique** : Sauvegarde des configurations précédentes
- **Validation** : Test avant sauvegarde

#### Modules Opérationnels
- ✅ Gestion employés (CRUD complet)
- ✅ Système de pointage (grille 31 jours)
- ✅ Gestion clients et distances
- ✅ Ordres de mission chauffeurs
- ✅ Avances salariales
- ✅ Crédits avec prorogation
- ✅ Calcul salaires automatique
- ✅ Génération PDF/Excel

### 📝 Documentation Initiale
- `STATUS.md` - État du système
- `GUIDE_UTILISATEUR.md` - Guide utilisateur
- `INSTALLATION.md` - Guide installation
- `DATABASE_CONFIG_FEATURE.md` - Config DB
- `TESTS_AUTHENTIFICATION.md` - Tests auth

---

## [0.9.0] - 2025-11-10

### 🔄 Migration Système Pointage
- **Ancien** : Valeurs texte ("Travaillé", "Absent", etc.)
- **Nouveau** : Valeurs numériques (0, 1, 2, 3, 4, 5)
- **Raison** : Performance + Compatibilité base de données
- **Script** : Migration automatique avec backup

### 📝 Documentation
- `MIGRATION_POINTAGE_NUMERIQUE.md`

---

## [0.5.0] - 2025-11-09

### 🎉 Initial Commit
- **Système RH Complet** : Toutes les fonctionnalités de base
- **Backend** : FastAPI + SQLAlchemy + MariaDB
- **Frontend** : React + Ant Design + Vite
- **PDF/Excel** : ReportLab + XlsxWriter
- **Calculs** : Salaires + IRG + Primes

### 📝 Documentation Initiale
- `README.md`
- `GUIDE_UTILISATEUR.md`
- `INSTALLATION.md`
- `EXEMPLES_DONNEES.md`
- `RESUME_PROJET.md`

---

## Types de Changements

- `✨ Added` - Nouvelles fonctionnalités
- `🔧 Changed` - Changements dans les fonctionnalités existantes
- `⚠️ Deprecated` - Fonctionnalités bientôt supprimées
- `❌ Removed` - Fonctionnalités supprimées
- `🐛 Fixed` - Corrections de bugs
- `🔐 Security` - Corrections de sécurité
- `🗄️ Database` - Changements de schéma DB
- `📝 Documentation` - Ajouts/modifications documentation

---

## Roadmap (v1.2.0 et au-delà)

### v1.2.0 - Prévu
- 🐛 Corriger warnings Ant Design (Input.addonAfter, Form.Item.defaultValue)
- 📊 Dashboard statistiques avancées
- 📈 Graphiques et visualisations
- 🌍 Internationalisation (FR/AR/EN)
- 📤 Export CSV logs et rapports
- 🔍 Recherche globale cross-module

### v1.3.0 - Futur
- 📱 Application mobile (React Native)
- 📧 Notifications par email
- 🔔 Système d'alertes (contrats expirant, crédits à échéance, etc.)
- 📊 Reporting avancé avec filtres complexes
- 🎨 Thèmes customisables
- 🔄 Synchronisation multi-sites

### v2.0.0 - Vision
- ☁️ Version cloud avec multi-tenant
- 🤖 IA pour prédictions (turnover, absences, etc.)
- 📊 Business Intelligence intégré
- 🔗 Intégrations ERP/Comptabilité
- 📱 PWA (Progressive Web App)
- 🌐 API publique avec webhooks

---

**Légende Versions**
- ✅ **Stable** - Production ready
- 🧪 **Beta** - Tests utilisateurs
- 🚧 **Alpha** - Développement actif
- 📅 **Planifié** - Roadmap

**Contributeurs** : FingaDZ  
**Licence** : Usage interne  
**Repository** : https://github.com/FingaDZ/AY

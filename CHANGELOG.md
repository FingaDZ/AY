# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [1.1.2] - 2025-11-13 ✅ ACTUELLE

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

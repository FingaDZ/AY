## [3.6.1] - 2025-12-22

### ✨ Nouvelles Fonctionnalités

#### 📅 Gestion Avancée des Congés
- **Mois de déduction flexible** : Les congés peuvent maintenant être déduits dans un mois différent de leur acquisition
- Ajout colonnes `mois_deduction` (1-12) et `annee_deduction` dans la table `conges`
- Validation stricte des dates (mois: 1-12, année: 2000-2100)
- Intégration complète avec les bulletins de paie pour comptabilité précise

#### 💰 Calculs Précis Crédits & Avances
- **Échéancier automatique** : Calcul automatique des dates de début et fin lors de la création d'un crédit
- Ajout colonnes : `mois_debut`, `annee_debut`, `mois_fin_prevu`, `annee_fin_prevu`
- Début des retenues : mois suivant la date d'octroi
- Fin calculée automatiquement selon le nombre de mensualités
- Validation renforcée des périodes de retenue
- Contrôle strict 70% du salaire pour les avances maintenu

#### 🔄 Auto-Désactivation Contrats Expirés
- **Service automatique** : Nouveau service de détection et désactivation des employés avec contrat expiré
- Création service `employe_service.py` avec 3 fonctions principales
- 3 nouveaux endpoints API :
  - `GET /employes/contrats-expires` : Lister sans désactiver
  - `POST /employes/verifier-contrats-expires` : Désactiver automatiquement (Admin uniquement)
  - `POST /employes/mettre-a-jour-dates-fin-contrat` : Calculer dates manquantes (Admin uniquement)
- Workflow de réactivation contrôlé (mise à jour manuelle date_fin_contrat + actif)
- Logging complet de toutes les désactivations automatiques

#### 🔒 Logging Amélioré
- **Traçabilité complète** : Tous les logs incluent maintenant :
  - `user_id` et `user_email` : Identification de l'utilisateur
  - `ip_address` : Adresse IP de la requête
  - `record_id` : ID de l'enregistrement modifié
- Modules concernés : Congés, Crédits, Avances, Missions, Clients, Employés
- Amélioration de l'audit et de la conformité

### 🔧 Améliorations Techniques

#### Backend
- Modèles Congé et Crédit : Nouvelles colonnes avec commentaires
- Service employé : Gestion automatique des contrats
- Routers : Logging enrichi dans 6 modules
- Configuration : Version 3.6.1

#### Frontend
- Version affichée : v3.6.1 (Dashboard et Login)
- Package.json : Version 3.6.1

#### Base de Données (MySQL)
- Script migration `migration_v3.6.1_conges_credits_contrats.sql`
- 6 nouvelles colonnes (2 congés + 4 crédits)
- 3 index ajoutés pour optimisation des performances
- Mise à jour automatique des données existantes

### 🐛 Correctifs
- **Migration SQL** : Syntaxe corrigée de PostgreSQL vers MySQL
  - `EXTRACT()` → `MONTH()`, `YEAR()`
  - `COMMENT ON COLUMN` → `COMMENT` inline
  - `INTEGER` → `INT`
  - `WHERE` dans index → syntaxe MySQL
  - `DATE_ADD()` avec `INTERVAL`
- Validation dates renforcée pour crédits et avances
- Index optimisés pour meilleures performances

### 📚 Documentation
- **RELEASE_V3.6.1.md** : Documentation complète des nouvelles fonctionnalités
- **UPGRADE_V3.6.1.md** : Guide de mise à jour détaillé avec checklist
- **GIT_DEPLOY_v3.6.1.md** : Instructions Git et déploiement GitHub
- **SUMMARY_v3.6.1.md** : Résumé technique complet
- **README.md** : Section nouveautés v3.6.1 ajoutée

### 📦 Versions
- Backend : `3.6.1`
- Frontend : `3.6.1`
- Migration : `migration_v3.6.1_conges_credits_contrats.sql`

---

## [3.5.0] - 2025-12-10
### 📄 Génération PDF Améliorée
- **Rapport Salaires**
  - Footer en pied de page sur toutes les pages : "Rapport généré le ... | Powered by AIRBAND"
  - Marges étroites (0.5cm) pour optimisation espace
  - Format paysage une seule page avec toutes colonnes
  
- **Page de Garde Bulletins**
  - En-tête entreprise détaillé : Nom, Adresse, N° Employeur SS, NIF (ligne par ligne)
  - Suppression : Total Jours Travaillés et Total Jours d'Absences
  - Ajout : Total CNAS 9% (sous Total Salaire Cotisable)
  - Ajout : Total IRG (sous Total Salaire Imposable)
  - Footer en pied de page : "Powered by AIRBAND"
  - Marges étroites (0.75cm)
  
- **Bulletin de Paie Individuel**
  - Nouvelle ligne : "Jours de congé pris ce mois" (si applicable)
  - Footer en pied de page : "Bulletin généré le ... | Powered by AIRBAND"
  
- **Attestation de Travail**
  - QR Code ajouté avec : Nom, Date Naissance, Date Recrutement, Durée Contrat, Poste, N°SS, N°ANEM
  - QR Code positionné à droite de la signature
  
- **Certificat de Travail**
  - QR Code ajouté avec : Nom, Date Naissance, Date Recrutement, Date Fin Contrat, Poste, N°SS, N°ANEM
  - QR Code positionné à droite de la signature
  
- **Contrat de Travail** (✅ COMPLÉTÉ)
  - Ajout N° ANEM après N° Sécurité Sociale (ligne salarié)
  - Génération automatique du numéro de contrat (Format: CT-XXXX-YYYY)
  - "Date de début" → "Date de Recrutement"
  - Durée calculée et inscrite en mois (calcul automatique entre dates)
  - Article 1 : Poste en gras (Helvetica-Bold pour le poste uniquement)
  - Article 3 : Mention déplacements national/international ajoutée
  - Article 5 : Rémunération sur une seule ligne (compacté)
  - Article 6 : Primes et indemnités du bulletin réelles (IN, IFSP, IEP, Prime Encouragement, Prime Chauffeur, Prime Nuit, Prime Déplacement, Panier, Transport)
  - Articles 7-8-9 : Espacement réduit (y -= 15 au lieu de 20)
  - Article 9 : Préavis de quinze (15) jours (au lieu de 1 mois)
  - Article 10 : Tribunal de Chelghoum Laid territorialement compétent (juridiction précisée)
  - QR Code en haut à droite avec toutes données (N° Contrat, Société, Nom, N°SS, N°ANEM, Dates, Poste, Salaire)
  - Footer avec numérotation sur chaque page : "Page X/2 | Powered by AIRBAND"
  - Marges optimisées pour footer

### 🗄️ Base de Données
- **Migration** : Ajout colonne `numero_anem` à la table `employes`
- **Index** : Création index sur `numero_anem` pour optimisation recherches

### 📦 Versions
- Backend : `3.5.0`
- Frontend : `3.5.0`

---

## [3.0.0] - 2025-12-09
### 🎉 Fonctionnalités Majeures
- **Traitement Salaires v3.0** : Nouveau module de calcul des salaires automatique et traçable
  - **Calcul Proratisé Intelligent** : Toutes les primes/indemnités proratisées sur base 30 jours (au lieu de montants mensuels fixes)
  - **IRG Extrapolé** : Calcul IRG avec proratisation (salaire → base 30j → IRG 30j → IRG proratisé)
  - **4 Statistiques en Temps Réel** : Masse Nette, Masse Cotisable, Masse Imposable, Total IRG
  - **Colonnes Enrichies** : Tableau avec Salaire Base, Cotisable, Imposable, IRG, Net
  - **Filtrage Multi-Critères** : Recherche par Nom, Statut (OK/Alerte/Erreur), Salaire Min/Max
  - **Interface Compacte** : Cartes statistiques homogénéisées et optimisées
  - **Validation Individuelle** : Aperçu détaillé 13 étapes + bouton Valider
  - **Validation Globale** : Bouton "Valider Tous" pour enregistrement en base

### 🔧 Améliorations Backend
- **Proratisation Base 30 Jours** : Correction calcul primes/indemnités
  - Indemnité Nuisance → proratisée
  - IFSP → proratisé
  - IEP → proratisé
  - Prime Encouragement → proratisée
  - Prime Chauffeur → proratisée
  - Prime Nuit Agent Sécurité → proratisée
  - Panier → proratisé
  - Prime Transport → proratisée
  - Prime Femme Foyer → proratisée
- **Correctifs Attributs** : Fix `Credit.montant_mensualite` et `Mission.prime_calculee`
- **Statistiques API** : Ajout `masse_cotisable`, `masse_imposable`, `total_irg`

### 🎨 Améliorations Frontend
- **Cartes Statistiques** : Design compact et homogénéisé (grid 6 colonnes)
- **Filtres Avancés** : Barre de recherche multi-critères avec compteur résultats
- **Colonnes Tableau** : Ajout Salaire Cotisable, Imposable, IRG avec couleurs différenciées
- **Responsive** : Optimisation affichage sur différentes tailles d'écran

### 📦 Versions
- Backend : `3.0.0`
- Frontend : `3.0.0`
- Login : `3.0.0`
- Layout/Sidebar : `3.0.0`

---

## [2.5.0] - 2025-12-08
### ✨ Fonctionnalités
- **Traitement Salaires** : Première version module calcul salaires (architecture + backend + frontend)
- **Désactivation Edition Salaires** : Ancien module désactivé dans menu

## [2.3.0] - 2025-11-29
### 🗑️ Simplification
- **Nettoyage** : Suppression du module "Logs Incomplets" (simplification du flux)
- **Version** : Passage global à la version 2.3.0

## [2.2.0] - 2025-11-29
### ✨ Fonctionnalités
- **Pointages** : Correction affichage (T/A au lieu de tirets)
- **Règles Métier** : 
  - Vendredis marqués automatiquement "Travaillé" (1) par défaut
  - Règle "Vendredi entre Absences" : Si Jeudi (0) et Samedi (0) => Vendredi (0)
  - Autres jours non pointés marqués "Absent" (0) par défaut
- **Doublons** : Correction création doublons pointages + contrainte unicité DB

## [2.0.1] - 2025-11-29
### 🐛 Correctifs
- Résolution des problèmes de cache navigateur après mise à jour
- Affichage de la version et branding sur tous les écrans
- Amélioration du script de déploiement

## [1.7.0] - 2025-11-28
### ✨ Fonctionnalités Majeures
- **Gestion Hybride des Logs Incomplets** : Solution complète pour les pointages manquants (ENTRY sans EXIT ou inversement)
  - **Calcul Intelligent** : Estimation automatique des heures (ex: ENTRY seul → sortie supposée 17h)
  - **Dashboard de Validation** : Interface RH pour valider/corriger les estimations
  - **Notifications** : Alertes automatiques lors de l'import de logs incomplets
  - **Traçabilité** : Historique complet des validations et corrections manuelles

### 🚀 Améliorations
- **Import Pointages** : Support robuste des erreurs de synchronisation
- **Interface** : Nouveau menu "Logs Incomplets" avec badges de notification
- **Base de Données** : Nouvelle table `incomplete_attendance_logs`

### 📄 Fichiers Ajoutés
- `backend/models/incomplete_log.py`
- `backend/schemas/incomplete_log.py`
- `backend/routers/incomplete_logs.py`
- `frontend/src/pages/IncompleteLogs/IncompleteLogsList.jsx`

---

## [1.3.0] - 2025-11-25

### ✨ Ajouté
- **Intégration Attendance** : Synchronisation complète avec système de pointage biométrique
  - Backend : 8 endpoints API REST pour sync employés, import logs, gestion conflits
  - Frontend : 3 pages (Import, Conflits, Service API)
  - Database : 3 nouvelles tables + colonne heures_supplementaires
- **Sync Employés** : HR → Attendance (nom, poste, PIN)
- **Import Pointages** : Attendance → HR avec conversion minutes → jours
- **Heures Supplémentaires** : Calcul automatique (>8h/jour)
- **Gestion Conflits** : Détection et résolution manuelle des conflits d'import
- **Mapping Intelligent** : Par numéro sécu sociale ou nom+prénom+date

### 📚 Documentation
- Guide stratégie : ATTENDANCE_INTEGRATION.md
- Guide frontend : ATTENDANCE_FRONTEND_GUIDE.md
- Guide déploiement : DEPLOYMENT_V1.3.0-BETA.md
- Instructions sync button : SYNC_BUTTON_INSTRUCTIONS.md
- Release summary : RELEASE_v1.3.0.md

### 🔧 Scripts
- upgrade.sh : Migration automatique v1.2.x → v1.3.0

---

## [1.3.0-beta] - 2025-11-25 ✅ ACTUELLE

### 🔗 Intégration Attendance (Backend)
- **Database** : Tables de mapping, sync log, et conflits
  - `attendance_employee_mapping` : Lien HR ↔ Attendance
  - `attendance_sync_log` : Historique des imports
  - `attendance_import_conflicts` : Gestion des conflits
  - Colonne `heures_supplementaires` ajoutée à `pointages`
- **Backend Services** :
  - `models/attendance_mapping.py` : Modèles SQLAlchemy
  - `services/attendance_service.py` : Logique de sync et import
  - `routers/attendance_integration.py` : 8 endpoints API
- **API Endpoints** :
  - `POST /sync-employee` : Sync employé vers Attendance
  - `POST /sync-all-employees` : Sync tous les employés
  - `POST /import-logs` : Importer logs de pointage
  - `GET /conflicts` : Lister conflits
  - `POST /conflicts/{id}/resolve` : Résoudre conflit
- **Documentation** :
  - `ATTENDANCE_FRONTEND_GUIDE.md` : Guide d'implémentation frontend
  - `ATTENDANCE_INTEGRATION.md` : Stratégie d'intégration

### ⚠️ Notes
- **Frontend** : Non inclus dans cette version (guide fourni)
- **Migration** : Exécuter `001_attendance_integration.sql` avant utilisation
- **Configuration** : Ajouter `ATTENDANCE_API_URL` dans `.env`

---

## [1.2.4] - 2025-11-25

### ✨ Fonctionnalités
- **Gestion Utilisateurs** : Restauration du module de gestion des utilisateurs (Admin)
  - Ajout du lien "Utilisateurs" dans la barre latérale
- **Intégration Attendance** : Analyse et documentation de l'intégration
  - Création de `ATTENDANCE_INTEGRATION.md`

### 📄 Fichiers Modifiés
- `frontend/src/components/Sidebar.jsx` - Ajout lien Utilisateurs
- `ATTENDANCE_INTEGRATION.md` - [NOUVEAU] Documentation technique

---

## [1.2.3] - 2025-11-25

### 🚀 Automatisation
- **Scripts** : Ajout de scripts d'automatisation pour simplifier la gestion du serveur
  - `update.sh` : Mise à jour en un clic (Git Pull + Build + Restart)
  - `install.sh` : Installation initiale automatisée
- **Documentation** : Mise à jour des guides pour inclure l'utilisation des scripts

### 📄 Fichiers Modifiés
- `update.sh` - [NOUVEAU] Script de mise à jour
- `install.sh` - [NOUVEAU] Script d'installation
- `DEPLOYMENT_LINUX.md` - Instructions automatisées
- `README.md` - Section mise à jour automatique

---

## [1.2.2] - 2025-11-25

### 🐛 Corrections
- **Documentation** : Correction de la structure du `README.md`
- **Version** : Bump v1.2.2 pour cohérence

---

## [1.2.1] - 2025-11-25

### 🐛 Corrections Critiques
- **Build Error** : Fix erreur de compilation due à un import dupliqué dans `Sidebar.jsx`
  - Suppression de l'import dupliqué de `SettingsIcon`

### 📚 Documentation
- Mise à jour des guides de déploiement (`DEPLOYMENT_LINUX.md`, `INSTALL_UBUNTU_22.04.md`)
- Mise à jour du `README.md` (Version, Badges)

### 📄 Fichiers Modifiés
- `frontend/src/components/Sidebar.jsx` - Fix import + Version 1.2.1
- `frontend/src/components/Layout.jsx` - Version 1.2.1
- `frontend/src/pages/Login/LoginPage.jsx` - Version 1.2.1
- `frontend/package.json` - Version 1.2.1
- `backend/config.py` - Version 1.2.1

---

## [1.2.0] - 2025-11-25

### ✨ Nouvelles Fonctionnalités
- **Gestion des Congés** : Module complet de suivi des congés
  - Tableau de bord des congés par employé et période
  - Calcul automatique des droits (Acquis vs Pris)
  - Saisie de la consommation mensuelle
- **Interface Utilisateur** : Réorganisation majeure de la barre latérale
  - Restauration de l'onglet **Postes**
  - Ajout de l'onglet **Base de données**
  - Réorganisation logique des menus (Dashboard > Employés > Postes > Pointages...)
  - Masquage esthétique de la barre de défilement (tout en restant fonctionnelle)

### 📄 Fichiers Modifiés
- `backend/routers/conges.py` - [NOUVEAU] API Congés
- `backend/main.py` - Enregistrement routeur Congés
- `frontend/src/pages/Conges/CongesList.jsx` - [NOUVEAU] Interface Congés
- `frontend/src/components/Sidebar.jsx` - Réorganisation + Postes + Scrollbar hidden
- `frontend/src/App.jsx` - Route Congés
- `frontend/package.json` - Version 1.2.0

---

## [1.1.11] - 2025-11-25

### 🐛 Corrections Critiques
- **Pages Blanches** : Fix affichage du contenu
  - Remplacement de `<Outlet />` par `{children}` dans `Layout.jsx` car le routage est géré dans `App.jsx` via composition et non par routes imbriquées.

### 📄 Fichiers Modifiés
- `frontend/src/components/Layout.jsx` - Fix Outlet -> children + Version 1.1.11
- `frontend/package.json` - Version 1.1.11
- `frontend/src/components/Sidebar.jsx` - Version 1.1.11
- `frontend/src/pages/Login/LoginPage.jsx` - Version 1.1.11

---

## [1.1.10] - 2025-11-25

### 🐛 Corrections Critiques
- **Build Error** : Fix erreur de compilation due à un import dupliqué dans `Sidebar.jsx`
  - Suppression de l'import dupliqué de `SettingsIcon`

### 📄 Fichiers Modifiés
- `frontend/src/components/Sidebar.jsx` - Fix import + Version 1.1.10
- `frontend/src/components/Layout.jsx` - Version 1.1.10
- `frontend/src/pages/Login/LoginPage.jsx` - Version 1.1.10
- `frontend/package.json` - Version 1.1.10

---

## [1.1.9] - 2025-11-25

### 🐛 Corrections Critiques
- **Accès WAN (403)** : Fix erreur "Blocked request" sur domaine externe
  - Ajout de `allowedHosts` dans `vite.config.js` pour autoriser `hgd09pzcrcm.sn.mynetname.net` et `192.168.20.53`
- **Pages Vides** : Fix CSS Layout pour garantir l'affichage du contenu
  - Ajustement de la structure Flexbox et des hauteurs
- **Navigation** : Ajout de l'onglet **Logs** manquant dans la barre latérale

### 📄 Fichiers Modifiés
- `frontend/vite.config.js` - Configuration `allowedHosts`
- `frontend/src/components/Layout.jsx` - Fix CSS + Version 1.1.9
- `frontend/src/components/Sidebar.jsx` - Ajout Logs + Version 1.1.9
- `frontend/src/pages/Login/LoginPage.jsx` - Version 1.1.9
- `frontend/package.json` - Version 1.1.9

---

## [1.1.8] - 2025-11-25

### 🐛 Corrections Critiques
- **Layout & Affichage** : Fix structure Layout pour garantir l'affichage du contenu
  - Simplification de la structure Flexbox
  - Correction du scrolling du contenu principal
- **Sidebar Scrolling** : Fix définitif du défilement de la barre latérale
  - Structure `flex-col` avec `h-full`
  - Scrollbar personnalisée pour le menu de navigation
- **CORS & Réseau** : Configuration permissive pour déploiement LAN/WAN
  - `CORS_ORIGINS="*"` pour autoriser toutes les origines (fix accès WAN)

### 🎨 Rebranding
- **Nom du Système** : Changement de "AY HR System" vers "HR System"
  - Mis à jour dans Sidebar, Layout, Login Page, Config Backend

### 📄 Fichiers Modifiés
- `frontend/src/components/Layout.jsx` - Fix structure + Branding
- `frontend/src/components/Sidebar.jsx` - Fix scrolling + Branding
- `frontend/src/pages/Login/LoginPage.jsx` - Branding
- `backend/config.py` - CORS "*" + Branding + Version 1.1.8
- `frontend/package.json` - Version 1.1.8

---

## [1.1.7] - 2025-11-25

### 🌐 Corrections Réseau
- **Accès WAN** : Fix erreur 403 sur domaine externe (hgd09pzcrcm.sn.mynetname.net)
  - Ajout configuration CORS pour le domaine externe dans backend/config.py
  - Note: Vite en mode dev n'a pas besoin de allowedHosts (géré par le serveur)

### 📝 Logging Complet
- **Ajout Logging Backend** : Implémentation logging pour 4 modules
  - ✅ `missions.py` - Logging CREATE, UPDATE, DELETE
  - ✅ `avances.py` - Logging CREATE, UPDATE, DELETE
  - ✅ `credits.py` - Logging CREATE, UPDATE, DELETE
  - ✅ `clients.py` - Logging CREATE, UPDATE, DELETE
  - Tous les modules principaux ont maintenant un logging complet sauf pointages et salaires (prévu v1.2.0)

### 🎨 Améliorations
- **Version Display** : Mise à jour version 1.1.7 partout
  - Backend config.py : APP_VERSION = "1.1.7"
  - Frontend package.json, Sidebar, Layout, LoginPage

### 📄 Fichiers Modifiés
- `backend/config.py` - CORS + version 1.1.7
- `backend/routers/missions.py` - Ajout logging
- `backend/routers/avances.py` - Ajout logging
- `backend/routers/credits.py` - Ajout logging
- `backend/routers/clients.py` - Ajout logging
- `frontend/package.json` - Version 1.1.7
- `frontend/src/components/Sidebar.jsx` - Version 1.1.7
- `frontend/src/components/Layout.jsx` - Version 1.1.7
- `frontend/src/pages/Login/LoginPage.jsx` - Version 1.1.7

---

## [1.1.6] - 2025-11-25

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

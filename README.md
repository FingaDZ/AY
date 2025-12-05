# HR System

[![Version](https://img.shields.io/badge/version-2.4.2-blue.svg)](https://github.com/FingaDZ/AY/releases/tag/v2.4.2)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/FingaDZ/AY)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)]()

> **Version actuelle** : 2.4.2
> **Dernière mise à jour** : 05 décembre 2025  
> **Statut** : ✅ Production Ready

## 📋 Description

Système complet de gestion des ressources humaines développé avec FastAPI (backend) et React (frontend).

### Fonctionnalités Principales

- ✅ **Gestion des Employés** : Suivi complet des dossiers (infos personnelles, contrats, postes).
- ✅ **Gestion des Postes** : Configuration dynamique des postes de travail.
- ✅ **Pointages** : Suivi des présences, absences et congés.
- ✅ **Gestion des Congés** : Suivi des droits, consommation et soldes.
- ✅ **Paie & Salaires** : Calcul automatisé des salaires, primes et retenues.
- ✅ **Avances & Crédits** : Gestion financière des employés.
- ✅ **Missions** : Suivi des ordres de mission.
- ✅ **Logs & Audit** : Traçabilité des actions critiques.
- 🆕 **Intégration Attendance** : Synchronisation avec système de pointage biométrique (v1.3.0-beta).

### 📸 Aperçu de l'Interface

<div align="center">
  <img src="docs/screenshots/dashboard.png" alt="Dashboard" width="800"/>
  <p><em>Tableau de bord principal avec statistiques en temps réel</em></p>
</div>

<div align="center">
  <img src="docs/screenshots/attendance.png" alt="Pointages" width="800"/>
  <p><em>Suivi des pointages et présences</em></p>
</div>


<div align="center">
  <img src="docs/screenshots/payroll.png" alt="Paie" width="800"/>
  <p><em>Calcul automatisé des salaires</em></p>
</div>

## 🛠️ Stack Technique

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Base de données**: MariaDB 10.5+ / MySQL 8.0+
- **ORM**: SQLAlchemy
- **Rapports**: ReportLab (PDF), XlsxWriter (Excel)
- **Validation**: Pydantic
- **Authentification**: JWT

### Frontend
- **Framework**: React 18 + Vite
- **UI Library**: Ant Design 5
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Date Handling**: Day.js

## 📁 Structure du Projet

```
AY HR/
├── backend/
│   ├── main.py              # Point d'entrée API
│   ├── config.py            # Configuration
│   ├── database.py          # Configuration DB
│   ├── models/              # Modèles SQLAlchemy
│   ├── schemas/             # Schémas Pydantic
│   ├── routers/             # Routes API
│   └── services/            # Logique métier
├── frontend/
│   ├── src/
│   │   ├── components/      # Composants React
│   │   ├── pages/           # Pages de l'application
│   │   ├── services/        # Services API
│   │   └── contexts/        # Contextes React
│   ├── package.json
│   └── vite.config.js
├── database/
│   └── create_database.sql  # Script d'initialisation DB
├── DEPLOYMENT_LINUX.md      # Guide déploiement Linux
├── INSTALL_UBUNTU_22.04.md  # Guide installation Ubuntu
├── CHANGELOG.md             # Historique des versions
└── README.md                # Ce fichier
```

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.9+
- Node.js 18+
- MariaDB 10.5+ ou MySQL 8.0+

### Installation Serveur (Production)

```bash
# 1. Cloner
git clone https://github.com/FingaDZ/AY.git /opt/ay-hr
cd /opt/ay-hr

# 2. Installer
chmod +x install.sh
sudo ./install.sh
```

### Mise à Jour Automatique

Pour mettre à jour vers la dernière version :

```bash
cd /opt/ay-hr
sudo ./update.sh
```

### Upgrade vers v1.3.0-beta (Attendance Integration)

Pour upgrader depuis v1.2.x vers v1.3.0-beta :

```bash
cd /opt/ay-hr
git pull origin main
chmod +x upgrade.sh
sudo ./upgrade.sh
```

Voir [DEPLOYMENT_V1.3.0-BETA.md](DEPLOYMENT_V1.3.0-BETA.md) pour les détails.

### Installation Locale (Développement)

#### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env avec vos paramètres

# Démarrer le serveur
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### Accès

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

## 📖 Documentation

- **[DEPLOYMENT_LINUX.md](DEPLOYMENT_LINUX.md)** - Guide de déploiement complet pour Linux
- **[INSTALL_UBUNTU_22.04.md](INSTALL_UBUNTU_22.04.md)** - Installation sur Ubuntu 22.04
- **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions

## 🔧 Configuration

### Base de Données

Créer un fichier `.env` dans le dossier `backend`:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost/ay_hr
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000

# Attendance Integration (v1.3.0+)
ATTENDANCE_API_URL=http://192.168.20.56:8000/api
ATTENDANCE_API_TIMEOUT=30
```

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL de connexion MySQL | - |
| `SECRET_KEY` | Clé secrète JWT | - |
| `CORS_ORIGINS` | Origines CORS autorisées | localhost:3000 |
| `DEBUG` | Mode debug | False |
| `ATTENDANCE_API_URL` | URL API Attendance (v1.3.0+) | http://192.168.20.56:8000/api |
| `ATTENDANCE_API_TIMEOUT` | Timeout API Attendance (v1.3.0+) | 30 |

## 📊 État du Système

| Module | Version | Statut | Dernière Mise à Jour |
|--------|---------|--------|----------------------|
| **Frontend** | v2.4.2 | ✅ Stable | 05 Déc 2025 |
| **Backend** | v2.4.2 | ✅ Stable | 05 Déc 2025 |
| **Base de Données** | MariaDB | ✅ Connecté | 05 Déc 2025 |

## 🔐 Sécurité

- ✅ Authentification JWT
- ✅ Hachage des mots de passe (bcrypt)
- ✅ Validation des données (Pydantic)
- ✅ CORS configuré
- ✅ Soft delete pour données sensibles
- ✅ Logging complet des actions

## 📝 Changelog

### v2.4.2 - 05 décembre 2025 ✨ ACTUELLE
- 🔒 **Rôles Utilisateur** : Réimplémentation complète du système de rôles (Admin vs Utilisateur)
- 📊 **PDF Logistique** : Export PDF soldes logistiques (individuel + global)
- 🛡️ **Protection Clients** : Impossible de supprimer clients avec mouvements logistiques
- 🎯 **Filtrage Routes** : Utilisateurs limités à Dashboard + Missions uniquement

### v2.4.1 - 05 décembre 2025
- 📝 **PDF Ordre Mission** : Correction erreur 500 + améliorations mise en page
- 📦 **Logistique** : Ajout cases Montant versé (x3) et Observations (x2.5)
- 🔗 **API Logistique** : Route `/clients/{id}/logistics-balance` pour soldes
- 🎨 **UI Clients** : Modal affichage soldes logistiques par client

### v2.3.0 - 29 novembre 2025
- 🗑️ **Nettoyage** : Suppression du module "Logs Incomplets"
- 🔄 **Version** : Passage global à la version 2.3.0

### v2.2.0 - 29 novembre 2025
- 🔄 **Refactoring Majeur** : Système d'import complètement refactoré
- 📊 **Calculs Journaliers** : 1 entrée + 1 sortie par jour avec règles métier
- ⚖️ **Règles Business** : Vendredis travaillés par défaut, règle "Vendredi entre Absences"
- 🎯 **Estimation Intelligente** : Entrée/sortie manquante estimée automatiquement
- 🗑️ **Nettoyage** : Suppression pages redondantes
- 🔍 **Filtres Avancés** : Statut + Employé + Date
- 📋 **Colonnes Améliorées** : Date, Jour, Entrée, Sortie, Durée, H.Sup, Statut, Pointage
- ⚡ **Import Direct** : Option import rapide sans prévisualisation

### v2.1.0 - 29 novembre 2025
- 🎯 **Import Preview** : Prévisualisation et validation avant import
- 🧠 **Matching Intelligent** : Fuzzy matching avec Levenshtein (auto-match ≥85%)
- ⚠️ **Validation Avancée** : Détection conflits, doublons, logs incomplets
- 📊 **Statistiques** : Résumé complet (OK/Warning/Error)
- 🔗 **Nouveaux Endpoints** : `/import-preview`, `/import-confirm`

### v2.0.3 - 29 novembre 2025
- 🐛 **Correctif Critique** : Fix compatibilité Pydantic v2 pour endpoint conflits (erreur 500)
- ✨ **Amélioration** : Affichage noms et postes employés sur page Conflits Import
- 📊 **UX** : Meilleure lisibilité des conflits d'importation

### v2.0.2 - 29 novembre 2025
- ✨ **Import Excel** : Ajout de l'importation manuelle de fichiers Excel pour les pointages
- 🐛 **Correctif** : Validation et parsing améliorés pour les fichiers d'import

### v2.0.1 - 29 novembre 2025
- 🐛 **Correctif** : Résolution des problèmes de cache navigateur après mise à jour
- 🐛 **Correctif** : Affichage de la version et branding sur tous les écrans
- 🔄 **Système** : Amélioration du script de déploiement

### v1.7.0 - 29 novembre 2025
- 🛡️ **Gestion Logs Incomplets** : Solution hybride (Calcul Smart + Validation RH)
- 📊 **Dashboard** : Interface de validation des estimations
- 🚀 **Fiabilité** : Import robuste sans perte de données
- 📱 **UI** : Notifications et badges pour actions requises

### v1.3.0 - 25 novembre 2025
- 🔗 **Intégration Attendance** : Backend complet (sync employés, import logs, gestion conflits)
- 🗄️ **Database** : 3 nouvelles tables + colonne heures_supplementaires

### v1.2.4 - 25 novembre 2025
- ✨ **Gestion Utilisateurs** : Restauration du module Admin
- 📄 **Documentation** : Analyse système Attendance
- 🔧 **Scripts** : install.sh et update.sh automatisés

[Voir le changelog complet](CHANGELOG.md)

## 🔗 Intégration Attendance

### Fonctionnalités (v1.3.0-beta)

- ✅ **Sync Employés** : HR → Attendance (nom, poste, PIN)
- ✅ **Import Pointages** : Attendance → HR (conversion minutes → jours)
- ✅ **Heures Supplémentaires** : Calcul automatique (>8h/jour)
- ✅ **Gestion Conflits** : Détection et résolution manuelle
- ✅ **Mapping Intelligent** : Par numéro sécu sociale ou nom+prénom+date

### Documentation

- [ATTENDANCE_INTEGRATION.md](ATTENDANCE_INTEGRATION.md) - Stratégie d'intégration
- [ATTENDANCE_FRONTEND_GUIDE.md](ATTENDANCE_FRONTEND_GUIDE.md) - Guide implémentation UI
- [DEPLOYMENT_V1.3.0-BETA.md](DEPLOYMENT_V1.3.0-BETA.md) - Guide déploiement

### API Endpoints

Accédez à la documentation interactive : `http://192.168.20.53:8000/docs`

Section **"Attendance Integration"** :
- `POST /sync-employee` - Synchroniser un employé
- `POST /sync-all-employees` - Synchroniser tous les employés
- `POST /import-logs` - Importer les pointages
- `GET /conflicts` - Lister les conflits
- `POST /conflicts/{id}/resolve` - Résoudre un conflit

## 🤝 Support

Pour toute question ou problème:
1. Consultez la [documentation API](http://192.168.20.53:8000/docs)
2. Vérifiez le [CHANGELOG.md](CHANGELOG.md)
3. Consultez les guides de déploiement
4. Intégration Attendance : voir [ATTENDANCE_INTEGRATION.md](ATTENDANCE_INTEGRATION.md)

## 📜 Licence

Usage interne - Tous droits réservés

---

**Développé par AIRBAND**  
**Version** : 2.4.2  
**Date** : 05 décembre 2025

# HR System

[![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)](https://github.com/FingaDZ/AY/releases/tag/v1.2.3)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/FingaDZ/AY)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)]()

> **Version actuelle** : 1.2.3  
> **Dernière mise à jour** : 25 novembre 2025  
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
```

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL de connexion MySQL | - |
| `SECRET_KEY` | Clé secrète JWT | - |
| `CORS_ORIGINS` | Origines CORS autorisées | localhost:3000 |
| `DEBUG` | Mode debug | False |

## 📊 État du Système

| Module | Version | Statut | Dernière Mise à Jour |
|--------|---------|--------|----------------------|
| **Frontend** | v1.2.3 | ✅ Stable | 25 Nov 2025 |
| **Backend** | v1.2.3 | ✅ Stable | 25 Nov 2025 |
| **Base de Données** | MariaDB | ✅ Connecté | 25 Nov 2025 |

## 🔐 Sécurité

- ✅ Authentification JWT
- ✅ Hachage des mots de passe (bcrypt)
- ✅ Validation des données (Pydantic)
- ✅ CORS configuré
- ✅ Soft delete pour données sensibles
- ✅ Logging complet des actions

## 📝 Changelog

### v1.2.2 - 25 novembre 2025
- 🐛 Fix: Correction structure README.md
- ⬆️ Bump: Version v1.2.2

### v1.2.1 - 25 novembre 2025
- 🐛 Fix: Erreur de compilation (import dupliqué)
- 📚 Docs: Mise à jour guides déploiement

[Voir le changelog complet](CHANGELOG.md)

## 🤝 Support

Pour toute question ou problème:
1. Consultez la [documentation API](http://localhost:8000/docs)
2. Vérifiez le [CHANGELOG.md](CHANGELOG.md)
3. Consultez les guides de déploiement

## 📜 Licence

Usage interne - Tous droits réservés

---

**Développé par AIRBAND**  
**Version** : 1.2.3  
**Date** : 25 novembre 2025

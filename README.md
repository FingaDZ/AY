# AY HR Management System

[![Version](https://img.shields.io/badge/version-1.1.5-blue.svg)](https://github.com/FingaDZ/AY/releases/tag/v1.1.5)
[![Status](https://img.shields.io/badge/status-production%20ready-success.svg)](https://github.com/FingaDZ/AY)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)]()

> **Version actuelle** : 1.1.5  
> **Dernière mise à jour** : 25 novembre 2025  
> **Statut** : ✅ Production Ready

## 📋 Description

Système complet de gestion des ressources humaines développé avec FastAPI (backend) et React (frontend).

### Fonctionnalités Principales

- ✅ Gestion des employés (CRUD complet)
- ✅ Gestion dynamique des postes de travail
- ✅ Système de pointage mensuel automatisé
- ✅ Gestion des clients et distances
- ✅ Ordres de mission pour chauffeurs avec calcul de primes
- ✅ Gestion des avances salariales
- ✅ Système de crédits avec retenues mensuelles
- ✅ Calcul automatique des salaires (cotisable, imposable, net)
- ✅ Génération de rapports PDF/Excel
- ✅ Calcul IRG selon barème personnalisable
- ✅ Système d'authentification JWT
- ✅ Logging complet des actions

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

## 📊 Modules Principaux

### 1. Gestion des Employés
- CRUD complet avec validation
- Gestion des contrats et durées
- Informations personnelles et professionnelles
- Soft delete pour protection des données

### 2. Système de Pointage
- Grille mensuelle (31 jours)
- Types: Travaillé, Absent, Congé, Maladie, Férié, Arrêt
- Calculs automatiques
- Verrouillage des pointages validés

### 3. Calcul des Salaires
- Salaire de base proratisé
- Heures supplémentaires (majoration 50%)
- Primes (IN, IFSP, IEP, encouragement, chauffeur)
- Retenues (Sécurité Sociale 9%, IRG)
- Déduction avances et crédits

### 4. Gestion des Crédits
- Crédits à long terme
- Mensualités automatiques
- Système de prorogation
- Suivi du solde

### 5. Rapports
- Bulletins de paie PDF
- Rapports Excel personnalisés
- Déclaration G29 (IRG annuel)
- Statistiques et analyses

## 🔐 Sécurité

- ✅ Authentification JWT
- ✅ Hachage des mots de passe (bcrypt)
- ✅ Validation des données (Pydantic)
- ✅ CORS configuré
- ✅ Soft delete pour données sensibles
- ✅ Logging complet des actions

## 📝 Changelog

### v1.1.5 - 25 novembre 2025
- 🐛 Fix: Correction validation salaire_base lors de l'édition d'employé
- 🧹 Nettoyage: Suppression fichiers non essentiels
- 📚 Documentation: Guides de déploiement mis à jour

### v1.1.4 - 15 novembre 2025
- 📦 Package de déploiement complet
- 📚 Guides de déploiement simplifiés

### v1.1.3 - 14 novembre 2025
- 🔒 Soft delete avec protection données liées
- 🌐 CORS ouvert pour réseau LAN
- 🔐 Encodage passwords spéciaux

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
**Version** : 1.1.5  
**Date** : 25 novembre 2025

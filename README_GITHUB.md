# AY HR Management System - Système de Gestion des Ressources Humaines

[![Version](https://img.shields.io/badge/version-3.5.0-blue.svg)](https://github.com/FingaDZ/AY/releases/tag/v3.5.0)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/FingaDZ/AY)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)]()
[![License](https://img.shields.io/badge/license-Private-red.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.3-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)

> **Version actuelle** : 3.5.0 (PDF Enhancement + ANEM Integration)  
> **Dernière mise à jour** : 11 décembre 2025  
> **Statut** : ✅ Production Ready

## 🎉 Nouveautés v3.5.0
- 📄 **PDF Améliorés** : Footer automatique, marges étroites, QR codes
- 🆔 **N° ANEM** : Intégration complète dans documents RH
- 📋 **Contrats** : Numérotation unique, mentions légales, QR codes
- 🎫 **Congés** : Ligne jours de congé dans bulletins de paie
- 📊 **Rapports** : Optimisation layout et footers en pied de page
- 🔧 **Pointages** : Congé comptabilisé comme jour travaillé (valeur = 1)

---

## 📋 Description

Système complet de gestion des ressources humaines (SIRH) développé avec **FastAPI** (backend) et **React** (frontend). Conçu pour gérer l'ensemble du cycle de vie RH : employés, pointages, paie, congés, missions et intégration avec système biométrique.

### ✨ Fonctionnalités Principales

- ✅ **Gestion des Employés** : CRUD complet, soft delete, génération documents (attestations, certificats)
- ✅ **Système de Pointage** : Grille mensuelle 31 jours, verrouillage, heures supplémentaires
- ✅ **Gestion de la Paie** : Calcul automatique, IRG progressif, primes, retenues, bulletins PDF
- ✅ **Gestion des Congés** : Calcul droits (2.5j/mois), suivi consommation, soldes
- ✅ **Missions Chauffeurs** : Ordres de mission, calcul primes selon distance
- ✅ **Avances & Crédits** : Gestion avances salariales, crédits avec prorogation
- ✅ **Intégration Biométrique** : Synchronisation avec système Attendance (v1.3.0+)
- ✅ **Logs Incomplets** : Estimation intelligente + validation RH (v1.7.0)
- ✅ **Audit & Traçabilité** : Logging complet des actions, historique JSON
- ✅ **Multi-utilisateurs** : Authentification JWT, rôles (Admin, Manager, User)

---

## 🛠️ Stack Technique

### Backend
- **Framework** : FastAPI 0.104.1
- **Base de données** : MariaDB 10.5+ / MySQL 8.0+
- **ORM** : SQLAlchemy 2.0.23
- **Validation** : Pydantic 2.5.0
- **Authentification** : JWT (python-jose)
- **Rapports** : ReportLab (PDF), XlsxWriter (Excel)

### Frontend
- **Framework** : React 18.3.1
- **Build Tool** : Vite 5.3.1
- **UI Library** : Ant Design 6.0.0
- **Styling** : Tailwind CSS 3.4.18
- **Routing** : React Router 6.23.1
- **HTTP Client** : Axios 1.7.2

### Infrastructure
- **Serveur** : Uvicorn (ASGI)
- **OS** : Ubuntu 22.04 / Windows 10+
- **Déploiement** : Systemd services (Linux)

---

## 🚀 Démarrage Rapide

### Installation Serveur (Production Linux)

```bash
# 1. Cloner le repository
git clone https://github.com/FingaDZ/AY.git /opt/ay-hr
cd /opt/ay-hr

# 2. Installation automatique
chmod +x install.sh
sudo ./install.sh
```

Le script `install.sh` configure automatiquement :
- Python 3.9+ avec environnement virtuel
- Node.js 18+ et dépendances npm
- MariaDB avec base de données
- Services systemd (backend + frontend)
- Permissions et configuration

### Mise à Jour Automatique

```bash
cd /opt/ay-hr
sudo ./update.sh
```

Le script `update.sh` v2.0 effectue :
- ✅ Sauvegarde DB et configuration
- ✅ Git pull depuis GitHub
- ✅ Mise à jour dépendances (pip, npm)
- ✅ Build frontend production
- ✅ Redémarrage services avec vérification

📖 **Guide complet** : [UPDATE_GUIDE.md](UPDATE_GUIDE.md)

### Installation Locale (Développement)

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env avec vos paramètres DB

# Démarrer
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Accès

- **Frontend** : http://localhost:3000 (dev) ou http://localhost:8000 (prod)
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs (Swagger UI)
- **Credentials par défaut** : `admin` / `admin123`

---

## 📁 Structure du Projet

```
AY HR/
├── backend/                    # API FastAPI
│   ├── models/                 # 16 modèles SQLAlchemy
│   ├── routers/                # 17 endpoints API
│   ├── services/               # 8 services métier
│   ├── schemas/                # Validation Pydantic
│   ├── middleware/             # Middleware custom
│   ├── main.py                 # Point d'entrée
│   └── requirements.txt        # Dépendances Python
├── frontend/                   # Application React
│   ├── src/
│   │   ├── components/         # Composants réutilisables
│   │   ├── pages/              # 16 modules fonctionnels
│   │   ├── services/           # Services API
│   │   └── contexts/           # Contextes React
│   ├── package.json
│   └── vite.config.js
├── database/                   # Scripts SQL
│   └── create_database.sql    # Initialisation DB
├── install.sh                  # Installation automatique
├── update.sh                   # Mise à jour automatique (v2.0)
├── CHANGELOG.md                # Historique des versions
├── UPDATE_GUIDE.md             # Guide de mise à jour
└── README.md                   # Ce fichier
```

---

## 📊 Modules Fonctionnels

| Module | Description | Statut |
|--------|-------------|--------|
| **Dashboard** | Statistiques, KPIs, actions rapides | ✅ Stable |
| **Employés** | CRUD, documents, export Excel | ✅ Stable |
| **Postes** | Gestion dynamique postes de travail | ✅ Stable |
| **Pointages** | Grille 31j, verrouillage, heures sup | ✅ Stable |
| **Congés** | Droits, consommation, soldes | ✅ Stable |
| **Missions** | Ordres de mission chauffeurs | ✅ Stable |
| **Avances** | Avances salariales | ✅ Stable |
| **Crédits** | Crédits avec prorogation | ✅ Stable |
| **Salaires** | Calcul auto, IRG, bulletins PDF | ✅ Stable |
| **Clients** | Gestion clients et tarifs | ✅ Stable |
| **Logs** | Audit trail, historique actions | ✅ Stable |
| **Logs Incomplets** | Validation estimations (v1.7.0) | ✅ Stable |
| **Paramètres** | Configuration entreprise | ✅ Stable |
| **Utilisateurs** | Gestion comptes, rôles | ✅ Stable |
| **Base de données** | Configuration connexion DB | ✅ Stable |
| **Intégration Attendance** | Sync biométrique (v1.3.0+) | ✅ Stable |

---

## 🔗 Intégration Attendance (v1.3.0+)

### Fonctionnalités

- ✅ **Sync Employés** : HR → Attendance (nom, poste, PIN)
- ✅ **Import Pointages** : Attendance → HR (conversion minutes → jours)
- ✅ **Heures Supplémentaires** : Calcul automatique (>8h/jour)
- ✅ **Gestion Conflits** : Détection et résolution manuelle
- ✅ **Logs Incomplets** : Estimation intelligente + validation RH (v1.7.0)

### Architecture

```
Système Biométrique (Attendance)
         ↓
   API REST (192.168.20.56:8000)
         ↓
AttendanceService (Python)
         ↓
Tables HR (pointages, mapping, sync_log, incomplete_logs)
```

### Documentation

- [ATTENDANCE_INTEGRATION.md](ATTENDANCE_INTEGRATION.md) - Stratégie d'intégration
- [ATTENDANCE_FRONTEND_GUIDE.md](ATTENDANCE_FRONTEND_GUIDE.md) - Guide UI
- [DEPLOYMENT_V1.3.0-BETA.md](DEPLOYMENT_V1.3.0-BETA.md) - Déploiement

---

## 🔒 Sécurité

- ✅ **Authentification JWT** avec expiration (30 min)
- ✅ **Hachage bcrypt** pour mots de passe
- ✅ **Soft delete** (protection données liées)
- ✅ **Validation stricte** (Pydantic + contraintes DB)
- ✅ **CORS configuré** (déploiement LAN/WAN)
- ✅ **Logging complet** (audit trail avec JSON)
- ✅ **Middleware authentification** (require_admin, require_auth)

---

## 📝 Changelog

### v2.3.0 - 29 novembre 2025 ✨ ACTUELLE

**Gestion Hybride des Logs Incomplets**
- 🛡️ Calcul intelligent des heures (ENTRY seul → sortie 17h, EXIT seul → entrée 8h)
- 📊 Dashboard de validation RH pour corriger estimations
- 🚀 Import robuste sans perte de données
- 📱 Notifications et badges pour actions requises

### v1.3.0 - 25 novembre 2025

**Intégration Attendance**
- 🔗 Backend complet (sync employés, import logs, gestion conflits)
- 🗄️ 3 nouvelles tables + colonne heures_supplementaires
- 📚 Documentation complète (guides, API)

### v1.2.4 - 25 novembre 2025

- ✨ Module utilisateurs restauré
- 🔧 Scripts automatisation (install.sh, update.sh)

### v1.1.3 - 13 novembre 2025

- ✨ Module postes dynamique
- 🔧 Durée contrat automatique
- 🐛 Corrections authentification

### v1.1.0 - 12 novembre 2025

- ✨ Système logging complet
- 🎨 Branding entreprise (logo, footer)

### v1.0.0 - 11 novembre 2025

- 🎉 Première version stable
- ✅ Tous modules opérationnels

[Voir le changelog complet](CHANGELOG.md)

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Ce fichier |
| [CHANGELOG.md](CHANGELOG.md) | Historique complet des versions |
| [UPDATE_GUIDE.md](UPDATE_GUIDE.md) | Guide de mise à jour (v2.0) |
| [DEPLOYMENT_LINUX.md](DEPLOYMENT_LINUX.md) | Déploiement Linux complet |
| [INSTALL_UBUNTU_22.04.md](INSTALL_UBUNTU_22.04.md) | Installation Ubuntu 22.04 |
| [DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md) | Déploiement Windows |
| [ATTENDANCE_INTEGRATION.md](ATTENDANCE_INTEGRATION.md) | Intégration biométrique |
| [DEPLOYMENT_V1.7.0.md](DEPLOYMENT_V1.7.0.md) | Déploiement v1.7.0 |

---

## 🔧 Configuration

### Variables d'Environnement (.env)

```env
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost/ay_hr

# Security
SECRET_KEY=your-secret-key-here
DEBUG=False

# CORS
CORS_ORIGINS=*

# Attendance Integration (v1.3.0+)
ATTENDANCE_API_URL=http://192.168.20.56:8000/api
ATTENDANCE_API_TIMEOUT=30
```

### Base de Données

**Tables** : 17 tables principales
- `users`, `employes`, `postes_travail`, `pointages`, `conges`
- `clients`, `missions`, `avances`, `credits`, `retenues_credit`, `prorogations_credit`
- `parametres`, `database_config`, `logging`
- `attendance_employee_mapping`, `attendance_sync_log`, `attendance_import_conflicts`
- `incomplete_attendance_logs` (v1.7.0)

**Encodage** : UTF8MB4 (support Unicode complet)  
**Moteur** : InnoDB (transactions ACID)

---

## 🤝 Contribution

Ce projet est à usage interne. Pour toute suggestion ou bug :

1. Créer une issue sur GitHub
2. Décrire le problème ou la fonctionnalité
3. Joindre logs et captures d'écran si applicable

---

## 📞 Support

**Documentation** :
- API Swagger : http://192.168.20.53:8000/docs
- Guides : Voir section [Documentation](#documentation)

**Logs** :
```bash
# Backend
sudo journalctl -u ayhr-backend -f

# Frontend
sudo journalctl -u ayhr-frontend -f
```

**Backup & Restauration** :
- Backups automatiques : `/opt/ay-hr/backups/`
- Rétention : 30 jours
- Voir [UPDATE_GUIDE.md](UPDATE_GUIDE.md) pour restauration

---

## 📜 Licence

Usage interne - Tous droits réservés

---

## 👥 Crédits

**Développé par** : AIRBAND  
**Repository** : https://github.com/FingaDZ/AY  
**Version** : 1.7.0  
**Date** : 28 novembre 2025

---

## 🎯 Roadmap

### v1.8.0 (Prévu Q1 2026)
- [ ] Tests automatisés (pytest, Jest)
- [ ] Backup automatique DB (cron)
- [ ] Monitoring (Sentry, Prometheus)
- [ ] Cache Redis

### v2.0.0 (Prévu Q2 2026)
- [ ] Application mobile (React Native)
- [ ] Internationalisation (FR, AR, EN)
- [ ] Rapports avancés (graphiques, filtres)
- [ ] Notifications email

### v3.0.0 (Vision)
- [ ] Version cloud multi-tenant
- [ ] IA prédictive (turnover, absences)
- [ ] Intégrations ERP/Comptabilité
- [ ] API publique avec webhooks

---

<div align="center">

**⭐ Si ce projet vous est utile, n'hésitez pas à le star sur GitHub ! ⭐**

Made with ❤️ by AIRBAND

</div>

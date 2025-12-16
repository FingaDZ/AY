# 🎉 Release Notes - AY HR System v3.6.0

**Date de Release** : 16 décembre 2025  
**Version** : 3.6.0  
**Status** : ✅ Production Ready

---

## 📊 Vue d'Ensemble

Cette release majeure apporte **5 nouvelles fonctionnalités** critiques pour améliorer la gestion des missions, des véhicules, et des accès utilisateurs. Elle inclut également une **refonte complète de la documentation et des outils d'installation** pour faciliter le déploiement sur Ubuntu, Windows, et Docker.

### 🎯 Objectifs Atteints
- ✅ Gestion complète du parc automobile
- ✅ Calcul kilométrique intelligent multi-clients
- ✅ Système de permissions à 3 niveaux
- ✅ Audit complet des connexions
- ✅ Amélioration UX paramètres salaires
- ✅ Déploiement simplifié (Ubuntu/Windows/Docker)

---

## ✨ Nouvelles Fonctionnalités

### 🚗 1. Module Gestion Camions
**Besoin métier** : Traçabilité du parc automobile pour les missions

**Fonctionnalités** :
- CRUD complet des véhicules (Marque, Modèle, Immatriculation)
- Association camion ↔ mission
- Affichage automatique dans PDF ordre de mission
- Validation unicité immatriculation

**Impact** :
- Meilleure gestion logistique
- Traçabilité complète véhicule/mission
- Conformité administrative

**Fichiers modifiés** :
- `backend/models/camion.py` (nouveau)
- `backend/routers/camions.py` (nouveau)
- `backend/schemas/mission.py` (camion_id)
- `backend/services/mission_service.py` (PDF intégration)
- `frontend/src/pages/Camions/` (nouveau module UI)

---

### 📊 2. Calcul Kilométrique Multi-Clients
**Besoin métier** : Rémunération juste pour missions à plusieurs clients

**Formule** :
```
km_total = km_max + (nombre_clients - 1) × km_supplementaire_par_client
```

**Paramètre** : `km_supplementaire_par_client` (défaut: 10 km)

**Exemple** :
- 1 client : 50 km → 50 km
- 3 clients : 50 km → 50 + (3-1)×10 = 70 km

**Impact** :
- Calcul automatique équitable
- Gain de temps pour les gestionnaires
- PDF multi-pages pour clarté

**Fichiers modifiés** :
- `backend/schemas/parametres_salaire.py` (km_supplementaire_par_client)
- `backend/services/mission_service.py` (algorithme)
- `frontend/src/pages/Parametres/MissionsParametres.jsx`

---

### 👥 3. Rôle Gestionnaire (3-Tier Permissions)
**Besoin métier** : Déléguer la gestion opérationnelle sans accès admin

**Niveaux** :
1. **Admin** : Accès total (utilisateurs, paramètres, salaires)
2. **Gestionnaire** : Missions, Clients, Camions, Avances, Crédits
3. **Utilisateur** : Lecture seule

**Fonctionnalités** :
- Sidebar dynamique selon le rôle
- Tags colorés : 🔴 Admin, 🟠 Gestionnaire, 🔵 Utilisateur
- Validation backend des permissions
- Interface utilisateurs avec CRUD rôles

**Impact** :
- Séparation des responsabilités
- Sécurité renforcée
- Facilite la délégation

**Fichiers modifiés** :
- `backend/models/user.py` (ENUM Gestionnaire)
- `backend/routers/utilisateurs.py` (validation)
- `frontend/src/components/Sidebar.jsx` (menu dynamique)
- `frontend/src/pages/Admin/UsersPage.jsx` (UI gestion)
- `database/migrate_gestionnaire_role.sql` (migration MySQL)

---

### 📝 4. Logs Connexions avec IP
**Besoin métier** : Audit de sécurité et traçabilité des accès

**Fonctionnalités** :
- Nouveau type d'action `LOGIN`
- Capture IP utilisateur
- Capture User-Agent (navigateur/OS)
- Icône 🔐 dans la page logs
- Filtre par type d'action

**Impact** :
- Conformité RGPD/audit
- Détection activités suspectes
- Traçabilité complète

**Fichiers modifiés** :
- `backend/routers/auth.py` (log LOGIN)
- `backend/models/log.py` (ActionType.LOGIN)
- `frontend/src/pages/Logs/LogsPage.jsx` (icône + filtre)

---

### 🔢 5. Congés Décimaux + UI Paramètres
**Besoin métier** : Précision des calculs de congés

**Changements** :
- API retourne `float` au lieu de `int`
- Affichage `.toFixed(2)` (ex: 2.50 jours)
- Réorganisation UI Paramètres Salaires en sections :
  - 📊 INDEMNITÉS (IN, IFSP, IEP)
  - 💰 PRIMES (Encouragement, Chauffeur, Nuit)
  - 💳 RETENUES (Sécurité Sociale)
  - 🚗 MISSIONS (Km supplémentaire)
  - ⚙️ PARAMÈTRES CALCUL (Congés, Options)

**Impact** :
- Calculs plus précis
- UI plus claire et organisée
- Meilleure UX configuration

**Fichiers modifiés** :
- `backend/services/conge_service.py` (float au lieu int)
- `frontend/src/pages/Conges/CongesPage.jsx` (.toFixed(2))
- `frontend/src/pages/Parametres/ParametresPage.jsx` (sections)

---

## 🚀 Outils d'Installation

### 🐧 Ubuntu/Debian - Installation Automatique
**Fichier** : [install-ubuntu.sh](install-ubuntu.sh)

**Fonctionnalités** :
- ✅ Installation complète en 10 minutes
- ✅ Configuration interactive (DB, ports, admin)
- ✅ Python 3.11 + Node.js 20 + MySQL 8.0
- ✅ Services systemd (ayhr-backend, ayhr-frontend)
- ✅ Nginx reverse proxy optionnel
- ✅ Génération SECRET_KEY automatique
- ✅ Import schema.sql + création admin
- ✅ Build frontend optimisé

**Usage** :
```bash
sudo bash install-ubuntu.sh
```

**Guide complet** : [DEPLOYMENT_LINUX.md](DEPLOYMENT_LINUX.md)

---

### 🪟 Windows - Guide Pas-à-Pas
**Fichier** : [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)

**Contenu** :
- ✅ Prérequis (Python 3.11+, Node.js 20, MySQL 8.0)
- ✅ 7 étapes d'installation manuelle
- ✅ Configuration .env complète
- ✅ Service Windows avec NSSM (recommandé)
- ✅ Alternative Task Scheduler
- ✅ Nginx pour Windows
- ✅ Section Troubleshooting (ports, MySQL, modules)
- ✅ Commandes utiles + sécurité

**Guide complet** : [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)

---

### 🐳 Docker - Multi-Plateforme
**Fichiers** :
- [docker-compose.yml](docker-compose.yml)
- [backend/Dockerfile](backend/Dockerfile)
- [frontend/Dockerfile](frontend/Dockerfile)
- [docker-start.sh](docker-start.sh) (Linux/Mac)
- [docker-start.ps1](docker-start.ps1) (Windows)

**Fonctionnalités** :
- ✅ 3 services (MySQL, Backend, Frontend)
- ✅ Healthchecks intégrés
- ✅ Volumes persistants
- ✅ Build multi-stage optimisé
- ✅ Nginx Alpine pour frontend
- ✅ Quick start en 5 minutes

**Usage** :
```bash
# Linux/Mac
bash docker-start.sh

# Windows
.\docker-start.ps1
```

**Guide complet** : [INSTALL_DOCKER.md](INSTALL_DOCKER.md)

---

## 🧹 Nettoyage Projet

### Fichiers Supprimés (60+)
- ✅ Scripts de test obsolètes (analyze_excel.py, debug_*.sh, test_*.py)
- ✅ Documentation v3.5.x (DEPLOIEMENT_V3.5.2.md, RAPPORT_V3.5.3.md, etc.)
- ✅ Fichiers temporaires (attendance_report.xlsx, test.db, temp_attendance/)
- ✅ Scripts de migration serveur (migrate_server_v3.5.0.sh, deploy_v3_server.sh)

### Fichiers Conservés
- ✅ README.md (mis à jour v3.6.0)
- ✅ CHANGELOG.md (historique complet)
- ✅ INDEX_DOCUMENTATION.md (réorganisé)
- ✅ PLAN_V3.6.0.md (roadmap)
- ✅ Guides d'installation (nouveaux)

**Script de nettoyage** : [cleanup.sh](cleanup.sh)

---

## 📚 Documentation

### Structure Complète
```
Documentation v3.6.0/
│
├── 📄 README.md                           ← Vue d'ensemble
├── 📄 CHANGELOG.md                        ← Historique versions
├── 📄 PLAN_V3.6.0.md                      ← Roadmap
├── 📄 INDEX_DOCUMENTATION.md              ← Index principal
├── 📄 RELEASE_V3.6.0.md                   ← Ce fichier
│
├── 🚀 INSTALLATION/
│   ├── install-ubuntu.sh                  ← Script auto Ubuntu
│   ├── INSTALL_WINDOWS.md                 ← Guide Windows
│   ├── INSTALL_DOCKER.md                  ← Guide Docker
│   ├── docker-start.sh                    ← Quick start Linux/Mac
│   ├── docker-start.ps1                   ← Quick start Windows
│   ├── DEPLOYMENT_LINUX.md                ← Détails Linux
│   └── DEPLOYMENT_WINDOWS.md              ← Détails Windows
│
└── 🛠️ CONFIGURATION/
    ├── docker-compose.yml                 ← Orchestration Docker
    ├── .env.docker                        ← Template config
    ├── cleanup.sh                         ← Script nettoyage
    └── ecosystem.config.js                ← PM2 config
```

---

## 🔧 Changements Techniques

### Backend (Python/FastAPI)
```python
# Nouveaux modèles
- models/camion.py

# Nouveaux routers
- routers/camions.py

# Modifications
- schemas/mission.py (camion_id)
- schemas/parametres_salaire.py (km_supplementaire_par_client)
- services/mission_service.py (calcul km, PDF)
- services/conge_service.py (float au lieu int)
- routers/auth.py (log LOGIN)
- routers/utilisateurs.py (validation Gestionnaire)
```

### Frontend (React/Ant Design)
```javascript
// Nouvelles pages
- src/pages/Camions/CamionsPage.jsx
- src/pages/Parametres/MissionsParametres.jsx

// Modifications
- src/components/Sidebar.jsx (menu dynamique)
- src/pages/Admin/UsersPage.jsx (gestion rôles)
- src/pages/Logs/LogsPage.jsx (filtre LOGIN)
- src/pages/Conges/CongesPage.jsx (.toFixed(2))
- src/pages/Parametres/ParametresPage.jsx (sections)
```

### Base de Données (MySQL)
```sql
-- Nouvelle table
CREATE TABLE camions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    marque VARCHAR(100) NOT NULL,
    modele VARCHAR(100) NOT NULL,
    immatriculation VARCHAR(50) UNIQUE NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Migration rôles
ALTER TABLE users 
MODIFY COLUMN role ENUM('Admin', 'Gestionnaire', 'Utilisateur') 
NOT NULL DEFAULT 'Utilisateur';

-- Nouveau paramètre
ALTER TABLE parametres_salaire 
ADD COLUMN km_supplementaire_par_client INT DEFAULT 10;
```

---

## 🧪 Tests et Validation

### Tests Backend
```bash
# Sanity checks
curl http://localhost:8000/
curl http://localhost:8000/api/camions

# Test authentification
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ay-hr.com","password":"Admin@2024!"}'

# Test permissions Gestionnaire
# (authentifié en tant que Gestionnaire)
curl http://localhost:8000/api/missions  # ✅ OK
curl http://localhost:8000/api/parametres  # ❌ 403 Forbidden
```

### Tests Frontend
- ✅ Connexion Admin → Voir tous les menus
- ✅ Connexion Gestionnaire → Menus limités
- ✅ Page Camions : CRUD complet
- ✅ Page Missions : Select camion + affichage dans PDF
- ✅ Page Paramètres : Km supplémentaire modifiable
- ✅ Page Congés : Affichage décimal (2.50)
- ✅ Page Logs : Filtre Connexion + icône 🔐

### Tests Docker
```bash
# Build et démarrage
docker-compose up -d --build

# Healthchecks
docker ps  # Tous healthy
curl http://localhost  # Frontend OK
curl http://localhost:8000  # Backend OK

# Logs
docker-compose logs -f backend
```

---

## 📈 Statistiques

### Code
- **Commits** : 25+ commits pour v3.6.0
- **Fichiers modifiés** : 40+
- **Fichiers supprimés** : 60+
- **Lignes ajoutées** : 3000+
- **Lignes supprimées** : 5000+

### Documentation
- **Guides créés** : 3 (Ubuntu, Windows, Docker)
- **Scripts créés** : 5 (install-ubuntu.sh, cleanup.sh, docker-start.sh/ps1)
- **Pages documentation** : 8+
- **Lignes documentation** : 2000+

### Fonctionnalités
- **Nouveaux modules** : 2 (Camions, Logs connexions)
- **Nouvelles tables DB** : 1 (camions)
- **Nouveaux paramètres** : 1 (km_supplementaire_par_client)
- **Nouveaux rôles** : 1 (Gestionnaire)

---

## 🔒 Sécurité

### Améliorations
- ✅ Validation rôles backend (Admin/Gestionnaire/Utilisateur)
- ✅ Permissions granulaires par endpoint
- ✅ Logs connexions avec IP (audit)
- ✅ Healthchecks Docker (disponibilité)
- ✅ Secrets Docker pour production
- ✅ SSL/TLS avec Let's Encrypt (guide)

### Recommandations
- 🔐 Changer les mots de passe par défaut
- 🔐 Utiliser des clés SSH pour déploiement
- 🔐 Activer SSL/TLS en production
- 🔐 Configurer firewall (ufw/Windows Firewall)
- 🔐 Backups réguliers MySQL

---

## 🚀 Déploiement Production

### Checklist Pré-Déploiement
- [ ] Backup base de données
- [ ] Vérifier requirements.txt à jour
- [ ] Tester installation sur VM propre
- [ ] Valider tous les tests fonctionnels
- [ ] Préparer procédure rollback
- [ ] Informer les utilisateurs

### Déploiement Serveur 192.168.20.55
```bash
# SSH vers le serveur
ssh root@192.168.20.55

# Pull dernière version
cd /opt/ay-hr
git pull origin main

# Restart services
systemctl restart ayhr-backend
systemctl restart ayhr-frontend  # ou nginx

# Vérifier logs
journalctl -u ayhr-backend -f
```

### Post-Déploiement
- [ ] Vérifier santé backend: http://192.168.20.55:8000/
- [ ] Vérifier frontend: http://192.168.20.55
- [ ] Tester login Admin
- [ ] Tester login Gestionnaire
- [ ] Vérifier création camion
- [ ] Vérifier logs connexions
- [ ] Monitorer erreurs 24h

---

## 🐛 Bugs Connus

Aucun bug critique connu à ce jour.

### Limitations
- Logs connexions : Pas de géolocalisation IP (seulement IP brute)
- PDF multi-pages : Peut être lent avec 10+ clients (optimisation future)
- Docker : Pas de hot-reload frontend (rebuild nécessaire)

---

## 📅 Roadmap v3.7.0 (Q1 2026)

### Fonctionnalités Prévues
- 📊 **Dashboard KPI** : Statistiques missions/salaires
- 📧 **Notifications Email** : Alertes automatiques
- 📱 **API Mobile** : Endpoints pour app mobile
- 🔍 **Recherche Globale** : Elasticsearch intégration
- 📈 **Exports Excel** : Rapports personnalisables
- 🌐 **Multi-langue** : FR/AR/EN

---

## 🆘 Support

### Ressources
- **Documentation** : [INDEX_DOCUMENTATION.md](INDEX_DOCUMENTATION.md)
- **Installation Ubuntu** : [install-ubuntu.sh](install-ubuntu.sh)
- **Installation Windows** : [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)
- **Installation Docker** : [INSTALL_DOCKER.md](INSTALL_DOCKER.md)
- **Changelog complet** : [CHANGELOG.md](CHANGELOG.md)

### Contact
- **Email** : admin@ay-hr.com
- **GitHub** : [FingaDZ/AY](https://github.com/FingaDZ/AY)
- **Version** : 3.6.0

---

## 🙏 Remerciements

Merci à toute l'équipe pour cette release majeure :
- Développement complet v3.6.0
- Documentation exhaustive
- Outils d'installation multi-plateformes
- Nettoyage projet production-ready

**Status** : ✅ **PRODUCTION READY - Décembre 2025**

---

*AY HR System v3.6.0 - Gestion des Ressources Humaines*

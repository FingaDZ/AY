# 📁 Organisation de la Documentation

## 📚 Structure du Projet

```
AY HR/
├── README.md                          # Vue d'ensemble du projet
├── CHANGELOG.md                       # Historique des versions
├── LISEZMOI_DEPLOIEMENT.md           # Guide rapide de déploiement
├── INSTALLATION_GUIDE.md             # Guide d'installation complet
├── INSTALL_UBUNTU_22.04.md           # Guide spécifique Ubuntu 22.04
├── ADMIN_GUIDE.md                    # Guide administrateur avancé
│
├── backend/                           # Code serveur FastAPI
├── frontend/                          # Interface React
├── database/                          # Scripts SQL
│
├── docs/                              # Documentation
│   ├── DEPLOYMENT_SUMMARY.md         # Récapitulatif du déploiement
│   ├── PACKAGE_README.md             # Documentation des packages
│   ├── INSTALLATION.md               # Guide d'installation alternatif
│   ├── ORDRE_MISSION_V2.1.md         # Spécifications ordres de mission
│   │
│   ├── guides/                        # Guides utilisateurs
│   │   ├── GUIDE_DEMARRAGE.md        # Démarrage rapide
│   │   ├── GUIDE_MISSIONS.md         # Guide missions chauffeurs
│   │   ├── GUIDE_UTILISATEUR.md      # Manuel utilisateur complet
│   │   ├── GUIDE_RELEASES_GITHUB.md  # Publication sur GitHub
│   │   └── TROUBLESHOOTING.md        # Dépannage
│   │
│   └── archives/                      # Documents historiques
│       ├── AMELIORATIONS_*.md        # Historique améliorations
│       ├── CORRECTIONS_*.md          # Historique corrections
│       ├── SESSION_*.md              # Notes de sessions
│       └── (autres documents d'archive)
│
└── scripts/                           # Scripts d'installation et déploiement
    ├── install-windows.ps1
    ├── install-linux.sh
    ├── install-service-windows.ps1
    ├── install-service-linux.sh
    ├── start-windows.ps1
    ├── start-linux.sh
    ├── stop-windows.ps1
    ├── stop-linux.sh
    ├── create-package-windows.ps1
    └── create-package-linux.sh
```

---

## 📖 Documentation par Cas d'Usage

### 🚀 Je veux installer l'application

#### Sur Windows
1. **Guide rapide** : [LISEZMOI_DEPLOIEMENT.md](../LISEZMOI_DEPLOIEMENT.md)
2. **Guide complet** : [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md)

#### Sur Ubuntu 22.04
1. **Guide spécifique** : [INSTALL_UBUNTU_22.04.md](../INSTALL_UBUNTU_22.04.md) ⭐ **RECOMMANDÉ**
2. **Guide générique Linux** : [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md)

### 👨‍💼 Je suis administrateur système

1. **Guide principal** : [ADMIN_GUIDE.md](../ADMIN_GUIDE.md)
   - Gestion des services
   - Surveillance et logs
   - Sauvegardes automatiques
   - Optimisations performance
   - Configuration sécurité

### 👤 Je suis utilisateur

1. **Démarrage rapide** : [docs/guides/GUIDE_DEMARRAGE.md](guides/GUIDE_DEMARRAGE.md)
2. **Manuel complet** : [docs/guides/GUIDE_UTILISATEUR.md](guides/GUIDE_UTILISATEUR.md)
3. **Missions chauffeurs** : [docs/guides/GUIDE_MISSIONS.md](guides/GUIDE_MISSIONS.md)

### 🔧 J'ai un problème

1. **Dépannage** : [docs/guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md)
2. **Logs** : Consulter `logs/backend.log` et `logs/frontend.log`

### 📦 Je veux créer un package de distribution

1. **Récapitulatif** : [docs/DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)
2. **Scripts** :
   - Windows : `create-package-windows.ps1`
   - Linux : `create-package-linux.sh`

### 📝 Je cherche l'historique du projet

1. **Changelog** : [CHANGELOG.md](../CHANGELOG.md)
2. **Archives** : [docs/archives/](archives/)

---

## 🎯 Documents Essentiels (Racine du Projet)

| Fichier | Description | Audience |
|---------|-------------|----------|
| **README.md** | Vue d'ensemble du projet | Tous |
| **CHANGELOG.md** | Historique des versions | Développeurs |
| **LISEZMOI_DEPLOIEMENT.md** | Installation rapide | Débutants |
| **INSTALLATION_GUIDE.md** | Installation complète | Admins |
| **INSTALL_UBUNTU_22.04.md** | Installation Ubuntu | Admins Linux |
| **ADMIN_GUIDE.md** | Gestion avancée | Admins système |

---

## 📂 Documents Secondaires (docs/)

### Déploiement
- **DEPLOYMENT_SUMMARY.md** : Vue d'ensemble du déploiement
- **PACKAGE_README.md** : Documentation des packages
- **INSTALLATION.md** : Installation alternative

### Spécifications
- **ORDRE_MISSION_V2.1.md** : Format des ordres de mission

---

## 📚 Guides Utilisateurs (docs/guides/)

| Guide | Contenu |
|-------|---------|
| **GUIDE_DEMARRAGE.md** | Premiers pas avec l'application |
| **GUIDE_UTILISATEUR.md** | Manuel utilisateur complet |
| **GUIDE_MISSIONS.md** | Gestion des missions chauffeurs |
| **GUIDE_RELEASES_GITHUB.md** | Publier sur GitHub |
| **TROUBLESHOOTING.md** | Résolution de problèmes |

---

## 🗄️ Archives (docs/archives/)

Documents historiques conservés pour référence :

### Améliorations
- `AMELIORATIONS_V1.1.md`
- `AMELIORATIONS_NOVEMBRE_2025.md`
- `AMELIORATIONS_EMPLOYES_AVANCES.md`

### Corrections
- `CORRECTIONS_V1.1.1.md`
- `CORRECTIONS_V1.1.2.md`

### Sessions de Développement
- `SESSION_CORRECTIONS_V1.1.3.md`

### Notes Techniques
- `STATUS.md` - État du système
- `RESUME_PROJET.md` - Résumé technique
- `RELEASE_NOTES_V1.1.3.md` - Notes de version

### Modules Spécifiques
- Missions : `MISSIONS_*.md`, `ORDRE_MISSION_*.md`, `RAPPORT_MISSIONS_*.md`
- Avances/Crédits : `AVANCES_*.md`, `CREDITS_*.md`, `FIX_AVANCES_*.md`
- Système : `DATABASE_CONFIG_*.md`, `MIGRATION_*.md`, `LOGGING_*.md`

---

## 🔍 Recherche Rapide

### Par Fonctionnalité

| Je cherche... | Consulter |
|---------------|-----------|
| Comment installer | [INSTALLATION_GUIDE.md](../INSTALLATION_GUIDE.md) |
| Installation Ubuntu | [INSTALL_UBUNTU_22.04.md](../INSTALL_UBUNTU_22.04.md) |
| Gérer les services | [ADMIN_GUIDE.md](../ADMIN_GUIDE.md) |
| Utiliser l'app | [docs/guides/GUIDE_UTILISATEUR.md](guides/GUIDE_UTILISATEUR.md) |
| Résoudre un problème | [docs/guides/TROUBLESHOOTING.md](guides/TROUBLESHOOTING.md) |
| Missions chauffeurs | [docs/guides/GUIDE_MISSIONS.md](guides/GUIDE_MISSIONS.md) |
| Historique versions | [CHANGELOG.md](../CHANGELOG.md) |
| Créer un package | [docs/DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) |

### Par Rôle

| Je suis... | Documents clés |
|------------|----------------|
| **Nouvel utilisateur** | README → LISEZMOI_DEPLOIEMENT → GUIDE_DEMARRAGE |
| **Administrateur système** | ADMIN_GUIDE → INSTALLATION_GUIDE → TROUBLESHOOTING |
| **Développeur** | README → CHANGELOG → docs/archives/ |
| **Utilisateur quotidien** | GUIDE_UTILISATEUR → GUIDE_MISSIONS |

---

## 📌 Notes

- ✅ **Documents à jour** : v1.1.4 (15 novembre 2025)
- 📁 **Organisation** : Nettoyage effectué le 15/11/2025
- 🗑️ **Fichiers supprimés** : Tests et scripts redondants déplacés ou supprimés
- 📦 **Packages disponibles** : Windows et Linux (voir releases GitHub)

---

## 🔄 Maintenance de la Documentation

### Règles d'Organisation

1. **Racine** : Uniquement documents essentiels et couramment utilisés
2. **docs/** : Documentation secondaire et spécialisée
3. **docs/guides/** : Guides utilisateurs par thème
4. **docs/archives/** : Historique et documents obsolètes (à conserver)

### Ajout de Nouveaux Documents

- **Guide utilisateur** → `docs/guides/`
- **Spécification technique** → `docs/`
- **Note de version** → `docs/archives/`
- **Document essentiel** → Racine (avec justification)

---

**Dernière mise à jour** : 15 novembre 2025  
**Version** : 1.1.4

# 📚 INDEX DOCUMENTATION v3.6.0

**Version AY HR** : 3.6.0  
**Date de release** : 16 décembre 2025  
**Status** : ✅ Production Ready

---

## 🎯 Documents par Besoin

### 🚀 **Je veux déployer l'application**

#### **Sur Ubuntu/Debian (Recommandé)**
→ **[install-ubuntu.sh](install-ubuntu.sh)** + **[DEPLOYMENT_LINUX.md](DEPLOYMENT_LINUX.md)**
- ⏱️ Installation automatique en 10 minutes
- 🐧 Ubuntu 22.04/24.04 LTS
- 🔧 Configuration interactive
- 📦 Python 3.11 + Node.js 20 + MySQL
- 🎯 Services systemd + Nginx

#### **Sur Windows**
→ **[INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)**
- 🪟 Windows 10/11
- 📋 Guide pas-à-pas détaillé
- 🔧 Service NSSM ou Task Scheduler
- 🌐 Nginx pour Windows
- 🐛 Troubleshooting complet

#### **Avec Docker (Multi-plateforme)**
→ **[INSTALL_DOCKER.md](INSTALL_DOCKER.md)** + Scripts: [docker-start.sh](docker-start.sh) / [docker-start.ps1](docker-start.ps1)
- 🐳 Docker Compose
- ⚡ Quick start en 5 minutes
- 🔄 MySQL + Backend + Frontend
- 📦 Volumes persistants
- 🔒 Configuration SSL/TLS

### 📖 **Je veux comprendre les fonctionnalités**
→ **[README.md](README.md)**
- 🎯 Vue d'ensemble v3.6.0
- 📊 Gestion Camions
- 🚗 Calcul Km Multi-Clients
- 👥 Rôle Gestionnaire
- 📝 Logs Connexions
- 📅 Congés Décimal
- 🛠️ Technologies utilisées

### 📅 **Je veux planifier les évolutions**
→ **[PLAN_V3.6.0.md](PLAN_V3.6.0.md)**
- 📋 Roadmap complète
- 🎯 5 phases d'implémentation
- ✅ Status de chaque phase
- 🔮 Fonctionnalités futures

### 📝 **Je veux voir l'historique des changements**
→ **[CHANGELOG.md](CHANGELOG.md)**
- 📅 Versions de 3.5.0 à 3.6.0
- 🐛 Corrections de bugs
- ✨ Nouvelles fonctionnalités
- 🔒 Améliorations sécurité

---

## 📂 Structure Documentation

```
Documentation v3.6.0/
│
├── 📄 INDEX_DOCUMENTATION.md              ← CE FICHIER
├── 📄 README.md                           ← Vue d'ensemble
├── 📄 CHANGELOG.md                        ← Historique versions
├── 📄 PLAN_V3.6.0.md                      ← Roadmap
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
    ├── .env.docker                        ← Template config Docker
    └── ecosystem.config.js                ← PM2 config
```

---

## 🎯 Guide par Rôle

### 👨‍💼 **DevOps / Administrateur Système**
1. **Installation rapide** : Utiliser [install-ubuntu.sh](install-ubuntu.sh) sur serveur Linux
2. **Installation Windows** : Suivre [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) pas-à-pas
3. **Conteneurisation** : Lancer [docker-start.sh](docker-start.sh) ou [docker-start.ps1](docker-start.ps1)
4. **Configuration** : Adapter les fichiers .env selon l'environnement
5. **Monitoring** : Consulter les logs (systemd/NSSM/Docker)

### 👨‍💻 **Développeur Backend**
1. **Vue d'ensemble** : Lire [README.md](README.md) section "Architecture Backend"
2. **Environnement local** : Suivre [INSTALL_DOCKER.md](INSTALL_DOCKER.md) pour dev
3. **Roadmap** : Consulter [PLAN_V3.6.0.md](PLAN_V3.6.0.md) pour les prochaines features
4. **Changements** : Lire [CHANGELOG.md](CHANGELOG.md) pour l'historique

### 🎨 **Développeur Frontend**
1. **Setup local** : Installation Docker recommandée
2. **Documentation** : [README.md](README.md) section "Architecture Frontend"
3. **Composants** : Voir le code dans `frontend/src/`

### � **Utilisateur Final / RH**
1. **Formation** : Consulter [README.md](README.md) pour les nouvelles fonctionnalités
2. **Support** : Contacter l'administrateur système pour assistance
3. **Accès** : Utiliser les credentials fournis par l'admin

---

## 🔑 Points Clés v3.6.0

### ✨ Nouvelles Fonctionnalités
```
✅ Gestion complète des camions
✅ Calcul kilométrique multi-clients
✅ Rôle Gestionnaire (3 tiers)
✅ Logs de connexions avec IP
✅ Congés en format décimal
✅ Interface paramètres réorganisée
```

### 🚀 Installation Simplifiée
```
✅ Script Ubuntu automatique (10 étapes)
✅ Guide Windows complet (NSSM/Task Scheduler)
✅ Docker Compose multi-plateforme
✅ Quick start en 5-15 minutes
✅ Configuration interactive
```

### 🔒 Sécurité et Performance
```
✅ Validation rôles améliorée
✅ Permissions granulaires
✅ Logs d'audit connexions
✅ Healthchecks Docker
✅ Multi-workers uvicorn
```

### RECAPITULATIF_VISUEL_V3.5.1.md
```
📊 Diagrammes flux utilisateur
🎨 ASCII art structuré
📈 Matrice de tests
🎯 Points critiques
📞 Support & contacts
```

### CONGES_NOUVELLES_REGLES_V3.5.1.md
```
📊 Règles anciennes vs nouvelles
🔧 Code implémentation
📋 Exemples calcul (4)
🗄️ Migration SQL complète
✅ Tests validation
🚀 Procédure déploiement
```

---

## 📝 Checklist Lecture Recommandée

### Avant Déploiement
- [ ] Lire DEPLOIEMENT_RAPIDE_V3.5.1.md (obligatoire)
- [ ] Lire AMELIORATIONS_V3.5.1_RESUME.md (recommandé)
- [ ] Parcourir CONGES_NOUVELLES_REGLES_V3.5.1.md (pour contexte)

### Après Déploiement
- [ ] Valider tous les tests de DEPLOIEMENT_RAPIDE_V3.5.1.md
- [ ] Vérifier points clés de RECAPITULATIF_VISUEL_V3.5.1.md
- [ ] Former utilisateurs avec exemples CONGES_NOUVELLES_REGLES_V3.5.1.md

---

## 🔍 Recherche Rapide

### Blocage Congés > Acquis
- Document : AMELIORATIONS_V3.5.1_RESUME.md § 1
- Code : backend/routers/conges.py ligne 95-113
- Test : DEPLOIEMENT_RAPIDE_V3.5.1.md § Test 1

### Notification Bulletins
- Document : AMELIORATIONS_V3.5.1_RESUME.md § 2
- Code : frontend/.../SalaireCalcul.jsx ligne 96-116
- Test : DEPLOIEMENT_RAPIDE_V3.5.1.md § Test 2

### Migration SQL
- Document : CONGES_NOUVELLES_REGLES_V3.5.1.md § Migration
- Fichier : database/migration_conges_v3.5.1.sql
- Commande : `mysql -u root -p ay_hr < database/migration_conges_v3.5.1.sql`

### Nouvelles Règles Congés
- Document : CONGES_NOUVELLES_REGLES_V3.5.1.md § Règles
- Règle 1 : 8 jours = 1 congé
- Règle 2 : Nouveaux 15 jours minimum
- Règle 3 : Plus de décimales
- Règle 4 : Exclusion congés pris

---

## 📊 Versions Documents

| Document | Version | Dernière MAJ | Taille |
|----------|---------|--------------|--------|
| DEPLOIEMENT_RAPIDE_V3.5.1.md | 1.0 | 12/12/2025 | 276 lignes |
| AMELIORATIONS_V3.5.1_RESUME.md | 1.0 | 12/12/2025 | 258 lignes |
| RECAPITULATIF_VISUEL_V3.5.1.md | 1.0 | 12/12/2025 | 301 lignes |
| CONGES_NOUVELLES_REGLES_V3.5.1.md | 1.0 | 12/12/2025 | 500+ lignes |
| INDEX_DOCUMENTATION.md | 1.0 | 12/12/2025 | Ce fichier |

---

## 🔗 Liens Utiles

### Code Source
- GitHub : https://github.com/FingaDZ/AY
- Branches : main (production)
- Derniers commits : 6b2612b → f5c3e73

### Documentation Générale
- README.md : Vue d'ensemble système
- CHANGELOG.md : Historique complet
- GITHUB_UPDATE_SUMMARY.md : Résumés releases

### Support
- Issues GitHub : https://github.com/FingaDZ/AY/issues
- Logs backend : `sudo journalctl -u ayhr-backend`
- Logs frontend : `sudo journalctl -u ayhr-frontend`

---

## 💡 FAQ Rapide

**Q: Quelle doc lire en premier ?**  
R: [AMELIORATIONS_V3.5.1_RESUME.md](AMELIORATIONS_V3.5.1_RESUME.md) pour vue d'ensemble

**Q: Comment déployer rapidement ?**  
R: [DEPLOIEMENT_RAPIDE_V3.5.1.md](DEPLOIEMENT_RAPIDE_V3.5.1.md) avec copier-coller

**Q: Où voir les diagrammes ?**  
R: [RECAPITULATIF_VISUEL_V3.5.1.md](RECAPITULATIF_VISUEL_V3.5.1.md)

**Q: Comment tester les nouvelles règles congés ?**  
R: [CONGES_NOUVELLES_REGLES_V3.5.1.md](CONGES_NOUVELLES_REGLES_V3.5.1.md) § Tests

**Q: Que faire si problème après déploiement ?**  
R: [DEPLOIEMENT_RAPIDE_V3.5.1.md](DEPLOIEMENT_RAPIDE_V3.5.1.md) § Résolution Problèmes

**Q: Comment faire rollback ?**  
R: [DEPLOIEMENT_RAPIDE_V3.5.1.md](DEPLOIEMENT_RAPIDE_V3.5.1.md) § Rollback

---

## 🎯 Prochaines Étapes

1. ✅ Lire documentation adaptée à votre rôle
2. ✅ Préparer environnement (backup DB)
3. ✅ Exécuter déploiement suivant guide
4. ✅ Valider tous les tests
5. ✅ Former utilisateurs finaux
6. ✅ Monitorer première semaine

---

## 📞 Contact & Support

En cas de question sur la documentation :
1. Vérifier FAQ ci-dessus
2. Chercher dans les 4 documents principaux
3. Consulter logs système
4. Créer issue GitHub si besoin

---

**Index créé le** : 12 décembre 2025  
**Maintenu par** : Équipe Développement AY HR  
**Version système** : 3.5.1  
**Status** : ✅ Complet et à jour

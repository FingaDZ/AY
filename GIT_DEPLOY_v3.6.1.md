# Instructions Git et Déploiement v3.6.1

## 📋 Résumé des Modifications

### Fichiers Modifiés
- `backend/config.py` → Version 3.6.1
- `backend/models/conge.py` → Ajout mois/année déduction
- `backend/models/credit.py` → Ajout dates échéancier
- `backend/routers/conges.py` → Support mois déduction
- `backend/routers/credits.py` → Calcul auto échéancier
- `backend/routers/employes.py` → 3 nouveaux endpoints contrats
- `backend/routers/avances.py` → Logging amélioré
- `backend/routers/missions.py` → Logging amélioré
- `backend/routers/clients.py` → Logging amélioré
- `backend/services/employe_service.py` → **NOUVEAU** - Service contrats
- `frontend/package.json` → Version 3.6.1
- `frontend/src/pages/Dashboard.jsx` → Version v3.6.1
- `frontend/src/pages/Login/LoginPage.jsx` → Version 3.6.1
- `database/migration_v3.6.1_conges_credits_contrats.sql` → **NOUVEAU** - Migration MySQL
- `README.md` → Nouveautés v3.6.1
- `RELEASE_V3.6.1.md` → **NOUVEAU** - Documentation complète
- `UPGRADE_V3.6.1.md` → **NOUVEAU** - Guide mise à jour

## 🚀 Commandes Git

### 1. Vérifier l'état
```bash
cd "F:\Code\AY HR"
git status
```

### 2. Ajouter tous les fichiers modifiés
```bash
git add .
```

### 3. Créer un commit avec message détaillé
```bash
git commit -m "Release v3.6.1 - Congés flexibles, Crédits auto, Contrats expirés

Nouvelles fonctionnalités:
- Gestion avancée congés: mois de déduction flexible
- Calculs précis crédits: échéancier automatique
- Auto-désactivation employés contrat expiré
- Logging amélioré avec user_id/ip_address

Modifications:
- Backend: Nouveaux modèles et routes
- Frontend: Version 3.6.1 affichée
- BDD: Script migration MySQL
- Documentation: RELEASE_V3.6.1.md, UPGRADE_V3.6.1.md

Correctifs:
- Migration corrigée pour MySQL (vs PostgreSQL)
- Validation dates crédits/avances renforcée
"
```

### 4. Créer un tag de version
```bash
git tag -a v3.6.1 -m "Version 3.6.1 - Gestion avancée congés, crédits et contrats"
```

### 5. Pousser vers GitHub
```bash
# Pousser le code
git push origin main

# Pousser les tags
git push origin --tags
```

## 📦 Créer une Release sur GitHub

### Option 1: Via l'interface GitHub
1. Aller sur https://github.com/FingaDZ/AY
2. Cliquer sur "Releases" → "Draft a new release"
3. Choisir le tag: `v3.6.1`
4. Titre: **Release v3.6.1 - Gestion Avancée**
5. Description (copier-coller):

```markdown
# 🎉 AY HR System v3.6.1

## 🆕 Nouvelles Fonctionnalités

### 📅 Gestion Avancée des Congés
- Mois de déduction flexible pour les bulletins de paie
- Colonnes `mois_deduction` et `annee_deduction`
- Validation stricte (1-12 pour mois, 2000-2100 pour année)

### 💰 Calculs Précis Crédits & Avances
- Échéancier automatique lors de la création d'un crédit
- Colonnes: `mois_debut`, `annee_debut`, `mois_fin_prevu`, `annee_fin_prevu`
- Validation renforcée des périodes
- Contrôle 70% avances maintenu

### 🔄 Auto-Désactivation Contrats Expirés
- Service automatique de détection
- 3 nouveaux endpoints API
- Workflow de réactivation contrôlé
- Logging complet

### 🔒 Logging Amélioré
- Traçabilité complète: `user_id`, `user_email`, `ip_address`, `record_id`
- Tous les modules: Congés, Crédits, Avances, Missions, Clients

## 📥 Installation

### Nouvelle Installation
Voir [README.md](README.md)

### Mise à Jour depuis v3.6.0
Suivre le guide [UPGRADE_V3.6.1.md](UPGRADE_V3.6.1.md)

**⚠️ Important**: Exécuter la migration MySQL avant de redémarrer

## 🗄️ Migration Base de Données

```bash
mysql -u root -p ay_hr < database/migration_v3.6.1_conges_credits_contrats.sql
```

## 📚 Documentation

- [RELEASE_V3.6.1.md](RELEASE_V3.6.1.md) - Documentation complète
- [UPGRADE_V3.6.1.md](UPGRADE_V3.6.1.md) - Guide de mise à jour
- [README.md](README.md) - Guide d'installation

## 🐛 Correctifs

- Script migration corrigé pour MySQL (syntaxe PostgreSQL → MySQL)
- Validation dates améliorée
- Index ajoutés pour performances

## 🔗 Liens Utiles

- [Commits](https://github.com/FingaDZ/AY/commits/main)
- [Issues](https://github.com/FingaDZ/AY/issues)
- [Wiki](https://github.com/FingaDZ/AY/wiki)

## 📞 Support

Pour toute question ou problème, ouvrir une [issue](https://github.com/FingaDZ/AY/issues/new).
```

6. Cocher "Set as the latest release"
7. Cliquer "Publish release"

### Option 2: Via GitHub CLI
```bash
# Installer GitHub CLI si nécessaire
# https://cli.github.com/

gh release create v3.6.1 \
  --title "Release v3.6.1 - Gestion Avancée" \
  --notes-file RELEASE_V3.6.1.md \
  --latest
```

## 🔍 Vérification Post-Push

### 1. Vérifier sur GitHub
- Aller sur https://github.com/FingaDZ/AY
- Vérifier que le commit est visible
- Vérifier que le tag v3.6.1 apparaît
- Vérifier que la release est publiée

### 2. Cloner ailleurs pour tester
```bash
cd /tmp
git clone https://github.com/FingaDZ/AY.git
cd AY
git checkout v3.6.1

# Vérifier la version
grep "APP_VERSION" backend/config.py
grep "version" frontend/package.json
```

## 📊 Statistiques du Commit

```bash
# Nombre de fichiers modifiés
git diff --stat v3.6.0..v3.6.1

# Lignes ajoutées/supprimées
git diff --shortstat v3.6.0..v3.6.1

# Liste des commits
git log v3.6.0..v3.6.1 --oneline
```

## 🌿 Workflow Branches (Optionnel)

Si vous utilisez des branches de développement:

```bash
# Créer branche develop si elle n'existe pas
git checkout -b develop
git push origin develop

# Pour les prochaines fonctionnalités
git checkout develop
git checkout -b feature/nouvelle-fonctionnalite

# Quand terminé
git checkout develop
git merge feature/nouvelle-fonctionnalite
git push origin develop

# Release
git checkout main
git merge develop
git tag v3.6.2
git push origin main --tags
```

## 🔐 Configuration .gitignore

Vérifier que ces fichiers ne sont PAS committés:
```gitignore
# Déjà dans .gitignore
.env
*.db
*.pyc
__pycache__/
node_modules/
.venv/
venv/
dist/
build/
*.log

# Fichiers sensibles
database/backup*.sql
*.pem
*.key
secrets.json
```

## 📝 CHANGELOG

Mettre à jour CHANGELOG.md:
```bash
cat >> CHANGELOG.md << 'EOF'

## [3.6.1] - 2025-12-22

### Added
- Congés: Colonnes mois_deduction et annee_deduction pour déduction flexible
- Crédits: Échéancier automatique avec dates prévisionnelles
- Employés: Service auto-désactivation contrats expirés
- Employés: 3 nouveaux endpoints pour gestion contrats
- Logging: user_id, user_email, ip_address, record_id dans tous les logs

### Changed
- Migration: Syntaxe PostgreSQL → MySQL
- Validation: Renforcement contrôles dates et montants
- Documentation: RELEASE_V3.6.1.md et UPGRADE_V3.6.1.md

### Fixed
- Script migration corrigé pour MySQL
- Index optimisés pour performances

EOF

git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for v3.6.1"
git push origin main
```

## ✅ Checklist Avant Push

- [ ] Tous les tests passent
- [ ] Migration MySQL testée
- [ ] Version mise à jour (backend, frontend, docs)
- [ ] README.md à jour
- [ ] RELEASE_V3.6.1.md créé
- [ ] UPGRADE_V3.6.1.md créé
- [ ] .gitignore vérifié (pas de fichiers sensibles)
- [ ] Commit message descriptif
- [ ] Tag v3.6.1 créé

## 🎯 Commandes Rapides

```bash
# Tout en une fois
cd "F:\Code\AY HR"
git add .
git commit -m "Release v3.6.1"
git tag -a v3.6.1 -m "Version 3.6.1"
git push origin main --tags
```

## 📞 Support Git

Problèmes courants:

### Erreur: remote rejected
```bash
# Forcer le push (attention!)
git push origin main --force

# OU créer nouvelle branche
git checkout -b v3.6.1-release
git push origin v3.6.1-release
```

### Erreur: Permission denied
```bash
# Vérifier credentials GitHub
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"

# Utiliser HTTPS avec token
git remote set-url origin https://TOKEN@github.com/FingaDZ/AY.git
```

### Annuler un commit (avant push)
```bash
git reset --soft HEAD~1  # Garde les changements
git reset --hard HEAD~1  # Supprime tout
```

---

**🎉 Bon déploiement de la v3.6.1 !**

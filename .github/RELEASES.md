# Releases - AY HR Management System

## Comment créer une nouvelle release sur GitHub

### 1. Via l'interface GitHub

1. Aller sur https://github.com/FingaDZ/AY/releases
2. Cliquer sur **"Draft a new release"**
3. Remplir le formulaire:
   - **Tag version** : v1.1.2 (doit correspondre au tag git)
   - **Release title** : Version 1.1.2 - Corrections finales
   - **Description** : Copier le contenu de la section correspondante dans CHANGELOG.md
4. Cocher **"Set as the latest release"** si c'est la version stable actuelle
5. Cliquer sur **"Publish release"**

### 2. Via la ligne de commande

```bash
# Créer et pousser un tag
git tag -a v1.1.2 -m "Version 1.1.2 - Corrections finales"
git push origin v1.1.2

# Ensuite, créer la release sur GitHub via l'interface web
```

### 3. Structure d'une release

#### Exemple pour v1.1.2

**Titre** : Version 1.1.2 - Corrections finales

**Description** :
```markdown
## 🐛 Corrections

- **PDF Bulletins de Paie** : Affichage dynamique des informations entreprise
- **Footer PDF** : Ajout automatique "Powered by AIRBAND"
- **Test Connexion DB** : Encodage correct des mots de passe spéciaux (!@#$)
- **Création Employé** : Correction erreur 500 - ajout champ actif
- **React Router** : Suppression warnings v7

## 📄 Fichiers Modifiés

- backend/services/pdf_generator.py
- backend/models/database_config.py
- backend/schemas/employe.py
- frontend/src/App.jsx

## 📝 Documentation

- [CORRECTIONS_V1.1.2.md](https://github.com/FingaDZ/AY/blob/main/CORRECTIONS_V1.1.2.md)
- [CHANGELOG.md](https://github.com/FingaDZ/AY/blob/main/CHANGELOG.md)

## ⬇️ Installation

```bash
git clone https://github.com/FingaDZ/AY.git
cd AY
git checkout v1.1.2
```

## 🔧 Déploiement

Voir [INSTALLATION.md](https://github.com/FingaDZ/AY/blob/main/INSTALLATION.md)
```

---

## Templates de Release

### Release Majeure (v2.0.0)

```markdown
# 🎉 Version 2.0.0 - Titre Accrocheur

## ✨ Nouveautés Majeures

- **Feature 1** : Description
- **Feature 2** : Description

## ⚠️ Breaking Changes

- **Change 1** : Impact et migration
- **Change 2** : Impact et migration

## 🐛 Corrections

- Fix 1
- Fix 2

## 📊 Statistiques

- X fichiers modifiés
- Y lignes ajoutées
- Z bugs corrigés

## 📝 Documentation

- [CHANGELOG.md](link)
- [GUIDE_MIGRATION_V2.md](link)
```

### Release Mineure (v1.2.0)

```markdown
# ✨ Version 1.2.0 - Nouvelles fonctionnalités

## ✨ Nouveautés

- Feature 1
- Feature 2

## 🐛 Corrections

- Fix 1
- Fix 2

## 📝 Documentation

- [CHANGELOG.md](link)
```

### Release Patch (v1.1.3)

```markdown
# 🐛 Version 1.1.3 - Corrections

## 🐛 Corrections

- Fix 1
- Fix 2
- Fix 3

## 📝 Documentation

- [CORRECTIONS_V1.1.3.md](link)
```

---

## Checklist avant Release

- [ ] Tests passés (backend + frontend)
- [ ] Documentation mise à jour (README.md, CHANGELOG.md)
- [ ] Version incrémentée (package.json, config.py, README.md)
- [ ] Tag git créé et poussé
- [ ] Commit de release créé
- [ ] CHANGELOG.md complété
- [ ] Documentation des corrections créée (CORRECTIONS_Vx.x.x.md)
- [ ] Screenshots/GIFs si UI changes
- [ ] Migration DB documentée si nécessaire

---

## Convention de Nommage

### Tags Git
- **Format** : `vX.Y.Z` (ex: v1.1.2)
- **X** (Majeur) : Breaking changes, refonte majeure
- **Y** (Mineur) : Nouvelles fonctionnalités, pas de breaking change
- **Z** (Patch) : Corrections de bugs uniquement

### Titres de Release
- **Majeure** : "Version X.0.0 - Nom Accrocheur"
- **Mineure** : "Version X.Y.0 - Description Courte"
- **Patch** : "Version X.Y.Z - Corrections"

### Fichiers Documentation
- **Corrections** : `CORRECTIONS_VX.Y.Z.md`
- **Nouvelles Features** : `AMELIORATIONS_VX.Y.md` ou nom descriptif
- **Changelog** : `CHANGELOG.md` (unique, cumulatif)

---

## Automatisation Future

### GitHub Actions (TODO)

```yaml
# .github/workflows/release.yml
name: Create Release
on:
  push:
    tags:
      - 'v*'
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: ./release-notes.md
          draft: false
          prerelease: false
```

---

## Historique des Releases

| Version | Date | Type | Highlights |
|---------|------|------|-----------|
| [v1.1.2](https://github.com/FingaDZ/AY/releases/tag/v1.1.2) | 2025-11-13 | Patch | Corrections PDF, DB, schemas |
| [v1.1.1](https://github.com/FingaDZ/AY/releases/tag/v1.1.1) | 2025-11-12 | Patch | Soft delete, protection données |
| [v1.1.0](https://github.com/FingaDZ/AY/releases/tag/v1.1.0) | 2025-11-12 | Minor | Logging system, branding |
| [v1.0.0](https://github.com/FingaDZ/AY/releases/tag/v1.0.0) | 2025-11-11 | Major | Première version stable |

---

## Support

Pour toute question sur les releases:
- Consulter [CHANGELOG.md](../CHANGELOG.md)
- Voir les [issues GitHub](https://github.com/FingaDZ/AY/issues)
- Contacter le mainteneur : @FingaDZ

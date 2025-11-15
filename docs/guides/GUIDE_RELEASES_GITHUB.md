# Guide Rapide - Création Release GitHub v1.1.2

## 🎯 Objectif
Créer une release visible sur https://github.com/FingaDZ/AY/releases avec toutes les informations de la version 1.1.2.

## 📋 Étapes

### 1. Aller sur GitHub Releases
🔗 https://github.com/FingaDZ/AY/releases

### 2. Cliquer sur "Draft a new release"
Bouton vert en haut à droite.

### 3. Remplir le formulaire

#### **Choose a tag**
Sélectionner le tag existant : `v1.1.2`
(Si le tag n'existe pas dans la liste, le créer en tapant `v1.1.2`)

#### **Release title**
```
Version 1.1.2 - Corrections finales
```

#### **Description**
Copier-coller le texte suivant :

```markdown
## 🐛 Corrections

- **PDF Bulletins de Paie** : Affichage dynamique des informations entreprise depuis `parametres_entreprise` (raison sociale, adresse, CNAS) au lieu de valeurs codées en dur
- **Footer PDF** : Ajout automatique de "Powered by AIRBAND" sur tous les bulletins de paie
- **Test Connexion DB** : Encodage correct des mots de passe avec caractères spéciaux (!@#$%^&*) via `quote_plus()` dans `DatabaseConfig.connection_string()`
- **Création Employé** : Correction erreur 500 - ajout du champ `actif: bool = True` dans les schémas Pydantic (EmployeBase, EmployeUpdate)
- **React Router** : Suppression des warnings v7 via ajout des future flags `v7_startTransition` et `v7_relativeSplatPath`

## 📄 Fichiers Modifiés

**Backend (3 fichiers)**
- `backend/services/pdf_generator.py` (12 lignes)
- `backend/models/database_config.py` (3 lignes)  
- `backend/schemas/employe.py` (2 lignes)

**Frontend (1 fichier)**
- `frontend/src/App.jsx` (6 lignes)

## 📝 Documentation

- 📋 [CHANGELOG complet](https://github.com/FingaDZ/AY/blob/main/CHANGELOG.md)
- 📄 [Détails corrections v1.1.2](https://github.com/FingaDZ/AY/blob/main/CORRECTIONS_V1.1.2.md)
- 🛡️ [Corrections critiques v1.1.1](https://github.com/FingaDZ/AY/blob/main/CORRECTIONS_V1.1.1.md)
- ✨ [Améliorations v1.1.0](https://github.com/FingaDZ/AY/blob/main/AMELIORATIONS_V1.1.md)

## ⬇️ Installation

```bash
git clone https://github.com/FingaDZ/AY.git
cd AY
git checkout v1.1.2
```

Puis suivre le [Guide d'installation](https://github.com/FingaDZ/AY/blob/main/INSTALLATION.md).

## 🚀 Déploiement

```powershell
# Démarrer l'application complète
.\start_all.ps1

# Ou séparément
.\start_backend.ps1  # Backend sur :8000
.\start_frontend.ps1 # Frontend sur :3000
```

## 📊 Statistiques

| Métrique | Valeur |
|----------|--------|
| Bugs corrigés | 4 |
| Fichiers modifiés | 4 |
| Lignes ajoutées | 14 |
| Lignes modifiées | 13 |
| Documentation | 374 lignes |

## 🔗 Liens Utiles

- 📚 [README](https://github.com/FingaDZ/AY/blob/main/README.md)
- 📖 [Guide Utilisateur](https://github.com/FingaDZ/AY/blob/main/GUIDE_UTILISATEUR.md)
- 🚀 [Guide Démarrage](https://github.com/FingaDZ/AY/blob/main/GUIDE_DEMARRAGE.md)
- 🐛 [Troubleshooting](https://github.com/FingaDZ/AY/blob/main/TROUBLESHOOTING.md)

---

**Version précédente** : [v1.1.1](https://github.com/FingaDZ/AY/releases/tag/v1.1.1)  
**Toutes les versions** : [CHANGELOG](https://github.com/FingaDZ/AY/blob/main/CHANGELOG.md)
```

### 4. Options

- ✅ Cocher **"Set as the latest release"** (c'est la version stable actuelle)
- ❌ Ne PAS cocher "Set as a pre-release" (c'est une version stable)

### 5. Publier

Cliquer sur **"Publish release"** (bouton vert en bas)

---

## ✅ Résultat Attendu

Après publication, vous verrez sur https://github.com/FingaDZ/AY :

1. **Badge "Latest"** à côté de la version
2. **Section Releases** dans la sidebar droite
3. **Description complète** formatée avec Markdown
4. **Liens vers documentation** cliquables
5. **Statistiques** visibles

---

## 🔄 Répéter pour les versions précédentes

### v1.1.1 (12 novembre 2025)

**Title** : `Version 1.1.1 - Corrections critiques`

**Description** : Voir [CORRECTIONS_V1.1.1.md](CORRECTIONS_V1.1.1.md) et copier le contenu approprié.

---

### v1.1.0 (12 novembre 2025)

**Title** : `Version 1.1.0 - Système de logging et branding entreprise`

**Description** : Voir [AMELIORATIONS_V1.1.md](AMELIORATIONS_V1.1.md).

---

### v1.0.0 (11 novembre 2025)

**Title** : `Version 1.0.0 - Première version stable`

**Description** :
```markdown
## 🎉 Première Version Stable

### ✨ Fonctionnalités Principales

- 👤 Système d'authentification et autorisation JWT
- 🔒 Rôles utilisateurs (Admin, User)
- 🗄️ Configuration base de données dynamique
- 👥 Gestion employés complète
- 📅 Système de pointage mensuel
- 🚗 Ordres de mission chauffeurs
- 💰 Gestion avances et crédits
- 💵 Calcul automatique des salaires
- 📄 Génération PDF/Excel

### 📝 Documentation

- [Guide Utilisateur](https://github.com/FingaDZ/AY/blob/main/GUIDE_UTILISATEUR.md)
- [Guide Installation](https://github.com/FingaDZ/AY/blob/main/INSTALLATION.md)
- [STATUS](https://github.com/FingaDZ/AY/blob/main/STATUS.md)
```

---

## 📞 Support

Si problème lors de la création de release :
1. Vérifier que le tag existe : `git tag -l`
2. Pousser le tag : `git push origin v1.1.2`
3. Rafraîchir la page GitHub
4. Réessayer

---

**Créé le** : 13 novembre 2025  
**Par** : @FingaDZ

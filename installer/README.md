# Installateur Windows NSIS - AY HR System v3.6.0

Ce dossier contient tous les fichiers nécessaires pour créer un installateur Windows autonome (.exe) pour AY HR System.

## 📦 Contenu

### Fichiers Principaux
- **ayhr_installer.nsi** - Script NSIS principal pour créer l'installateur
- **build_package.ps1** - Script PowerShell automatique de préparation du package
- **QUICK_START.md** - Guide rapide de démarrage
- **BUILD_INSTALLER.md** - Documentation complète et détaillée

### Scripts d'Installation
Le dossier `scripts/` contient :
- **init_database.bat** - Initialisation de la base de données MariaDB
- **generate_secret.ps1** - Génération de la clé secrète JWT
- **start_ayhr.bat** - Démarrage des services
- **stop_ayhr.bat** - Arrêt des services
- **status_ayhr.bat** - Vérification du statut des services
- **backup_database.bat** - Sauvegarde de la base de données

## 🚀 Utilisation Rapide

### 1. Préparer le Package
```powershell
.\build_package.ps1
```

### 2. Compiler l'Installateur
```powershell
.\build_package.ps1 -CompileNow
```

### 3. Résultat
Un fichier `AY_HR_Setup_v3.6.0.exe` sera créé (~200-250 MB)

## 📚 Documentation

- **Guide Rapide** : [QUICK_START.md](QUICK_START.md)
- **Guide Complet** : [BUILD_INSTALLER.md](BUILD_INSTALLER.md)

## 💡 Ce qui est Inclus dans l'Installateur

L'installateur Windows contient **TOUT** ce qui est nécessaire pour faire fonctionner l'application sans connexion Internet :

✅ **Python 3.11 Embedded** avec tous les packages
✅ **MariaDB 10.11** serveur de base de données portable
✅ **Nginx** serveur web
✅ **NSSM** gestionnaire de services Windows
✅ **Backend** code Python complet
✅ **Frontend** application React compilée
✅ **Base de données** structure et données initiales
✅ **Scripts** de gestion automatique

## 🎯 Fonctionnalités de l'Installateur

- ✅ Installation en un clic (mode assistant)
- ✅ Configuration automatique de tous les services
- ✅ Création des services Windows automatiques
- ✅ Base de données initialisée automatiquement
- ✅ Raccourcis bureau et menu démarrer
- ✅ Désinstallation propre
- ✅ Aucune connexion Internet requise après installation

## 📋 Prérequis pour Créer l'Installateur

- Windows 10/11
- NSIS 3.x installé
- PowerShell
- ~2 GB d'espace disque libre
- Connexion Internet (pour télécharger les composants)

## 🔧 Composants Téléchargés Automatiquement

Le script `build_package.ps1` télécharge automatiquement :

1. **Python 3.11 Embedded** (150 MB)
2. **Tous les packages Python** (openpyxl, fastapi, etc.)
3. **Node.js Portable** (50 MB)
4. **MariaDB 10.11** (200 MB)
5. **Nginx 1.24** (15 MB)
6. **NSSM 2.24** (1 MB)

## 🧪 Test de l'Installateur

Testez toujours l'installateur sur une **machine virtuelle Windows propre** sans aucun logiciel préinstallé (Python, Node, MySQL, etc.).

## 📞 Support

Pour toute question :
- Consultez [BUILD_INSTALLER.md](BUILD_INSTALLER.md)
- Email: support@aycompany.dz

---

**Version** : 3.6.0  
**Date** : Décembre 2025  
**Auteur** : AY Company

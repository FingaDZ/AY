# Guide Rapide - Installateur NSIS
## AY HR System v3.6.0

## 🚀 Installation Rapide

### Prérequis
- Windows 10/11
- Droits administrateur
- ~2 GB d'espace disque libre
- Connexion Internet (pour la préparation uniquement)

### Étape 1: Installer NSIS
```powershell
# Télécharger NSIS depuis:
# https://nsis.sourceforge.io/Download

# Ou via Chocolatey:
choco install nsis -y
```

### Étape 2: Préparer le Package
```powershell
cd installer
.\build_package.ps1
```

Ce script va automatiquement:
- ✅ Télécharger Python 3.11 Embedded
- ✅ Télécharger tous les packages Python
- ✅ Télécharger Node.js portable
- ✅ Compiler le frontend React
- ✅ Télécharger MariaDB
- ✅ Télécharger Nginx
- ✅ Télécharger NSSM
- ✅ Copier le code source
- ✅ Créer les configurations

⏱️ **Durée estimée**: 30-45 minutes

### Étape 3: Ajouter les Icônes (Optionnel)
```powershell
# Créer ou copier les icônes dans:
cd package\resources\

# Fichiers nécessaires (ou utiliser des icônes par défaut):
# - app.ico
# - header.bmp (150x57 px)
# - wizard.bmp (164x314 px)
```

### Étape 4: Compiler l'Installateur
```powershell
# Option A: Avec le script
.\build_package.ps1 -CompileNow

# Option B: Manuellement
makensis.exe ayhr_installer.nsi
```

**Résultat**: `AY_HR_Setup_v3.6.0.exe` (~200-250 MB)

---

## 🧪 Test de l'Installateur

### Sur une Machine de Test
1. Créer une VM Windows propre (sans Python, Node, MySQL)
2. Copier `AY_HR_Setup_v3.6.0.exe` dans la VM
3. Exécuter en tant qu'administrateur
4. Suivre l'assistant d'installation
5. Tester l'application: http://localhost
6. Identifiants par défaut:
   - Email: `admin@ayhr.dz`
   - Mot de passe: `admin123`

### Vérifier les Services
```cmd
sc query AYHR_MySQL
sc query AYHR_Backend
sc query AYHR_Nginx
```

---

## 📦 Options du Script build_package.ps1

```powershell
# Sauter les téléchargements (si déjà fait)
.\build_package.ps1 -SkipDownloads

# Sauter la compilation du frontend
.\build_package.ps1 -SkipBuild

# Compiler directement après la préparation
.\build_package.ps1 -CompileNow

# Combiner les options
.\build_package.ps1 -SkipDownloads -CompileNow
```

---

## 📂 Structure Finale

```
installer/
├── AY_HR_Setup_v3.6.0.exe    ← Installateur final
├── ayhr_installer.nsi         ← Script NSIS
├── build_package.ps1          ← Script de préparation
├── BUILD_INSTALLER.md         ← Documentation complète
├── QUICK_START.md            ← Ce fichier
├── scripts/                   ← Scripts d'installation
│   ├── init_database.bat
│   ├── generate_secret.ps1
│   ├── start_ayhr.bat
│   ├── stop_ayhr.bat
│   └── backup_database.bat
└── package/                   ← Tous les composants
    ├── python/               (150 MB)
    ├── nodejs/               (50 MB)
    ├── mariadb/              (200 MB)
    ├── nginx/                (15 MB)
    ├── nssm/                 (1 MB)
    ├── backend/              (10 MB)
    ├── frontend/             (5 MB)
    ├── frontend-dist/        (5 MB)
    ├── database/             (1 MB)
    └── resources/            (icônes)
```

---

## ✅ Checklist

- [ ] NSIS installé
- [ ] Script build_package.ps1 exécuté
- [ ] Tous les téléchargements terminés
- [ ] Frontend compilé
- [ ] Icônes ajoutées (optionnel)
- [ ] Installateur compilé
- [ ] Test sur VM réussi
- [ ] Services démarrent correctement
- [ ] Application accessible
- [ ] Désinstallation testée

---

## 🎯 Ce qui est Inclus

L'installateur contient **TOUT** ce qui est nécessaire:

✅ **Python 3.11** avec tous les packages (FastAPI, SQLAlchemy, etc.)
✅ **MariaDB 10.11** serveur de base de données
✅ **Nginx** serveur web
✅ **NSSM** gestionnaire de services
✅ **Backend** code Python complet
✅ **Frontend** application React compilée
✅ **Base de données** structure SQL complète
✅ **Scripts** démarrage/arrêt/backup automatiques

❌ **Aucune connexion Internet requise** après installation
❌ **Aucun logiciel tiers à installer**

---

## 🔧 Personnalisation

### Changer les Ports
Éditer avant compilation:
- **MariaDB**: `package\mariadb\my.ini` → `port=3307`
- **Backend**: Script NSIS → `--port 8000`
- **Nginx**: `package\nginx-config\nginx.conf` → `listen 80`

### Changer les Mots de Passe
Éditer `scripts\init_database.bat`:
```batch
set DB_PASSWORD=votre_mot_de_passe
set DB_ROOT_PASSWORD=votre_mot_de_passe_root
```

---

## 🐛 Dépannage

### Le script build_package.ps1 échoue
```powershell
# Activer l'exécution des scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Téléchargement lent
- Utiliser un VPN si les sites sont bloqués
- Télécharger manuellement et placer dans les bons dossiers

### Compilation NSIS échoue
- Vérifier que NSIS est dans le PATH
- Utiliser le chemin complet: `"C:\Program Files (x86)\NSIS\makensis.exe"`

---

## 📞 Support

- Documentation complète: [BUILD_INSTALLER.md](BUILD_INSTALLER.md)
- Projet: [README.md](../README.md)
- Email: support@aycompany.dz

---

**🎉 Vous êtes prêt à créer votre installateur Windows !**

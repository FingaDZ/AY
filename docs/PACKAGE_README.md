# Package de Distribution - AIRBAND HR v1.1.4

## 📦 Création des Packages

Ce dossier contient les scripts pour créer des packages de distribution prêts à l'emploi pour Windows et Linux.

## Scripts Disponibles

### Windows
```powershell
.\create-package-windows.ps1
```

Crée un package ZIP contenant:
- Code source du backend (sans fichiers de test)
- Code source du frontend (sans node_modules)
- Scripts d'installation automatique
- Scripts de démarrage/arrêt
- Script d'installation en tant que service Windows
- Documentation complète

**Sortie**: `ay-hr-v1.1.4-windows.zip`

### Linux
```bash
chmod +x create-package-linux.sh
./create-package-linux.sh
```

Crée un package TAR.GZ contenant:
- Code source du backend (sans fichiers de test)
- Code source du frontend (sans node_modules)
- Scripts d'installation automatique
- Scripts de démarrage/arrêt
- Script d'installation en tant que service systemd
- Documentation complète

**Sortie**: `ay-hr-v1.1.4-linux.tar.gz`

## Contenu des Packages

### Structure Commune
```
ay-hr-v1.1.4/
├── backend/                    # Code serveur FastAPI
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── requirements.txt
├── frontend/                   # Interface React
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── database/                   # Scripts SQL
│   └── create_database.sql
├── INSTALLATION_GUIDE.md       # Guide complet
└── README_PACKAGE.md           # Instructions rapides
```

### Fichiers Spécifiques Windows
```
├── install-windows.ps1         # Installation automatique
├── start-windows.ps1           # Démarrage manuel
├── stop-windows.ps1            # Arrêt
└── install-service-windows.ps1 # Installation comme service
```

### Fichiers Spécifiques Linux
```
├── install-linux.sh            # Installation automatique
├── start-linux.sh              # Démarrage manuel
├── stop-linux.sh               # Arrêt
└── install-service-linux.sh    # Installation comme service systemd
```

## Fichiers Exclus des Packages

Les fichiers suivants sont automatiquement exclus pour réduire la taille:

- ✓ `.venv/` et `venv/` (environnements virtuels)
- ✓ `node_modules/` (dépendances Node.js)
- ✓ `__pycache__/` et `*.pyc` (cache Python)
- ✓ `.git/` (historique Git)
- ✓ `logs/`, `backups/`, `uploads/` (données locales)
- ✓ `test_*.py` et `check_*.py` (fichiers de test)
- ✓ Anciennes archives (*.zip, *.tar.gz)

## Utilisation des Packages

### Pour Windows

1. **Extraire le package**:
   ```powershell
   Expand-Archive -Path ay-hr-v1.1.4-windows.zip -DestinationPath C:\AY-HR
   ```

2. **Installer**:
   ```powershell
   cd C:\AY-HR\ay-hr-v1.1.4-windows
   .\install-windows.ps1
   ```

3. **Démarrer** (mode manuel):
   ```powershell
   .\start-windows.ps1
   ```

4. **Installer comme service** (optionnel):
   ```powershell
   .\install-service-windows.ps1
   ```

### Pour Linux

1. **Extraire le package**:
   ```bash
   tar -xzf ay-hr-v1.1.4-linux.tar.gz
   cd ay-hr-v1.1.4-linux
   ```

2. **Installer**:
   ```bash
   chmod +x install-linux.sh
   sudo ./install-linux.sh
   ```

3. **Démarrer** (mode manuel):
   ```bash
   ./start-linux.sh
   ```

4. **Installer comme service** (optionnel):
   ```bash
   sudo ./install-service-linux.sh
   ```

## Prérequis Système

### Windows
- Windows 10/11 ou Windows Server 2016+
- Python 3.11+
- Node.js 18+
- MariaDB 10.11+

### Linux
- Ubuntu 20.04+ ou Debian 11+
- Python 3.11+
- Node.js 18+
- MariaDB 10.11+

## Documentation Incluse

Chaque package contient:

1. **README_PACKAGE.md** - Instructions d'installation rapides
2. **INSTALLATION_GUIDE.md** - Guide détaillé avec:
   - Installation pas à pas
   - Configuration de la base de données
   - Dépannage
   - Configuration réseau
   - Procédures de sauvegarde
   - Configuration de sécurité

## Taille Estimée des Packages

- **Windows ZIP**: ~5-10 MB (sans dépendances)
- **Linux TAR.GZ**: ~5-10 MB (sans dépendances)

Les dépendances (Python packages et Node modules) sont téléchargées lors de l'installation.

## Mise à Jour d'une Installation Existante

### Windows
```powershell
# Arrêter l'application
.\stop-windows.ps1

# Sauvegarder la base de données
# (voir INSTALLATION_GUIDE.md)

# Extraire et installer la nouvelle version
Expand-Archive ay-hr-v1.1.4-windows.zip
cd ay-hr-v1.1.4-windows
.\install-windows.ps1

# Redémarrer
.\start-windows.ps1
```

### Linux
```bash
# Arrêter l'application
./stop-linux.sh

# Sauvegarder la base de données
# (voir INSTALLATION_GUIDE.md)

# Extraire et installer la nouvelle version
tar -xzf ay-hr-v1.1.4-linux.tar.gz
cd ay-hr-v1.1.4-linux
sudo ./install-linux.sh

# Redémarrer
./start-linux.sh
```

## Distribution

Ces packages sont prêts pour:
- ✓ Distribution interne
- ✓ Déploiement sur serveurs de production
- ✓ Installation sur postes clients
- ✓ Archives GitHub Releases

## Support

Pour toute question:
1. Consultez `INSTALLATION_GUIDE.md` (section Dépannage)
2. Vérifiez les logs dans `logs/backend.log` et `logs/frontend.log`
3. Contactez l'équipe de support

## Changelog v1.1.4

### Nouvelles Fonctionnalités
- ✓ Numérotation automatique des listes (employés, postes)
- ✓ Filtres avancés (actifs/inactifs)
- ✓ Réactivation des employés supprimés
- ✓ QR codes sur les fiches de paie
- ✓ Pieds de page améliorés sur les PDF

### Améliorations Techniques
- ✓ Optimisation des requêtes database
- ✓ Gestion améliorée des états
- ✓ Interface utilisateur plus intuitive
- ✓ Documentation complète

### Package de Déploiement
- ✓ Scripts d'installation automatique
- ✓ Installation en tant que service (Windows/Linux)
- ✓ Démarrage automatique au boot
- ✓ Guide simplifié pour non-techniciens

---

**Version**: 1.1.4  
**Date**: Janvier 2025  
**Auteur**: AY HR Management Team

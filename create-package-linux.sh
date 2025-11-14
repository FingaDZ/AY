#!/bin/bash
# ============================================================================
# Script de Création du Package Linux
# AIRBAND HR v1.1.4
# ============================================================================

VERSION="${1:-1.1.4}"

echo ""
echo "========================================"
echo " Création du Package Linux v$VERSION"
echo "========================================"
echo ""

# Dossiers et fichiers à exclure
EXCLUDE_PATTERNS=(
    ".venv"
    "venv"
    "node_modules"
    "__pycache__"
    ".pytest_cache"
    ".git"
    ".gitignore"
    ".vscode"
    ".idea"
    "*.log"
    "logs"
    "backups"
    "uploads"
    "test_*.py"
    "check_*.py"
    "*.tar.gz"
    "*.zip"
)

# Construire les options d'exclusion pour rsync
EXCLUDE_OPTS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTS="$EXCLUDE_OPTS --exclude=$pattern"
done

# Créer le dossier temporaire
TEMP_DIR="temp_package"
PACKAGE_NAME="ay-hr-v$VERSION-linux"
PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"

echo "[1/6] Nettoyage des anciens packages..."
rm -rf "$TEMP_DIR"
rm -f "$PACKAGE_NAME.tar.gz"

echo "[2/6] Création de la structure du package..."
mkdir -p "$PACKAGE_DIR"

echo "[3/6] Copie du backend..."
rsync -a $EXCLUDE_OPTS backend/ "$PACKAGE_DIR/backend/"

echo "[4/6] Copie du frontend..."
rsync -a $EXCLUDE_OPTS frontend/ "$PACKAGE_DIR/frontend/"

echo "[5/6] Copie des fichiers d'installation..."
FILES_TO_COPY=(
    "database/create_database.sql"
    "install-linux.sh"
    "start-linux.sh"
    "stop-linux.sh"
    "install-service-linux.sh"
    "INSTALLATION_GUIDE.md"
    "README.md"
)

for file in "${FILES_TO_COPY[@]}"; do
    if [ -f "$file" ]; then
        mkdir -p "$PACKAGE_DIR/$(dirname "$file")"
        cp "$file" "$PACKAGE_DIR/$file"
    fi
done

# Rendre les scripts exécutables
chmod +x "$PACKAGE_DIR"/*.sh

echo "[6/6] Création du README du package..."
cat > "$PACKAGE_DIR/README_PACKAGE.md" << EOF
# AY HR Management v$VERSION - Package Linux

## Installation Rapide

1. Extraire cette archive dans un dossier de votre choix:
   \`\`\`bash
   tar -xzf $PACKAGE_NAME.tar.gz
   cd $PACKAGE_NAME
   \`\`\`

2. Rendre le script d'installation exécutable:
   \`\`\`bash
   chmod +x install-linux.sh
   \`\`\`

3. Exécuter le script d'installation:
   \`\`\`bash
   sudo ./install-linux.sh
   \`\`\`

## Contenu du Package

- **backend/** - Code source du serveur API
- **frontend/** - Code source de l'interface web
- **database/** - Scripts SQL de création de la base de données
- **install-linux.sh** - Script d'installation automatique
- **start-linux.sh** - Script de démarrage manuel
- **stop-linux.sh** - Script d'arrêt
- **install-service-linux.sh** - Installation en tant que service systemd
- **INSTALLATION_GUIDE.md** - Guide d'installation complet

## Prérequis

- Ubuntu 20.04+ ou Debian 11+
- Python 3.11 ou supérieur
- Node.js 18 ou supérieur
- MariaDB 10.11 ou supérieur

## Documentation

Consultez le fichier **INSTALLATION_GUIDE.md** pour:
- Instructions d'installation détaillées
- Configuration de la base de données
- Dépannage
- Configuration réseau
- Procédures de sauvegarde

## Support

Pour toute question ou problème:
- Consultez INSTALLATION_GUIDE.md section "Dépannage"
- Vérifiez les logs dans le dossier logs/
- Contactez votre administrateur système

## Version

Version: $VERSION
Date: $(date +"%d/%m/%Y")
EOF

echo ""
echo "[Compression] Création de l'archive TAR.GZ..."
tar -czf "$PACKAGE_NAME.tar.gz" -C "$TEMP_DIR" "$PACKAGE_NAME"

echo ""
echo "[Nettoyage] Suppression des fichiers temporaires..."
rm -rf "$TEMP_DIR"

# Calculer la taille du fichier
SIZE=$(du -h "$PACKAGE_NAME.tar.gz" | cut -f1)

echo ""
echo "========================================"
echo " Package créé avec succès!"
echo "========================================"
echo ""
echo "Fichier: $PACKAGE_NAME.tar.gz"
echo "Taille: $SIZE"
echo ""
echo "Le package est prêt pour la distribution!"

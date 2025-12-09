#!/bin/bash

###############################################################################
#                    FIX FRONTEND BUILD - QUICK PATCH                         #
###############################################################################

set -e

echo "🔧 Correction du problème de build frontend..."

cd /opt/ay-hr

# 1. Déplacer package-lock.json dans frontend/
if [ -f "package-lock.json" ]; then
    echo "📦 Déplacement de package-lock.json vers frontend/"
    mv package-lock.json frontend/
fi

# 2. Nettoyer node_modules
echo "🧹 Nettoyage de node_modules..."
cd frontend
rm -rf node_modules package-lock.json

# 3. Réinstaller les dépendances
echo "📥 Installation des dépendances..."
npm install

# 4. Build frontend
echo "🏗️  Build du frontend..."
npm run build

# 5. Fixer les permissions
echo "🔐 Correction des permissions..."
cd /opt/ay-hr
chown -R root:root frontend/
chmod -R 755 frontend/dist/

echo "✅ Frontend corrigé et buildé avec succès!"
echo ""
echo "Redémarrez les services:"
echo "  sudo systemctl start ayhr-backend"
echo "  sudo systemctl start ayhr-frontend"

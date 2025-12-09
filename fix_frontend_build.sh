#!/bin/bash

###############################################################################
#           FIX NPM BUILD - Résolution problème @rollup/rollup-linux-x64-gnu #
###############################################################################

set -e

echo "🔧 Correction du problème de build npm/rollup..."
echo ""

cd /opt/ay-hr/frontend

# 1. Nettoyer complètement
echo "🧹 Nettoyage complet de npm..."
rm -rf node_modules package-lock.json

# 2. Vider le cache npm
echo "🗑️  Vidage du cache npm..."
npm cache clean --force

# 3. Réinstaller avec --force
echo "📥 Réinstallation des dépendances (avec --force)..."
npm install --force

# 4. Build
echo "🏗️  Build du frontend..."
npm run build

# 5. Vérifier le résultat
if [ -f "dist/index.html" ]; then
    echo ""
    echo "✅ Build réussi!"
    echo ""
    echo "📊 Fichiers générés:"
    ls -lh dist/
    ls -lh dist/assets/
else
    echo ""
    echo "❌ Erreur: Le build n'a pas généré dist/index.html"
    exit 1
fi

# 6. Permissions
echo ""
echo "🔐 Correction des permissions..."
cd /opt/ay-hr
chown -R root:root frontend/dist/
chmod -R 755 frontend/dist/

echo ""
echo "✅ Correction terminée! Redémarrez le frontend:"
echo "   sudo systemctl restart ayhr-frontend"

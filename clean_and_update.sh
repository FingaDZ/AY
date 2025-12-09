#!/bin/bash

###############################################################################
#           NETTOYAGE ET MISE À JOUR - Serveur Production                    #
###############################################################################

set -e

echo "🧹 Nettoyage des fichiers locaux et mise à jour..."
echo ""

cd /opt/ay-hr

# 1. Stash les modifications locales
echo "📦 Sauvegarde temporaire des modifications locales..."
git stash

# 2. Nettoyer les fichiers non trackés dans frontend/dist
echo "🗑️  Suppression des fichiers build non trackés..."
rm -rf frontend/dist/*

# 3. Pull depuis GitHub
echo "📥 Récupération des mises à jour depuis GitHub..."
git pull origin main

# 4. Rebuild Frontend complet
echo "🏗️  Rebuild complet du Frontend..."
cd frontend
rm -rf node_modules
npm install
npm run build

# 5. Fixer les permissions
echo "🔐 Correction des permissions..."
cd /opt/ay-hr
chown -R root:root frontend/dist/
chmod -R 755 frontend/dist/

# 6. Redémarrer les services
echo "🚀 Redémarrage des services..."
sudo systemctl start ayhr-backend ayhr-frontend

echo ""
echo "✅ Mise à jour terminée avec succès!"
echo ""
echo "📊 Statut des services:"
sudo systemctl status ayhr-backend --no-pager -l | head -15
echo ""
sudo systemctl status ayhr-frontend --no-pager -l | head -15

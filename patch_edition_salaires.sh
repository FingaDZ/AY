#!/bin/bash

###############################################################################
#           PATCH RAPIDE EDITION SALAIRES - Serveur Production               #
###############################################################################

set -e

echo "🔧 Application du patch Edition Salaires..."
echo ""

cd /opt/ay-hr

# 1. Arrêter les services
echo "⏸️  Arrêt des services..."
sudo systemctl stop ayhr-backend ayhr-frontend

# 2. Pull depuis GitHub
echo "📥 Récupération des corrections depuis GitHub..."
git pull origin main

# 3. Rebuild Frontend
echo "🏗️  Rebuild Frontend..."
cd frontend
rm -rf node_modules dist
npm install
npm run build

# 4. Redémarrer les services
echo "🚀 Redémarrage des services..."
sudo systemctl start ayhr-backend ayhr-frontend

echo ""
echo "✅ Patch appliqué avec succès!"
echo ""
echo "Vérifications:"
sudo systemctl status ayhr-backend --no-pager -l
echo ""
sudo systemctl status ayhr-frontend --no-pager -l

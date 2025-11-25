#!/bin/bash

# Script de déploiement v1.3.0 sur serveur production
# Usage: sudo ./deploy_v1.3.0.sh

set -e  # Exit on error

echo "========================================="
echo "  Déploiement AY HR v1.3.0"
echo "  Attendance Integration Complete"
echo "========================================="
echo ""

# Vérifier qu'on est root
if [ "$EUID" -ne 0 ]; then 
  echo "❌ Ce script doit être exécuté en tant que root (sudo)"
  exit 1
fi

# Variables
PROJECT_DIR="/opt/ay-hr"
BACKUP_DIR="/opt/ay-hr-backup-$(date +%Y%m%d-%H%M%S)"

echo "📁 Répertoire projet: $PROJECT_DIR"
echo "💾 Backup: $BACKUP_DIR"
echo ""

# Étape 1: Backup
echo "1️⃣  Création backup..."
cp -r "$PROJECT_DIR" "$BACKUP_DIR"
echo "✅ Backup créé: $BACKUP_DIR"
echo ""

# Étape 2: Git Pull
echo "2️⃣  Mise à jour depuis GitHub..."
cd "$PROJECT_DIR"
git fetch --tags
git pull origin main
echo "✅ Code mis à jour"
echo ""

# Étape 3: Vérifier la version
echo "3️⃣  Vérification version..."
CURRENT_TAG=$(git describe --tags 2>/dev/null || echo "unknown")
echo "📌 Version actuelle: $CURRENT_TAG"
echo ""

# Étape 4: Installation dépendances backend
echo "4️⃣  Installation dépendances backend..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
pip install -r requirements.txt --quiet
echo "✅ Dépendances backend installées"
echo ""

# Étape 5: Build frontend
echo "5️⃣  Build frontend..."
cd "$PROJECT_DIR/frontend"
npm install --silent
npm run build
echo "✅ Frontend buildé"
echo ""

# Étape 6: Redémarrage services
echo "6️⃣  Redémarrage services..."
systemctl restart ayhr-backend
systemctl restart ayhr-frontend
sleep 3
echo "✅ Services redémarrés"
echo ""

# Étape 7: Vérification
echo "7️⃣  Vérification services..."
BACKEND_STATUS=$(systemctl is-active ayhr-backend)
FRONTEND_STATUS=$(systemctl is-active ayhr-frontend)

if [ "$BACKEND_STATUS" = "active" ] && [ "$FRONTEND_STATUS" = "active" ]; then
  echo "✅ Backend: $BACKEND_STATUS"
  echo "✅ Frontend: $FRONTEND_STATUS"
  echo ""
  echo "========================================="
  echo "🎉 Déploiement v1.3.0 réussi !"
  echo "========================================="
  echo ""
  echo "📊 Nouveautés v1.3.0:"
  echo "  ✅ Bouton 'Sync Attendance' dans liste employés"
  echo "  ✅ Page 'Importer Pointages'"
  echo "  ✅ Page 'Conflits Import'"
  echo "  ✅ 8 endpoints API Attendance"
  echo ""
  echo "🔗 Accès:"
  echo "  Frontend: http://192.168.20.53:3000"
  echo "  Backend API: http://192.168.20.53:8000/docs"
  echo ""
  echo "📝 Backup disponible: $BACKUP_DIR"
else
  echo "❌ Erreur: Services non actifs"
  echo "Backend: $BACKEND_STATUS"
  echo "Frontend: $FRONTEND_STATUS"
  echo ""
  echo "🔍 Vérifier les logs:"
  echo "  journalctl -u ayhr-backend -n 50"
  echo "  journalctl -u ayhr-frontend -n 50"
  exit 1
fi

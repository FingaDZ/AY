#!/bin/bash

# Script de déploiement propre - V3.0
# Ce script nettoie complètement l'environnement et redéploie depuis GitHub

set -e  # Arrêter en cas d'erreur

echo "🧹 Nettoyage complet de l'environnement..."

# 1. Arrêter et supprimer TOUS les processus PM2
echo "Arrêt de PM2..."
pm2 kill || true
pm2 delete all || true

# 2. Tuer TOUS les processus Python et Uvicorn
echo "Arrêt de tous les processus Python/Uvicorn..."
pkill -9 -f "uvicorn" || true
pkill -9 -f "python.*uvicorn" || true
pkill -9 -f "venv/bin/python" || true
sleep 2

# 3. Vérifier que le port 8000 est libre
echo "Vérification du port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 encore occupé, nettoyage forcé..."
    lsof -ti:8000 | xargs kill -9 || true
    sleep 2
fi

# 4. Vérifier à nouveau
if lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ ERREUR: Impossible de libérer le port 8000"
    lsof -i :8000
    exit 1
fi

echo "✅ Port 8000 libéré"

# 5. Aller dans le répertoire du projet
cd /opt/ay-hr

# 6. Sauvegarder les fichiers de configuration locaux
echo "📦 Sauvegarde des configurations..."
cp backend/.env backend/.env.backup 2>/dev/null || true

# 7. Pull depuis GitHub
echo "📥 Récupération du code depuis GitHub..."
git fetch origin
git reset --hard origin/main
git pull origin main

# 8. Restaurer les configurations
echo "📂 Restauration des configurations..."
cp backend/.env.backup backend/.env 2>/dev/null || true

# 9. Mise à jour du backend
echo "🔧 Installation des dépendances backend..."
cd backend

# Créer le venv si nécessaire
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activer et installer
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

cd ..

# 10. Mise à jour du frontend
echo "🎨 Build du frontend..."
cd frontend
npm install
npm run build
cd ..

# 11. Exécuter la migration SQL
echo "🗄️  Exécution de la migration SQL..."
read -p "Utilisateur MySQL (défaut: root): " MYSQL_USER
MYSQL_USER=${MYSQL_USER:-root}

read -sp "Mot de passe MySQL: " MYSQL_PASSWORD
echo

read -p "Base de données (défaut: ay_hr): " MYSQL_DB
MYSQL_DB=${MYSQL_DB:-ay_hr}

read -p "Hôte MySQL (défaut: localhost): " MYSQL_HOST
MYSQL_HOST=${MYSQL_HOST:-localhost}

echo "Exécution de la migration..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DB" < backend/migrations/fix_v3_migration.sql

if [ $? -eq 0 ]; then
    echo "✅ Migration SQL réussie"
else
    echo "⚠️  Erreur lors de la migration SQL (peut-être déjà appliquée)"
fi

# 12. Redémarrer PM2 proprement
echo "🚀 Démarrage des services..."

# Supprimer l'ancien daemon PM2
pm2 kill

# Attendre un peu
sleep 3

# Démarrer avec ecosystem.config.js
pm2 start ecosystem.config.js

# Sauvegarder la configuration PM2
pm2 save

# Configurer PM2 pour démarrer au boot
pm2 startup || true

# 13. Vérification
echo ""
echo "📊 Vérification des services..."
sleep 5

pm2 list

echo ""
echo "🔍 Vérification du port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "✅ Backend écoute sur le port 8000"
    lsof -i :8000
else
    echo "❌ Backend ne répond pas sur le port 8000"
fi

echo ""
echo "🧪 Test de l'API..."
sleep 2
curl -s http://localhost:8000/health || echo "❌ API ne répond pas"

echo ""
echo "📋 Logs du backend (20 dernières lignes):"
pm2 logs ay-hr-backend --lines 20 --nostream

echo ""
echo "✅ Déploiement terminé !"
echo ""
echo "Pour voir les logs en temps réel:"
echo "  pm2 logs"
echo ""
echo "Pour redémarrer les services:"
echo "  pm2 restart all"
echo ""
echo "Pour arrêter les services:"
echo "  pm2 stop all"

#!/bin/bash

# Script d'installation propre - V3.0
# Supprime tout et réinstalle depuis GitHub
# CONSERVE UNIQUEMENT LA BASE DE DONNÉES

set -e

echo "🗑️  INSTALLATION PROPRE - Suppression et réinstallation complète"
echo "⚠️  Ce script va SUPPRIMER /opt/ay-hr et tout réinstaller"
echo "✅ La base de données sera CONSERVÉE"
echo ""
read -p "Continuer? (oui/non): " confirm

if [ "$confirm" != "oui" ]; then
    echo "❌ Installation annulée"
    exit 1
fi

echo ""
echo "🛑 Arrêt de tous les services..."

# 1. Tuer PM2 complètement
pm2 kill || true

# 2. Tuer TOUS les processus Python/Node
killall -9 python python3 uvicorn node || true

# 3. Libérer les ports
fuser -k 8000/tcp || true
fuser -k 3000/tcp || true
fuser -k 3001/tcp || true

sleep 3

# 4. Vérifier que les ports sont libres
if lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ ERREUR: Port 8000 encore occupé"
    lsof -i :8000
    exit 1
fi

echo "✅ Tous les services arrêtés"

# 5. Sauvegarder le fichier .env
echo "💾 Sauvegarde de la configuration..."
if [ -f /opt/ay-hr/backend/.env ]; then
    cp /opt/ay-hr/backend/.env /tmp/ay-hr-env-backup
    echo "✅ Configuration sauvegardée dans /tmp/ay-hr-env-backup"
else
    echo "⚠️  Aucun fichier .env trouvé"
fi

# 6. Supprimer complètement le répertoire
echo "🗑️  Suppression de /opt/ay-hr..."
rm -rf /opt/ay-hr

echo "✅ Ancien projet supprimé"

# 7. Cloner depuis GitHub
echo "📥 Clonage depuis GitHub..."
cd /opt
git clone https://github.com/FingaDZ/AY.git ay-hr

cd /opt/ay-hr

echo "✅ Code récupéré depuis GitHub"

# 8. Restaurer le fichier .env
echo "📂 Restauration de la configuration..."
if [ -f /tmp/ay-hr-env-backup ]; then
    cp /tmp/ay-hr-env-backup backend/.env
    echo "✅ Configuration restaurée"
else
    echo "⚠️  Pas de configuration à restaurer"
    echo "⚠️  Vous devrez créer backend/.env manuellement"
fi

# 9. Installation du backend
echo "🔧 Installation du backend..."
cd backend

# Créer le virtualenv
python3 -m venv venv

# Activer et installer
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

cd ..

echo "✅ Backend installé"

# 10. Installation du frontend
echo "🎨 Installation du frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Frontend installé"

# 11. Migration SQL
echo "🗄️  Configuration de la base de données..."
read -p "Utilisateur MySQL (défaut: root): " MYSQL_USER
MYSQL_USER=${MYSQL_USER:-root}

read -sp "Mot de passe MySQL: " MYSQL_PASSWORD
echo

read -p "Base de données (défaut: ay_hr): " MYSQL_DB
MYSQL_DB=${MYSQL_DB:-ay_hr}

read -p "Hôte MySQL (défaut: localhost): " MYSQL_HOST
MYSQL_HOST=${MYSQL_HOST:-localhost}

echo "Exécution de la migration V3.0..."
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DB" < backend/migrations/fix_v3_migration.sql

if [ $? -eq 0 ]; then
    echo "✅ Migration SQL réussie"
else
    echo "⚠️  Erreur lors de la migration (peut-être déjà appliquée)"
fi

# 12. Démarrage des services
echo "🚀 Démarrage des services avec PM2..."

# S'assurer que PM2 est complètement arrêté
pm2 kill

sleep 2

# Démarrer
pm2 start ecosystem.config.js

# Sauvegarder
pm2 save

# Configurer le démarrage automatique
pm2 startup || true

echo ""
echo "⏳ Attente du démarrage des services..."
sleep 10

# 13. Vérification
echo ""
echo "📊 État des services:"
pm2 list

echo ""
echo "🔍 Vérification du port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "✅ Backend écoute sur le port 8000"
    lsof -i :8000 | head -2
else
    echo "❌ Backend ne répond pas sur le port 8000"
    echo "Vérifiez les logs: pm2 logs ay-hr-backend"
fi

echo ""
echo "🧪 Test de l'API..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API répond correctement (HTTP $HTTP_CODE)"
else
    echo "⚠️  API répond avec le code HTTP $HTTP_CODE"
fi

echo ""
echo "📋 Logs du backend (dernières lignes):"
pm2 logs ay-hr-backend --lines 15 --nostream

echo ""
echo "✅ ========================================="
echo "✅ INSTALLATION TERMINÉE !"
echo "✅ ========================================="
echo ""
echo "📝 Commandes utiles:"
echo "  - Voir les logs:        pm2 logs"
echo "  - Redémarrer:           pm2 restart all"
echo "  - Arrêter:              pm2 stop all"
echo "  - État des services:    pm2 list"
echo ""
echo "🌐 Accès à l'application:"
echo "  - Frontend: http://192.168.20.53"
echo "  - Backend:  http://192.168.20.53:8000"
echo ""

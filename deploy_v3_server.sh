#!/bin/bash

# Script de déploiement V3.0 pour le serveur (Linux/Ubuntu)
# À placer à la racine du projet sur le serveur

echo "🚀 Démarrage du déploiement V3.0 (Module Salaires)..."

# 1. Aller dans le dossier du projet
# Utiliser le répertoire actuel ou /opt/ay-hr
PROJECT_DIR="/opt/ay-hr"
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
else
    # Fallback au répertoire courant si /opt/ay-hr n'existe pas
    cd "$(dirname "$0")"
fi

# 2. Récupérer les derniers changements
echo "⬇️ Récupération du code depuis GitHub..."
git pull origin main

# 3. Mettre à jour le backend
echo "🐍 Mise à jour du Backend..."
cd backend

# Créer venv s'il n'existe pas
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Creation du virtualenv python..."
    python3 -m venv venv
fi

# Activer venv (supporte venv ou .venv)
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

pip install -r requirements.txt

# 4. Exécuter les migrations BDD
echo "🗄️ Migration de la base de données..."
# On force 'o' pour valider automatiquement
echo "o" | python scripts/migrate_v3_salaires.py

# 5. Importer les IRG (si fichier présent)
if [ -f "data/irg.xlsx" ] || [ -f "../irg.xlsx" ]; then
    echo "📊 Importation du barème IRG..."
    echo "o" | python scripts/import_irg_v3.py
else
    echo "⚠️ Fichier irg.xlsx non trouvé, saut de l'import IRG."
fi

# 6. Mettre à jour le Frontend
echo "⚛️ Mise à jour du Frontend..."
cd ../frontend
npm install
npm run build

# 7. Redémarrer les services (PM2)
echo "🔄 Redémarrage des services..."
pm2 restart all

echo "✅ Déploiement V3.0 terminé avec succès !"

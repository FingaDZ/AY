#!/bin/bash

# Script de déploiement rapide - Fix Pointages Sauvegarde
# Date: 11 décembre 2025
# Commit: 2dc8c40 (envoi de TOUS les jours 1-31)

echo "=========================================="
echo "Déploiement Fix Pointages - v3.5.0"
echo "Commit: 2dc8c40"
echo "=========================================="

cd /opt/ay-hr

echo ""
echo "1. Récupération du code depuis GitHub..."
git fetch origin
git pull origin main

echo ""
echo "2. Rebuild du frontend..."
cd /opt/ay-hr/frontend
npm run build

echo ""
echo "3. Redémarrage des services..."
cd /opt/ay-hr
sudo systemctl restart ayhr-backend
sudo systemctl restart ayhr-frontend

echo ""
echo "4. Vérification du statut..."
sleep 3
echo "Backend:"
sudo systemctl status ayhr-backend --no-pager -l | head -10
echo ""
echo "Frontend:"
sudo systemctl status ayhr-frontend --no-pager -l | head -10

echo ""
echo "=========================================="
echo "✅ Déploiement terminé !"
echo "=========================================="
echo ""
echo "Pour tester:"
echo "1. Ouvrir Pointages dans le frontend"
echo "2. Modifier un jour manuellement"
echo "3. Cliquer sur 'Tout sauvegarder'"
echo "4. Actualiser la page"
echo "5. Vérifier que la modification est bien enregistrée"
echo ""
echo "Logs backend:"
echo "sudo journalctl -u ayhr-backend -n 20 -f"

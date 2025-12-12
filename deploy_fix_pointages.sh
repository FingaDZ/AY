#!/bin/bash

# Script de déploiement v3.5.1 - Correctif Sauvegarde Pointages
# Date: 12 décembre 2025
# Commit: 986723f (Backend + Frontend fix)

echo "=========================================="
echo "Déploiement v3.5.1 - Correctif Pointages"
echo "Commit: 986723f"
echo "Fix: Backend n'envoie que jours non-NULL"
echo "     Frontend n'envoie que jours avec valeur"
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

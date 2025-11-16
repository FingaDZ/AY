#!/bin/bash

#################################################
# Script de démarrage final des services
# AY HR Management System v1.1.4
#################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}==========================================
  Démarrage des Services AY HR v1.1.4
==========================================${NC}\n"

# Arrêter les services
echo -e "${YELLOW}[1/4] Arrêt des services${NC}"
systemctl stop ayhr-backend ayhr-frontend 2>/dev/null || true
echo -e "${GREEN}✓ Services arrêtés${NC}\n"

# Corriger les permissions frontend
echo -e "${YELLOW}[2/4] Correction des permissions${NC}"
chmod +x /opt/ay-hr/frontend/node_modules/.bin/vite
echo -e "${GREEN}✓ Permissions corrigées${NC}\n"

# Démarrer backend
echo -e "${YELLOW}[3/4] Démarrage du backend${NC}"
systemctl start ayhr-backend
sleep 5

if systemctl is-active --quiet ayhr-backend; then
    echo -e "${GREEN}✓ Backend démarré${NC}"
else
    echo -e "${RED}✗ Échec backend${NC}"
    journalctl -u ayhr-backend -n 20 --no-pager
    exit 1
fi

# Démarrer frontend
echo -e "${YELLOW}[4/4] Démarrage du frontend${NC}"
systemctl start ayhr-frontend
sleep 5

if systemctl is-active --quiet ayhr-frontend; then
    echo -e "${GREEN}✓ Frontend démarré${NC}"
else
    echo -e "${RED}✗ Échec frontend${NC}"
    journalctl -u ayhr-frontend -n 20 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}==========================================
  ✓ SERVICES DÉMARRÉS AVEC SUCCÈS !
==========================================${NC}\n"

echo "Statut des services:"
systemctl status ayhr-backend ayhr-frontend --no-pager | grep -E "(Active:|Main PID:)"

echo ""
echo -e "${GREEN}🎉 Application accessible:${NC}"
echo "  🌐 Frontend:  http://192.168.20.53:3000"
echo "  📡 Backend:   http://192.168.20.53:8000/docs"
echo ""
echo -e "${BLUE}Connexion par défaut:${NC}"
echo "  👤 Login:     admin"
echo "  🔑 Password:  admin123"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT: Changez le mot de passe admin !${NC}"
echo ""
echo "Commandes utiles:"
echo "  • Logs backend:   journalctl -u ayhr-backend -f"
echo "  • Logs frontend:  journalctl -u ayhr-frontend -f"
echo "  • Redémarrer:     systemctl restart ayhr-backend ayhr-frontend"
echo "  • Arrêter:        systemctl stop ayhr-backend ayhr-frontend"
echo ""

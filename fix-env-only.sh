#!/bin/bash

#################################################
# Script rapide de correction du fichier .env
# AY HR Management System v1.1.4
#################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKEND_DIR="/opt/ay-hr/backend"

echo -e "${BLUE}Correction rapide du fichier .env backend${NC}\n"

# Arrêter le service backend
systemctl stop ayhr-backend 2>/dev/null || true

# Générer une nouvelle clé secrète
SECRET_KEY=$(openssl rand -hex 32)

# Recréer le .env avec le bon format (mot de passe URL-encodé: ! = %21, @ = %40)
cat > "$BACKEND_DIR/.env" << EOF
# Configuration Backend AY HR - Format Pydantic Settings
DATABASE_URL=mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr
SECRET_KEY=$SECRET_KEY
CORS_ORIGINS=http://localhost:3000,http://192.168.20.53:3000
EOF

echo -e "${GREEN}✓ Fichier .env corrigé${NC}"
echo ""
cat "$BACKEND_DIR/.env"
echo ""

# Redémarrer les services
echo "Redémarrage des services..."
systemctl daemon-reload
systemctl restart ayhr-backend
systemctl restart ayhr-frontend

sleep 3

echo ""
echo -e "${GREEN}✓ Services redémarrés${NC}"
echo ""
systemctl status ayhr-backend ayhr-frontend --no-pager

echo ""
echo "Testez l'accès:"
echo "  Frontend: http://192.168.20.53:3000"
echo "  Backend:  http://192.168.20.53:8000/docs"

#!/bin/bash

#################################################
# Script de correction finale - Installation complète
# AY HR Management System v1.1.4
#################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/opt/ay-hr"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo -e "${BLUE}==========================================
  Correction Finale AY HR v1.1.4
==========================================${NC}\n"

# Arrêter les services
echo -e "${YELLOW}[ÉTAPE 1/5] Arrêt des services${NC}"
echo "-------------------------------------------"
systemctl stop ayhr-backend ayhr-frontend 2>/dev/null || true
echo -e "${GREEN}✓ Services arrêtés${NC}\n"

# Corriger les dépendances Python
echo -e "${YELLOW}[ÉTAPE 2/5] Correction Backend - Dépendances Python${NC}"
echo "-------------------------------------------"
cd "$BACKEND_DIR"
source .venv/bin/activate

echo "Installation des modules manquants..."
pip install --quiet qrcode[pil] pillow email-validator

echo "Correction du fichier .env (URL-encoding du mot de passe)..."
SECRET_KEY=$(openssl rand -hex 32)
cat > "$BACKEND_DIR/.env" << EOF
# Configuration Backend AY HR - Format Pydantic Settings
DATABASE_URL=mysql+pymysql://ayhr_user:%21Yara@2014@localhost/ay_hr
SECRET_KEY=$SECRET_KEY
CORS_ORIGINS=http://localhost:3000,http://192.168.20.53:3000
EOF

echo "Vérification des imports critiques..."
python -c "import qrcode; print('✓ qrcode OK')"
python -c "import email_validator; print('✓ email_validator OK')"
python -c "from config import settings; print('✓ config OK')"
python -c "from main import app; print('✓ main.py OK')"

deactivate
echo -e "${GREEN}✓ Backend corrigé${NC}\n"

# Corriger le service systemd backend
echo -e "${YELLOW}[ÉTAPE 3/5] Correction service systemd backend${NC}"
echo "-------------------------------------------"

cat > /etc/systemd/system/ayhr-backend.service << 'EOF'
[Unit]
Description=AY HR Management - Backend API
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ay-hr/backend
Environment="PATH=/opt/ay-hr/backend/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=/opt/ay-hr/backend"
ExecStart=/opt/ay-hr/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service backend corrigé (utilise uvicorn directement)${NC}\n"

# Corriger le service systemd frontend
echo -e "${YELLOW}[ÉTAPE 4/5] Correction service systemd frontend${NC}"
echo "-------------------------------------------"

cat > /etc/systemd/system/ayhr-frontend.service << 'EOF'
[Unit]
Description=AY HR Management - Frontend Web Interface
After=network.target ayhr-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ay-hr/frontend
Environment="PATH=/usr/bin:/usr/local/bin:/bin"
Environment="NODE_ENV=development"
ExecStart=/usr/bin/npm run dev -- --host 0.0.0.0 --port 3000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Service frontend corrigé${NC}\n"

# Recharger et démarrer
echo -e "${YELLOW}[ÉTAPE 5/5] Démarrage des services${NC}"
echo "-------------------------------------------"

systemctl daemon-reload

echo "Démarrage backend..."
systemctl start ayhr-backend
sleep 5

if systemctl is-active --quiet ayhr-backend; then
    echo -e "${GREEN}✓ Backend démarré avec succès${NC}"
else
    echo -e "${RED}✗ Backend n'a pas démarré${NC}"
    echo "Logs:"
    journalctl -u ayhr-backend -n 20 --no-pager
    exit 1
fi

echo "Démarrage frontend..."
systemctl start ayhr-frontend
sleep 5

if systemctl is-active --quiet ayhr-frontend; then
    echo -e "${GREEN}✓ Frontend démarré avec succès${NC}"
else
    echo -e "${RED}✗ Frontend n'a pas démarré${NC}"
    echo "Logs:"
    journalctl -u ayhr-frontend -n 20 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}==========================================
  ✓ INSTALLATION RÉUSSIE !
==========================================${NC}\n"

echo "Statut des services:"
systemctl status ayhr-backend ayhr-frontend --no-pager | grep -E "(Active:|Main PID:)"

echo ""
echo -e "${GREEN}Accès à l'application:${NC}"
echo "  🌐 Frontend:  http://192.168.20.53:3000"
echo "  📡 Backend:   http://192.168.20.53:8000/docs"
echo ""
echo -e "${BLUE}Connexion par défaut:${NC}"
echo "  👤 Login:     admin"
echo "  🔑 Password:  admin123"
echo ""
echo -e "${YELLOW}⚠ Changez le mot de passe admin immédiatement !${NC}"
echo ""
echo "Commandes utiles:"
echo "  • Logs backend:   journalctl -u ayhr-backend -f"
echo "  • Logs frontend:  journalctl -u ayhr-frontend -f"
echo "  • Redémarrer:     systemctl restart ayhr-backend ayhr-frontend"
echo "  • Arrêter:        systemctl stop ayhr-backend ayhr-frontend"
echo ""

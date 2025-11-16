#!/bin/bash

#################################################
# Script de diagnostic et correction des services
# AY HR Management System v1.1.4
#################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/opt/ay-hr"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo -e "${BLUE}==========================================
  Diagnostic et Correction des Services
  AY HR v1.1.4
==========================================${NC}\n"

# Arrêter les services
echo -e "${YELLOW}[ÉTAPE 1/5] Arrêt des services${NC}"
echo "-------------------------------------------"
systemctl stop ayhr-backend ayhr-frontend 2>/dev/null || true
echo -e "${GREEN}✓ Services arrêtés${NC}\n"

# Diagnostic Backend
echo -e "${YELLOW}[ÉTAPE 2/5] Diagnostic Backend${NC}"
echo "-------------------------------------------"

# Vérifier si start_clean.py existe
if [ ! -f "$BACKEND_DIR/start_clean.py" ]; then
    echo -e "${RED}✗ start_clean.py n'existe pas${NC}"
    echo "Création du fichier start_clean.py..."
    
    cat > "$BACKEND_DIR/start_clean.py" << 'EOF'
#!/usr/bin/env python3
"""
Script de démarrage propre du backend AY HR
Lance l'API FastAPI avec Uvicorn
"""

import os
import sys
import uvicorn

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("🚀 Démarrage du serveur backend AY HR...")
    print(f"📁 Répertoire de travail: {backend_dir}")
    
    # Changer vers le répertoire backend
    os.chdir(backend_dir)
    
    # Démarrer Uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Pas de reload en production
        log_level="info"
    )
EOF
    chmod +x "$BACKEND_DIR/start_clean.py"
    echo -e "${GREEN}✓ start_clean.py créé${NC}"
else
    echo -e "${GREEN}✓ start_clean.py existe${NC}"
fi

# Vérifier l'environnement virtuel
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo -e "${RED}✗ Environnement virtuel manquant${NC}"
    echo "Création de l'environnement virtuel..."
    cd "$BACKEND_DIR"
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    echo -e "${GREEN}✓ Environnement virtuel créé${NC}"
else
    echo -e "${GREEN}✓ Environnement virtuel OK${NC}"
fi

# Vérifier le fichier .env
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${RED}✗ Fichier .env backend manquant${NC}"
    echo "Création du fichier .env..."
    
    SECRET_KEY=$(openssl rand -hex 32)
    
    cat > "$BACKEND_DIR/.env" << EOF
# Configuration Backend AY HR
DATABASE_URL=mysql+pymysql://ayhr_user:!Yara@2014@localhost/ay_hr
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000","http://192.168.20.53:3000"]
EOF
    echo -e "${GREEN}✓ Fichier .env créé${NC}"
else
    echo -e "${GREEN}✓ Fichier .env existe${NC}"
fi

# Tester le backend manuellement
echo "Test du backend..."
cd "$BACKEND_DIR"
"$BACKEND_DIR/.venv/bin/python" -c "import sys; print(f'Python: {sys.version}')"
"$BACKEND_DIR/.venv/bin/python" -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')" 2>&1
"$BACKEND_DIR/.venv/bin/python" -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')" 2>&1

# Tester l'import de main
echo "Test de l'import main.py..."
"$BACKEND_DIR/.venv/bin/python" -c "from main import app; print('✓ Import main.py OK')" 2>&1 || {
    echo -e "${RED}✗ Erreur lors de l'import de main.py${NC}"
    echo "Logs détaillés:"
    "$BACKEND_DIR/.venv/bin/python" "$BACKEND_DIR/start_clean.py" 2>&1 | head -20
    exit 1
}

echo -e "${GREEN}✓ Backend diagnostiqué${NC}\n"

# Diagnostic Frontend
echo -e "${YELLOW}[ÉTAPE 3/5] Diagnostic Frontend${NC}"
echo "-------------------------------------------"

# Vérifier node_modules
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${RED}✗ node_modules manquant${NC}"
    echo "Installation des dépendances..."
    cd "$FRONTEND_DIR"
    npm install
    echo -e "${GREEN}✓ Dépendances installées${NC}"
else
    echo -e "${GREEN}✓ node_modules OK${NC}"
fi

# Vérifier le fichier .env
if [ ! -f "$FRONTEND_DIR/.env" ]; then
    echo -e "${RED}✗ Fichier .env frontend manquant${NC}"
    echo "Création du fichier .env..."
    
    cat > "$FRONTEND_DIR/.env" << EOF
VITE_API_URL=http://192.168.20.53:8000
VITE_APP_NAME=AY HR Management
VITE_APP_VERSION=1.1.4
EOF
    echo -e "${GREEN}✓ Fichier .env créé${NC}"
else
    echo -e "${GREEN}✓ Fichier .env existe${NC}"
fi

# Vérifier les permissions npm
echo "Vérification des permissions npm..."
which npm
npm --version

echo -e "${GREEN}✓ Frontend diagnostiqué${NC}\n"

# Corriger les services systemd
echo -e "${YELLOW}[ÉTAPE 4/5] Correction des services systemd${NC}"
echo "-------------------------------------------"

# Service Backend
cat > /etc/systemd/system/ayhr-backend.service << EOF
[Unit]
Description=AY HR Management - Backend API
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$BACKEND_DIR/.venv/bin/python $BACKEND_DIR/start_clean.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Service Frontend
cat > /etc/systemd/system/ayhr-frontend.service << EOF
[Unit]
Description=AY HR Management - Frontend Web Interface
After=network.target ayhr-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=$FRONTEND_DIR
Environment="PATH=/usr/bin:/bin:/usr/local/bin"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm run dev -- --host 0.0.0.0 --port 3000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo -e "${GREEN}✓ Services systemd corrigés${NC}\n"

# Démarrer les services
echo -e "${YELLOW}[ÉTAPE 5/5] Démarrage des services${NC}"
echo "-------------------------------------------"

echo "Démarrage du backend..."
systemctl start ayhr-backend
sleep 3

if systemctl is-active --quiet ayhr-backend; then
    echo -e "${GREEN}✓ Backend démarré${NC}"
else
    echo -e "${RED}✗ Échec démarrage backend${NC}"
    echo "Logs backend:"
    journalctl -u ayhr-backend -n 30 --no-pager
    exit 1
fi

echo "Démarrage du frontend..."
systemctl start ayhr-frontend
sleep 3

if systemctl is-active --quiet ayhr-frontend; then
    echo -e "${GREEN}✓ Frontend démarré${NC}"
else
    echo -e "${RED}✗ Échec démarrage frontend${NC}"
    echo "Logs frontend:"
    journalctl -u ayhr-frontend -n 30 --no-pager
    exit 1
fi

echo ""
echo -e "${GREEN}==========================================
  ✓ CORRECTION TERMINÉE AVEC SUCCÈS
==========================================${NC}\n"

echo "Statut des services:"
systemctl status ayhr-backend ayhr-frontend --no-pager

echo ""
echo "Informations d'accès:"
echo "  • Frontend:  http://192.168.20.53:3000"
echo "  • Backend:   http://192.168.20.53:8000/docs"
echo "  • Login:     admin"
echo "  • Password:  admin123"
echo ""
echo "Commandes utiles:"
echo "  • Logs backend:   journalctl -u ayhr-backend -f"
echo "  • Logs frontend:  journalctl -u ayhr-frontend -f"
echo "  • Redémarrer:     systemctl restart ayhr-backend ayhr-frontend"
echo ""

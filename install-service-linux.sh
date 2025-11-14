#!/bin/bash
# ============================================================================
# Installation des Services Systemd - AY HR Management
# Pour Linux (Ubuntu/Debian)
# ============================================================================

echo ""
echo "========================================"
echo " Installation Services Systemd"
echo " AIRBAND HR v1.1.4"
echo "========================================"
echo ""

# Vérifier sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script nécessite sudo"
    echo "Exécutez: sudo ./install-service-linux.sh"
    exit 1
fi

# Chemins
INSTALL_PATH=$(dirname "$(readlink -f "$0")")
BACKEND_PATH="$INSTALL_PATH/backend"
FRONTEND_PATH="$INSTALL_PATH/frontend"
PYTHON_VENV="$BACKEND_PATH/.venv/bin/python"
SYSTEMD_PATH="/etc/systemd/system"

# Obtenir l'utilisateur qui a lancé sudo
if [ -n "$SUDO_USER" ]; then
    REAL_USER=$SUDO_USER
else
    REAL_USER=$(whoami)
fi

echo "[1/4] Création des fichiers de service..."
echo ""

# ============================================================================
# Service Backend
# ============================================================================
echo -n "  → Création de ayhr-backend.service... "
cat > $SYSTEMD_PATH/ayhr-backend.service << EOF
[Unit]
Description=AY HR Management - Backend API
After=network.target mariadb.service
Wants=mariadb.service

[Service]
Type=simple
User=$REAL_USER
WorkingDirectory=$BACKEND_PATH
Environment="PATH=$BACKEND_PATH/.venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PYTHON_VENV -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_PATH/logs/backend-service.log
StandardError=append:$INSTALL_PATH/logs/backend-service-error.log

[Install]
WantedBy=multi-user.target
EOF
echo "OK"

# ============================================================================
# Service Frontend
# ============================================================================
echo -n "  → Création de ayhr-frontend.service... "
cat > $SYSTEMD_PATH/ayhr-frontend.service << EOF
[Unit]
Description=AY HR Management - Frontend Web
After=network.target ayhr-backend.service
Wants=ayhr-backend.service

[Service]
Type=simple
User=$REAL_USER
WorkingDirectory=$FRONTEND_PATH
Environment="PATH=/usr/bin:/bin:/usr/local/bin"
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_PATH/logs/frontend-service.log
StandardError=append:$INSTALL_PATH/logs/frontend-service-error.log

[Install]
WantedBy=multi-user.target
EOF
echo "OK"

echo ""
echo "[2/4] Configuration des permissions..."
echo ""

# Créer le dossier logs avec les bonnes permissions
mkdir -p $INSTALL_PATH/logs
chown -R $REAL_USER:$REAL_USER $INSTALL_PATH/logs
chmod 755 $INSTALL_PATH/logs

echo -n "  → Permissions configurées... "
echo "OK"

echo ""
echo "[3/4] Activation des services..."
echo ""

# Recharger systemd
echo -n "  → Rechargement de systemd... "
systemctl daemon-reload
echo "OK"

# Activer les services (démarrage automatique)
echo -n "  → Activation de ayhr-backend... "
systemctl enable ayhr-backend.service
echo "OK"

echo -n "  → Activation de ayhr-frontend... "
systemctl enable ayhr-frontend.service
echo "OK"

echo ""
echo "[4/4] Démarrage des services..."
echo ""

# Démarrer les services
echo -n "  → Démarrage de ayhr-backend... "
systemctl start ayhr-backend.service
sleep 3
echo "OK"

echo -n "  → Démarrage de ayhr-frontend... "
systemctl start ayhr-frontend.service
sleep 3
echo "OK"

echo ""
echo "Vérification des services..."
echo ""

# Vérifier le statut
BACKEND_STATUS=$(systemctl is-active ayhr-backend.service)
FRONTEND_STATUS=$(systemctl is-active ayhr-frontend.service)

if [ "$BACKEND_STATUS" == "active" ]; then
    echo "  ✓ ayhr-backend  : $BACKEND_STATUS"
else
    echo "  ✗ ayhr-backend  : $BACKEND_STATUS"
fi

if [ "$FRONTEND_STATUS" == "active" ]; then
    echo "  ✓ ayhr-frontend : $FRONTEND_STATUS"
else
    echo "  ✗ ayhr-frontend : $FRONTEND_STATUS"
fi

echo ""
echo "========================================"
echo " Services Systemd Installés!"
echo "========================================"
echo ""
echo "Les services démarreront automatiquement au boot"
echo ""
echo "Gestion des services:"
echo "  Démarrer  : sudo systemctl start ayhr-backend ayhr-frontend"
echo "  Arrêter   : sudo systemctl stop ayhr-backend ayhr-frontend"
echo "  Redémarrer: sudo systemctl restart ayhr-backend ayhr-frontend"
echo "  Statut    : sudo systemctl status ayhr-backend ayhr-frontend"
echo "  Logs      : sudo journalctl -u ayhr-backend -f"
echo "              sudo journalctl -u ayhr-frontend -f"
echo ""
echo "Accès à l'application:"
echo "  Interface Web: http://localhost:3000"
echo ""

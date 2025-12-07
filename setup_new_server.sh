#!/bin/bash

# ==============================================================================
# AY HR System - Script d'Installation Nouveau Serveur V3.0
# Cible: Ubuntu 22.04 LTS (IP: 192.168.20.55)
# Auteur: Antigravity AI
# ==============================================================================

APP_DIR="/opt/ay-hr"
REPO_URL="https://github.com/FingaDZ/AY.git"
LOG_FILE="/var/log/ayhr_install_v3.log"
OLD_SERVER_IP="192.168.20.53"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Fonctions de log
log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; echo "[$(date +'%H:%M:%S')] $1" >> "$LOG_FILE"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; echo "[INFO] $1" >> "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; echo "[WARN] $1" >> "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; echo "[ERROR] $1" >> "$LOG_FILE"; exit 1; }

# Vérification root
if [ "$EUID" -ne 0 ]; then error "Ce script doit être exécuté en tant que root"; fi

clear
echo -e "${BLUE}"
cat <<"EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       AY HR SYSTEM - INSTALLATION NOUVEAU SERVEUR         ║
║                VERSION 3.0 (Clean Install)                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log "Démarrage de l'installation..."
log "Log file: $LOG_FILE"

# 1. Mise à jour du système
# ==============================================================================
info "[1/6] Mise à jour du système..."
apt update
DEBIAN_FRONTEND=noninteractive apt full-upgrade -y

# 2. Installation des dépendances
# ==============================================================================
info "[2/6] Installation des dépendances..."
apt install -y git curl wget build-essential \
    python3.11 python3.11-venv python3.11-dev \
    mariadb-server mariadb-client \
    nginx certbot python3-certbot-nginx \
    acl htop net-tools unzip

# Node.js 20 LTS
if ! command -v node &> /dev/null; then
    info "Installation Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# 3. Configuration Base de Données
# ==============================================================================
info "[3/6] Configuration MariaDB..."
systemctl start mariadb
systemctl enable mariadb

# Sécurisation basique et création DB
mysql -e "CREATE DATABASE IF NOT EXISTS ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'ayhr_user'@'localhost' IDENTIFIED BY '!Yara@2014';"
mysql -e "GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

log "Base de données 'ay_hr' prête."

# 4. Installation de l'Application
# ==============================================================================
info "[4/6] Installation Application..."

# Création dossier
mkdir -p "$APP_DIR"
cd "$APP_DIR" || error "Impossible d'accéder à $APP_DIR"

# Clone/Pull
if [ -d ".git" ]; then
    info "Mise à jour du dépôt existant..."
    git pull origin main
else
    info "Clonage du dépôt..."
    git clone "$REPO_URL" .
fi

# Permissions
chown -R root:root "$APP_DIR"
chmod +x *.sh

# Backend Setup
info "Installation Backend..."
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install 'bcrypt<4.0.0' --force-reinstall
deactivate

# Configuration Backend (.env)
if [ ! -f .env ]; then
    info "Création configuration Backend..."
    cat > .env << EOF
DATABASE_URL=mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr
SECRET_KEY=$(openssl rand -hex 32)
# CORS: Autoriser localhost et l'IP du serveur (à détecter)
CORS_ORIGINS=http://localhost:3000,http://$(hostname -I | awk '{print $1}'):3000
APP_NAME=AY HR Management v3.0
DEBUG=False
EOF
fi
cd ..

# Frontend Setup
info "Installation Frontend..."
cd frontend
npm install
npm run build

# Configuration Frontend (.env)
if [ ! -f .env ]; then
    cat > .env << EOF
VITE_API_URL=http://$(hostname -I | awk '{print $1}'):8000
EOF
fi
cd ..

# 5. Configuration Services Systemd
# ==============================================================================
info "[5/6] Configuration Services..."

# Backend Service
cat > /etc/systemd/system/ayhr-backend.service << EOF
[Unit]
Description=AY HR Management - Backend API
After=network.target mariadb.service
Wants=mariadb.service

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR/backend
Environment="PATH=$APP_DIR/backend/venv/bin"
ExecStart=$APP_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Frontend Service (Serve avec 'serve' pour la prod ou 'preview')
npm install -g serve
cat > /etc/systemd/system/ayhr-frontend.service << EOF
[Unit]
Description=AY HR Management - Frontend
After=network.target ayhr-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR/frontend
# Utilisation de 'serve' pour servir le build de production (plus léger que vite preview)
ExecStart=/usr/bin/npx serve -s dist -l 3000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ayhr-backend ayhr-frontend

# 6. Migration des Données
# ==============================================================================
info "[6/6] Migration des Données..."

echo ""
warn "Voulez-vous importer les données depuis l'ancien serveur ($OLD_SERVER_IP) ?"
read -p "Tapez 'oui' pour importer, sinon Entrée pour continuer (installation vierge): " IMPORT_CHOICE

if [[ "$IMPORT_CHOICE" == "oui" ]]; then
    
    warn "⚠️  Assurez-vous que l'ancien serveur est accessible via SSH."
    read -p "Utilisateur SSH ancien serveur (ex: root): " SSH_USER
    SSH_USER=${SSH_USER:-root}
    
    DUMP_FILE="migration_dump_$(date +%Y%m%d).sql"
    
    info "Récupération du dump depuis $OLD_SERVER_IP..."
    
    # Commande pour dumper à distance et piper directement ici
    ssh "$SSH_USER@$OLD_SERVER_IP" "mysqldump -u root -p ay_hr --single-transaction --quick --lock-tables=false" > "$DUMP_FILE"
    
    if [ -s "$DUMP_FILE" ]; then
        info "Dump récupéré avec succès ($(du -h $DUMP_FILE | cut -f1)). Importation..."
        mysql -u root ay_hr < "$DUMP_FILE"
        success "Données importées avec succès !"
        
        # Migrations éventuelles (si la structure a changé)
        # Ici on suppose que le code est à jour avec la DB importée
    else
        error "Échec de récupération du dump (fichier vide ou connexion refusée)"
    fi
else
    info "Installation vierge (pas d'import de données)."
    # Initialisation DB vierge si nécessaire (via scripts Python ou Alembic)
fi

# Démarrage final
systemctl restart ayhr-backend ayhr-frontend

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅ INSTALLATION TERMINÉE AVEC SUCCÈS           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Backend:  http://$(hostname -I | awk '{print $1}'):8000"
echo -e "Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo ""

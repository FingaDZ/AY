#!/bin/bash

# AY HR System - Automated Installer
# Tested on Ubuntu 22.04 LTS

APP_DIR="/opt/ay-hr"
REPO_URL="https://github.com/FingaDZ/AY.git"
LOG_FILE="/var/log/ayhr_install.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
    echo "[$(date +'%H:%M:%S')] $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    echo "[ERROR] $1" >> "$LOG_FILE"
    exit 1
}

# Check root
if [ "$EUID" -ne 0 ]; then 
  error "Please run as root"
fi

log "Starting Installation..."

# 1. System Updates & Dependencies
log "Updating system and installing dependencies..."
apt update && apt upgrade -y
apt install -y git curl wget build-essential python3.11 python3.11-venv python3.11-dev mariadb-server mariadb-client

# Node.js 20
if ! command -v node &> /dev/null; then
    log "Installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# 2. Database Setup
log "Configuring Database..."
systemctl start mariadb
systemctl enable mariadb

# Check if DB exists
if ! mysql -e "USE ay_hr" 2>/dev/null; then
    log "Creating Database and User..."
    mysql -e "CREATE DATABASE ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    mysql -e "CREATE USER IF NOT EXISTS 'ayhr_user'@'localhost' IDENTIFIED BY '!Yara@2014';"
    mysql -e "GRANT ALL PRIVILEGES ON ay_hr.* TO 'ayhr_user'@'localhost';"
    mysql -e "FLUSH PRIVILEGES;"
else
    log "Database already exists, skipping creation."
fi

# 3. Application Setup
log "Setting up Application..."
if [ -d "$APP_DIR" ]; then
    log "Directory exists, pulling latest changes..."
    cd "$APP_DIR" && git pull
else
    log "Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR" || error "Failed to access app directory"

# Backend Setup
log "Setting up Backend..."
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Fix bcrypt if needed
pip install 'bcrypt<4.0.0' --force-reinstall

# Create .env if missing
if [ ! -f .env ]; then
    log "Creating backend .env..."
    cat > .env << EOF
DATABASE_URL=mysql+pymysql://ayhr_user:%21Yara%402014@localhost/ay_hr
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=http://localhost:3000,http://192.168.20.53:3000
APP_NAME=AY HR Management
DEBUG=False
EOF
fi
deactivate
cd ..

# Frontend Setup
log "Setting up Frontend..."
cd frontend
npm install
npm run build

# Create .env if missing
if [ ! -f .env ]; then
    log "Creating frontend .env..."
    echo "VITE_API_URL=http://localhost:8000" > .env
fi
cd ..

# 4. Services Setup
log "Configuring Systemd Services..."

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
Environment="PATH=$APP_DIR/backend/.venv/bin"
ExecStart=$APP_DIR/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Frontend Service
cat > /etc/systemd/system/ayhr-frontend.service << EOF
[Unit]
Description=AY HR Management - Frontend
After=network.target ayhr-backend.service
Wants=ayhr-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR/frontend
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 3000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 5. Finalize
log "Starting Services..."
systemctl daemon-reload
systemctl enable ayhr-backend ayhr-frontend
systemctl restart ayhr-backend ayhr-frontend

# Permissions
chmod +x "$APP_DIR"/*.sh

log "Installation Complete! 🚀"
echo -e "${GREEN}Access Frontend: http://$(hostname -I | awk '{print $1}'):3000${NC}"
echo -e "${GREEN}Access Backend: http://$(hostname -I | awk '{print $1}'):8000/docs${NC}"

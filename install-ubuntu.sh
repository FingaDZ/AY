#!/bin/bash
# Script d'installation automatique AY HR System v3.6.0
# Pour Ubuntu 22.04 LTS / 24.04 LTS
# Usage: sudo bash install-ubuntu.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables par défaut
DEFAULT_INSTALL_DIR="/opt/ay-hr"
DEFAULT_DB_NAME="ay_hr"
DEFAULT_DB_USER="ayhr_user"
DEFAULT_BACKEND_PORT="8000"
DEFAULT_FRONTEND_PORT="3000"

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Installation AY HR System v3.6.0 - Ubuntu    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Vérification root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Ce script doit être exécuté en tant que root${NC}"
    echo "Usage: sudo bash install-ubuntu.sh"
    exit 1
fi

# Configuration interactive
echo -e "${YELLOW}📋 Configuration de l'installation${NC}"
echo ""

read -p "📁 Répertoire d'installation [$DEFAULT_INSTALL_DIR]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_INSTALL_DIR}

read -p "🗄️  Nom de la base de données [$DEFAULT_DB_NAME]: " DB_NAME
DB_NAME=${DB_NAME:-$DEFAULT_DB_NAME}

read -p "👤 Utilisateur MySQL [$DEFAULT_DB_USER]: " DB_USER
DB_USER=${DB_USER:-$DEFAULT_DB_USER}

read -sp "🔐 Mot de passe MySQL (requis): " DB_PASSWORD
echo ""
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}❌ Le mot de passe est obligatoire${NC}"
    exit 1
fi

read -p "🚀 Port backend [$DEFAULT_BACKEND_PORT]: " BACKEND_PORT
BACKEND_PORT=${BACKEND_PORT:-$DEFAULT_BACKEND_PORT}

read -p "🌐 Port frontend [$DEFAULT_FRONTEND_PORT]: " FRONTEND_PORT
FRONTEND_PORT=${FRONTEND_PORT:-$DEFAULT_FRONTEND_PORT}

read -p "👨‍💼 Email admin par défaut: " ADMIN_EMAIL
if [ -z "$ADMIN_EMAIL" ]; then
    echo -e "${RED}❌ L'email admin est obligatoire${NC}"
    exit 1
fi

read -sp "🔐 Mot de passe admin: " ADMIN_PASSWORD
echo ""
if [ -z "$ADMIN_PASSWORD" ]; then
    echo -e "${RED}❌ Le mot de passe admin est obligatoire${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Configuration enregistrée${NC}"
echo ""

# Résumé
echo -e "${BLUE}📝 Résumé de la configuration:${NC}"
echo "  Installation: $INSTALL_DIR"
echo "  Base de données: $DB_NAME"
echo "  Utilisateur MySQL: $DB_USER"
echo "  Port backend: $BACKEND_PORT"
echo "  Port frontend: $FRONTEND_PORT"
echo "  Admin: $ADMIN_EMAIL"
echo ""

read -p "Continuer? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Installation annulée${NC}"
    exit 1
fi

# 1. Mise à jour du système
echo ""
echo -e "${YELLOW}📦 1/10 Mise à jour du système...${NC}"
apt update && apt upgrade -y

# 2. Installation dépendances système
echo ""
echo -e "${YELLOW}🔧 2/10 Installation des dépendances système...${NC}"
apt install -y git curl wget build-essential software-properties-common

# 3. Installation Python 3.11+
echo ""
echo -e "${YELLOW}🐍 3/10 Installation Python 3.11...${NC}"
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# 4. Installation Node.js 20 LTS
echo ""
echo -e "${YELLOW}📦 4/10 Installation Node.js 20 LTS...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# 5. Installation MySQL/MariaDB
echo ""
echo -e "${YELLOW}🗄️  5/10 Installation MySQL Server...${NC}"
apt install -y mysql-server mysql-client

# Démarrage MySQL
systemctl start mysql
systemctl enable mysql

# 6. Configuration base de données
echo ""
echo -e "${YELLOW}🔐 6/10 Configuration de la base de données...${NC}"

mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';"
mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

echo -e "${GREEN}✅ Base de données créée: $DB_NAME${NC}"

# 7. Clonage du projet
echo ""
echo -e "${YELLOW}📥 7/10 Clonage du projet AY HR...${NC}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  Le répertoire $INSTALL_DIR existe déjà${NC}"
    read -p "Supprimer et réinstaller? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        echo -e "${RED}❌ Installation annulée${NC}"
        exit 1
    fi
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone depuis GitHub (à adapter avec votre repo)
echo "ℹ️  Veuillez fournir l'URL du repository GitHub:"
read -p "URL: " GITHUB_URL
git clone "$GITHUB_URL" .

# 8. Installation Backend
echo ""
echo -e "${YELLOW}⚙️  8/10 Configuration du backend...${NC}"

cd "$INSTALL_DIR/backend"

# Création environnement virtuel Python
python3.11 -m venv venv
source venv/bin/activate

# Installation dépendances Python
pip install --upgrade pip
pip install -r requirements.txt

# Configuration .env
cat > .env << EOL
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
CORS_ORIGINS=http://localhost:${FRONTEND_PORT},http://localhost
ATTENDANCE_API_URL=http://localhost:8000/api
ATTENDANCE_API_TIMEOUT=30
EOL

echo -e "${GREEN}✅ Backend configuré${NC}"

# Import schéma base de données
echo "📊 Import du schéma de la base de données..."
if [ -f "../database/schema.sql" ]; then
    mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < ../database/schema.sql
    echo -e "${GREEN}✅ Schéma importé${NC}"
else
    echo -e "${YELLOW}⚠️  Fichier schema.sql non trouvé${NC}"
fi

# Création utilisateur admin
echo "👤 Création de l'utilisateur administrateur..."
python3 << EOF
import sys
sys.path.insert(0, '.')
from passlib.context import CryptContext
import pymysql

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("$ADMIN_PASSWORD")

conn = pymysql.connect(
    host='localhost',
    user='$DB_USER',
    password='$DB_PASSWORD',
    database='$DB_NAME'
)
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO users (email, nom, prenom, password_hash, role, actif)
    VALUES (%s, 'Admin', 'System', %s, 'Admin', 1)
    ON DUPLICATE KEY UPDATE password_hash=%s
""", ("$ADMIN_EMAIL", hashed_password, hashed_password))
conn.commit()
cursor.close()
conn.close()
print("✅ Utilisateur admin créé")
EOF

# 9. Installation Frontend
echo ""
echo -e "${YELLOW}🌐 9/10 Configuration du frontend...${NC}"

cd "$INSTALL_DIR/frontend"

# Installation dépendances Node.js
npm install

# Configuration environnement
cat > .env << EOL
VITE_API_URL=http://localhost:${BACKEND_PORT}
EOL

# Build frontend
npm run build

echo -e "${GREEN}✅ Frontend configuré et compilé${NC}"

# 10. Configuration systemd services
echo ""
echo -e "${YELLOW}🔧 10/10 Configuration des services système...${NC}"

# Service backend
cat > /etc/systemd/system/ayhr-backend.service << EOL
[Unit]
Description=AY HR Management - Backend API
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}/backend
Environment="PATH=${INSTALL_DIR}/backend/venv/bin"
ExecStart=${INSTALL_DIR}/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Service frontend (optionnel, pour dev)
cat > /etc/systemd/system/ayhr-frontend.service << EOL
[Unit]
Description=AY HR Management - Frontend Dev Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}/frontend
ExecStart=/usr/bin/npm run dev -- --host 0.0.0.0 --port ${FRONTEND_PORT}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd
systemctl daemon-reload

# Démarrage services
systemctl start ayhr-backend
systemctl enable ayhr-backend

echo -e "${GREEN}✅ Service backend démarré${NC}"

# Configuration Nginx (optionnel)
echo ""
read -p "🌐 Installer et configurer Nginx? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    apt install -y nginx
    
    cat > /etc/nginx/sites-available/ayhr << EOL
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root ${INSTALL_DIR}/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:${BACKEND_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOL

    ln -sf /etc/nginx/sites-available/ayhr /etc/nginx/sites-enabled/
    nginx -t && systemctl restart nginx
    systemctl enable nginx
    
    echo -e "${GREEN}✅ Nginx configuré${NC}"
fi

# Résumé final
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ Installation terminée avec succès!      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Informations importantes:${NC}"
echo ""
echo "📁 Répertoire: $INSTALL_DIR"
echo "🗄️  Base de données: $DB_NAME"
echo "👤 Admin: $ADMIN_EMAIL"
echo ""
echo "🌐 URLs d'accès:"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  Frontend: http://$(hostname -I | awk '{print $1}')"
    echo "  Backend API: http://$(hostname -I | awk '{print $1}')/api"
else
    echo "  Backend API: http://$(hostname -I | awk '{print $1}'):$BACKEND_PORT"
    echo "  Frontend: npm run dev dans $INSTALL_DIR/frontend"
fi
echo ""
echo "🔧 Commandes utiles:"
echo "  Logs backend:  journalctl -u ayhr-backend -f"
echo "  Restart:       systemctl restart ayhr-backend"
echo "  Status:        systemctl status ayhr-backend"
echo ""
echo -e "${YELLOW}⚠️  Pensez à configurer le pare-feu si nécessaire:${NC}"
echo "  ufw allow 80/tcp"
echo "  ufw allow 443/tcp"
echo ""

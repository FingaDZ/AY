#!/bin/bash

##############################################
# Script d'Installation Complète AY HR
# Ubuntu 22.04 - Version Automatique
##############################################

set -e  # Arrêter en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuration
DB_NAME="ay_hr"
DB_USER="ayhr_user"
DB_PASS="!Yara@2014"
SERVER_IP="192.168.20.53"
INSTALL_DIR="/opt/ay-hr"

echo -e "${BLUE}=========================================="
echo "  Installation Complète AY HR v1.1.4"
echo "  Ubuntu 22.04 LTS"
echo "==========================================${NC}\n"

##############################################
# Fonction: Afficher l'étape
##############################################
step() {
    echo -e "\n${BLUE}[ÉTAPE $1/$2]${NC} ${GREEN}$3${NC}"
    echo "-------------------------------------------"
}

##############################################
# Fonction: Succès
##############################################
success() {
    echo -e "${GREEN}✓${NC} $1"
}

##############################################
# Fonction: Erreur
##############################################
error() {
    echo -e "${RED}✗${NC} $1"
}

##############################################
# Fonction: Avertissement
##############################################
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

##############################################
# ÉTAPE 1: Vérification des prérequis
##############################################
step 1 10 "Vérification des prérequis"

# Vérifier si on est root
if [ "$EUID" -ne 0 ]; then 
    error "Ce script doit être exécuté en tant que root"
    echo "Utilisez: sudo $0"
    exit 1
fi

success "Exécution en tant que root"

# Vérifier la connexion Internet
if ping -c 1 google.com &> /dev/null; then
    success "Connexion Internet OK"
else
    warning "Pas de connexion Internet détectée"
fi

##############################################
# ÉTAPE 2: Mise à jour du système
##############################################
step 2 10 "Mise à jour du système"

apt update -qq
apt install -y apt-transport-https ca-certificates curl wget git software-properties-common
success "Système mis à jour"

##############################################
# ÉTAPE 3: Installation de Python 3.11
##############################################
step 3 10 "Installation de Python 3.11"

if ! command -v python3.11 &> /dev/null; then
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update -qq
    apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    success "Python 3.11 installé"
else
    success "Python 3.11 déjà installé"
fi

python3 --version

##############################################
# ÉTAPE 4: Installation de Node.js 20 LTS
##############################################
step 4 10 "Installation de Node.js 20 LTS"

# Corriger apt_pkg si nécessaire
apt install --reinstall python3-apt -y 2>/dev/null || true

# Supprimer les anciennes versions
apt remove -y nodejs nodejs-doc libnode72 2>/dev/null || true
apt autoremove -y

# Installer Node.js 20
if ! command -v node &> /dev/null || [[ $(node --version | cut -d'.' -f1 | sed 's/v//') -lt 18 ]]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
    success "Node.js 20 installé"
else
    success "Node.js $(node --version) déjà installé"
fi

node --version
npm --version

##############################################
# ÉTAPE 5: Installation de MariaDB
##############################################
step 5 10 "Installation et Configuration de MariaDB"

if ! command -v mysql &> /dev/null; then
    apt install -y mariadb-server mariadb-client
    systemctl start mariadb
    systemctl enable mariadb
    success "MariaDB installé et démarré"
else
    success "MariaDB déjà installé"
    systemctl start mariadb 2>/dev/null || true
fi

##############################################
# ÉTAPE 6: Configuration de la base de données
##############################################
step 6 10 "Configuration de la base de données"

# Créer la base de données
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

success "Base de données ${DB_NAME} créée"
success "Utilisateur ${DB_USER} configuré"

##############################################
# ÉTAPE 7: Vérification du projet
##############################################
step 7 10 "Vérification de la structure du projet"

if [ ! -d "$INSTALL_DIR" ]; then
    error "Le dossier $INSTALL_DIR n'existe pas"
    echo "Clonez d'abord le projet avec:"
    echo "git clone https://github.com/FingaDZ/AY.git $INSTALL_DIR"
    exit 1
fi

cd "$INSTALL_DIR"
success "Projet trouvé dans $INSTALL_DIR"

# Rendre les scripts exécutables
chmod +x *.sh 2>/dev/null || true
success "Scripts rendus exécutables"

##############################################
# ÉTAPE 8: Initialisation des tables SQL
##############################################
step 8 10 "Initialisation des tables de la base de données"

if [ -f "$INSTALL_DIR/database/create_database.sql" ]; then
    mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$INSTALL_DIR/database/create_database.sql"
    success "Tables créées depuis create_database.sql"
else
    warning "Fichier create_database.sql non trouvé"
fi

# Vérifier les tables créées
TABLE_COUNT=$(mysql -u "$DB_USER" -p"$DB_PASS" -e "USE $DB_NAME; SHOW TABLES;" | wc -l)
success "Nombre de tables créées: $((TABLE_COUNT - 1))"

##############################################
# ÉTAPE 9: Configuration Backend
##############################################
step 9 10 "Configuration du Backend (Python/FastAPI)"

cd "$INSTALL_DIR/backend"

# Créer l'environnement virtuel
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    success "Environnement virtuel créé"
else
    success "Environnement virtuel existe déjà"
fi

# Activer et installer les dépendances
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
success "Dépendances Python installées"

# Générer SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# Créer le fichier .env
# Créer le fichier .env avec le bon format Pydantic (URL-encode le mot de passe)
# ! devient %21, @ devient %40
DB_PASS_ENCODED="%21Yara%402014"
cat > .env <<EOF
# Configuration Backend AY HR - Format Pydantic Settings
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASS_ENCODED}@localhost/${DB_NAME}
SECRET_KEY=${SECRET_KEY}
CORS_ORIGINS=http://localhost:3000,http://${SERVER_IP}:3000
EOF

success "Fichier .env backend créé"

# Initialiser les données (utilisateur admin, etc.)
if [ -f "init_sample_data.py" ]; then
    python3 init_sample_data.py 2>/dev/null || warning "Erreur lors de l'initialisation des données"
    success "Données d'initialisation créées (utilisateur admin)"
else
    warning "Script init_sample_data.py non trouvé"
fi

deactivate

##############################################
# ÉTAPE 10: Configuration Frontend
##############################################
step 10 10 "Configuration du Frontend (React/Vite)"

cd "$INSTALL_DIR/frontend"

# Installer les dépendances
npm install
success "Dépendances Node.js installées"

# Créer le fichier .env
cat > .env <<EOF
VITE_API_URL=http://${SERVER_IP}:8000
EOF

success "Fichier .env frontend créé"

##############################################
# ÉTAPE 11: Configuration des services systemd
##############################################
echo -e "\n${BLUE}[ÉTAPE BONUS]${NC} ${GREEN}Configuration des services systemd${NC}"
echo "-------------------------------------------"

# Créer le service backend
cat > /etc/systemd/system/ayhr-backend.service <<EOF
[Unit]
Description=AY HR Management - Backend API
After=network.target mariadb.service
Wants=mariadb.service

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}/backend
Environment="PATH=${INSTALL_DIR}/backend/.venv/bin"
ExecStart=${INSTALL_DIR}/backend/.venv/bin/python start_clean.py
Restart=always
RestartSec=10
StandardOutput=append:${INSTALL_DIR}/logs/backend.log
StandardError=append:${INSTALL_DIR}/logs/backend.log

[Install]
WantedBy=multi-user.target
EOF

# Créer le service frontend
cat > /etc/systemd/system/ayhr-frontend.service <<EOF
[Unit]
Description=AY HR Management - Frontend Web Interface
After=network.target ayhr-backend.service
Wants=ayhr-backend.service

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=10
StandardOutput=append:${INSTALL_DIR}/logs/frontend.log
StandardError=append:${INSTALL_DIR}/logs/frontend.log

[Install]
WantedBy=multi-user.target
EOF

# Créer le dossier logs
mkdir -p "$INSTALL_DIR/logs"

# Recharger systemd
systemctl daemon-reload
success "Services systemd créés"

# Activer les services
systemctl enable ayhr-backend
systemctl enable ayhr-frontend
success "Services activés pour démarrage automatique"

# Démarrer les services
systemctl start ayhr-backend
sleep 3
systemctl start ayhr-frontend
sleep 2

success "Services démarrés"

##############################################
# ÉTAPE 12: Configuration du pare-feu
##############################################
echo -e "\n${BLUE}[ÉTAPE BONUS]${NC} ${GREEN}Configuration du pare-feu (UFW)${NC}"
echo "-------------------------------------------"

if command -v ufw &> /dev/null; then
    ufw allow 22/tcp comment 'SSH' 2>/dev/null || true
    ufw allow 8000/tcp comment 'Backend API' 2>/dev/null || true
    ufw allow 3000/tcp comment 'Frontend Web' 2>/dev/null || true
    success "Règles pare-feu configurées"
else
    warning "UFW non installé, ignoré"
fi

##############################################
# RÉSUMÉ FINAL
##############################################
echo -e "\n${GREEN}=========================================="
echo "  ✓ INSTALLATION TERMINÉE AVEC SUCCÈS"
echo "==========================================${NC}\n"

echo -e "${BLUE}Informations d'accès:${NC}"
echo "  • Frontend:  http://${SERVER_IP}:3000"
echo "  • Backend:   http://${SERVER_IP}:8000/docs"
echo "  • Login:     admin"
echo "  • Password:  admin123"
echo ""

echo -e "${BLUE}Services systemd:${NC}"
systemctl status ayhr-backend --no-pager -l | grep Active
systemctl status ayhr-frontend --no-pager -l | grep Active
echo ""

echo -e "${BLUE}Base de données:${NC}"
echo "  • Database:  ${DB_NAME}"
echo "  • User:      ${DB_USER}"
echo "  • Tables:    $((TABLE_COUNT - 1))"
echo ""

echo -e "${BLUE}Commandes utiles:${NC}"
echo "  • Voir logs backend:   journalctl -u ayhr-backend -f"
echo "  • Voir logs frontend:  journalctl -u ayhr-frontend -f"
echo "  • Redémarrer services: systemctl restart ayhr-backend ayhr-frontend"
echo "  • Statut services:     systemctl status ayhr-*"
echo ""

echo -e "${YELLOW}⚠ IMPORTANT:${NC}"
echo "  Changez le mot de passe admin dès la première connexion!"
echo ""

echo -e "${GREEN}Installation complète! 🎉${NC}\n"

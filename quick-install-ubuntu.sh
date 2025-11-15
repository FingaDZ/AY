#!/bin/bash
# ============================================================================
# Installation Rapide - AY HR sur Ubuntu 22.04
# ============================================================================

echo "============================================"
echo " Installation AY HR Management v1.1.4"
echo " Ubuntu 22.04 LTS"
echo "============================================"
echo ""

# Vérifier les privilèges root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Ce script doit être exécuté en tant que root"
    echo "   Utiliser: sudo $0"
    exit 1
fi

# Obtenir l'utilisateur réel
REAL_USER="${SUDO_USER:-$USER}"
INSTALL_DIR="/opt/ay-hr"

echo "📋 Configuration:"
echo "   Utilisateur: $REAL_USER"
echo "   Dossier: $INSTALL_DIR"
echo ""
read -p "Continuer l'installation? (o/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "Installation annulée."
    exit 0
fi

echo ""
echo "[1/8] Mise à jour du système..."
apt update && apt upgrade -y
apt install -y software-properties-common apt-transport-https ca-certificates curl wget git

echo ""
echo "[2/8] Installation de Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

echo ""
echo "[3/8] Installation de Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

echo ""
echo "[4/8] Installation de MariaDB 10.11..."
apt install -y mariadb-server mariadb-client
systemctl start mariadb
systemctl enable mariadb

echo ""
echo "[5/8] Configuration de la base de données..."
echo "⚠️  Vous devez maintenant configurer MariaDB"
echo ""
read -p "Mot de passe root MariaDB: " -s MYSQL_ROOT_PASS
echo ""
read -p "Nom de la base de données [ay_hr]: " DB_NAME
DB_NAME=${DB_NAME:-ay_hr}
read -p "Utilisateur de la base [ayhr_user]: " DB_USER
DB_USER=${DB_USER:-ayhr_user}
read -p "Mot de passe utilisateur: " -s DB_PASS
echo ""

# Créer la base de données et l'utilisateur
mysql -u root -p"$MYSQL_ROOT_PASS" << EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Base de données créée"
else
    echo "❌ Erreur lors de la création de la base de données"
    exit 1
fi

echo ""
echo "[6/8] Copie des fichiers du projet..."
mkdir -p "$INSTALL_DIR"
cp -r . "$INSTALL_DIR/"
cd "$INSTALL_DIR"

echo ""
echo "[7/8] Installation des dépendances..."
# Backend
cd "$INSTALL_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Frontend
cd "$INSTALL_DIR/frontend"
npm install

echo ""
echo "[8/8] Configuration finale..."
# Générer SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# Créer le fichier .env backend
cat > "$INSTALL_DIR/backend/.env" << EOF
# Base de données
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASS

# Sécurité
SECRET_KEY=$SECRET_KEY

# Server
HOST=0.0.0.0
PORT=8000

# CORS
FRONTEND_URL=http://localhost:3000
EOF

# Créer le fichier .env frontend
cat > "$INSTALL_DIR/frontend/.env" << EOF
VITE_API_URL=http://localhost:8000
EOF

# Initialiser la base de données
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$INSTALL_DIR/database/create_database.sql"

# Créer les dossiers
mkdir -p "$INSTALL_DIR"/{logs,backups,uploads}

# Corriger les permissions
chown -R "$REAL_USER":"$REAL_USER" "$INSTALL_DIR"

echo ""
echo "============================================"
echo " ✅ Installation Terminée!"
echo "============================================"
echo ""
echo "📌 Prochaines étapes:"
echo ""
echo "1. Installer comme service (auto-démarrage):"
echo "   sudo $INSTALL_DIR/install-service-linux.sh"
echo ""
echo "2. Ou démarrer manuellement:"
echo "   $INSTALL_DIR/start-linux.sh"
echo ""
echo "3. Accéder à l'application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000/docs"
echo "   Login:    admin / admin123"
echo ""
echo "⚠️  IMPORTANT: Changer le mot de passe admin!"
echo ""
echo "📚 Documentation: $INSTALL_DIR/INSTALL_UBUNTU_22.04.md"
echo ""

#!/bin/bash
# ============================================================================
# Script d'Installation Automatique - AY HR Management v1.1.4
# Pour Ubuntu/Debian Linux
# ============================================================================

echo ""
echo "========================================"
echo " AIRBAND HR v1.1.4"
echo " Installation Automatique Linux"
echo "========================================"
echo ""

# Vérifier si le script est exécuté avec sudo
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Ne pas exécuter ce script avec sudo"
    echo "Le script demandera sudo uniquement si nécessaire"
    exit 1
fi

# Vérification des prérequis
echo "[1/8] Vérification des prérequis..."
echo ""

# Vérifier Python
echo -n "  → Vérification de Python... "
if command -v python3.11 &> /dev/null; then
    PYTHON_VERSION=$(python3.11 --version)
    echo "OK ($PYTHON_VERSION)"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "OK ($PYTHON_VERSION)"
    alias python3.11=python3
else
    echo "ERREUR"
    echo ""
    echo "Python 3.11+ n'est pas installé."
    echo "Installation de Python 3.11..."
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3-pip
fi

# Vérifier Node.js
echo -n "  → Vérification de Node.js... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "OK ($NODE_VERSION)"
else
    echo "ERREUR"
    echo ""
    echo "Node.js n'est pas installé."
    echo "Installation de Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
fi

# Vérifier MariaDB
echo -n "  → Vérification de MariaDB... "
if command -v mysql &> /dev/null; then
    echo "OK"
    # Démarrer MariaDB si non actif
    sudo systemctl start mariadb 2>/dev/null
    sudo systemctl enable mariadb 2>/dev/null
else
    echo "ERREUR"
    echo ""
    echo "MariaDB n'est pas installé."
    echo "Installation de MariaDB..."
    sudo apt install -y mariadb-server
    sudo systemctl start mariadb
    sudo systemctl enable mariadb
    echo ""
    echo "⚠️  Veuillez sécuriser MariaDB:"
    echo "sudo mysql_secure_installation"
    read -p "Appuyez sur Entrée après avoir sécurisé MariaDB..."
fi

echo ""
echo "[2/8] Création de l'environnement Python..."
echo ""

# Créer l'environnement virtuel
if [ -d "backend/.venv" ]; then
    echo "  → Environnement virtuel existant trouvé"
else
    echo -n "  → Création de l'environnement virtuel... "
    cd backend
    python3.11 -m venv .venv
    if [ $? -eq 0 ]; then
        echo "OK"
    else
        echo "ERREUR"
        exit 1
    fi
    cd ..
fi

echo ""
echo "[3/8] Installation des dépendances Python..."
echo ""

cd backend
source .venv/bin/activate
echo -n "  → Mise à jour de pip... "
pip install --upgrade pip --quiet
echo "OK"

echo -n "  → Installation des packages Python... "
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo "OK"
else
    echo "ERREUR"
    deactivate
    cd ..
    exit 1
fi
deactivate
cd ..

echo ""
echo "[4/8] Installation des dépendances Node.js..."
echo ""

cd frontend
echo -n "  → Installation des packages Node.js... "
npm install --silent 2>&1 > /dev/null
if [ $? -eq 0 ]; then
    echo "OK"
else
    echo "ERREUR"
    cd ..
    exit 1
fi
cd ..

echo ""
echo "[5/8] Configuration de la base de données..."
echo ""

# Demander les informations de connexion
echo "  Veuillez fournir les informations de connexion MariaDB:"
echo ""

read -p "  Hôte [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "  Port [3306]: " DB_PORT
DB_PORT=${DB_PORT:-3306}

read -p "  Utilisateur [root]: " DB_USER
DB_USER=${DB_USER:-root}

read -sp "  Mot de passe: " DB_PASSWORD
echo ""

echo ""
echo -n "  → Test de connexion... "
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p"$DB_PASSWORD" -e "SELECT 1;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "OK"
else
    echo "ERREUR"
    echo ""
    echo "Impossible de se connecter à la base de données."
    echo "Vérifiez vos identifiants et réessayez."
    exit 1
fi

echo ""
echo "[6/8] Création des fichiers de configuration..."
echo ""

# Générer une clé secrète
SECRET_KEY=$(openssl rand -hex 32)

# Créer le fichier .env backend
echo -n "  → Création de backend/.env... "
cat > backend/.env << EOF
# Configuration Base de Données
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=ay_hr

# Configuration Sécurité
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Configuration Serveur
HOST=0.0.0.0
PORT=8000
EOF
echo "OK"

# Créer le fichier .env frontend
echo -n "  → Création de frontend/.env... "
echo "VITE_API_URL=http://localhost:8000" > frontend/.env
echo "OK"

echo ""
echo "[7/8] Initialisation de la base de données..."
echo ""

echo -n "  → Création de la base de données ay_hr... "
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p"$DB_PASSWORD" < database/create_database.sql 2>/dev/null
if [ $? -eq 0 ]; then
    echo "OK"
else
    echo "ERREUR"
    echo ""
    echo "Erreur lors de la création de la base de données."
    echo "Vérifiez que MariaDB est démarré et que les permissions sont correctes."
    exit 1
fi

echo ""
echo "[8/8] Création des dossiers nécessaires..."
echo ""

# Créer les dossiers
for folder in logs backups uploads; do
    if [ ! -d "$folder" ]; then
        echo -n "  → Création de $folder... "
        mkdir -p $folder
        echo "OK"
    fi
done

echo ""
echo "========================================"
echo " Installation Terminée avec Succès!"
echo "========================================"
echo ""
echo "Pour démarrer l'application:"
echo "  ./start-linux.sh"
echo ""
echo "Pour installer comme service système:"
echo "  sudo ./install-service-linux.sh"
echo ""
echo "Accès à l'application:"
echo "  Interface Web    : http://localhost:3000"
echo "  API Backend      : http://localhost:8000"
echo "  Documentation API: http://localhost:8000/docs"
echo ""
echo "Identifiants par défaut:"
echo "  Nom d'utilisateur: admin"
echo "  Mot de passe     : admin123"
echo ""
echo "⚠️  IMPORTANT: Changez le mot de passe admin dès la première connexion!"
echo ""

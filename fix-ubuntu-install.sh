#!/bin/bash
# ============================================================================
# Script de Correction - Installation Ubuntu 22.04
# Pour résoudre les problèmes apt_pkg, Node.js et permissions
# ============================================================================

echo "============================================"
echo " Correction Installation Ubuntu 22.04"
echo "============================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Vérifier si on est root
if [ "$EUID" -eq 0 ]; then 
    print_error "Ne pas exécuter ce script en tant que root"
    echo "Utiliser: ./fix-ubuntu-install.sh"
    exit 1
fi

echo "[1/6] Correction du module apt_pkg..."
sudo apt install --reinstall python3-apt -y 2>&1 | grep -v "Traceback" | grep -v "apt_pkg"
if python3 -c "import apt_pkg" 2>/dev/null; then
    print_success "Module apt_pkg corrigé"
else
    print_warning "apt_pkg toujours problématique, mais ça ne bloquera pas l'installation"
fi

echo ""
echo "[2/6] Vérification de Node.js..."
NODE_VERSION=$(node --version 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)

if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 18 ]; then
    print_warning "Node.js $NODE_VERSION détecté, installation de Node.js 20 LTS..."
    
    # Supprimer l'ancienne version
    sudo apt remove nodejs nodejs-doc -y 2>&1 | tail -3
    sudo apt autoremove -y 2>&1 | tail -1
    
    # Installer Node.js 20
    curl -fsSL https://deb.nodesource.com/setup_20.x 2>/dev/null | sudo -E bash - 2>&1 | grep -v "apt_pkg" | tail -5
    sudo apt install -y nodejs 2>&1 | tail -3
    
    print_success "Node.js $(node --version) et npm $(npm --version) installés"
else
    print_success "Node.js $(node --version) OK"
fi

echo ""
echo "[3/6] Correction des permissions des scripts..."
cd /opt/ay-hr 2>/dev/null || cd $(pwd)
chmod +x *.sh 2>/dev/null
print_success "Scripts rendus exécutables"

echo ""
echo "[4/6] Vérification de la structure..."
if [ -d "backend" ] && [ -d "frontend" ] && [ -d "database" ]; then
    print_success "Structure du projet OK"
else
    print_error "Structure du projet incomplète"
    echo "Vous devez cloner le projet depuis GitHub"
fi

echo ""
echo "[5/6] Vérification de Python..."
PYTHON_VERSION=$(python3 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    print_success "Python OK: $PYTHON_VERSION"
else
    print_error "Python non installé correctement"
fi

echo ""
echo "[6/6] Vérification de MariaDB..."
if systemctl is-active --quiet mariadb; then
    print_success "MariaDB en cours d'exécution"
elif systemctl is-active --quiet mysql; then
    print_success "MySQL/MariaDB en cours d'exécution"
else
    print_warning "MariaDB/MySQL non démarré"
    echo "Démarrer avec: sudo systemctl start mariadb"
fi

echo ""
echo "============================================"
echo " Correction Terminée"
echo "============================================"
echo ""
echo "Prochaines étapes:"
echo ""
echo "1. Continuer l'installation manuelle:"
echo "   cd /opt/ay-hr/backend"
echo "   python3 -m venv .venv"
echo "   source .venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "2. Ou utiliser le script d'installation:"
echo "   cd /opt/ay-hr"
echo "   ./install-linux.sh"
echo ""
echo "3. Si vous êtes connecté en root, créer un utilisateur:"
echo "   sudo adduser ayhr"
echo "   sudo usermod -aG sudo ayhr"
echo "   sudo chown -R ayhr:ayhr /opt/ay-hr"
echo "   su - ayhr"
echo ""

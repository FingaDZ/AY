#!/bin/bash
# ============================================
# Script de Déploiement AY HR v3.6.1
# Serveur: 192.168.20.55 (root)
# Date: 23 Décembre 2025
# À exécuter directement sur le serveur
# ============================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/root/AY_HR"
BACKUP_DIR="/root/backups/ay_hr"
DB_NAME="ay_hr"
DB_USER="root"
LOG_FILE="/var/log/ay_hr_backend.log"

echo -e "${CYAN}========================================"
echo -e "   DÉPLOIEMENT AY HR v3.6.1"
echo -e "========================================${NC}\n"

# Fonction pour afficher les messages
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier que le script est exécuté en tant que root
if [ "$EUID" -ne 0 ]; then 
    log_error "Ce script doit être exécuté en tant que root"
    exit 1
fi

# 1. Créer les répertoires de sauvegarde
log_info "[1/8] Création des répertoires de sauvegarde..."
mkdir -p "$BACKUP_DIR"
log_success "Répertoires créés"

# 2. Sauvegarde de la base de données
log_info "[2/8] Sauvegarde de la base de données..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if mysqldump -u "$DB_USER" -p"$DB_NAME" > "$BACKUP_DIR/ay_hr_backup_$TIMESTAMP.sql" 2>/dev/null; then
    log_success "Base de données sauvegardée: ay_hr_backup_$TIMESTAMP.sql"
else
    log_warning "Sauvegarde DB peut nécessiter le mot de passe MySQL"
    mysqldump -u "$DB_USER" -p "$DB_NAME" > "$BACKUP_DIR/ay_hr_backup_$TIMESTAMP.sql"
fi

# 3. Sauvegarde des fichiers actuels
log_info "[3/8] Sauvegarde des fichiers actuels..."
if [ -d "$APP_DIR" ]; then
    cp -r "$APP_DIR" "$BACKUP_DIR/ay_hr_files_$TIMESTAMP"
    log_success "Fichiers sauvegardés"
else
    log_warning "Aucun fichier existant à sauvegarder (première installation)"
fi

# 4. Clone ou mise à jour du dépôt Git
log_info "[4/8] Mise à jour du code depuis GitHub..."
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR"
    git fetch origin
    git reset --hard origin/main
    git pull origin main
    log_success "Dépôt mis à jour"
else
    log_warning "Clonage du dépôt (première installation)..."
    rm -rf "$APP_DIR"
    git clone https://github.com/FingaDZ/AY.git "$APP_DIR"
    cd "$APP_DIR"
    log_success "Dépôt cloné"
fi

# 5. Vérifier la version
log_info "Vérification de la version..."
cd "$APP_DIR/backend"
VERSION=$(grep "APP_VERSION" config.py | cut -d'"' -f2)
log_success "Version actuelle: $VERSION"

# 6. Application des migrations de base de données
log_info "[5/8] Application des migrations de base de données..."
cd "$APP_DIR/database"

if [ -f "migration_v3.6.1_conges_credits_contrats.sql" ]; then
    log_info "Application de la migration v3.6.1..."
    if mysql -u "$DB_USER" -p"$DB_NAME" < migration_v3.6.1_conges_credits_contrats.sql 2>/dev/null; then
        log_success "Migration v3.6.1 appliquée"
    else
        log_warning "Application de la migration avec mot de passe..."
        mysql -u "$DB_USER" -p "$DB_NAME" < migration_v3.6.1_conges_credits_contrats.sql
        log_success "Migration v3.6.1 appliquée"
    fi
else
    log_warning "Fichier de migration v3.6.1 non trouvé"
fi

# 7. Installation/Mise à jour des dépendances backend
log_info "[6/8] Mise à jour des dépendances backend..."
cd "$APP_DIR/backend"

# Créer ou activer l'environnement virtuel
if [ -d "venv" ]; then
    log_info "Activation de l'environnement virtuel existant..."
    source venv/bin/activate
else
    log_info "Création d'un nouvel environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Installer les dépendances
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
log_success "Dépendances Python installées"

# 8. Build du frontend (optionnel)
log_info "[7/8] Build du frontend..."
cd "$APP_DIR/frontend"
if [ -f "package.json" ]; then
    if command -v npm &> /dev/null; then
        npm install --silent
        npm run build
        log_success "Frontend construit"
    else
        log_warning "npm non installé, build frontend ignoré"
    fi
else
    log_warning "package.json non trouvé, build frontend ignoré"
fi

# 9. Redémarrage des services
log_info "[8/8] Redémarrage des services..."

# Arrêter les processus existants
log_info "Arrêt des processus existants..."
pkill -f 'uvicorn main:app' 2>/dev/null && log_info "Backend arrêté" || log_warning "Aucun processus backend en cours"
pkill -f 'npm.*vite' 2>/dev/null && log_info "Frontend arrêté" || log_warning "Aucun processus frontend en cours"

# Attendre un peu
sleep 2

# Redémarrer le backend
log_info "Démarrage du backend..."
cd "$APP_DIR/backend"
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!
log_success "Backend démarré (PID: $BACKEND_PID) sur le port 8000"

# Attendre que le backend démarre
log_info "Attente du démarrage de l'API..."
sleep 5

# Vérification finale
echo -e "\n${CYAN}========================================"
echo -e "   VÉRIFICATION DU DÉPLOIEMENT"
echo -e "========================================${NC}\n"

# Vérifier si le processus backend est en cours
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    log_success "Processus backend actif (PID: $BACKEND_PID)"
else
    log_error "Le processus backend ne semble pas actif"
fi

# Vérifier si le port 8000 est ouvert
if lsof -i :8000 > /dev/null 2>&1; then
    log_success "Port 8000 est ouvert"
else
    log_warning "Port 8000 ne semble pas ouvert"
fi

# Tester l'API
log_info "Test de l'API..."
sleep 2
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    log_success "API accessible"
else
    log_warning "API non accessible immédiatement (peut prendre quelques secondes...)"
fi

# Afficher les dernières lignes des logs
log_info "Dernières lignes des logs:"
tail -10 "$LOG_FILE"

# Résumé final
echo -e "\n${GREEN}========================================"
echo -e "   DÉPLOIEMENT TERMINÉ!"
echo -e "========================================${NC}\n"

echo -e "${CYAN}📊 Version déployée:${NC} v3.6.1"
echo -e "${CYAN}🌐 API Backend:${NC} http://192.168.20.55:8000"
echo -e "${CYAN}📚 Documentation:${NC} http://192.168.20.55:8000/docs"
echo -e "${CYAN}💾 Sauvegardes:${NC} $BACKUP_DIR"
echo -e "${CYAN}📝 Logs backend:${NC} $LOG_FILE"
echo -e ""

echo -e "${YELLOW}📝 Prochaines étapes:${NC}"
echo -e "  ${GREEN}1.${NC} Tester l'API: http://192.168.20.55:8000/docs"
echo -e "  ${GREEN}2.${NC} Vérifier les logs: tail -f $LOG_FILE"
echo -e "  ${GREEN}3.${NC} Tester les nouvelles fonctionnalités v3.6.1"
echo -e ""

echo -e "${YELLOW}✨ Nouvelles fonctionnalités v3.6.1:${NC}"
echo -e "  ${GREEN}✓${NC} Gestion des congés avec déduction flexible"
echo -e "  ${GREEN}✓${NC} Échéancier automatique des crédits"
echo -e "  ${GREEN}✓${NC} Auto-désactivation des contrats expirés"
echo -e "  ${GREEN}✓${NC} Logging amélioré avec user_id et ip_address"
echo -e ""

echo -e "${YELLOW}⚠️  Notes importantes:${NC}"
echo -e "  - Vérifiez le fichier .env: $APP_DIR/backend/.env"
echo -e "  - Testez la connexion à la base de données MySQL"
echo -e "  - En cas de problème: tail -f $LOG_FILE"
echo -e ""

log_success "Déploiement terminé avec succès!"

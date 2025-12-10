#!/bin/bash

#==============================================================================
# AY HR System - Script de Mise à Jour Automatique
# Version: 2.2
# Date: 29 novembre 2025
#==============================================================================

# Configuration
APP_DIR="/opt/ay-hr"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/update_$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR="$APP_DIR/backups"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${2}$1${NC}" | tee -a "$LOG_FILE"
}

error_exit() {
    log "❌ ERREUR: $1" "$RED"
    exit 1
}

success() {
    log "✅ $1" "$GREEN"
}

info() {
    log "ℹ️  $1" "$BLUE"
}

warning() {
    log "⚠️  $1" "$YELLOW"
}

# Banner
echo -e "${BLUE}"
cat <<"EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           AY HR SYSTEM - MISE À JOUR                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log "Début de la mise à jour: $(date)" "$YELLOW"
log "Fichier de log: $LOG_FILE" "$BLUE"

#==============================================================================
# Vérifications préliminaires
#==============================================================================

info "[0/8] Vérifications préliminaires..."

# Check root
if [ "$EUID" -ne 0 ]; then 
    error_exit "Ce script doit être exécuté en tant que root (sudo)"
fi

# Check directories
if [ ! -d "$APP_DIR" ]; then
    error_exit "Répertoire $APP_DIR introuvable"
fi

# Create log and backup directories
mkdir -p "$LOG_DIR" "$BACKUP_DIR"

# Get current version
CURRENT_VERSION=$(grep -oP '(?<=APP_VERSION: str = ")[^"]*' "$BACKEND_DIR/config.py" 2>/dev/null || echo "unknown")
info "Version actuelle: $CURRENT_VERSION"

#==============================================================================
# Backup de la base de données
#==============================================================================

info "[1/8] Sauvegarde de la base de données..."

# Extract DB credentials from .env
if [ -f "$BACKEND_DIR/.env" ]; then
    DB_URL=$(grep DATABASE_URL "$BACKEND_DIR/.env" | cut -d '=' -f2)
    DB_NAME=$(echo "$DB_URL" | grep -oP '(?<=/)[\w_]+$')
    DB_USER=$(echo "$DB_URL" | grep -oP '(?<=://)[^:]+')
    DB_PASS=$(echo "$DB_URL" | grep -oP '(?<=:)[^@]+(?=@)')
    DB_HOST=$(echo "$DB_URL" | grep -oP '(?<=@)[^/]+')
    
    if [ -n "$DB_NAME" ]; then
        BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
        mysqldump -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_FILE" 2>> "$LOG_FILE"
        
        if [ $? -eq 0 ]; then
            gzip "$BACKUP_FILE"
            success "Base de données sauvegardée: $BACKUP_FILE.gz"
        else
            warning "Échec de la sauvegarde DB (non bloquant)"
        fi
    fi
else
    warning "Fichier .env introuvable, sauvegarde DB ignorée"
fi

#==============================================================================
# Backup des fichiers de configuration
#==============================================================================

info "[2/8] Sauvegarde des fichiers de configuration..."

CONFIG_BACKUP="$BACKUP_DIR/config_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$CONFIG_BACKUP" \
    "$BACKEND_DIR/.env" \
    "$BACKEND_DIR/config.py" \
    2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    success "Configuration sauvegardée: $CONFIG_BACKUP"
else
    warning "Échec sauvegarde config (non bloquant)"
fi

#==============================================================================
# Arrêt des services
#==============================================================================

info "[3/8] Arrêt des services..."

systemctl stop ayhr-backend 2>> "$LOG_FILE"
systemctl stop ayhr-frontend 2>> "$LOG_FILE"

# Force kill port 8000 if stuck
if command -v fuser >/dev/null 2>&1; then
    fuser -k 8000/tcp >> "$LOG_FILE" 2>&1
fi

success "Services arrêtés"

#==============================================================================
# Mise à jour du code depuis GitHub
#==============================================================================

info "[4/8] Récupération du code depuis GitHub..."

cd "$APP_DIR" || error_exit "Impossible d'accéder à $APP_DIR"

# Stash local changes (if any)
git stash save "Auto-stash before update $(date)" >> "$LOG_FILE" 2>&1

# Pull latest code
git pull origin main >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    error_exit "Échec du git pull. Vérifiez les logs."
fi

success "Code mis à jour depuis GitHub"

# Get new version
NEW_VERSION=$(grep -oP '(?<=APP_VERSION: str = ")[^"]*' "$BACKEND_DIR/config.py" 2>/dev/null || echo "unknown")
info "Nouvelle version: $NEW_VERSION"

#==============================================================================
# Mise à jour Backend
#==============================================================================

info "[5/8] Mise à jour du Backend..."

cd "$BACKEND_DIR" || error_exit "Impossible d'accéder à $BACKEND_DIR"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    error_exit "Environnement virtuel Python introuvable (cherché: venv/ et .venv/)"
fi

# Update dependencies
pip install --upgrade pip >> "$LOG_FILE" 2>&1
pip install -r requirements.txt >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    error_exit "Échec de l'installation des dépendances Python"
fi

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

deactivate

# Run DB schema fix (migration)
if [ -f "fix_db_schema.py" ]; then
    info "Vérification et correction du schéma de base de données..."
    if [ -f "$BACKEND_DIR/venv/bin/python" ]; then
        "$BACKEND_DIR/venv/bin/python" fix_db_schema.py >> "$LOG_FILE" 2>&1
    elif [ -f "$BACKEND_DIR/.venv/bin/python" ]; then
        "$BACKEND_DIR/.venv/bin/python" fix_db_schema.py >> "$LOG_FILE" 2>&1
    else
        warning "Impossible de trouver l'interpréteur Python pour fix_db_schema.py"
    fi
fi

# Create static directory if not exists
mkdir -p static

success "Backend mis à jour"

#==============================================================================
# Mise à jour Frontend
#==============================================================================

info "[6/8] Mise à jour du Frontend..."

# Fix: Move package-lock.json if it's in root
if [ -f "$APP_DIR/package-lock.json" ]; then
    info "Déplacement de package-lock.json vers frontend/"
    mv "$APP_DIR/package-lock.json" "$FRONTEND_DIR/" >> "$LOG_FILE" 2>&1
fi

cd "$FRONTEND_DIR" || error_exit "Impossible d'accéder à $FRONTEND_DIR"

# Clean node_modules if build issues
if [ -d "node_modules" ]; then
    info "Nettoyage de node_modules existants..."
    rm -rf node_modules >> "$LOG_FILE" 2>&1
fi

# Install dependencies
info "Installation des dépendances npm..."
npm install >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    error_exit "Échec de l'installation des dépendances npm"
fi

# Build production
info "Build du frontend..."
npm run build >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    error_exit "Échec du build frontend"
fi

success "Frontend mis à jour et compilé"

#==============================================================================
# Permissions et propriétés
#==============================================================================

info "[7/8] Correction des permissions..."

cd "$APP_DIR" || exit

# Set ownership
chown -R root:root "$APP_DIR"

# Make scripts executable
chmod +x "$APP_DIR"/*.sh 2>/dev/null

# Set proper permissions for logs and backups
chmod 755 "$LOG_DIR" "$BACKUP_DIR"

success "Permissions corrigées"

#==============================================================================
# Redémarrage des services
#==============================================================================

info "[8/8] Redémarrage des services..."

systemctl start ayhr-backend
sleep 2
systemctl start ayhr-frontend

# Wait for services to start
sleep 3

# Check service status
BACKEND_STATUS=$(systemctl is-active ayhr-backend)
FRONTEND_STATUS=$(systemctl is-active ayhr-frontend)

if [ "$BACKEND_STATUS" = "active" ] && [ "$FRONTEND_STATUS" = "active" ]; then
    success "Services redémarrés avec succès"
else
    error_exit "Échec du redémarrage des services"
fi

#==============================================================================
# Nettoyage des anciens backups
#==============================================================================

info "Nettoyage des anciens backups (>30 jours)..."

find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete 2>/dev/null
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete 2>/dev/null
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null

success "Nettoyage effectué"

#==============================================================================
# Résumé final
#==============================================================================

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}║           ✅ MISE À JOUR TERMINÉE AVEC SUCCÈS            ║${NC}"
echo -e "${GREEN}║                                                           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

log "📊 RÉSUMÉ DE LA MISE À JOUR" "$BLUE"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "$BLUE"
log "Version précédente : $CURRENT_VERSION" "$BLUE"
log "Version actuelle   : $NEW_VERSION" "$BLUE"
log "Backend            : $BACKEND_STATUS" "$GREEN"
log "Frontend           : $FRONTEND_STATUS" "$GREEN"
log "Backup DB          : $BACKUP_FILE.gz" "$BLUE"
log "Backup Config      : $CONFIG_BACKUP" "$BLUE"
log "Log complet        : $LOG_FILE" "$BLUE"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "$BLUE"
echo ""

log "🌐 Accès à l'application:" "$BLUE"
log "   - Local:  http://localhost:8000" "$BLUE"
log "   - LAN:    http://$(hostname -I | awk '{print $1}'):8000" "$BLUE"
echo ""

log "📝 Pour voir les logs en temps réel:" "$BLUE"
log "   sudo journalctl -u ayhr-backend -f" "$BLUE"
echo ""

log "Fin de la mise à jour: $(date)" "$YELLOW"

exit 0

#!/bin/bash
# Script de migration v3.5.0 sur serveur (à exécuter directement sur 192.168.20.55)
# Date: 10 décembre 2025

set -e  # Arrêter en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_PATH="/opt/ay_hr"  # Adapter selon votre installation
DB_NAME="ay_hr"
DB_USER="root"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     MIGRATION AY HR v3.5.0 - Serveur Production         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Vérifier si on est sur le serveur
echo -e "${YELLOW}[INFO] Vérification de l'environnement...${NC}"
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}✗ Répertoire $PROJECT_PATH introuvable${NC}"
    echo -e "${YELLOW}Modifier la variable PROJECT_PATH dans le script${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Répertoire trouvé: $PROJECT_PATH${NC}"

# =====================================
# ÉTAPE 1: Backup base de données
# =====================================
echo -e "\n${CYAN}[1/6] Création du backup de la base de données...${NC}"

BACKUP_FILE="/tmp/ay_hr_backup_$(date +%Y%m%d_%H%M%S).sql"
echo -e "${YELLOW}Backup: $BACKUP_FILE${NC}"
echo -e "${YELLOW}Note: Le mot de passe MySQL sera demandé${NC}"

mysqldump -u $DB_USER -p $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backup créé avec succès${NC}"
    ls -lh $BACKUP_FILE
else
    echo -e "${RED}✗ Échec création backup${NC}"
    read -p "Continuer sans backup? (oui/non): " continue_without_backup
    if [ "$continue_without_backup" != "oui" ]; then
        exit 1
    fi
fi

# =====================================
# ÉTAPE 2: Vérifier les fichiers
# =====================================
echo -e "\n${CYAN}[2/6] Vérification des fichiers...${NC}"

FILES=(
    "$PROJECT_PATH/database/migrations/add_numero_anem.sql"
    "$PROJECT_PATH/backend/services/pdf_generator.py"
    "$PROJECT_PATH/backend/config.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ Fichier manquant: $file${NC}"
        echo -e "${YELLOW}Transférez d'abord les fichiers depuis votre machine locale${NC}"
        exit 1
    fi
done

# =====================================
# ÉTAPE 3: Migration SQL
# =====================================
echo -e "\n${CYAN}[3/6] Exécution de la migration SQL...${NC}"

cd $PROJECT_PATH
echo -e "${YELLOW}Note: Le mot de passe MySQL sera demandé${NC}"

mysql -u $DB_USER -p $DB_NAME < database/migrations/add_numero_anem.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migration SQL exécutée${NC}"
    
    # Vérifier que la colonne existe
    echo -e "\n${YELLOW}Vérification de la colonne numero_anem:${NC}"
    mysql -u $DB_USER -p $DB_NAME -e "DESCRIBE employes;" | grep numero_anem
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Colonne numero_anem créée${NC}"
    else
        echo -e "${RED}✗ Colonne non trouvée${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Échec migration SQL${NC}"
    exit 1
fi

# =====================================
# ÉTAPE 4: Installation dépendances
# =====================================
echo -e "\n${CYAN}[4/6] Installation des dépendances Python...${NC}"

cd $PROJECT_PATH/backend

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Environnement virtuel 'venv' introuvable${NC}"
    exit 1
fi

source venv/bin/activate

echo -e "${YELLOW}Installation: qrcode, pillow, reportlab${NC}"
pip install qrcode[pil] pillow reportlab --quiet

# Test import
python -c "import qrcode; from reportlab.lib.utils import ImageReader; print('OK')" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dépendances installées et testées${NC}"
else
    echo -e "${RED}✗ Problème avec les dépendances${NC}"
    exit 1
fi

deactivate

# =====================================
# ÉTAPE 5: Redémarrage backend
# =====================================
echo -e "\n${CYAN}[5/6] Redémarrage du backend...${NC}"

# Détection du gestionnaire de service
if systemctl is-active --quiet ayhr-backend; then
    echo -e "${YELLOW}Redémarrage avec systemctl...${NC}"
    sudo systemctl restart ayhr-backend
    sleep 3
    
    if systemctl is-active --quiet ayhr-backend; then
        echo -e "${GREEN}✓ Backend redémarré (systemctl)${NC}"
    else
        echo -e "${RED}✗ Échec redémarrage${NC}"
        sudo systemctl status ayhr-backend
        exit 1
    fi
elif command -v pm2 &> /dev/null && pm2 list | grep -q ayhr-backend; then
    echo -e "${YELLOW}Redémarrage avec PM2...${NC}"
    pm2 restart ayhr-backend
    sleep 2
    
    if pm2 list | grep -q "online"; then
        echo -e "${GREEN}✓ Backend redémarré (PM2)${NC}"
    else
        echo -e "${RED}✗ Échec redémarrage${NC}"
        pm2 logs ayhr-backend --lines 20
        exit 1
    fi
else
    echo -e "${YELLOW}Gestionnaire de service non détecté${NC}"
    echo -e "${YELLOW}Redémarrez manuellement le backend${NC}"
    echo -e "  cd $PROJECT_PATH/backend"
    echo -e "  source venv/bin/activate"
    echo -e "  uvicorn main:app --host 0.0.0.0 --port 8000"
fi

# =====================================
# ÉTAPE 6: Tests de validation
# =====================================
echo -e "\n${CYAN}[6/6] Tests de validation...${NC}"

# Test 1: Version API
echo -e "${YELLOW}Test 1: Vérification version API...${NC}"
sleep 2  # Laisser le temps au backend de démarrer

API_RESPONSE=$(curl -s http://localhost:8000/ 2>/dev/null)
if echo "$API_RESPONSE" | grep -q "3.5.0"; then
    echo -e "${GREEN}✓ Version 3.5.0 détectée${NC}"
else
    echo -e "${RED}✗ Version non détectée ou backend non accessible${NC}"
    echo -e "${YELLOW}Réponse API: $API_RESPONSE${NC}"
fi

# Test 2: Colonne numero_anem
echo -e "\n${YELLOW}Test 2: Vérification colonne numero_anem...${NC}"
mysql -u $DB_USER -p $DB_NAME -e "SHOW COLUMNS FROM employes LIKE 'numero_anem';" 2>/dev/null | grep -q numero_anem

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Colonne numero_anem existe${NC}"
else
    echo -e "${RED}✗ Colonne non trouvée${NC}"
fi

# Test 3: Logs
echo -e "\n${YELLOW}Test 3: Vérification des logs (dernières 10 lignes)...${NC}"
if systemctl is-active --quiet ayhr-backend; then
    sudo journalctl -u ayhr-backend -n 10 --no-pager
elif command -v pm2 &> /dev/null; then
    pm2 logs ayhr-backend --lines 10 --nostream
fi

# =====================================
# RÉSUMÉ
# =====================================
echo -e "\n${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              MIGRATION TERMINÉE                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}✓ Migration v3.5.0 complétée avec succès${NC}\n"

echo -e "${YELLOW}PROCHAINES ACTIONS:${NC}"
echo "1. Testez la génération de PDF depuis l'interface web"
echo "   - Attestation de travail (vérifiez le QR code)"
echo "   - Contrat de travail (vérifiez le numéro + QR code)"
echo "   - Rapport salaires (vérifiez le footer)"
echo ""
echo "2. Si tout fonctionne, supprimez le backup:"
echo "   rm $BACKUP_FILE"
echo ""
echo "3. En cas de problème, restaurez le backup:"
echo "   mysql -u $DB_USER -p $DB_NAME < $BACKUP_FILE"
echo ""
echo -e "${YELLOW}Logs en temps réel:${NC}"
if systemctl is-active --quiet ayhr-backend; then
    echo "  sudo journalctl -u ayhr-backend -f"
elif command -v pm2 &> /dev/null; then
    echo "  pm2 logs ayhr-backend"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

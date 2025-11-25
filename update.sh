#!/bin/bash

# Configuration
APP_DIR="/opt/ay-hr"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
LOG_FILE="$APP_DIR/logs/update.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting AY HR System Update...${NC}"
echo "Date: $(date)" | tee -a "$LOG_FILE"

# Check root
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}Please run as root${NC}"
  exit 1
fi

# 1. Update Code
echo -e "${GREEN}[1/5] Pulling latest code from GitHub...${NC}"
cd "$APP_DIR" || exit
git pull origin main | tee -a "$LOG_FILE"

# 2. Update Backend
echo -e "${GREEN}[2/5] Updating Backend dependencies...${NC}"
cd "$BACKEND_DIR" || exit
source .venv/bin/activate
pip install -r requirements.txt | tee -a "$LOG_FILE"
# Clean cache
find . -type d -name "__pycache__" -exec rm -rf {} +
deactivate

# 3. Update Frontend
echo -e "${GREEN}[3/5] Building Frontend...${NC}"
cd "$FRONTEND_DIR" || exit
npm install | tee -a "$LOG_FILE"
npm run build | tee -a "$LOG_FILE"

# 4. Permissions
echo -e "${GREEN}[4/5] Fixing permissions...${NC}"
chown -R root:root "$APP_DIR"
chmod +x "$APP_DIR"/*.sh

# 5. Restart Services
echo -e "${GREEN}[5/5] Restarting services...${NC}"
systemctl restart ayhr-backend
systemctl restart ayhr-frontend

# Status check
if systemctl is-active --quiet ayhr-backend && systemctl is-active --quiet ayhr-frontend; then
    echo -e "${GREEN}✅ Update completed successfully!${NC}"
    echo -e "Backend Status: ${GREEN}Active${NC}"
    echo -e "Frontend Status: ${GREEN}Active${NC}"
else
    echo -e "${RED}❌ Update completed with errors. Check logs.${NC}"
    systemctl status ayhr-backend ayhr-frontend
fi

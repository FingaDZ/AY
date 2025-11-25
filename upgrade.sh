#!/bin/bash

#############################################
# AY HR System - Upgrade to v1.3.0-beta
# Attendance Integration Backend
#############################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AY HR - Upgrade to v1.3.0-beta${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

APP_DIR="/opt/ay-hr"
BACKEND_DIR="$APP_DIR/backend"

cd "$APP_DIR" || exit

# Step 1: Git Update
echo -e "${YELLOW}[1/6] Updating code from GitHub...${NC}"
git checkout -f main
git pull origin main
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

# Step 2: Verify files
echo -e "${YELLOW}[2/6] Verifying new files...${NC}"
if [ ! -f "database/migrations/001_attendance_integration.sql" ]; then
    echo -e "${RED}✗ Migration file not found!${NC}"
    exit 1
fi
if [ ! -f "backend/models/attendance_mapping.py" ]; then
    echo -e "${RED}✗ attendance_mapping.py not found!${NC}"
    exit 1
fi
if [ ! -f "backend/services/attendance_service.py" ]; then
    echo -e "${RED}✗ attendance_service.py not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ All files present${NC}"
echo ""

# Step 3: Database Migration
echo -e "${YELLOW}[3/6] Running database migration...${NC}"
echo -e "${YELLOW}Enter MySQL root password:${NC}"
mysql -u root -p ay_hr < database/migrations/001_attendance_integration.sql

# Verify tables
echo -e "${YELLOW}Verifying tables...${NC}"
TABLES=$(mysql -u root -p ay_hr -e "SHOW TABLES LIKE 'attendance%';" 2>/dev/null | grep -c attendance || true)
if [ "$TABLES" -eq 3 ]; then
    echo -e "${GREEN}✓ 3 tables created successfully${NC}"
else
    echo -e "${RED}✗ Expected 3 tables, found $TABLES${NC}"
    exit 1
fi
echo ""

# Step 4: Update .env
echo -e "${YELLOW}[4/6] Updating backend configuration...${NC}"
if ! grep -q "ATTENDANCE_API_URL" "$BACKEND_DIR/.env"; then
    echo "" >> "$BACKEND_DIR/.env"
    echo "# Attendance Integration" >> "$BACKEND_DIR/.env"
    echo "ATTENDANCE_API_URL=http://192.168.20.56:8000/api" >> "$BACKEND_DIR/.env"
    echo "ATTENDANCE_API_TIMEOUT=30" >> "$BACKEND_DIR/.env"
    echo -e "${GREEN}✓ Configuration added${NC}"
else
    echo -e "${YELLOW}⚠ Configuration already exists${NC}"
fi
echo ""

# Step 5: Install Python dependencies (if any new)
echo -e "${YELLOW}[5/6] Updating Python dependencies...${NC}"
cd "$BACKEND_DIR"
source .venv/bin/activate
pip install -q requests  # Ensure requests is installed
deactivate
echo -e "${GREEN}✓ Dependencies updated${NC}"
echo ""

# Step 6: Restart Backend
echo -e "${YELLOW}[6/6] Restarting backend service...${NC}"
systemctl restart ayhr-backend
sleep 3

# Check status
if systemctl is-active --quiet ayhr-backend; then
    echo -e "${GREEN}✓ Backend restarted successfully${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo -e "${YELLOW}Showing last 20 log lines:${NC}"
    journalctl -u ayhr-backend -n 20 --no-pager
    exit 1
fi
echo ""

# Final verification
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Upgrade completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test API: http://192.168.20.53:8000/docs"
echo "2. Look for 'Attendance Integration' section"
echo "3. Test sync: POST /api/attendance-integration/sync-employee"
echo ""
echo -e "${YELLOW}Rollback (if needed):${NC}"
echo "mysql -u root -p ay_hr << 'EOF'"
echo "DROP TABLE IF EXISTS attendance_import_conflicts;"
echo "DROP TABLE IF EXISTS attendance_sync_log;"
echo "DROP TABLE IF EXISTS attendance_employee_mapping;"
echo "ALTER TABLE pointages DROP COLUMN IF EXISTS heures_supplementaires;"
echo "EOF"
echo ""

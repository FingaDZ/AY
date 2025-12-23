# ============================================
# Script de Déploiement Simple AY HR v3.6.1
# À exécuter sur le serveur: root@192.168.20.55
# ============================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   DEPLOIEMENT AY HR v3.6.1" -ForegroundColor Cyan
Write-Host "   Serveur: 192.168.20.55" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$SERVER = "root@192.168.20.55"
$APP_DIR = "/root/AY_HR"

Write-Host "[Etape 1] Connexion et preparation..." -ForegroundColor Yellow
ssh $SERVER "mkdir -p /root/backups/ay_hr"

Write-Host "`n[Etape 2] Sauvegarde base de donnees..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Write-Host "Veuillez entrer le mot de passe MySQL root quand demande"
ssh $SERVER "mysqldump -u root -p ay_hr > /root/backups/ay_hr/backup_$timestamp.sql"

Write-Host "`n[Etape 3] Mise a jour code depuis GitHub..." -ForegroundColor Yellow
ssh $SERVER @"
cd $APP_DIR
git fetch origin
git reset --hard origin/main
git pull origin main
"@

Write-Host "`n[Etape 4] Migration base de donnees..." -ForegroundColor Yellow
Write-Host "Veuillez entrer le mot de passe MySQL root quand demande"
ssh $SERVER "cd $APP_DIR/database && mysql -u root -p ay_hr < migration_v3.6.1_conges_credits_contrats.sql"

Write-Host "`n[Etape 5] Installation dependances backend..." -ForegroundColor Yellow
ssh $SERVER @"
cd $APP_DIR/backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
"@

Write-Host "`n[Etape 6] Redemarrage services..." -ForegroundColor Yellow
ssh $SERVER @"
pkill -f 'uvicorn main:app'
cd $APP_DIR/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/ay_hr_backend.log 2>&1 &
sleep 3
"@

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   DEPLOIEMENT TERMINE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "API Backend: http://192.168.20.55:8000/docs" -ForegroundColor Cyan
Write-Host "Logs: ssh $SERVER tail -f /var/log/ay_hr_backend.log" -ForegroundColor Cyan
Write-Host ""

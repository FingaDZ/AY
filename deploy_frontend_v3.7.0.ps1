# Script de déploiement frontend v3.7.0
# Usage: .\deploy_frontend_v3.7.0.ps1

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        DÉPLOIEMENT FRONTEND v3.7.0 sur 192.168.20.55        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$SERVER = "192.168.20.55"
$USER = "root"
$REMOTE_PATH = "/opt/ay-hr/frontend"

Write-Host "`n1. Git pull sur le serveur..." -ForegroundColor Yellow
ssh ${USER}@${SERVER} "cd ${REMOTE_PATH} && git pull origin main"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Code mis à jour" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur git pull" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Build du frontend..." -ForegroundColor Yellow
ssh ${USER}@${SERVER} "cd ${REMOTE_PATH} && npm run build"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build réussi" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur build" -ForegroundColor Red
    exit 1
}

Write-Host "`n3. Redémarrage service frontend..." -ForegroundColor Yellow
ssh ${USER}@${SERVER} "systemctl restart ayhr-frontend"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Service redémarré" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur redémarrage" -ForegroundColor Red
    exit 1
}

Write-Host "`n4. Vérification statut..." -ForegroundColor Yellow
ssh ${USER}@${SERVER} "systemctl status ayhr-frontend --no-pager -l"

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                 ✅ DÉPLOIEMENT TERMINÉ                       ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n🌐 Accès: http://192.168.20.55:3000" -ForegroundColor Cyan
Write-Host "📊 Tester: Module Congés → Sélectionner un employé → Cliquer 'Déduire'" -ForegroundColor Cyan
Write-Host ""

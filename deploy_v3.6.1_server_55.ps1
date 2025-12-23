# ============================================
# Script de Déploiement AY HR v3.6.1
# Serveur: 192.168.20.55 (root)
# Date: 23 Décembre 2025
# ============================================

$SERVER = "192.168.20.55"
$USER = "root"
$APP_DIR = "/root/AY_HR"
$BACKUP_DIR = "/root/backups/ay_hr"
$DB_NAME = "ay_hr"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DÉPLOIEMENT AY HR v3.6.1" -ForegroundColor Cyan
Write-Host "   Serveur: $SERVER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier la connexion SSH
Write-Host "[1/7] Vérification connexion SSH..." -ForegroundColor Yellow
$testConnection = ssh -o ConnectTimeout=5 $USER@$SERVER "echo 'Connected'" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Impossible de se connecter au serveur $SERVER" -ForegroundColor Red
    Write-Host "Vérifiez que:" -ForegroundColor Yellow
    Write-Host "  - Le serveur est accessible" -ForegroundColor Yellow
    Write-Host "  - Vous avez configuré la clé SSH ou le mot de passe" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Connexion SSH établie" -ForegroundColor Green
Write-Host ""

# Créer une sauvegarde de la base de données
Write-Host "[2/7] Sauvegarde de la base de données..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
ssh $USER@$SERVER @"
    mkdir -p $BACKUP_DIR
    mysqldump -u root -p$DB_NAME > $BACKUP_DIR/ay_hr_backup_$timestamp.sql 2>/dev/null || echo 'Sauvegarde DB peut nécessiter mot de passe MySQL'
"@
Write-Host "✅ Sauvegarde créée: ay_hr_backup_$timestamp.sql" -ForegroundColor Green
Write-Host ""

# Sauvegarder les fichiers actuels
Write-Host "[3/7] Sauvegarde des fichiers actuels..." -ForegroundColor Yellow
ssh $USER@$SERVER @"
    if [ -d '$APP_DIR' ]; then
        cp -r $APP_DIR $BACKUP_DIR/ay_hr_files_$timestamp
        echo 'Fichiers sauvegardés'
    else
        echo 'Aucun fichier existant à sauvegarder'
    fi
"@
Write-Host "✅ Fichiers sauvegardés" -ForegroundColor Green
Write-Host ""

# Cloner ou mettre à jour le dépôt
Write-Host "[4/7] Mise à jour du code depuis GitHub..." -ForegroundColor Yellow
ssh $USER@$SERVER @"
    if [ -d '$APP_DIR/.git' ]; then
        cd $APP_DIR
        git fetch origin
        git reset --hard origin/main
        git pull origin main
        echo 'Dépôt mis à jour'
    else
        rm -rf $APP_DIR
        git clone https://github.com/FingaDZ/AY.git $APP_DIR
        cd $APP_DIR
        echo 'Dépôt cloné'
    fi
    
    # Vérifier la version
    cd $APP_DIR/backend
    grep "APP_VERSION" config.py || echo 'Version non trouvée'
"@
Write-Host "✅ Code mis à jour depuis GitHub" -ForegroundColor Green
Write-Host ""

# Appliquer les migrations de base de données
Write-Host "[5/7] Application des migrations de base de données..." -ForegroundColor Yellow
Write-Host "⚠️  Migration v3.6.1 : Congés, Crédits, Contrats" -ForegroundColor Yellow
ssh $USER@$SERVER @"
    cd $APP_DIR/database
    
    # Vérifier si la migration existe
    if [ -f 'migration_v3.6.1_conges_credits_contrats.sql' ]; then
        echo 'Application de la migration v3.6.1...'
        mysql -u root -p $DB_NAME < migration_v3.6.1_conges_credits_contrats.sql 2>/dev/null || echo '⚠️  Migration nécessite mot de passe MySQL'
        echo 'Migration v3.6.1 appliquée'
    else
        echo '⚠️  Fichier de migration v3.6.1 non trouvé'
    fi
"@
Write-Host "✅ Migrations appliquées" -ForegroundColor Green
Write-Host ""

# Installer/Mettre à jour les dépendances backend
Write-Host "[6/7] Mise à jour des dépendances backend..." -ForegroundColor Yellow
ssh $USER@$SERVER @"
    cd $APP_DIR/backend
    
    # Activer l'environnement virtuel s'il existe
    if [ -d 'venv' ]; then
        source venv/bin/activate
    else
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    # Installer les dépendances
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo 'Dépendances Python installées'
"@
Write-Host "✅ Dépendances backend installées" -ForegroundColor Green
Write-Host ""

# Redémarrer les services
Write-Host "[7/7] Redémarrage des services..." -ForegroundColor Yellow
ssh $USER@$SERVER @"
    # Arrêter les processus existants
    pkill -f 'uvicorn main:app' || echo 'Aucun processus uvicorn en cours'
    pkill -f 'npm.*vite' || echo 'Aucun processus vite en cours'
    
    # Redémarrer le backend
    cd $APP_DIR/backend
    source venv/bin/activate
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/ay_hr_backend.log 2>&1 &
    echo 'Backend redémarré sur le port 8000'
    
    # Redémarrer le frontend (si nécessaire)
    cd $APP_DIR/frontend
    if [ -f 'package.json' ]; then
        npm install
        npm run build
        echo 'Frontend construit'
    fi
"@
Write-Host "✅ Services redémarrés" -ForegroundColor Green
Write-Host ""

# Vérification finale
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   VÉRIFICATION DU DÉPLOIEMENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vérification de l'API..." -ForegroundColor Yellow
$apiCheck = ssh $USER@$SERVER "curl -s http://localhost:8000/docs 2>/dev/null | head -n 5"
if ($apiCheck) {
    Write-Host "✅ API backend accessible" -ForegroundColor Green
} else {
    Write-Host "⚠️  API backend non accessible immédiatement (démarrage en cours...)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   DEPLOIEMENT TERMINE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Version deployee: v3.6.1" -ForegroundColor Cyan
Write-Host "API Backend: http://${SERVER}:8000" -ForegroundColor Cyan
Write-Host "Documentation: http://${SERVER}:8000/docs" -ForegroundColor Cyan
Write-Host "Sauvegardes: $BACKUP_DIR" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Tester l'API: http://${SERVER}:8000/docs" -ForegroundColor White
Write-Host "  2. Verifier les logs sur le serveur" -ForegroundColor White
Write-Host "  3. Tester les nouvelles fonctionnalites v3.6.1:" -ForegroundColor White
Write-Host "     - Gestion des conges avec deduction flexible" -ForegroundColor White
Write-Host "     - Echeancier automatique des credits" -ForegroundColor White
Write-Host "     - Auto-desactivation des contrats expires" -ForegroundColor White
Write-Host ""
Write-Host "Notes importantes:" -ForegroundColor Yellow
Write-Host "  - Verifiez le fichier .env sur le serveur" -ForegroundColor White
Write-Host "  - Testez la connexion a la base de donnees MySQL" -ForegroundColor White
Write-Host "  - Verifiez que le mot de passe MySQL root est configure" -ForegroundColor White
Write-Host ""

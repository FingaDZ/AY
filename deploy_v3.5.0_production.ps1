# Script de déploiement v3.5.0 sur serveur 192.168.20.55
# Date: 10 décembre 2025

param(
    [string]$ServerIP = "192.168.20.55",
    [string]$Username = "",
    [string]$RemotePath = "/opt/ay_hr",
    [switch]$DryRun
)

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     DÉPLOIEMENT AY HR v3.5.0 - Serveur Production       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Vérifier que l'utilisateur est fourni
if ([string]::IsNullOrEmpty($Username)) {
    $Username = Read-Host "Nom d'utilisateur SSH sur le serveur $ServerIP"
}

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Serveur: $ServerIP"
Write-Host "  Utilisateur: $Username"
Write-Host "  Chemin distant: $RemotePath"
Write-Host "  Mode: $(if($DryRun){'DRY RUN (test)'}else{'PRODUCTION'})`n"

if ($DryRun) {
    Write-Host "MODE DRY RUN - Aucune modification ne sera effectuée" -ForegroundColor Yellow
}

# Confirmation
$confirm = Read-Host "Continuer avec le déploiement? (oui/non)"
if ($confirm -ne "oui") {
    Write-Host "Déploiement annulé." -ForegroundColor Red
    exit 1
}

# =====================================
# ÉTAPE 1: Test de connexion
# =====================================
Write-Host "`n[1/7] Test de connexion SSH..." -ForegroundColor Green

if ($DryRun) {
    Write-Host "  [DRY RUN] Test connexion SSH vers $Username@$ServerIP" -ForegroundColor Yellow
} else {
    $testCmd = "ssh -o ConnectTimeout=5 $Username@$ServerIP 'echo OK'"
    $result = Invoke-Expression $testCmd 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Échec de connexion SSH" -ForegroundColor Red
        Write-Host "  Vérifiez: ssh $Username@$ServerIP" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "  ✓ Connexion SSH établie" -ForegroundColor Green
}

# =====================================
# ÉTAPE 2: Backup avant migration
# =====================================
Write-Host "`n[2/7] Création du backup de la base de données..." -ForegroundColor Green

$backupCmd = @"
mysqldump -u root -p ay_hr > /tmp/ay_hr_backup_$(date +%Y%m%d_%H%M%S).sql && \
echo 'Backup créé dans /tmp/'
"@

if ($DryRun) {
    Write-Host "  [DRY RUN] Création backup: /tmp/ay_hr_backup_YYYYMMDD_HHMMSS.sql" -ForegroundColor Yellow
} else {
    Write-Host "  Note: Le mot de passe MySQL sera demandé" -ForegroundColor Yellow
    ssh "$Username@$ServerIP" $backupCmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Backup créé avec succès" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Échec création backup" -ForegroundColor Red
        $continue = Read-Host "Continuer sans backup? (oui/non)"
        if ($continue -ne "oui") { exit 1 }
    }
}

# =====================================
# ÉTAPE 3: Transfert des fichiers
# =====================================
Write-Host "`n[3/7] Transfert des fichiers modifiés..." -ForegroundColor Green

$files = @(
    @{Local="database\migrations\add_numero_anem.sql"; Remote="$RemotePath/database/migrations/"},
    @{Local="backend\services\pdf_generator.py"; Remote="$RemotePath/backend/services/"},
    @{Local="backend\config.py"; Remote="$RemotePath/backend/"}
)

foreach ($file in $files) {
    $localPath = "f:\Code\AY HR\$($file.Local)"
    $remotePath = "$Username@$ServerIP`:$($file.Remote)"
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Transfert: $($file.Local) -> $($file.Remote)" -ForegroundColor Yellow
    } else {
        Write-Host "  Transfert: $($file.Local)..."
        scp $localPath $remotePath
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $($file.Local) transféré" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Échec transfert $($file.Local)" -ForegroundColor Red
            exit 1
        }
    }
}

# =====================================
# ÉTAPE 4: Migration base de données
# =====================================
Write-Host "`n[4/7] Exécution de la migration SQL..." -ForegroundColor Green

$migrationCmd = @"
cd $RemotePath && \
mysql -u root -p ay_hr < database/migrations/add_numero_anem.sql && \
mysql -u root -p ay_hr -e "DESCRIBE employes;" | grep numero_anem
"@

if ($DryRun) {
    Write-Host "  [DRY RUN] Exécution: add_numero_anem.sql" -ForegroundColor Yellow
} else {
    Write-Host "  Note: Le mot de passe MySQL sera demandé" -ForegroundColor Yellow
    ssh "$Username@$ServerIP" $migrationCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Migration SQL exécutée avec succès" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Échec de la migration SQL" -ForegroundColor Red
        Write-Host "  Vérifiez les logs MySQL" -ForegroundColor Yellow
        exit 1
    }
}

# =====================================
# ÉTAPE 5: Installation dépendances
# =====================================
Write-Host "`n[5/7] Installation des dépendances Python..." -ForegroundColor Green

$depsCmd = @"
cd $RemotePath/backend && \
source venv/bin/activate && \
pip install qrcode[pil] pillow reportlab --quiet && \
python -c "import qrcode; from reportlab.lib.utils import ImageReader; print('OK')"
"@

if ($DryRun) {
    Write-Host "  [DRY RUN] Installation: qrcode, pillow, reportlab" -ForegroundColor Yellow
} else {
    ssh "$Username@$ServerIP" $depsCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Dépendances installées" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Échec installation dépendances" -ForegroundColor Red
        exit 1
    }
}

# =====================================
# ÉTAPE 6: Redémarrage backend
# =====================================
Write-Host "`n[6/7] Redémarrage du backend..." -ForegroundColor Green

$restartCmd = @"
sudo systemctl restart ayhr-backend && \
sleep 3 && \
sudo systemctl is-active ayhr-backend
"@

if ($DryRun) {
    Write-Host "  [DRY RUN] Redémarrage: systemctl restart ayhr-backend" -ForegroundColor Yellow
} else {
    ssh "$Username@$ServerIP" $restartCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Backend redémarré avec succès" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Échec redémarrage automatique" -ForegroundColor Yellow
        Write-Host "  Essayez manuellement: sudo systemctl restart ayhr-backend" -ForegroundColor Yellow
    }
}

# =====================================
# ÉTAPE 7: Tests de validation
# =====================================
Write-Host "`n[7/7] Tests de validation..." -ForegroundColor Green

$testCmd = @"
curl -s http://localhost:8000/ | grep -o '3.5.0' && \
mysql -u root -p ay_hr -e "SHOW COLUMNS FROM employes LIKE 'numero_anem';" | grep numero_anem
"@

if ($DryRun) {
    Write-Host "  [DRY RUN] Tests:" -ForegroundColor Yellow
    Write-Host "    - Version API: 3.5.0" -ForegroundColor Yellow
    Write-Host "    - Colonne numero_anem existe" -ForegroundColor Yellow
} else {
    Write-Host "  Test 1: Vérification version API..."
    ssh "$Username@$ServerIP" "curl -s http://localhost:8000/ 2>/dev/null" | Select-String "3.5.0" | Out-Null
    
    if ($?) {
        Write-Host "  ✓ Version 3.5.0 détectée" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Version non détectée" -ForegroundColor Red
    }
    
    Write-Host "  Test 2: Vérification colonne numero_anem..."
    Write-Host "  Note: Le mot de passe MySQL sera demandé" -ForegroundColor Yellow
    ssh "$Username@$ServerIP" "mysql -u root -p ay_hr -e 'SHOW COLUMNS FROM employes LIKE \"numero_anem\";' 2>/dev/null" | Select-String "numero_anem" | Out-Null
    
    if ($?) {
        Write-Host "  ✓ Colonne numero_anem existe" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Colonne non trouvée" -ForegroundColor Red
    }
}

# =====================================
# RÉSUMÉ
# =====================================
Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              DÉPLOIEMENT TERMINÉ                         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "MODE DRY RUN - Aucune modification effectuée" -ForegroundColor Yellow
    Write-Host "Relancez sans -DryRun pour déployer réellement`n" -ForegroundColor Yellow
} else {
    Write-Host "PROCHAINES ACTIONS:" -ForegroundColor Yellow
    Write-Host "1. Testez la génération de PDF depuis l'interface"
    Write-Host "   - Attestation de travail (QR code)"
    Write-Host "   - Contrat de travail (numéro + QR code)"
    Write-Host "   - Rapport salaires (footer)"
    Write-Host ""
    Write-Host "2. Vérifiez les logs:"
    Write-Host "   ssh $Username@$ServerIP"
    Write-Host "   sudo journalctl -u ayhr-backend -n 50"
    Write-Host ""
    Write-Host "3. En cas de problème, restaurez le backup:"
    Write-Host "   mysql -u root -p ay_hr < /tmp/ay_hr_backup_*.sql`n"
}

Write-Host "✓ Script terminé" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n"

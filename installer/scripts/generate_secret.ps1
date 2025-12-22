# ====================================
# Génération de la clé secrète
# ====================================

Write-Host "[INFO] Génération de la clé secrète JWT..." -ForegroundColor Cyan

# Générer une clé aléatoire de 64 caractères
$SecretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})

# Chemin du fichier .env
$EnvFile = Join-Path $PSScriptRoot "..\..\.env"

# Lire le fichier .env
$Content = Get-Content $EnvFile -Raw

# Remplacer la clé secrète
$Content = $Content -replace 'SECRET_KEY=.*', "SECRET_KEY=$SecretKey"

# Mettre à jour l'URL de la base de données
$Content = $Content -replace 'DATABASE_URL=.*', 'DATABASE_URL=mysql+pymysql://ayhr_user:ayhr_password_2024@localhost:3307/ay_hr'

# Sauvegarder
Set-Content -Path $EnvFile -Value $Content -NoNewline

Write-Host "[SUCCESS] Clé secrète générée et fichier .env configuré !" -ForegroundColor Green
Write-Host "[INFO] Fichier: $EnvFile" -ForegroundColor Yellow

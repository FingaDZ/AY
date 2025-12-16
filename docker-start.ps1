# Quick Start Script pour Docker - AY HR System v3.6.0 (Windows)
# Usage: .\docker-start.ps1

$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "  AY HR System v3.6.0 - Docker Setup  " -ForegroundColor Blue
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host ""

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker installé: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas installé" -ForegroundColor Red
    Write-Host "Installez Docker Desktop: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker compose version
    Write-Host "✓ Docker Compose installé: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose n'est pas disponible" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check .env file
if (-Not (Test-Path ".env")) {
    Write-Host "⚠ Fichier .env non trouvé" -ForegroundColor Yellow
    Write-Host "Création de .env depuis .env.docker..."
    Copy-Item ".env.docker" ".env"
    
    # Generate SECRET_KEY
    $bytes = New-Object byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $SECRET_KEY = [BitConverter]::ToString($bytes) -replace '-', ''
    
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace "your-secret-key-generate-with-openssl-rand-hex-32", $SECRET_KEY.ToLower()
    Set-Content ".env" $envContent
    
    Write-Host "✓ Fichier .env créé" -ForegroundColor Green
    Write-Host "⚠ Modifiez le fichier .env avec vos paramètres" -ForegroundColor Yellow
    Write-Host ""
    
    $edit = Read-Host "Voulez-vous éditer .env maintenant? (y/N)"
    if ($edit -eq 'y' -or $edit -eq 'Y') {
        notepad .env
    }
}

# Build and start
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "  Démarrage des conteneurs Docker...  " -ForegroundColor Blue
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

docker compose up -d --build

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host "  Attente du démarrage des services... " -ForegroundColor Blue
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
Write-Host ""

# Wait for MySQL
Write-Host "MySQL: " -NoNewline
for ($i = 1; $i -le 30; $i++) {
    try {
        docker exec ayhr-mysql mysqladmin ping -h localhost --silent 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Prêt" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    Write-Host "." -NoNewline
}
Write-Host ""

# Wait for Backend
Write-Host "Backend: " -NoNewline
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Prêt" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    Write-Host "." -NoNewline
}
Write-Host ""

# Wait for Frontend
Write-Host "Frontend: " -NoNewline
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Prêt" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline
}
Write-Host ""

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host "    ✓ Installation terminée !          " -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Statut des conteneurs:" -ForegroundColor Blue
docker compose ps
Write-Host ""
Write-Host "🌐 URLs d'accès:" -ForegroundColor Blue
Write-Host "  • Frontend:   http://localhost" -ForegroundColor Green
Write-Host "  • Backend:    http://localhost:8000" -ForegroundColor Green
Write-Host "  • API Docs:   http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "🔐 Credentials par défaut:" -ForegroundColor Blue
Write-Host "  • Email:      admin@ay-hr.com" -ForegroundColor Yellow
Write-Host "  • Password:   Admin@2024!" -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 Commandes utiles:" -ForegroundColor Blue
Write-Host "  • Voir les logs:    docker compose logs -f" -ForegroundColor Yellow
Write-Host "  • Arrêter:          docker compose down" -ForegroundColor Yellow
Write-Host "  • Redémarrer:       docker compose restart" -ForegroundColor Yellow
Write-Host "  • Shell backend:    docker exec -it ayhr-backend bash" -ForegroundColor Yellow
Write-Host "  • MySQL console:    docker exec -it ayhr-mysql mysql -u root -p" -ForegroundColor Yellow
Write-Host ""
Write-Host "✓ Accédez à l'application: http://localhost" -ForegroundColor Green
Write-Host ""

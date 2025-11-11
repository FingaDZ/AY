# Script de test des endpoints API
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AY HR - Test des Endpoints API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api"

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -ErrorAction Stop
        $status = $response.StatusCode
        
        if ($status -eq 200) {
            Write-Host "✅ $Name" -NoNewline
            Write-Host " - " -NoNewline
            Write-Host "OK ($status)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $Name" -NoNewline
            Write-Host " - " -NoNewline
            Write-Host "Unexpected ($status)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ $Name" -NoNewline
        Write-Host " - " -NoNewline
        Write-Host "FAILED" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor DarkRed
    }
}

Write-Host "Testing endpoints..." -ForegroundColor White
Write-Host ""

# Test des endpoints principaux
Test-Endpoint "Health Check" "$baseUrl/../health"
Test-Endpoint "Root" "$baseUrl/.."
Write-Host ""

Test-Endpoint "Employés (List)" "$baseUrl/employes/"
Test-Endpoint "Employés (Actifs)" "$baseUrl/employes/?statut=Actif"
Write-Host ""

Test-Endpoint "Clients (List)" "$baseUrl/clients/"
Write-Host ""

Test-Endpoint "Missions (List)" "$baseUrl/missions/"
Write-Host ""

Test-Endpoint "Pointages (List)" "$baseUrl/pointages/"
Write-Host ""

Test-Endpoint "Avances (List)" "$baseUrl/avances/"
Write-Host ""

Test-Endpoint "Crédits (List)" "$baseUrl/credits/"
Write-Host ""

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test terminé" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

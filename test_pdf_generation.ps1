# Test PDF generation endpoints

$baseUrl = "http://localhost:8000/api"

Write-Host "=== Test Génération PDF ===" -ForegroundColor Cyan

# Test 1: Get a mission to generate ordre
Write-Host "`n1. Récupération d'une mission..." -ForegroundColor Yellow
$missions = Invoke-RestMethod -Uri "$baseUrl/missions/" -Method Get
if ($missions.missions.Count -gt 0) {
    $missionId = $missions.missions[0].id
    Write-Host "Mission ID: $missionId" -ForegroundColor Green
    
    # Test 2: Generate ordre de mission PDF
    Write-Host "`n2. Génération ordre de mission PDF..." -ForegroundColor Yellow
    try {
        $pdfPath = "f:\Code\AY HR\test_ordre_mission_$missionId.pdf"
        Invoke-RestMethod -Uri "$baseUrl/missions/$missionId/ordre-mission/pdf" -Method Get -OutFile $pdfPath
        if (Test-Path $pdfPath) {
            $fileSize = (Get-Item $pdfPath).Length
            Write-Host "OK - PDF ordre de mission genere: $pdfPath ($fileSize bytes)" -ForegroundColor Green
        }
    } catch {
        Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Test 3: Generate rapport PDF
    Write-Host "`n3. Génération rapport missions PDF..." -ForegroundColor Yellow
    try {
        $pdfPath = "f:\Code\AY HR\test_rapport_missions.pdf"
        Invoke-RestMethod -Uri "$baseUrl/missions/rapport/pdf" -Method Post -OutFile $pdfPath
        if (Test-Path $pdfPath) {
            $fileSize = (Get-Item $pdfPath).Length
            Write-Host "OK - PDF rapport genere: $pdfPath ($fileSize bytes)" -ForegroundColor Green
        }
    } catch {
        Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Aucune mission trouvée pour tester" -ForegroundColor Red
}

Write-Host "`n=== Tests terminés ===" -ForegroundColor Cyan

# Test du nouvel ordre de mission A5

$baseUrl = "http://localhost:8000/api"

Write-Host "=== Test Ordre de Mission A5 ===" -ForegroundColor Cyan

# Get mission
$missions = Invoke-RestMethod -Uri "$baseUrl/missions/" -Method Get
if ($missions.missions.Count -gt 0) {
    $mission = $missions.missions[0]
    $missionId = $mission.id
    $dateStr = $mission.date_mission
    
    Write-Host "`nMission ID: $missionId" -ForegroundColor Yellow
    Write-Host "Date: $dateStr" -ForegroundColor Yellow
    
    # Format attendu: YYMMDD-XXXXX
    $date = [DateTime]::Parse($dateStr)
    $yymmdd = $date.ToString("yyMMdd")
    $numeroAttendu = "$yymmdd-$($missionId.ToString('00000'))"
    Write-Host "Numero attendu: $numeroAttendu" -ForegroundColor Cyan
    
    # Generate PDF
    Write-Host "`nGeneration PDF..." -ForegroundColor Yellow
    try {
        $pdfPath = "f:\Code\AY HR\test_ordre_A5.pdf"
        Invoke-RestMethod -Uri "$baseUrl/missions/$missionId/ordre-mission/pdf" -Method Get -OutFile $pdfPath
        
        if (Test-Path $pdfPath) {
            $fileSize = (Get-Item $pdfPath).Length
            Write-Host "OK - PDF genere: $pdfPath" -ForegroundColor Green
            Write-Host "Taille: $fileSize bytes" -ForegroundColor Green
            Write-Host "`nCaracteristiques:" -ForegroundColor Cyan
            Write-Host "- Format: A5 (148mm x 210mm)" -ForegroundColor White
            Write-Host "- Couleurs: Noir et blanc" -ForegroundColor White
            Write-Host "- Numero: Format YYMMDD-XXXXX" -ForegroundColor White
            Write-Host "- Date: Une seule date" -ForegroundColor White
            Write-Host "- Signatures: Chauffeur, Client, Responsable" -ForegroundColor White
            Write-Host "`nOuvrez le fichier pour verifier!" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Aucune mission trouvee" -ForegroundColor Red
}

Write-Host "`n=== Test termine ===" -ForegroundColor Cyan

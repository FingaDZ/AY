# Test script for missions CRUD and filters

$baseUrl = "http://localhost:8000/api"

Write-Host "=== Test Missions CRUD et Filtres ===" -ForegroundColor Cyan

# Test 1: List all missions
Write-Host "`n1. Lister toutes les missions..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$baseUrl/missions/" -Method Get
Write-Host "Total missions: $($response.total)" -ForegroundColor Green
Write-Host "Missions trouvées: $($response.missions.Count)"

# Test 2: Filter by chauffeur
if ($response.missions.Count -gt 0) {
    $firstMission = $response.missions[0]
    $chauffeurId = $firstMission.chauffeur_id
    
    Write-Host "`n2. Filtrer par chauffeur (ID: $chauffeurId)..." -ForegroundColor Yellow
    $filtered = Invoke-RestMethod -Uri "$baseUrl/missions/?chauffeur_id=$chauffeurId" -Method Get
    Write-Host "Missions pour ce chauffeur: $($filtered.total)" -ForegroundColor Green
}

# Test 3: Get totaux chauffeur
Write-Host "`n3. Obtenir totaux par chauffeur..." -ForegroundColor Yellow
$totaux = Invoke-RestMethod -Uri "$baseUrl/missions/totaux-chauffeur" -Method Get
Write-Host "Chauffeurs avec missions: $($totaux.totaux.Count)" -ForegroundColor Green
foreach ($t in $totaux.totaux) {
    Write-Host "  - $($t.nom_complet): $($t.nombre_missions) missions, $($t.total_distance) km, $($t.total_primes) DA"
}

# Test 4: Update a mission (if any exist)
if ($response.missions.Count -gt 0) {
    $missionId = $response.missions[0].id
    Write-Host "`n4. Mise à jour mission (ID: $missionId)..." -ForegroundColor Yellow
    
    # Get mission details
    $mission = $response.missions[0]
    
    # Update data
    $updateData = @{
        date_mission = $mission.date_mission
        chauffeur_id = $mission.chauffeur_id
        client_id = $mission.client_id
    } | ConvertTo-Json
    
    try {
        $updated = Invoke-RestMethod -Uri "$baseUrl/missions/$missionId" -Method Put -Body $updateData -ContentType "application/json"
        Write-Host "Mission mise à jour avec succès!" -ForegroundColor Green
        Write-Host "  Distance: $($updated.distance) km, Prime: $($updated.prime_calculee) DA"
    } catch {
        Write-Host "Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== Tests terminés ===" -ForegroundColor Cyan

# Test rapide des endpoints v3.7.0
# Usage: .\test_v3.7.0_quick.ps1

$BASE_URL = "http://192.168.20.55:8000/api"
$EMPLOYE_ID = 1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " TEST RAPIDE v3.7.0 - Endpoints Déductions Congés" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n1. Test Synthèse Congés (GET /conges/synthese/$EMPLOYE_ID)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/conges/synthese/$EMPLOYE_ID" -Method Get
    $response | ConvertTo-Json -Depth 5
    Write-Host "✅ OK" -ForegroundColor Green
} catch {
    Write-Host "❌ ERREUR: $_" -ForegroundColor Red
}

Write-Host "`n2. Test Calcul Solde (GET /deductions-conges/solde/$EMPLOYE_ID)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/deductions-conges/solde/$EMPLOYE_ID" -Method Get
    $response | ConvertTo-Json -Depth 5
    Write-Host "✅ OK" -ForegroundColor Green
} catch {
    Write-Host "❌ ERREUR: $_" -ForegroundColor Red
}

Write-Host "`n3. Test Liste Déductions (GET /deductions-conges/employe/$EMPLOYE_ID)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/deductions-conges/employe/$EMPLOYE_ID" -Method Get
    Write-Host "Nombre de déductions: $($response.Count)"
    $response | ConvertTo-Json -Depth 3
    Write-Host "✅ OK" -ForegroundColor Green
} catch {
    Write-Host "❌ ERREUR: $_" -ForegroundColor Red
}

Write-Host "`n4. Test Liste Tous les Congés (GET /conges/?employe_id=$EMPLOYE_ID)" -ForegroundColor Yellow
Write-Host "------------------------------------------------------------"
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/conges/?employe_id=$EMPLOYE_ID" -Method Get
    Write-Host "Nombre de périodes: $($response.Count)"
    $response | Select-Object -First 3 | ConvertTo-Json -Depth 2
    Write-Host "✅ OK" -ForegroundColor Green
} catch {
    Write-Host "❌ ERREUR: $_" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " RÉSUMÉ DES TESTS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`nPour créer une déduction (nécessite authentification):"
Write-Host @"
curl -X POST http://192.168.20.55:8000/api/deductions-conges/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "employe_id": 1,
    "jours_deduits": 2.5,
    "mois_deduction": 12,
    "annee_deduction": 2024,
    "type_conge": "ANNUEL"
  }'
"@

Write-Host "`nEndpoints disponibles:" -ForegroundColor Cyan
Write-Host "  GET  /api/conges/synthese/{id}           - Synthèse avec totaux"
Write-Host "  GET  /api/deductions-conges/solde/{id}   - Calcul détaillé solde"
Write-Host "  GET  /api/deductions-conges/employe/{id} - Liste déductions"
Write-Host "  POST /api/deductions-conges/             - Créer déduction (auth)"
Write-Host "  DELETE /api/deductions-conges/{id}       - Supprimer (auth)"

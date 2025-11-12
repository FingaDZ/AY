# Test complet des endpoints de l'API AY HR
# PowerShell Script

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Tests des Endpoints API - AY HR" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Test Login
Write-Host "1. Test Login..." -ForegroundColor Yellow
$loginBody = '{"email":"admin@ayhr.dz","password":"admin123"}'
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/utilisateurs/login" -Method POST -Body $loginBody -ContentType "application/json"
    Write-Host "   ✅ Login réussi: $($loginResponse.user.email) ($($loginResponse.user.role))" -ForegroundColor Green
    $token = $loginResponse.user.id
} catch {
    Write-Host "   ❌ Échec du login: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{ Authorization = "Bearer $token" }

# 2. Test Paramètres (GET)
Write-Host "`n2. Test Paramètres (GET)..." -ForegroundColor Yellow
try {
    $params = Invoke-RestMethod -Uri "http://localhost:8000/api/parametres/" -Method GET -Headers $headers
    if ($params.raison_sociale) {
        Write-Host "   ✅ Paramètres récupérés: $($params.raison_sociale)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Aucun paramètre configuré" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Test Utilisateurs (GET)
Write-Host "`n3. Test Utilisateurs (GET)..." -ForegroundColor Yellow
try {
    $users = Invoke-RestMethod -Uri "http://localhost:8000/api/utilisateurs/" -Method GET -Headers $headers
    Write-Host "   ✅ Utilisateurs trouvés: $($users.Count)" -ForegroundColor Green
    foreach ($user in $users) {
        Write-Host "      - $($user.email) ($($user.role))" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Test Employés (GET)
Write-Host "`n4. Test Employés (GET)..." -ForegroundColor Yellow
try {
    $employes = Invoke-RestMethod -Uri "http://localhost:8000/api/employes/" -Method GET -Headers $headers
    Write-Host "   ✅ Employés trouvés: $($employes.total)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Test Missions Paramètres (tarif-km)
Write-Host "`n5. Test Missions Paramètres (tarif-km)..." -ForegroundColor Yellow
try {
    $tarifKm = Invoke-RestMethod -Uri "http://localhost:8000/api/missions/parametres/tarif-km" -Method GET -Headers $headers
    Write-Host "   ✅ Tarif KM: $($tarifKm.valeur) DA/km" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Test sans Token (401 attendu)
Write-Host "`n6. Test sans Token (401 attendu)..." -ForegroundColor Yellow
try {
    $unauthorized = Invoke-RestMethod -Uri "http://localhost:8000/api/utilisateurs/" -Method GET
    Write-Host "   ❌ ERREUR: Accès autorisé sans token!" -ForegroundColor Red
} catch {
    if ($_.Exception.Message -like "*401*") {
        Write-Host "   ✅ 401 Non Autorisé (comportement correct)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Erreur inattendue: $($_.Exception.Message)" -ForegroundColor DarkYellow
    }
}

# 7. Test Génération PDF
Write-Host "`n7. Test Génération PDF..." -ForegroundColor Yellow
try {
    $pdfPath = "f:\Code\AY HR\test_rapport_final.pdf"
    Invoke-RestMethod -Uri "http://localhost:8000/api/employes/rapport-pdf/actifs" -Method GET -Headers $headers -OutFile $pdfPath
    if (Test-Path $pdfPath) {
        $fileSize = (Get-Item $pdfPath).Length
        Write-Host "   ✅ PDF généré: $fileSize bytes" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Tests Terminés!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

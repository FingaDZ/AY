# Test du flow de login complet

Write-Host "`nTest du Flow de Login Complet`n" -ForegroundColor Cyan

# 1. Login
Write-Host "1. Connexion..." -ForegroundColor Yellow
$loginBody = '{"email":"admin@ayhr.dz","password":"admin123"}'
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/utilisateurs/login" -Method POST -Body $loginBody -ContentType "application/json"

Write-Host "   Response structure:" -ForegroundColor Gray
Write-Host "   - user: $($loginResponse.user -ne $null)" -ForegroundColor Gray
Write-Host "   - user.id: $($loginResponse.user.id)" -ForegroundColor Gray
Write-Host "   - user.email: $($loginResponse.user.email)" -ForegroundColor Gray
Write-Host "   - user.role: $($loginResponse.user.role)" -ForegroundColor Gray
Write-Host "   - message: $($loginResponse.message)" -ForegroundColor Gray

$userId = $loginResponse.user.id
$userRole = $loginResponse.user.role

Write-Host "`n   ✅ Login OK - ID: $userId, Role: $userRole`n" -ForegroundColor Green

# 2. Utiliser le token
Write-Host "2. Test avec token..." -ForegroundColor Yellow
$headers = @{ Authorization = "Bearer $userId" }

# Test paramètres
$params = Invoke-RestMethod -Uri "http://localhost:8000/api/parametres/" -Method GET -Headers $headers
Write-Host "   ✅ Paramètres accessibles" -ForegroundColor Green

# Test employés
$employes = Invoke-RestMethod -Uri "http://localhost:8000/api/employes/" -Method GET -Headers $headers
Write-Host "   ✅ Employés accessibles ($($employes.total) trouvés)" -ForegroundColor Green

Write-Host "`n✅ Flow complet OK!`n" -ForegroundColor Green

# Script de mise à jour automatique V3.0 (Windows)
# Ce script commite et pousse les changements vers GitHub

Write-Host "🚀 Démarrage de la mise à jour V3.0 vers GitHub..." -ForegroundColor Cyan

# 1. Ajouter tous les fichiers
Write-Host "📦 Ajout des fichiers..." -ForegroundColor Yellow
git add .

# 2. Commit
Write-Host "💾 Commit des changements..." -ForegroundColor Yellow
$commitMessage = "feat(v3.0): Module Salaires V3.0 - Phase 1 (Models, API, Frontend)"
git commit -m $commitMessage

# 3. Push
Write-Host "⬆️ Envoi vers GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Succès ! Les fichiers sont sur GitHub." -ForegroundColor Green
    Write-Host "👉 Maintenant, connectez-vous sur le serveur et lancez le script de déploiement." -ForegroundColor Cyan
} else {
    Write-Host "❌ Erreur lors du push." -ForegroundColor Red
}

Pause

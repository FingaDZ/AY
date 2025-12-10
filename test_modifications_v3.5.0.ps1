# Script de Test PDF v3.5.0
# Vérifie que toutes les modifications sont bien implémentées

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  TEST DES MODIFICATIONS PDF v3.5.0" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$errors = 0
$warnings = 0

# Fonction pour vérifier présence de chaîne dans fichier
function Test-StringInFile {
    param($FilePath, $SearchString, $Description)
    
    $content = Get-Content $FilePath -Raw
    if ($content -match [regex]::Escape($SearchString)) {
        Write-Host "[OK] $Description" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[ERREUR] $Description - Non trouvé: $SearchString" -ForegroundColor Red
        $script:errors++
        return $false
    }
}

# Test 1: Vérifier import ImageReader
Write-Host "`n--- Test 1: Imports ---" -ForegroundColor Yellow
Test-StringInFile "backend\services\pdf_generator.py" "from reportlab.lib.utils import ImageReader" "Import ImageReader pour QR codes"

# Test 2: Footer rapport salaires
Write-Host "`n--- Test 2: Rapport Salaires ---" -ForegroundColor Yellow
Test-StringInFile "backend\services\pdf_generator.py" "def add_page_footer(canvas, doc):" "Fonction footer rapport"
Test-StringInFile "backend\services\pdf_generator.py" "Powered by AIRBAND" "Footer AIRBAND"
Test-StringInFile "backend\services\pdf_generator.py" "rightMargin=0.5*cm, leftMargin=0.5*cm" "Marges étroites rapport"

# Test 3: Page de garde bulletins
Write-Host "`n--- Test 3: Page de Garde Bulletins ---" -ForegroundColor Yellow
Test-StringInFile "backend\services\pdf_generator.py" "Total CNAS 9%" "Total CNAS 9%"
Test-StringInFile "backend\services\pdf_generator.py" "Total IRG" "Total IRG"
Test-StringInFile "backend\services\pdf_generator.py" "leftMargin=0.75*cm, rightMargin=0.75*cm" "Marges page de garde"

# Test 4: Bulletin individuel
Write-Host "`n--- Test 4: Bulletin Individuel ---" -ForegroundColor Yellow
Test-StringInFile "backend\services\pdf_generator.py" "Jours de congé pris ce mois" "Ligne jours de congé"

# Test 5: QR Codes attestations/certificats
Write-Host "`n--- Test 5: QR Codes (Attestations/Certificats) ---" -ForegroundColor Yellow
Test-StringInFile "backend\services\pdf_generator.py" "qr_data_attestation" "Génération QR attestation"
Test-StringInFile "backend\services\pdf_generator.py" "N°ANEM:" "N°ANEM dans QR attestation"
Test-StringInFile "backend\services\pdf_generator.py" "signature_qr_table" "Table signature + QR"

# Test 6: Contrat de travail - Modifications complètes
Write-Host "`n--- Test 6: Contrat de Travail (13 modifications) ---" -ForegroundColor Yellow
Test-StringInFile "backend\services\pdf_generator.py" "numero_contrat = f`"CT-{employe_data.get('id', 0):04d}-{datetime.now().year}`"" "Numéro contrat généré"
Test-StringInFile "backend\services\pdf_generator.py" "qr_data_contrat" "QR code contrat"
Test-StringInFile "backend\services\pdf_generator.py" "N° ANEM : {numero_anem}" "N°ANEM dans section salarié"
Test-StringInFile "backend\services\pdf_generator.py" "Date de Recrutement :" "Label Date de Recrutement"
Test-StringInFile "backend\services\pdf_generator.py" "duree_mois_calculee" "Calcul durée en mois"
Test-StringInFile "backend\services\pdf_generator.py" "Helvetica-Bold" "Poste en gras (Article 1)"
Test-StringInFile "backend\services\pdf_generator.py" "déplacements sur le" "Mention déplacements (Article 3)"
Test-StringInFile "backend\services\pdf_generator.py" "Ce salaire pourra être complété par les primes prévues par le règlement intérieur et la législation en vigueur." "Article 5 une ligne"
Test-StringInFile "backend\services\pdf_generator.py" "Indemnité de Nuisance (IN)" "Primes réelles Article 6"
Test-StringInFile "backend\services\pdf_generator.py" "y -= 15" "Articles compactés (y -= 15)"
Test-StringInFile "backend\services\pdf_generator.py" "quinze (15) jours" "Préavis 15 jours (Article 9)"
Test-StringInFile "backend\services\pdf_generator.py" "tribunal de Chelghoum Laid" "Tribunal Chelghoum Laid (Article 10)"
Test-StringInFile "backend\services\pdf_generator.py" "Page {page_num}/2" "Numérotation pages"

# Test 7: Versions mises à jour
Write-Host "`n--- Test 7: Versions ---" -ForegroundColor Yellow
Test-StringInFile "backend\config.py" "APP_VERSION: str = `"3.5.0`"" "Version backend 3.5.0"
Test-StringInFile "frontend\package.json" "`"version`": `"3.5.0`"" "Version frontend 3.5.0"

# Test 8: Migration base de données
Write-Host "`n--- Test 8: Migration Base de Données ---" -ForegroundColor Yellow
if (Test-Path "database\migrations\add_numero_anem.sql") {
    Write-Host "[OK] Fichier migration existe" -ForegroundColor Green
    Test-StringInFile "database\migrations\add_numero_anem.sql" "ALTER TABLE employes ADD COLUMN" "SQL ALTER TABLE"
    Test-StringInFile "database\migrations\add_numero_anem.sql" "numero_anem" "Colonne numero_anem"
} else {
    Write-Host "[ERREUR] Fichier migration manquant" -ForegroundColor Red
    $errors++
}

# Test 9: Documentation
Write-Host "`n--- Test 9: Documentation ---" -ForegroundColor Yellow
if (Test-Path "CHANGELOG.md") {
    Test-StringInFile "CHANGELOG.md" "[3.5.0]" "CHANGELOG version 3.5.0"
    Write-Host "[OK] CHANGELOG.md existe" -ForegroundColor Green
} else {
    Write-Host "[ERREUR] CHANGELOG.md manquant" -ForegroundColor Red
    $errors++
}

if (Test-Path "DEPLOYMENT_V3.5.0.md") {
    Write-Host "[OK] DEPLOYMENT_V3.5.0.md existe" -ForegroundColor Green
} else {
    Write-Host "[AVERTISSEMENT] DEPLOYMENT_V3.5.0.md manquant" -ForegroundColor Yellow
    $warnings++
}

if (Test-Path "COMPLETION_REPORT_V3.5.0.md") {
    Write-Host "[OK] COMPLETION_REPORT_V3.5.0.md existe" -ForegroundColor Green
} else {
    Write-Host "[AVERTISSEMENT] COMPLETION_REPORT_V3.5.0.md manquant" -ForegroundColor Yellow
    $warnings++
}

# Résumé
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  RÉSUMÉ DES TESTS" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "`n✅ TOUS LES TESTS RÉUSSIS !" -ForegroundColor Green
    Write-Host "   Le système est prêt pour le déploiement." -ForegroundColor Green
} elseif ($errors -eq 0) {
    Write-Host "`n⚠️  TESTS RÉUSSIS AVEC AVERTISSEMENTS" -ForegroundColor Yellow
    Write-Host "   Erreurs: 0" -ForegroundColor Green
    Write-Host "   Avertissements: $warnings" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ TESTS ÉCHOUÉS" -ForegroundColor Red
    Write-Host "   Erreurs: $errors" -ForegroundColor Red
    Write-Host "   Avertissements: $warnings" -ForegroundColor Yellow
}

Write-Host "`n================================================`n" -ForegroundColor Cyan

# Actions recommandées
if ($errors -eq 0) {
    Write-Host "PROCHAINES ÉTAPES:" -ForegroundColor Cyan
    Write-Host "1. Exécuter migration: mysql -u root -p ay_hr < database\migrations\add_numero_anem.sql" -ForegroundColor White
    Write-Host "2. Redémarrer backend: systemctl restart ayhr-backend" -ForegroundColor White
    Write-Host "3. Tester génération PDF: Attestation, Certificat, Contrat" -ForegroundColor White
    Write-Host "4. Scanner QR codes pour vérifier données" -ForegroundColor White
    Write-Host "5. Git commit & tag: git tag v3.5.0`n" -ForegroundColor White
}

exit $errors

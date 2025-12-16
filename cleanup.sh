#!/bin/bash
# Script de nettoyage du projet AY HR
# Version: 3.6.0
# Usage: ./cleanup.sh

set -e

echo "🧹 Nettoyage du projet AY HR v3.6.0"
echo "======================================"
echo ""

# Confirmation
read -p "⚠️  Ce script va supprimer les fichiers de test et documentation obsolète. Continuer? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Annulé"
    exit 1
fi

echo "📂 Suppression des fichiers de test..."
rm -f analyze_excel.py check_salaires_table.sh clean_and_update.sh
rm -f clean_deploy_server.sh create_db_dump.py create_gestionnaire_user.py
rm -f create_test_user.py debug_edition_salaires.sh debug_salary_engine.py
rm -f deploy_fix_pointages.sh deploy_v1.3.0.sh deploy_v3_server.sh
rm -f diagnose_edition_salaires.sh dump_and_restore_db.py fix_db_schema.py
rm -f fix_frontend_build.sh fix_schema_salaires.py fresh_install_server.sh
rm -f import_employes_from_excel.py legacy_salaire_calculator.py
rm -f migrate_server_v3.5.0.sh patch_edition_salaires.sh reproduce_500.py
rm -f restore_to_mariadb.py restore_via_app_server.py setup_dual_access.sh
rm -f setup_new_server.sh sync_postes_travail.py test_api_conges_rapide.py
rm -f test_bulletin_conges.py test_certificates_api.py
rm -f test_modifications_v3.5.0.ps1 test_pdf_generation.py
rm -f update_salaires_from_excel.py verify_conges_bulletin.sh verify_db_schema.py

echo "📝 Suppression documentation obsolète..."
rm -f 0 AMELIORATIONS_V3.5.1_RESUME.md ANALYSE_LOGIQUE_CONGES_V3.5.3.md
rm -f ANALYSE_PROJET.md ATTENDANCE_FRONTEND_GUIDE.md ATTENDANCE_INTEGRATION.md
rm -f BUSINESS_RULES.md CHANGELOG_V3.5.2.md COMPLETION_REPORT_V3.5.0.md
rm -f CONGES_NOUVELLES_REGLES_V3.5.1.md CORRECTIFS_CALCUL_AUTO_CONGES_V3.5.3.md
rm -f CORRECTIF_AFFICHAGE_CONGES_BULLETINS_V3.5.3.md
rm -f CORRECTIF_FINAL_AFFICHAGE_CONGES_V3.5.3.md
rm -f DEPLOIEMENT_CORRECTIFS_V3.5.3.md DEPLOIEMENT_RAPIDE_V3.5.1.md
rm -f DEPLOIEMENT_V3.5.2.md DEPLOIEMENT_V3.6.0-ALPHA.md DEPLOYMENT_STEPS.md
rm -f DEPLOYMENT_V3.5.0.md GITHUB_UPDATE_SUMMARY.md MODIFICATIONS_PDF_RESUME.md
rm -f OU_EST_LA_LIGNE_CONGES.md PLAN_V3.5.2.md QUICK_DEPLOY.md
rm -f RAPPORT_FINAL_V3.5.2.md RAPPORT_V3.5.3.md README_GITHUB.md
rm -f README_V3.5.0_DEPLOY.txt RECAPITULATIF_VISUEL_V3.5.1.md SESSION_RAPPORT.md
rm -f STATUS_V3.5.2.md STATUT_FINAL_V3.5.0.md TRAITEMENT_SALAIRES_ARCHITECTURE.md
rm -f VERIFICATION_COMPLETE_V3.5.0.txt

echo "📊 Suppression fichiers Excel de test..."
rm -f "attendance_report (10).xlsx" "attendance_report (7).xlsx" employees.xlsx

echo "🗄️ Suppression bases de test..."
rm -f test.db

echo "📦 Suppression dossiers temporaires..."
rm -rf temp_attendance/

echo ""
echo "✅ Nettoyage terminé!"
echo ""
echo "📋 Fichiers conservés:"
echo "  - README.md"
echo "  - CHANGELOG.md"
echo "  - INDEX_DOCUMENTATION.md"
echo "  - PLAN_V3.6.0.md"
echo "  - DEPLOYMENT_LINUX.md"
echo "  - DEPLOYMENT_WINDOWS.md"
echo "  - UPDATE_GUIDE.md"
echo "  - INSTALL_UBUNTU_22.04.md"
echo "  - backend/"
echo "  - frontend/"
echo "  - database/"
echo "  - docs/"
echo ""

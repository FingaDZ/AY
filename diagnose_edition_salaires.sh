#!/bin/bash

###############################################################################
#           DIAGNOSTIC COMPLET EDITION SALAIRES                               #
###############################################################################

echo "🔍 Diagnostic Edition Salaires - Erreur 500"
echo "============================================"
echo ""

# 1. Vérifier les logs backend
echo "📋 LOGS BACKEND (Erreurs récentes):"
echo "------------------------------------"
journalctl -u ayhr-backend -n 100 --no-pager | grep -E "ERROR|Exception|Traceback|edition-salaires" -A 3 -B 1 || echo "Aucune erreur trouvée dans les logs"

echo ""
echo ""
echo "📋 LOGS BACKEND (30 dernières lignes):"
echo "---------------------------------------"
journalctl -u ayhr-backend -n 30 --no-pager

echo ""
echo ""
echo "🔍 TEST BASE DE DONNÉES:"
echo "------------------------"

# 2. Vérifier la structure de la table employes
echo "Table employes (colonnes):"
mysql -u ay_hr_user -p'YourSecurePassword123!' ay_hr_db -e "DESCRIBE employes;" 2>/dev/null || echo "Erreur: Impossible de se connecter à MySQL"

echo ""
echo "Nombre d'employés actifs:"
mysql -u ay_hr_user -p'YourSecurePassword123!' ay_hr_db -e "
SELECT COUNT(*) as total_actifs 
FROM employes 
WHERE active = TRUE;
" 2>/dev/null || echo "Erreur: Colonne 'active' n'existe pas?"

echo ""
echo "Vérification nom colonne (actif vs active):"
mysql -u ay_hr_user -p'YourSecurePassword123!' ay_hr_db -e "
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'ay_hr_db' 
  AND TABLE_NAME = 'employes' 
  AND COLUMN_NAME LIKE '%actif%' OR COLUMN_NAME LIKE '%active%';
" 2>/dev/null

echo ""
echo "🔍 TEST ENDPOINT API:"
echo "---------------------"
echo "Test direct de l'endpoint:"
curl -s -X GET "http://localhost:8000/api/edition-salaires/preview?annee=2025&mois=12" \
  -H "Authorization: Bearer test_token" \
  -H "Content-Type: application/json" || echo "Erreur lors de l'appel API"

echo ""
echo ""
echo "✅ Diagnostic terminé"

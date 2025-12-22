#!/bin/bash
# Test rapide des endpoints v3.7.0 (sans auth)
# Usage: ./test_v3.7.0_quick.sh

BASE_URL="http://localhost:8000/api"
EMPLOYE_ID=1

echo "============================================================"
echo " TEST RAPIDE v3.7.0 - Endpoints Déductions Congés"
echo "============================================================"

echo ""
echo "1. Test Synthèse Congés (GET /conges/synthese/{id})"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/conges/synthese/${EMPLOYE_ID}" | python3 -m json.tool

echo ""
echo ""
echo "2. Test Calcul Solde (GET /deductions-conges/solde/{id})"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/deductions-conges/solde/${EMPLOYE_ID}" | python3 -m json.tool

echo ""
echo ""
echo "3. Test Liste Déductions (GET /deductions-conges/employe/{id})"
echo "------------------------------------------------------------"
curl -s "${BASE_URL}/deductions-conges/employe/${EMPLOYE_ID}" | python3 -m json.tool

echo ""
echo ""
echo "4. Vérification Base de Données"
echo "------------------------------------------------------------"
echo "SELECT * FROM deductions_conges LIMIT 3;" | mysql -u root -p ay_hr

echo ""
echo "============================================================"
echo " FIN DES TESTS"
echo "============================================================"

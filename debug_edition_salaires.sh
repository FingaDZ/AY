#!/bin/bash

echo "🔍 Diagnostic Edition Salaires - Erreur 500"
echo "============================================"
echo ""

# 1. Vérifier les logs backend en temps réel
echo "📋 Logs Backend (dernières erreurs):"
journalctl -u ayhr-backend -n 100 --no-pager | grep -i "error\|exception\|traceback" -A 5

echo ""
echo "📋 Logs Backend complets (dernières 30 lignes):"
journalctl -u ayhr-backend -n 30 --no-pager

echo ""
echo "🔍 Vérification de la table salaires:"
mysql -u ay_hr_user -p'YourSecurePassword123!' ay_hr_db -e "DESCRIBE salaires;"

echo ""
echo "🔍 Vérification des données dans salaires:"
mysql -u ay_hr_user -p'YourSecurePassword123!' ay_hr_db -e "SELECT COUNT(*) as total FROM salaires;"

echo ""
echo "🔍 Test de la requête problématique:"
mysql -u ay_hr_user -p'YourSecurePassword123!' ay_hr_db -e "
SELECT e.id, e.nom, e.prenom, e.poste_id, e.salaire_base_annuel
FROM employes e
WHERE e.active = TRUE AND e.salaire_base_annuel IS NOT NULL
LIMIT 5;
"

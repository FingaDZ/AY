#!/bin/bash
# Script de vérification - Affichage congés bulletins v3.5.3

echo "=== VÉRIFICATION CONGÉS BULLETINS ==="
echo ""

# 1. Vérifier que le code est à jour
echo "1. Version Git:"
cd /opt/ay-hr
git log --oneline -1

echo ""
echo "2. Backend actif:"
systemctl is-active ayhr-backend

echo ""
echo "3. Ligne congé présente dans pdf_generator.py:"
grep -n "Jours de congé pris ce mois" /opt/ay-hr/backend/services/pdf_generator.py | head -1

echo ""
echo "4. Récupération congés dans salary_processor.py:"
grep -A 2 "NOUVEAU v3.5.3: Récupérer les congés" /opt/ay-hr/backend/services/salary_processor.py | head -3

echo ""
echo "5. Données congés dans la base (employés avec congés pris):"
mysql -u root -p'!Yara@2014' ay_hr <<EOF
SELECT 
    e.nom, 
    e.prenom, 
    c.annee, 
    c.mois, 
    c.jours_conges_pris
FROM conges c
JOIN employes e ON c.employe_id = e.id
WHERE c.jours_conges_pris > 0 
  AND c.annee = 2025 
  AND c.mois >= 11
ORDER BY c.annee DESC, c.mois DESC
LIMIT 5;
EOF

echo ""
echo "=== FIN VÉRIFICATION ==="

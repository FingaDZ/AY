#!/bin/bash

# Script pour vérifier et configurer la table salaires sur le serveur

echo "=== Vérification table salaires ==="
mysql -u root -p'Massi@2024' ay_hr -e "SHOW TABLES LIKE 'salaires';"

echo ""
echo "=== Structure table salaires ==="
mysql -u root -p'Massi@2024' ay_hr -e "DESC salaires;"

echo ""
echo "=== Nombre de salaires enregistrés ==="
mysql -u root -p'Massi@2024' ay_hr -e "SELECT COUNT(*) as total FROM salaires;"

echo ""
echo "=== Salaires par année ==="
mysql -u root -p'Massi@2024' ay_hr -e "SELECT annee, COUNT(*) as nb_salaires FROM salaires GROUP BY annee;"

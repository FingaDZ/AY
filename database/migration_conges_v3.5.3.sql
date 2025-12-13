-- Migration v3.5.3 : Revenir aux décimales pour les congés
-- Date : 13 décembre 2025
-- Objectif : Passer de INTEGER à DECIMAL(5,2) pour supporter max 2.5j/mois avec décimales

-- Étape 1 : Modifier les types de colonnes INTEGER → DECIMAL(5,2)
ALTER TABLE conges 
    MODIFY COLUMN jours_conges_acquis DECIMAL(5, 2) DEFAULT 0.00,
    MODIFY COLUMN jours_conges_pris DECIMAL(5, 2) DEFAULT 0.00,
    MODIFY COLUMN jours_conges_restants DECIMAL(5, 2) DEFAULT 0.00;

-- Étape 2 : Recalculer les valeurs existantes (si nécessaire)
-- Les valeurs entières deviennent automatiquement X.00

-- Étape 3 : Vérifier la migration
SELECT 
    id, 
    employe_id, 
    annee, 
    mois,
    jours_travailles,
    jours_conges_acquis,
    jours_conges_pris,
    jours_conges_restants
FROM conges 
ORDER BY id DESC 
LIMIT 10;

-- Note : Les nouvelles règles v3.5.3
-- - Formule : (jours_travaillés / 30) * 2.5
-- - Maximum : 2.5 jours par mois
-- - Décimales supportées : 0.5j, 1.2j, 2.5j...
-- - Congés pris exclus du calcul des droits

-- Statistiques après migration
SELECT 
    COUNT(*) as total_enregistrements,
    MIN(jours_conges_acquis) as min_acquis,
    MAX(jours_conges_acquis) as max_acquis,
    AVG(jours_conges_acquis) as moy_acquis,
    SUM(jours_conges_acquis) as total_acquis,
    SUM(jours_conges_pris) as total_pris
FROM conges;

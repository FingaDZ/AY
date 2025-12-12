-- Migration v3.5.1: Conversion des congés de DECIMAL → INTEGER
-- Date: 12 décembre 2025
-- Objectif: Supprimer les décimales, tout en arrondissant intelligemment

-- Étape 1: Modifier les types de colonnes
ALTER TABLE conges 
    MODIFY COLUMN jours_conges_acquis INT DEFAULT 0,
    MODIFY COLUMN jours_conges_pris INT DEFAULT 0,
    MODIFY COLUMN jours_conges_restants INT DEFAULT 0;

-- Étape 2: Arrondir les valeurs existantes
-- Arrondi standard pour jours_conges_acquis (0.5 et + → arrondi supérieur)
UPDATE conges 
SET jours_conges_acquis = ROUND(jours_conges_acquis);

-- Arrondi pour jours_conges_pris (0.5 et + → arrondi supérieur)
UPDATE conges 
SET jours_conges_pris = ROUND(jours_conges_pris);

-- Recalculer jours_conges_restants = acquis - pris
UPDATE conges 
SET jours_conges_restants = jours_conges_acquis - jours_conges_pris;

-- Vérification
SELECT 
    COUNT(*) as total_records,
    SUM(jours_conges_acquis) as total_acquis,
    SUM(jours_conges_pris) as total_pris,
    SUM(jours_conges_restants) as total_restants
FROM conges;

-- Afficher quelques exemples
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

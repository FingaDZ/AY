-- Migration: Ajouter colonne mode_calcul_conges à table salaires
-- v3.7.0 - Correction schéma manquant

-- Vérifier et ajouter si manquant
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_SCHEMA = 'ay_hr' 
               AND TABLE_NAME = 'salaires' 
               AND COLUMN_NAME = 'mode_calcul_conges');

SET @query = IF(@exist = 0,
    'ALTER TABLE salaires ADD COLUMN mode_calcul_conges VARCHAR(20) NULL COMMENT "Mode de calcul si congés présents" AFTER jours_conges',
    'SELECT "Colonne mode_calcul_conges existe déjà"');

PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'Migration mode_calcul_conges terminée' AS status;

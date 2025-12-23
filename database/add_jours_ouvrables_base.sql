-- Migration: Ajouter colonne jours_ouvrables_base à parametres_salaire
-- v3.7.0 - Correction bug AttributeError

-- Ajouter la colonne si elle n'existe pas
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_SCHEMA = 'ay_hr' 
               AND TABLE_NAME = 'parametres_salaire' 
               AND COLUMN_NAME = 'jours_ouvrables_base');

SET @query = IF(@exist = 0,
    'ALTER TABLE parametres_salaire ADD COLUMN jours_ouvrables_base INT DEFAULT 26 NOT NULL AFTER taux_securite_sociale',
    'SELECT "Colonne jours_ouvrables_base existe déjà"');

PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Mettre à jour les enregistrements existants pour avoir la valeur par défaut
UPDATE parametres_salaire SET jours_ouvrables_base = 26 WHERE jours_ouvrables_base IS NULL;

SELECT 'Migration jours_ouvrables_base terminée' AS status;

-- Migration: Ajout du champ numero_anem pour les contrats de travail
-- Base de données: ay_hr
-- Date: 2025-12-10
-- Description: Ajoute la colonne numero_anem à la table employes pour stocker le numéro ANEM

USE ay_hr;

-- Ajout du champ numero_anem
ALTER TABLE employes 
ADD COLUMN IF NOT EXISTS numero_anem VARCHAR(50) COMMENT 'Numéro ANEM de l''employé';

-- Créer un index pour améliorer les recherches
CREATE INDEX IF NOT EXISTS idx_numero_anem ON employes(numero_anem);

-- Vérification
SELECT 
    COLUMN_NAME, 
    COLUMN_TYPE, 
    IS_NULLABLE, 
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'ay_hr' 
AND TABLE_NAME = 'employes'
AND COLUMN_NAME = 'numero_anem';

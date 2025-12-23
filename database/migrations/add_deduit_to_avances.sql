-- Migration: Ajouter champ deduit à la table avances
-- Date: 2025-12-23
-- Description: Permet de tracer si une avance a été déduite du salaire

-- Ajouter colonne deduit
ALTER TABLE avances 
ADD COLUMN deduit BOOLEAN DEFAULT FALSE NOT NULL 
COMMENT 'Indique si l avance a été déduite du salaire';

-- Ajouter date_deduction pour traçabilité
ALTER TABLE avances 
ADD COLUMN date_deduction DATE NULL 
COMMENT 'Date à laquelle l avance a été déduite du salaire';

-- Index pour recherches rapides
CREATE INDEX idx_avances_deduit ON avances(deduit);
CREATE INDEX idx_avances_date_deduction ON avances(date_deduction);

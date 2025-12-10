-- Migration: Ajouter colonnes pour dates de congé
-- Date: 2025-12-10
-- Description: Ajout des colonnes date_debut, date_fin, type_conge et commentaire à la table conges

ALTER TABLE conges 
ADD COLUMN IF NOT EXISTS date_debut DATE NULL COMMENT 'Date de début du congé pris';

ALTER TABLE conges 
ADD COLUMN IF NOT EXISTS date_fin DATE NULL COMMENT 'Date de fin du congé pris';

ALTER TABLE conges 
ADD COLUMN IF NOT EXISTS type_conge VARCHAR(50) DEFAULT 'ANNUEL' COMMENT 'Type: ANNUEL, MALADIE, AUTRE';

ALTER TABLE conges 
ADD COLUMN IF NOT EXISTS commentaire VARCHAR(500) NULL COMMENT 'Commentaire ou raison';

-- Créer un index pour améliorer les performances des requêtes sur les dates
CREATE INDEX IF NOT EXISTS idx_conges_dates ON conges(date_debut, date_fin);

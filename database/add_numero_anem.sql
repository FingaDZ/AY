-- Migration: Ajout du N° ANEM aux employés
-- Date: 2025-11-11

-- Ajouter la colonne numero_anem à la table employes
ALTER TABLE employes 
ADD COLUMN numero_anem VARCHAR(50) NULL AFTER numero_compte_bancaire;

-- Créer un index pour optimiser les recherches
CREATE INDEX idx_employes_numero_anem ON employes(numero_anem);

-- Afficher un message de confirmation
SELECT 'Migration terminée: colonne numero_anem ajoutée avec succès' AS status;

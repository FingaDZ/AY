-- Script pour ajouter la colonne tarif_km à la table clients
-- Date: 2025-11-11

USE ay_hr;

-- Ajouter la colonne tarif_km à la table clients
ALTER TABLE clients
ADD COLUMN tarif_km DECIMAL(10,2) DEFAULT 3.00 NOT NULL
COMMENT 'Tarif kilométrique spécifique au client (DA/km)';

-- Mettre à jour les clients existants avec une valeur par défaut
UPDATE clients SET tarif_km = 3.00 WHERE tarif_km IS NULL;

-- Vérifier l'ajout
SELECT id, nom, prenom, distance, tarif_km FROM clients;

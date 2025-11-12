-- Migration : Ajout du champ prime_nuit_agent_securite à la table employes
-- Date : 2025-11-11
-- Description : Ajoute un champ booléen pour la prime de nuit des agents de sécurité (750 DA/mois)

USE ay_hr;

-- Ajouter la colonne prime_nuit_agent_securite
ALTER TABLE employes 
ADD COLUMN prime_nuit_agent_securite BOOLEAN NOT NULL DEFAULT FALSE 
COMMENT 'Prime de nuit pour agents de sécurité (750 DA/mois cotisable et imposable)';

-- Afficher la structure modifiée
DESCRIBE employes;

SELECT 'Migration terminée : prime_nuit_agent_securite ajoutée' AS message;

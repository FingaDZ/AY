-- Ajout de la colonne duree_contrat pour calculer automatiquement la date de fin de contrat
-- Durée en mois (ex: 6, 12, 24, etc.)

ALTER TABLE employes 
ADD COLUMN duree_contrat INT NULL 
COMMENT 'Durée du contrat en mois';

-- Index pour les requêtes fréquentes
CREATE INDEX idx_duree_contrat ON employes(duree_contrat);

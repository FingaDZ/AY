-- Ajouter colonne jours_conges à la table salaires
-- Cette colonne stocke les jours de congés déduits pour ce bulletin

ALTER TABLE salaires 
ADD COLUMN jours_conges DECIMAL(10,2) DEFAULT 0.00 AFTER jours_ouvrables;

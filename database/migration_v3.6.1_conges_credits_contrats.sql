-- Migration v3.6.1 - Ajout colonnes pour gestion avancée congés et crédits
-- Date: 2025-12-22
-- Base de données: MySQL

-- 1. Ajouter colonnes mois/année de déduction pour les congés
ALTER TABLE conges 
ADD COLUMN IF NOT EXISTS mois_deduction INT DEFAULT NULL COMMENT 'Mois où les jours de congé sont déduits du salaire (1-12)',
ADD COLUMN IF NOT EXISTS annee_deduction INT DEFAULT NULL COMMENT 'Année où les jours de congé sont déduits du salaire';

-- 2. Ajouter colonnes dates de début/fin pour les crédits
ALTER TABLE credits 
ADD COLUMN IF NOT EXISTS mois_debut INT DEFAULT NULL COMMENT 'Mois de début des retenues (1-12)',
ADD COLUMN IF NOT EXISTS annee_debut INT DEFAULT NULL COMMENT 'Année de début des retenues',
ADD COLUMN IF NOT EXISTS mois_fin_prevu INT DEFAULT NULL COMMENT 'Mois de fin prévu des retenues (1-12)',
ADD COLUMN IF NOT EXISTS annee_fin_prevu INT DEFAULT NULL COMMENT 'Année de fin prévue des retenues';

-- 3. Créer index pour améliorer les performances des requêtes
CREATE INDEX IF NOT EXISTS idx_conges_deduction ON conges(annee_deduction, mois_deduction);
CREATE INDEX IF NOT EXISTS idx_credits_periode ON credits(annee_debut, mois_debut);
CREATE INDEX IF NOT EXISTS idx_employes_date_fin_contrat ON employes(date_fin_contrat, actif);

-- 4. Mettre à jour les crédits existants avec dates de début/fin calculées
-- (Pour les crédits qui n'ont pas encore ces dates)
UPDATE credits 
SET 
    mois_debut = MONTH(DATE_ADD(date_octroi, INTERVAL 1 MONTH)),
    annee_debut = YEAR(DATE_ADD(date_octroi, INTERVAL 1 MONTH)),
    mois_fin_prevu = MONTH(DATE_ADD(date_octroi, INTERVAL nombre_mensualites MONTH)),
    annee_fin_prevu = YEAR(DATE_ADD(date_octroi, INTERVAL nombre_mensualites MONTH))
WHERE mois_debut IS NULL OR annee_debut IS NULL;

-- 5. Mettre à jour les congés existants avec mois/année de déduction
-- Par défaut, le mois de déduction = mois où les congés sont pris
UPDATE conges 
SET 
    mois_deduction = mois,
    annee_deduction = annee
WHERE mois_deduction IS NULL;

COMMIT;

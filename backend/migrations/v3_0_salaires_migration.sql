-- Migration SQL pour Module Salaires V3.0
-- Base de données: MySQL/MariaDB
-- Date: 2025-12-05
-- Description: Création des tables ParametresSalaire, IRGBareme, ReportAvanceCredit
--              et ajout de colonnes au modèle Salaire

-- ============================================
-- 1. TABLE: parametres_salaire
-- ============================================
CREATE TABLE IF NOT EXISTS `parametres_salaire` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Indemnités (%)
    `taux_in` DECIMAL(5,2) NOT NULL DEFAULT 5.00 COMMENT 'Indemnité Nuisance (%)',
    `taux_ifsp` DECIMAL(5,2) NOT NULL DEFAULT 5.00 COMMENT 'IFSP (%)',
    `taux_iep_par_an` DECIMAL(5,2) NOT NULL DEFAULT 1.00 COMMENT 'IEP par année d''ancienneté (%)',
    `taux_prime_encouragement` DECIMAL(5,2) NOT NULL DEFAULT 10.00 COMMENT 'Prime Encouragement (%)',
    `anciennete_min_encouragement` INT NOT NULL DEFAULT 1 COMMENT 'Ancienneté min pour prime encouragement (années)',
    
    -- Primes fixes (DA)
    `prime_chauffeur_jour` DECIMAL(10,2) NOT NULL DEFAULT 100.00 COMMENT 'Prime chauffeur par jour (DA)',
    `prime_nuit_securite` DECIMAL(10,2) NOT NULL DEFAULT 750.00 COMMENT 'Prime nuit sécurité mensuelle (DA)',
    `panier_jour` DECIMAL(10,2) NOT NULL DEFAULT 100.00 COMMENT 'Panier par jour (DA)',
    `transport_jour` DECIMAL(10,2) NOT NULL DEFAULT 100.00 COMMENT 'Transport par jour (DA)',
    `prime_femme_foyer` DECIMAL(10,2) NOT NULL DEFAULT 1000.00 COMMENT 'Prime femme au foyer (DA)',
    
    -- Retenues (%)
    `taux_securite_sociale` DECIMAL(5,2) NOT NULL DEFAULT 9.00 COMMENT 'Retenue Sécurité Sociale (%)',
    
    -- Options de calcul
    `calculer_heures_supp` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Activer calcul heures supplémentaires',
    `mode_calcul_conges` VARCHAR(20) NOT NULL DEFAULT 'complet' COMMENT 'Mode calcul congés: complet|proratise|hybride',
    `jours_ouvrables_base` INT NOT NULL DEFAULT 26 COMMENT 'Nombre de jours ouvrables par mois',
    
    -- IRG
    `irg_proratise` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Proratiser IRG selon jours travaillés',
    
    -- Métadonnées
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insérer paramètres par défaut
INSERT INTO `parametres_salaire` (id) VALUES (1);

-- ============================================
-- 2. TABLE: irg_bareme
-- ============================================
CREATE TABLE IF NOT EXISTS `irg_bareme` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Tranches de salaire
    `salaire_min` DECIMAL(10,2) NOT NULL COMMENT 'Salaire minimum de la tranche (DA)',
    `salaire_max` DECIMAL(10,2) NULL COMMENT 'Salaire maximum de la tranche (DA), NULL pour dernière tranche',
    
    -- IRG correspondant
    `irg` DECIMAL(10,2) NOT NULL COMMENT 'Montant IRG pour cette tranche (DA)',
    
    -- Gestion des versions du barème
    `actif` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Barème actuellement utilisé',
    `date_debut` DATE NULL COMMENT 'Date de début de validité',
    `date_fin` DATE NULL COMMENT 'Date de fin de validité',
    
    -- Métadonnées
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    KEY `idx_salaire_min` (`salaire_min`),
    KEY `idx_salaire_max` (`salaire_max`),
    KEY `idx_actif` (`actif`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 3. TABLE: reports_avance_credit
-- ============================================
CREATE TABLE IF NOT EXISTS `reports_avance_credit` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Identification
    `employe_id` INT NOT NULL COMMENT 'ID employé',
    `type` VARCHAR(20) NOT NULL COMMENT 'Type: avance ou credit',
    
    -- Références aux entités d'origine
    `avance_id` INT NULL COMMENT 'ID avance',
    `credit_id` INT NULL COMMENT 'ID crédit',
    
    -- Montants
    `montant_reporte` DECIMAL(10,2) NOT NULL COMMENT 'Montant reporté (DA)',
    
    -- Périodes
    `mois_origine` INT NOT NULL COMMENT 'Mois où le report a été créé',
    `annee_origine` INT NOT NULL COMMENT 'Année où le report a été créé',
    `mois_destination` INT NOT NULL COMMENT 'Mois où appliquer le report',
    `annee_destination` INT NOT NULL COMMENT 'Année où appliquer le report',
    
    -- Contexte
    `motif` TEXT NULL COMMENT 'Raison du report (obligatoire si manuel)',
    `automatique` BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Report automatique (salaire insuffisant) ou manuel',
    
    -- Suivi
    `traite` BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Report déjà appliqué dans un calcul de salaire',
    `date_traitement` DATETIME NULL COMMENT 'Quand le report a été appliqué',
    `salaire_id` INT NULL COMMENT 'Salaire où le report a été appliqué',
    
    -- Audit
    `cree_par` INT NULL COMMENT 'ID utilisateur créateur',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    KEY `idx_employe_id` (`employe_id`),
    KEY `idx_mois_destination` (`mois_destination`, `annee_destination`),
    KEY `idx_traite` (`traite`),
    
    FOREIGN KEY (`employe_id`) REFERENCES `employes`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`avance_id`) REFERENCES `avances`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`credit_id`) REFERENCES `credits`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`salaire_id`) REFERENCES `salaires`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`cree_par`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 4. MODIFICATIONS TABLE salaires
-- ============================================

-- Ajouter colonnes pour gestion congés
ALTER TABLE `salaires` 
ADD COLUMN `jours_conges` INT NOT NULL DEFAULT 0 COMMENT 'Jours de congés payés dans ce mois' AFTER `jours_ouvrables`,
ADD COLUMN `mode_calcul_conges` VARCHAR(20) NULL COMMENT 'Mode de calcul si congés présents' AFTER `jours_conges`;

-- Ajouter colonnes pour IRG proratisé
ALTER TABLE `salaires` 
ADD COLUMN `irg_base_30j` DECIMAL(10,2) NULL COMMENT 'IRG calculé sur base 30j (avant proratisation)' AFTER `irg`;

-- Ajouter colonnes pour reports
ALTER TABLE `salaires` 
ADD COLUMN `avances_reportees` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Avances reportées au mois suivant' AFTER `retenue_credit`,
ADD COLUMN `credits_reportes` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT 'Crédits reportés au mois suivant' AFTER `avances_reportees`,
ADD COLUMN `alerte_insuffisance` VARCHAR(50) NULL COMMENT 'Type d''alerte si salaire insuffisant' AFTER `credits_reportes`;

-- Ajouter commentaire sur statut existant
ALTER TABLE `salaires` 
MODIFY COLUMN `statut` VARCHAR(20) NOT NULL DEFAULT 'brouillon' COMMENT 'brouillon|valide|paye';

-- Ajouter colonnes workflow
ALTER TABLE `salaires` 
ADD COLUMN `commentaire` TEXT NULL AFTER `notes`,
ADD COLUMN `valide_par` INT NULL COMMENT 'ID utilisateur valideur' AFTER `commentaire`,
ADD COLUMN `paye_par` INT NULL COMMENT 'ID utilisateur payeur' AFTER `valide_par`,
ADD COLUMN `date_validation` DATETIME NULL AFTER `paye_par`,
ADD COLUMN `date_paiement_effective` DATETIME NULL AFTER `date_validation`;

-- Ajouter foreign keys pour workflow
ALTER TABLE `salaires` 
ADD CONSTRAINT `fk_salaires_valide_par` FOREIGN KEY (`valide_par`) REFERENCES `users`(`id`) ON DELETE SET NULL,
ADD CONSTRAINT `fk_salaires_paye_par` FOREIGN KEY (`paye_par`) REFERENCES `users`(`id`) ON DELETE SET NULL;

-- ============================================
-- 5. VÉRIFIER/AJOUTER colonne verouille à pointages
-- ============================================

-- Ajouter si n'existe pas déjà
ALTER TABLE `pointages` 
ADD COLUMN IF NOT EXISTS `verouille` BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Pointage verrouillé, ne peut plus être modifié',
ADD COLUMN IF NOT EXISTS `date_verrouillage` DATETIME NULL COMMENT 'Date de verrouillage du pointage';

ALTER TABLE `pointages`
ADD KEY IF NOT EXISTS `idx_verouille` (`verouille`);

-- ============================================
-- 6. MIGRATION DONNÉES IRG depuis Excel
-- ============================================
-- NOTE: Cette partie sera exécutée par le script Python migrate_irg_to_db.py
-- qui lira le fichier backend/data/irg.xlsx et insérera les données

-- ============================================
-- ROLLBACK (en cas de problème)
-- ============================================
/*
-- Supprimer tables
DROP TABLE IF EXISTS `reports_avance_credit`;
DROP TABLE IF EXISTS `irg_bareme`;
DROP TABLE IF EXISTS `parametres_salaire`;

-- Supprimer colonnes ajoutées à salaires
ALTER TABLE `salaires` 
DROP COLUMN `date_paiement_effective`,
DROP COLUMN `date_validation`,
DROP FOREIGN KEY `fk_salaires_paye_par`,
DROP FOREIGN KEY `fk_salaires_valide_par`,
DROP COLUMN `paye_par`,
DROP COLUMN `valide_par`,
DROP COLUMN `commentaire`,
DROP COLUMN `alerte_insuffisance`,
DROP COLUMN `credits_reportes`,
DROP COLUMN `avances_reportees`,
DROP COLUMN `irg_base_30j`,
DROP COLUMN `mode_calcul_conges`,
DROP COLUMN `jours_conges`;

-- Supprimer colonnes pointages
ALTER TABLE `pointages`
DROP COLUMN `date_verrouillage`,
DROP COLUMN `verouille`;
*/

-- ============================================
-- FIN DE LA MIGRATION
-- ============================================

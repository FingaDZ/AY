-- Migration v3.7.0: Nouvelle architecture congés
-- Date: 22 Décembre 2025
-- Objectif: Séparer acquisition et consommation des congés

-- 1. Créer la nouvelle table deductions_conges
CREATE TABLE IF NOT EXISTS deductions_conges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employe_id INT NOT NULL,
    
    -- Nombre de jours déduits
    jours_deduits DECIMAL(5,2) NOT NULL COMMENT 'Nombre de jours de congé pris',
    
    -- Période de déduction sur bulletin
    mois_deduction INT NOT NULL COMMENT 'Mois où les jours sont déduits du bulletin (1-12)',
    annee_deduction INT NOT NULL COMMENT 'Année où les jours sont déduits du bulletin',
    
    -- Informations complémentaires
    date_debut DATE NULL COMMENT 'Date de début du congé',
    date_fin DATE NULL COMMENT 'Date de fin du congé',
    type_conge VARCHAR(50) DEFAULT 'ANNUEL' COMMENT 'Type: ANNUEL, MALADIE, EXCEPTIONNEL, etc.',
    motif VARCHAR(255) NULL COMMENT 'Motif ou description',
    
    -- Métadonnées
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INT NULL COMMENT 'ID utilisateur créateur',
    
    -- Relations
    FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Index
    INDEX idx_employe_periode (employe_id, annee_deduction, mois_deduction),
    INDEX idx_periode (annee_deduction, mois_deduction)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Déductions de congés - Enregistre chaque prise de congé séparément';

-- 2. Migrer les données existantes de conges.jours_conges_pris vers deductions_conges
-- Seulement si jours_conges_pris > 0 et différent de NULL
INSERT INTO deductions_conges (
    employe_id, 
    jours_deduits, 
    mois_deduction, 
    annee_deduction, 
    type_conge,
    motif,
    created_at
)
SELECT 
    employe_id,
    jours_conges_pris,
    COALESCE(mois_deduction, mois) as mois_deduction,
    COALESCE(annee_deduction, annee) as annee_deduction,
    'ANNUEL',
    CONCAT('Migration depuis conges - Période acquisition: ', mois, '/', annee),
    derniere_mise_a_jour
FROM conges
WHERE jours_conges_pris > 0;

-- 3. Réinitialiser jours_conges_pris dans la table conges (optionnel, pour nettoyage)
-- UPDATE conges SET jours_conges_pris = 0;
-- Note: On garde les anciennes colonnes pour compatibilité, mais elles ne seront plus utilisées

-- 4. Ajouter une vue pour faciliter les requêtes
CREATE OR REPLACE VIEW v_conges_avec_deductions AS
SELECT 
    c.id as conge_id,
    c.employe_id,
    e.nom,
    e.prenom,
    c.annee,
    c.mois,
    c.jours_travailles,
    c.jours_conges_acquis,
    
    -- Total déduit de cette période (acquis de ce mois utilisé dans n'importe quel bulletin)
    COALESCE(SUM(d.jours_deduits), 0) as jours_deduits_total,
    
    -- Solde de cette période
    c.jours_conges_acquis - COALESCE(SUM(d.jours_deduits), 0) as solde_periode,
    
    -- Solde cumulé (calculé via sous-requête)
    (
        SELECT SUM(c2.jours_conges_acquis) - COALESCE(SUM(d2.jours_deduits), 0)
        FROM conges c2
        LEFT JOIN deductions_conges d2 ON d2.employe_id = c2.employe_id
        WHERE c2.employe_id = c.employe_id
        AND (c2.annee < c.annee OR (c2.annee = c.annee AND c2.mois <= c.mois))
    ) as solde_cumule
    
FROM conges c
JOIN employes e ON c.employe_id = e.id
LEFT JOIN deductions_conges d ON d.employe_id = c.employe_id
GROUP BY c.id, c.employe_id, e.nom, e.prenom, c.annee, c.mois, c.jours_travailles, c.jours_conges_acquis
ORDER BY c.employe_id, c.annee, c.mois;

-- 5. Vérification post-migration
SELECT 
    'Nombre de congés avec jours_pris > 0' as description,
    COUNT(*) as count
FROM conges
WHERE jours_conges_pris > 0

UNION ALL

SELECT 
    'Nombre de déductions migrées' as description,
    COUNT(*) as count
FROM deductions_conges

UNION ALL

SELECT 
    'Total jours pris (ancien)' as description,
    SUM(jours_conges_pris) as count
FROM conges

UNION ALL

SELECT 
    'Total jours déduits (nouveau)' as description,
    SUM(jours_deduits) as count
FROM deductions_conges;

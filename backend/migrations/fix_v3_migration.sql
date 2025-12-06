-- =====================================================
-- Migration V3.0 - Correction Complète (Idempotent)
-- Date: 2025-12-06
-- Ce script peut être exécuté plusieurs fois sans erreur
-- =====================================================

-- Désactiver les vérifications de clés étrangères temporairement
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- 1. TABLE POINTAGES - Colonne verouille
-- =====================================================

-- Vérifier si la colonne existe avant de l'ajouter
SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'pointages' 
    AND COLUMN_NAME = 'verouille'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE pointages ADD COLUMN verouille TINYINT(1) DEFAULT 0 NOT NULL COMMENT "Verrouillage: 0=non, 1=oui"',
    'SELECT "Colonne pointages.verouille existe déjà" AS info'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Créer l'index si nécessaire
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'pointages' 
    AND INDEX_NAME = 'idx_verouille'
);

SET @sql = IF(@idx_exists = 0,
    'CREATE INDEX idx_verouille ON pointages(verouille)',
    'SELECT "Index idx_verouille existe déjà" AS info'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- =====================================================
-- 2. TABLE IRG_BAREME
-- =====================================================

CREATE TABLE IF NOT EXISTS irg_bareme (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tranche_min DECIMAL(15,2) NOT NULL COMMENT 'Montant minimum',
    tranche_max DECIMAL(15,2) NULL COMMENT 'Montant maximum (NULL = infini)',
    taux DECIMAL(5,2) NOT NULL COMMENT 'Taux IRG %',
    montant_deduit DECIMAL(15,2) DEFAULT 0 COMMENT 'Montant à déduire',
    actif TINYINT(1) DEFAULT 1 COMMENT '1=actif, 0=archivé',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_actif (actif),
    INDEX idx_tranche (tranche_min, tranche_max)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 3. TABLE SALAIRES - Colonnes workflow
-- =====================================================

-- Colonne statut
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'salaires' AND COLUMN_NAME = 'statut');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE salaires ADD COLUMN statut VARCHAR(20) DEFAULT "brouillon"', 'SELECT "salaires.statut existe" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Colonne date_validation
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'salaires' AND COLUMN_NAME = 'date_validation');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE salaires ADD COLUMN date_validation DATETIME NULL', 'SELECT "salaires.date_validation existe" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Colonne date_paiement_effective
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'salaires' AND COLUMN_NAME = 'date_paiement_effective');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE salaires ADD COLUMN date_paiement_effective DATETIME NULL', 'SELECT "salaires.date_paiement_effective existe" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Colonne valide_par
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'salaires' AND COLUMN_NAME = 'valide_par');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE salaires ADD COLUMN valide_par INT NULL', 'SELECT "salaires.valide_par existe" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Colonne paye_par
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'salaires' AND COLUMN_NAME = 'paye_par');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE salaires ADD COLUMN paye_par INT NULL', 'SELECT "salaires.paye_par existe" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Colonne commentaire
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'salaires' AND COLUMN_NAME = 'commentaire');
SET @sql = IF(@col_exists = 0, 'ALTER TABLE salaires ADD COLUMN commentaire TEXT NULL', 'SELECT "salaires.commentaire existe" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Index statut
SET @idx_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'salaires' AND INDEX_NAME = 'idx_salaire_statut');
SET @sql = IF(@idx_exists = 0, 'CREATE INDEX idx_salaire_statut ON salaires(statut)', 'SELECT "idx_salaire_statut existe" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Index periode
SET @idx_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'salaires' AND INDEX_NAME = 'idx_salaire_periode');
SET @sql = IF(@idx_exists = 0, 'CREATE INDEX idx_salaire_periode ON salaires(annee, mois)', 'SELECT "idx_salaire_periode existe" AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- =====================================================
-- 4. TABLE PARAMETRES_SALAIRE
-- =====================================================

CREATE TABLE IF NOT EXISTS parametres_salaire (
    id INT AUTO_INCREMENT PRIMARY KEY,
    indemnite_nuisance DECIMAL(10,2) DEFAULT 0,
    ifsp DECIMAL(10,2) DEFAULT 0,
    iep DECIMAL(10,2) DEFAULT 0,
    prime_encouragement DECIMAL(10,2) DEFAULT 0,
    prime_chauffeur DECIMAL(10,2) DEFAULT 0,
    prime_nuit_agent_securite DECIMAL(10,2) DEFAULT 0,
    prime_deplacement DECIMAL(10,2) DEFAULT 0,
    prime_femme_foyer DECIMAL(10,2) DEFAULT 0,
    panier DECIMAL(10,2) DEFAULT 0,
    prime_transport DECIMAL(10,2) DEFAULT 0,
    taux_securite_sociale DECIMAL(5,2) DEFAULT 9.00,
    activer_heures_supp TINYINT(1) DEFAULT 1,
    activer_irg_proratise TINYINT(1) DEFAULT 1,
    mode_calcul_conges VARCHAR(20) DEFAULT 'proratise',
    date_modification DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insérer paramètres par défaut si vide
INSERT INTO parametres_salaire (
    indemnite_nuisance, ifsp, iep, prime_encouragement,
    prime_chauffeur, prime_nuit_agent_securite, prime_deplacement,
    prime_femme_foyer, panier, prime_transport,
    taux_securite_sociale, activer_heures_supp, activer_irg_proratise,
    mode_calcul_conges
)
SELECT 1000.00, 500.00, 300.00, 500.00, 800.00, 600.00, 400.00, 1000.00, 300.00, 500.00, 9.00, 1, 1, 'proratise'
WHERE NOT EXISTS (SELECT 1 FROM parametres_salaire LIMIT 1);

-- =====================================================
-- 5. TABLE REPORT_AVANCE_CREDIT
-- =====================================================

CREATE TABLE IF NOT EXISTS report_avance_credit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employe_id INT NOT NULL,
    type VARCHAR(10) NOT NULL COMMENT 'avance ou credit',
    montant_initial DECIMAL(10,2) NOT NULL,
    montant_reporte DECIMAL(10,2) NOT NULL,
    mois_origine INT NOT NULL,
    annee_origine INT NOT NULL,
    mois_destination INT NOT NULL,
    annee_destination INT NOT NULL,
    motif TEXT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employe (employe_id),
    INDEX idx_destination (annee_destination, mois_destination)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ajouter la clé étrangère si elle n'existe pas
SET @fk_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'report_avance_credit' 
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    AND CONSTRAINT_NAME LIKE '%employe%'
);

SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE report_avance_credit ADD CONSTRAINT fk_report_employe FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE',
    'SELECT "FK report_avance_credit.employe_id existe" AS info'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Réactiver les vérifications de clés étrangères
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- Fin de la migration - Script idempotent
-- =====================================================
SELECT '✅ Migration V3.0 terminée avec succès!' AS status;

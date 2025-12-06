-- ============================================================================
-- Migration IRG: Simplification de la table irg_bareme
-- Version: 2.4.3
-- Date: 07 décembre 2025
-- ============================================================================

-- IMPORTANT: Sauvegarder les données avant migration !
-- mysqldump -u root -p ay_hr irg_bareme > backup_irg_bareme_20251207.sql

USE ay_hr;

-- Étape 1: Créer une table temporaire avec la nouvelle structure
CREATE TABLE irg_bareme_new (
    id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    salaire DECIMAL(15,2) NOT NULL COMMENT 'Salaire (MONTANT du fichier Excel)',
    montant_irg DECIMAL(15,2) NOT NULL COMMENT 'Montant IRG à retenir',
    actif TINYINT(1) DEFAULT 1 COMMENT 'Barème actif',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_salaire (salaire),
    INDEX idx_actif (actif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Étape 2: Copier les données existantes
INSERT INTO irg_bareme_new (id, salaire, montant_irg, actif, date_creation)
SELECT 
    id,
    tranche_min AS salaire,
    taux AS montant_irg,
    actif,
    date_creation
FROM irg_bareme;

-- Étape 3: Vérifier que les données sont correctes
SELECT 'Vérification des données:' AS info;
SELECT COUNT(*) AS total_ancien FROM irg_bareme;
SELECT COUNT(*) AS total_nouveau FROM irg_bareme_new;
SELECT * FROM irg_bareme_new ORDER BY salaire LIMIT 10;

-- Étape 4: Renommer les tables (ATTENTION: Point de non-retour !)
-- DÉCOMMENTER CES LIGNES APRÈS VÉRIFICATION
-- DROP TABLE irg_bareme;
-- RENAME TABLE irg_bareme_new TO irg_bareme;

-- Étape 5: Vérification finale
-- SELECT 'Migration terminée!' AS info;
-- SELECT COUNT(*) AS total FROM irg_bareme;
-- DESCRIBE irg_bareme;

-- ============================================================================
-- Instructions d'utilisation sur le serveur:
-- ============================================================================
-- 1. Se connecter au serveur: ssh root@AIRBAND-HR
-- 2. Sauvegarder: mysqldump -u root -p ay_hr irg_bareme > /opt/ay-hr/backups/irg_bareme_backup.sql
-- 3. Exécuter ce script: mysql -u root -p ay_hr < migration_irg.sql
-- 4. Vérifier les données
-- 5. Décommenter les lignes DROP/RENAME et réexécuter
-- 6. Redémarrer le backend: systemctl restart ayhr-backend
-- ============================================================================

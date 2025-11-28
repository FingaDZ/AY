-- ============================================================================
-- Migration: Ajout table incomplete_attendance_logs
-- Version: 1.7.0
-- Date: 28 novembre 2025
-- Description: Gestion des logs de pointage incomplets (ENTRY sans EXIT ou inversement)
-- ============================================================================

USE ay_hr;

-- Créer la table incomplete_attendance_logs
CREATE TABLE IF NOT EXISTS incomplete_attendance_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Références
    attendance_log_id INT NOT NULL COMMENT 'ID du log dans le système Attendance',
    attendance_sync_log_id INT COMMENT 'ID du sync log associé',
    hr_employee_id INT NOT NULL COMMENT 'ID employé dans HR',
    employee_name VARCHAR(200) COMMENT 'Nom complet employé (cache)',
    
    -- Informations du log
    log_date DATE NOT NULL COMMENT 'Date du pointage',
    log_type ENUM('ENTRY', 'EXIT') NOT NULL COMMENT 'Type de log incomplet',
    log_timestamp DATETIME NOT NULL COMMENT 'Timestamp exact du log',
    
    -- Estimation
    estimated_minutes INT NOT NULL COMMENT 'Minutes estimées par calcul smart',
    estimation_rule VARCHAR(100) COMMENT 'Règle utilisée pour estimation',
    
    -- Validation
    status ENUM('pending', 'validated', 'corrected') DEFAULT 'pending' COMMENT 'Statut de validation',
    validated_minutes INT COMMENT 'Minutes validées/corrigées par RH',
    validated_by VARCHAR(100) COMMENT 'Utilisateur ayant validé',
    validated_at DATETIME COMMENT 'Date/heure de validation',
    notes TEXT COMMENT 'Notes de validation/correction',
    
    -- Métadonnées
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création',
    
    -- Index
    INDEX idx_hr_employee (hr_employee_id),
    INDEX idx_status (status),
    INDEX idx_log_date (log_date),
    INDEX idx_attendance_log (attendance_log_id),
    
    -- Contraintes
    FOREIGN KEY (hr_employee_id) REFERENCES employes(id) ON DELETE CASCADE,
    FOREIGN KEY (attendance_sync_log_id) REFERENCES attendance_sync_log(id) ON DELETE SET NULL
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Logs de pointage incomplets nécessitant validation RH';

-- Vérifier la création
SELECT 
    'Table incomplete_attendance_logs créée avec succès!' AS Message,
    COUNT(*) AS 'Nombre de colonnes'
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'ay_hr' 
  AND TABLE_NAME = 'incomplete_attendance_logs';

-- Afficher la structure
DESCRIBE incomplete_attendance_logs;

COMMIT;

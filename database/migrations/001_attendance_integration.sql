-- Migration: Add Attendance Integration Tables
-- Version: 1.3.0
-- Date: 2025-11-25

-- 1. Employee Mapping Table
CREATE TABLE IF NOT EXISTS attendance_employee_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hr_employee_id INT NOT NULL,
    attendance_employee_id INT NOT NULL,
    attendance_employee_name VARCHAR(200),
    sync_method ENUM('SECU_SOCIALE', 'NAME_DOB') DEFAULT 'NAME_DOB',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_mapping (hr_employee_id, attendance_employee_id),
    FOREIGN KEY (hr_employee_id) REFERENCES employes(id) ON DELETE CASCADE,
    INDEX idx_attendance_employee (attendance_employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Attendance Sync Log Table
CREATE TABLE IF NOT EXISTS attendance_sync_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_log_id INT NOT NULL,
    hr_employee_id INT NOT NULL,
    sync_date DATE NOT NULL,
    worked_minutes INT,
    overtime_minutes INT,
    log_type ENUM('ENTRY', 'EXIT') DEFAULT 'EXIT',
    imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_log (attendance_log_id),
    FOREIGN KEY (hr_employee_id) REFERENCES employes(id) ON DELETE CASCADE,
    INDEX idx_sync_date (sync_date),
    INDEX idx_employee_date (hr_employee_id, sync_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Attendance Import Conflicts Table
CREATE TABLE IF NOT EXISTS attendance_import_conflicts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hr_employee_id INT NOT NULL,
    attendance_log_id INT NOT NULL,
    conflict_date DATE NOT NULL,
    hr_existing_value INT COMMENT '0=absent, 1=travaillé',
    attendance_worked_minutes INT,
    status ENUM('pending', 'resolved_keep_hr', 'resolved_use_attendance') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    resolved_by VARCHAR(100) NULL,
    FOREIGN KEY (hr_employee_id) REFERENCES employes(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_conflict_date (conflict_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Add heures_supplementaires column to pointages
ALTER TABLE pointages 
ADD COLUMN IF NOT EXISTS heures_supplementaires DECIMAL(5,2) DEFAULT 0 
COMMENT 'Heures supplémentaires mensuelles calculées depuis Attendance';

-- 5. Add index for better performance
ALTER TABLE pointages 
ADD INDEX IF NOT EXISTS idx_annee_mois (annee, mois);

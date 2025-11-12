-- Table pour le système de logging
CREATE TABLE IF NOT EXISTS logging (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT NULL,
    user_email VARCHAR(255) NULL,
    module_name VARCHAR(100) NOT NULL,
    action_type ENUM('CREATE', 'UPDATE', 'DELETE') NOT NULL,
    record_id INT NULL,
    old_data JSON NULL,
    new_data JSON NULL,
    description TEXT NULL,
    ip_address VARCHAR(45) NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id),
    INDEX idx_module (module_name),
    INDEX idx_action (action_type),
    INDEX idx_record (record_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

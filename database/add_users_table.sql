-- Création de la table users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Utilisateur') NOT NULL DEFAULT 'Utilisateur',
    actif BOOLEAN DEFAULT TRUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion DATETIME DEFAULT NULL,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insérer un utilisateur admin par défaut (mot de passe: admin123)
-- Hash bcrypt de 'admin123': $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILY8Z6K5i
INSERT INTO users (email, nom, prenom, password_hash, role, actif)
VALUES ('admin@ayhr.dz', 'Admin', 'Système', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILY8Z6K5i', 'Admin', TRUE)
ON DUPLICATE KEY UPDATE email=email;

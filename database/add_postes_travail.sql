-- Création de la table postes_travail pour gérer les postes de travail
-- avec gestion des droits de modification et soft delete

CREATE TABLE IF NOT EXISTS postes_travail (
    id INT PRIMARY KEY AUTO_INCREMENT,
    libelle VARCHAR(100) NOT NULL UNIQUE COMMENT 'Nom du poste (ex: Chauffeur, Agent de sécurité)',
    est_chauffeur BOOLEAN DEFAULT FALSE NOT NULL COMMENT 'Indique si le poste est chauffeur (pour les missions)',
    modifiable BOOLEAN DEFAULT TRUE NOT NULL COMMENT 'Indique si le poste peut être modifié/supprimé',
    actif BOOLEAN DEFAULT TRUE NOT NULL COMMENT 'Soft delete',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_actif (actif),
    INDEX idx_est_chauffeur (est_chauffeur),
    INDEX idx_libelle (libelle)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Table des postes de travail avec gestion des chauffeurs et soft delete';

-- Insertion des postes de base
INSERT INTO postes_travail (libelle, est_chauffeur, modifiable, actif) VALUES
('Chauffeur', TRUE, FALSE, TRUE),
('Agent de sécurité', FALSE, TRUE, TRUE),
('Gardien', FALSE, TRUE, TRUE),
('Technicien', FALSE, TRUE, TRUE);

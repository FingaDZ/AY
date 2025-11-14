-- ============================================================================
-- Script de Création de la Base de Données
-- AIRBAND HR v1.1.4
-- ============================================================================

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ay_hr;

-- ============================================================================
-- Table: users (utilisateurs du système)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'manager', 'user') DEFAULT 'user',
    actif BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_actif (actif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: postes_travail (postes de travail)
-- ============================================================================
CREATE TABLE IF NOT EXISTS postes_travail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    libelle VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    est_chauffeur BOOLEAN DEFAULT FALSE,
    modifiable BOOLEAN DEFAULT TRUE,
    actif BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_libelle (libelle),
    INDEX idx_actif (actif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: employes
-- ============================================================================
CREATE TABLE IF NOT EXISTS employes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NOT NULL,
    lieu_naissance VARCHAR(200) NOT NULL,
    adresse TEXT NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    numero_secu_sociale VARCHAR(50) UNIQUE NOT NULL,
    numero_compte_bancaire VARCHAR(50) NOT NULL,
    numero_anem VARCHAR(50),
    situation_familiale ENUM('Célibataire', 'Marié') DEFAULT 'Célibataire',
    femme_au_foyer BOOLEAN DEFAULT FALSE,
    date_recrutement DATE NOT NULL,
    duree_contrat INT,
    date_fin_contrat DATE,
    poste_travail VARCHAR(100) NOT NULL,
    salaire_base DECIMAL(10,2) NOT NULL CHECK (salaire_base >= 20000),
    prime_nuit_agent_securite BOOLEAN DEFAULT FALSE,
    statut_contrat ENUM('Actif', 'Inactif') DEFAULT 'Actif',
    actif BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nom (nom),
    INDEX idx_prenom (prenom),
    INDEX idx_statut (statut_contrat),
    INDEX idx_actif (actif),
    INDEX idx_numero_secu (numero_secu_sociale),
    FULLTEXT idx_search (nom, prenom)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: pointages (feuilles de présence)
-- ============================================================================
CREATE TABLE IF NOT EXISTS pointages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employe_id INT NOT NULL,
    mois INT NOT NULL CHECK (mois BETWEEN 1 AND 12),
    annee INT NOT NULL CHECK (annee BETWEEN 2000 AND 2100),
    jours JSON NOT NULL,
    jours_travailles INT DEFAULT 0,
    absences INT DEFAULT 0,
    verrouille BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_pointage (employe_id, mois, annee),
    INDEX idx_employe_id (employe_id),
    INDEX idx_periode (mois, annee),
    INDEX idx_verrouille (verrouille)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: conges (gestion des congés)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employe_id INT NOT NULL,
    annee INT NOT NULL CHECK (annee BETWEEN 2000 AND 2100),
    mois INT NOT NULL CHECK (mois BETWEEN 1 AND 12),
    jours_travailles INT DEFAULT 0,
    jours_conges_acquis DECIMAL(5,2) DEFAULT 0.00 CHECK (jours_conges_acquis >= 0 AND jours_conges_acquis <= 2.5),
    jours_conges_pris DECIMAL(5,2) DEFAULT 0.00,
    jours_conges_restants DECIMAL(5,2) DEFAULT 0.00,
    date_calcul DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_mise_a_jour DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_conge (employe_id, annee, mois),
    INDEX idx_employe_id (employe_id),
    INDEX idx_periode (annee, mois)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: clients
-- ============================================================================
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(20),
    email VARCHAR(100),
    tarif_km DECIMAL(10,2) DEFAULT 0.00,
    actif BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nom (nom),
    INDEX idx_actif (actif)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: missions
-- ============================================================================
CREATE TABLE IF NOT EXISTS missions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chauffeur_id INT NOT NULL,
    client_id INT NOT NULL,
    date_mission DATE NOT NULL,
    distance DECIMAL(10,2) NOT NULL CHECK (distance >= 0),
    prime_calculee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (chauffeur_id) REFERENCES employes(id) ON DELETE CASCADE,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    INDEX idx_chauffeur (chauffeur_id),
    INDEX idx_client (client_id),
    INDEX idx_date (date_mission)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: avances (avances sur salaire)
-- ============================================================================
CREATE TABLE IF NOT EXISTS avances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employe_id INT NOT NULL,
    montant DECIMAL(10,2) NOT NULL CHECK (montant > 0),
    date_avance DATE NOT NULL,
    mois INT NOT NULL CHECK (mois BETWEEN 1 AND 12),
    annee INT NOT NULL CHECK (annee BETWEEN 2000 AND 2100),
    motif TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE,
    INDEX idx_employe_id (employe_id),
    INDEX idx_periode (mois, annee)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: credits (crédits salariaux)
-- ============================================================================
CREATE TABLE IF NOT EXISTS credits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employe_id INT NOT NULL,
    montant_total DECIMAL(10,2) NOT NULL CHECK (montant_total > 0),
    montant_mensuel DECIMAL(10,2) NOT NULL CHECK (montant_mensuel > 0),
    nombre_mensualites INT NOT NULL CHECK (nombre_mensualites > 0),
    date_debut DATE NOT NULL,
    montant_deja_retenu DECIMAL(10,2) DEFAULT 0.00,
    montant_restant DECIMAL(10,2) NOT NULL,
    statut ENUM('En cours', 'Soldé', 'Annulé') DEFAULT 'En cours',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE,
    INDEX idx_employe_id (employe_id),
    INDEX idx_statut (statut)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: retenues_credit (historique des retenues)
-- ============================================================================
CREATE TABLE IF NOT EXISTS retenues_credit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    credit_id INT NOT NULL,
    mois INT NOT NULL CHECK (mois BETWEEN 1 AND 12),
    annee INT NOT NULL CHECK (annee BETWEEN 2000 AND 2100),
    montant_retenu DECIMAL(10,2) NOT NULL,
    date_retenue DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (credit_id) REFERENCES credits(id) ON DELETE CASCADE,
    INDEX idx_credit_id (credit_id),
    INDEX idx_periode (mois, annee)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: prorogations_credit (prorogations de crédits)
-- ============================================================================
CREATE TABLE IF NOT EXISTS prorogations_credit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    credit_id INT NOT NULL,
    ancienne_duree INT NOT NULL,
    nouvelle_duree INT NOT NULL,
    ancien_montant_mensuel DECIMAL(10,2) NOT NULL,
    nouveau_montant_mensuel DECIMAL(10,2) NOT NULL,
    motif TEXT,
    date_prorogation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (credit_id) REFERENCES credits(id) ON DELETE CASCADE,
    INDEX idx_credit_id (credit_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: parametres (paramètres de l'entreprise)
-- ============================================================================
CREATE TABLE IF NOT EXISTS parametres (
    id INT PRIMARY KEY DEFAULT 1,
    raison_sociale VARCHAR(200) DEFAULT 'VOTRE ENTREPRISE',
    rc VARCHAR(50) DEFAULT '',
    nif VARCHAR(50) DEFAULT '',
    nis VARCHAR(50) DEFAULT '',
    art VARCHAR(50) DEFAULT '',
    numero_secu_employeur VARCHAR(50) DEFAULT '',
    adresse TEXT DEFAULT '',
    telephone VARCHAR(20) DEFAULT '',
    email VARCHAR(100) DEFAULT '',
    banque VARCHAR(100) DEFAULT '',
    compte_bancaire VARCHAR(30) DEFAULT '',
    logo_path VARCHAR(255),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (id = 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: parametres_entreprise (alias pour compatibilité)
-- ============================================================================
CREATE OR REPLACE VIEW parametres_entreprise AS SELECT * FROM parametres;

-- ============================================================================
-- Table: database_config (configuration système)
-- ============================================================================
CREATE TABLE IF NOT EXISTS database_config (
    id INT PRIMARY KEY DEFAULT 1,
    tarif_km_default DECIMAL(10,2) DEFAULT 0.00,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (id = 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Table: logging (journal d'activité)
-- ============================================================================
CREATE TABLE IF NOT EXISTS logging (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    module_name VARCHAR(50) NOT NULL,
    action_type ENUM('CREATE', 'UPDATE', 'DELETE', 'READ') NOT NULL,
    record_id INT,
    old_data JSON,
    new_data JSON,
    description TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_module (module_name),
    INDEX idx_action (action_type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- Données Initiales
-- ============================================================================

-- Insérer les paramètres par défaut
INSERT INTO parametres (id, raison_sociale) 
VALUES (1, 'VOTRE ENTREPRISE')
ON DUPLICATE KEY UPDATE id=id;

-- Insérer la configuration par défaut
INSERT INTO database_config (id, tarif_km_default) 
VALUES (1, 0.00)
ON DUPLICATE KEY UPDATE id=id;

-- Créer l'utilisateur admin par défaut
-- Mot de passe: admin123
INSERT INTO users (username, email, hashed_password, role) 
VALUES ('admin', 'admin@ayhr.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5QK7TJk/bQhau', 'admin')
ON DUPLICATE KEY UPDATE username=username;

-- Insérer les postes par défaut
INSERT INTO postes_travail (libelle, description, est_chauffeur, modifiable) VALUES
('Chauffeur', 'Chauffeur transport de personnes', TRUE, FALSE),
('Agent de sécurité', 'Agent de sécurité et surveillance', FALSE, TRUE),
('Superviseur', 'Superviseur d\'équipe', FALSE, TRUE),
('Manager', 'Manager opérationnel', FALSE, TRUE)
ON DUPLICATE KEY UPDATE libelle=libelle;

-- ============================================================================
-- Validation et Commit
-- ============================================================================
COMMIT;

-- Afficher un message de succès
SELECT 'Base de données ay_hr créée avec succès!' AS Message;
SELECT 'Utilisateur admin créé (mot de passe: admin123)' AS Info;

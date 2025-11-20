-- Création de la table salaires pour le suivi mensuel
-- Nécessaire pour la génération du rapport G29

CREATE TABLE IF NOT EXISTS salaires (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employe_id INT NOT NULL,
    annee INT NOT NULL,
    mois INT NOT NULL, -- 1-12
    
    -- Salaire de base
    salaire_base DECIMAL(10,2) DEFAULT 0,
    heures_travaillees DECIMAL(8,2) DEFAULT 0,
    jours_travailles INT DEFAULT 0,
    
    -- Primes
    prime_rendement DECIMAL(10,2) DEFAULT 0,
    prime_fidelite DECIMAL(10,2) DEFAULT 0,
    prime_experience DECIMAL(10,2) DEFAULT 0,
    prime_panier DECIMAL(10,2) DEFAULT 0,
    prime_transport DECIMAL(10,2) DEFAULT 0,
    prime_nuit DECIMAL(10,2) DEFAULT 0,
    autres_primes DECIMAL(10,2) DEFAULT 0,
    
    -- Totaux
    total_primes DECIMAL(10,2) DEFAULT 0,
    salaire_brut DECIMAL(10,2) DEFAULT 0,
    
    -- Déductions
    cotisation_cnr DECIMAL(10,2) DEFAULT 0,
    cotisation_secu_sociale DECIMAL(10,2) DEFAULT 0,
    irg_retenu DECIMAL(10,2) DEFAULT 0,
    autres_deductions DECIMAL(10,2) DEFAULT 0,
    
    -- Résultat
    total_deductions DECIMAL(10,2) DEFAULT 0,
    salaire_net DECIMAL(10,2) DEFAULT 0,
    
    -- Métadonnées
    date_paiement DATE,
    statut VARCHAR(20) DEFAULT 'brouillon', -- brouillon, validé, payé
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_salaire (employe_id, annee, mois),
    INDEX idx_annee (annee),
    INDEX idx_mois (mois),
    INDEX idx_employe_annee (employe_id, annee)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

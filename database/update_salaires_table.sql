-- Mise à jour de la table salaires pour correspondre au calcul réel
-- Cette version remplace la structure initiale

DROP TABLE IF EXISTS salaires;

CREATE TABLE salaires (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employe_id INT NOT NULL,
    annee INT NOT NULL,
    mois INT NOT NULL,
    
    -- Données de base
    jours_travailles INT DEFAULT 0,
    jours_ouvrables INT DEFAULT 26,
    
    -- Salaire et heures
    salaire_base_proratis DECIMAL(10,2) DEFAULT 0,
    heures_supplementaires DECIMAL(10,2) DEFAULT 0,
    
    -- Primes incluses dans le salaire cotisable
    indemnite_nuisance DECIMAL(10,2) DEFAULT 0,  -- IN: 5%
    ifsp DECIMAL(10,2) DEFAULT 0,  -- 5%
    iep DECIMAL(10,2) DEFAULT 0,  -- Ancienneté
    prime_encouragement DECIMAL(10,2) DEFAULT 0,  -- 10% si > 1 an
    prime_chauffeur DECIMAL(10,2) DEFAULT 0,  -- 100 DA/jour
    prime_nuit_agent_securite DECIMAL(10,2) DEFAULT 0,  -- 750 DA/mois
    prime_deplacement DECIMAL(10,2) DEFAULT 0,
    prime_objectif DECIMAL(10,2) DEFAULT 0,
    prime_variable DECIMAL(10,2) DEFAULT 0,
    
    -- Salaire cotisable (AVANT déduction SS, SANS panier/transport)
    salaire_cotisable DECIMAL(10,2) DEFAULT 0,
    
    -- Déduction sécurité sociale (9%)
    retenue_securite_sociale DECIMAL(10,2) DEFAULT 0,
    
    -- Primes NON cotisables mais IMPOSABLES
    panier DECIMAL(10,2) DEFAULT 0,  -- 100 DA/jour
    prime_transport DECIMAL(10,2) DEFAULT 0,  -- 100 DA/jour
    
    -- Salaire imposable (cotisable - SS + panier + transport)
    salaire_imposable DECIMAL(10,2) DEFAULT 0,
    
    -- IRG calculé sur salaire imposable
    irg DECIMAL(10,2) DEFAULT 0,
    
    -- Autres déductions
    total_avances DECIMAL(10,2) DEFAULT 0,
    retenue_credit DECIMAL(10,2) DEFAULT 0,
    
    -- Prime femme au foyer (non imposable, non cotisable)
    prime_femme_foyer DECIMAL(10,2) DEFAULT 0,
    
    -- Salaire net final
    salaire_net DECIMAL(10,2) DEFAULT 0,
    
    -- Métadonnées
    date_paiement DATE,
    statut VARCHAR(20) DEFAULT 'brouillon',  -- brouillon, validé, payé
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employe_id) REFERENCES employes(id) ON DELETE CASCADE,
    UNIQUE KEY unique_salaire (employe_id, annee, mois),
    INDEX idx_annee (annee),
    INDEX idx_mois (mois),
    INDEX idx_employe_annee (employe_id, annee),
    INDEX idx_statut (statut)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

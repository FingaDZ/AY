-- Création de la table parametres_entreprise
CREATE TABLE IF NOT EXISTS parametres_entreprise (
    id INT AUTO_INCREMENT PRIMARY KEY,
    raison_sociale VARCHAR(255) DEFAULT NULL,
    nom_entreprise VARCHAR(255) DEFAULT NULL,
    adresse VARCHAR(500) DEFAULT NULL,
    rc VARCHAR(100) DEFAULT NULL,
    nif VARCHAR(100) DEFAULT NULL,
    nis VARCHAR(100) DEFAULT NULL,
    art VARCHAR(100) DEFAULT NULL,
    numero_secu_employeur VARCHAR(100) DEFAULT NULL,
    telephone VARCHAR(100) DEFAULT NULL,
    compte_bancaire VARCHAR(255) DEFAULT NULL,
    banque VARCHAR(255) DEFAULT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_mise_a_jour DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


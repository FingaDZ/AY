-- Script d'initialisation de la base de données AY HR Management
-- À exécuter dans MariaDB

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ay_hr;

-- Note: Les tables seront créées automatiquement par SQLAlchemy
-- Ce script contient des données de démarrage et des exemples

-- Insérer le paramètre du tarif kilométrique par défaut
INSERT INTO parametres (cle, valeur, description) 
VALUES ('tarif_km', '3.00', 'Tarif kilométrique pour les missions (DA/km)')
ON DUPLICATE KEY UPDATE valeur = valeur;

-- Données d'exemple pour tester (optionnel)

-- Exemple d'employés
/*
INSERT INTO employes (nom, prenom, date_naissance, lieu_naissance, adresse, mobile, 
                      numero_secu_sociale, numero_compte_bancaire, situation_familiale,
                      femme_au_foyer, date_recrutement, date_fin_contrat, poste_travail,
                      salaire_base, statut_contrat)
VALUES 
    ('BENALI', 'Ahmed', '1985-03-15', 'Alger', '123 Rue de la République, Alger', 
     '0555123456', '198503123456789', 'CCP1234567890', 'Marié', 0, 
     '2020-01-01', NULL, 'Chauffeur', 30000.00, 'Actif'),
     
    ('KACI', 'Fatima', '1990-07-22', 'Oran', '456 Boulevard Zabana, Oran',
     '0661234567', '199007223456789', '00799123456789012', 'Célibataire', 0,
     '2021-06-15', NULL, 'Comptable', 35000.00, 'Actif'),
     
    ('HAMIDI', 'Mohamed', '1988-11-10', 'Constantine', '789 Avenue Didouche, Constantine',
     '0770123456', '198811103456789', 'CCP9876543210', 'Marié', 1,
     '2019-03-01', NULL, 'Responsable RH', 45000.00, 'Actif');
*/

-- Exemple de clients
/*
INSERT INTO clients (nom, prenom, distance, telephone)
VALUES
    ('SAIDI', 'Rachid', 25.5, '0555987654'),
    ('BOUZID', 'Samira', 50.0, '0661876543'),
    ('MAMMERI', 'Karim', 15.0, '0770456789');
*/

COMMIT;

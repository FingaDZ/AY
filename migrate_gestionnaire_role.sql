-- Migration v3.6.0: Ajouter Gestionnaire à l'ENUM role
ALTER TABLE users MODIFY COLUMN role ENUM('Admin', 'Gestionnaire', 'Utilisateur') NOT NULL DEFAULT 'Utilisateur';

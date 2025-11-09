-- Script de création de la base de données AY HR
-- Exécuter ce script en tant qu'administrateur MySQL/MariaDB

-- Créer la base de données
CREATE DATABASE IF NOT EXISTS ay_hr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur et lui donner tous les droits
CREATE USER IF NOT EXISTS 'n8n'@'%' IDENTIFIED BY 'n8n';
GRANT ALL PRIVILEGES ON ay_hr.* TO 'n8n'@'%';
FLUSH PRIVILEGES;

-- Vérification
USE ay_hr;
SHOW TABLES;

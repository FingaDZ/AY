-- Script pour modifier la définition ENUM dans la table pointages
-- Passer de ENUM('TRAVAILLE','ABSENT',...) à ENUM('Tr','Ab',...)

USE ay_hr;

-- Modifier la définition de toutes les colonnes jour_XX
ALTER TABLE pointages 
  MODIFY COLUMN jour_01 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_02 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_03 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_04 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_05 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_06 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_07 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_08 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_09 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_10 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_11 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_12 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_13 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_14 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_15 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_16 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_17 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_18 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_19 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_20 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_21 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_22 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_23 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_24 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_25 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_26 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_27 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_28 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_29 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_30 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL,
  MODIFY COLUMN jour_31 ENUM('Tr','Ab','Co','Ma','Fe','Ar') NULL;

SELECT 'Structure de table modifiée avec succès' AS status;

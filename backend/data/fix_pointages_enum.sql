-- Script de migration des valeurs enum dans la table pointages
-- Convertir les noms d'enum en valeurs courtes

USE ay_hr;

-- Mise à jour de toutes les colonnes jour_XX
UPDATE pointages SET
  jour_01 = CASE jour_01
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_01
  END,
  jour_02 = CASE jour_02
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_02
  END,
  jour_03 = CASE jour_03
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_03
  END,
  jour_04 = CASE jour_04
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_04
  END,
  jour_05 = CASE jour_05
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_05
  END,
  jour_06 = CASE jour_06
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_06
  END,
  jour_07 = CASE jour_07
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_07
  END,
  jour_08 = CASE jour_08
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_08
  END,
  jour_09 = CASE jour_09
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_09
  END,
  jour_10 = CASE jour_10
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_10
  END,
  jour_11 = CASE jour_11
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_11
  END,
  jour_12 = CASE jour_12
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_12
  END,
  jour_13 = CASE jour_13
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_13
  END,
  jour_14 = CASE jour_14
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_14
  END,
  jour_15 = CASE jour_15
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_15
  END,
  jour_16 = CASE jour_16
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_16
  END,
  jour_17 = CASE jour_17
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_17
  END,
  jour_18 = CASE jour_18
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_18
  END,
  jour_19 = CASE jour_19
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_19
  END,
  jour_20 = CASE jour_20
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_20
  END,
  jour_21 = CASE jour_21
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_21
  END,
  jour_22 = CASE jour_22
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_22
  END,
  jour_23 = CASE jour_23
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_23
  END,
  jour_24 = CASE jour_24
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_24
  END,
  jour_25 = CASE jour_25
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_25
  END,
  jour_26 = CASE jour_26
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_26
  END,
  jour_27 = CASE jour_27
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_27
  END,
  jour_28 = CASE jour_28
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_28
  END,
  jour_29 = CASE jour_29
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_29
  END,
  jour_30 = CASE jour_30
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_30
  END,
  jour_31 = CASE jour_31
    WHEN 'TRAVAILLE' THEN 'Tr'
    WHEN 'ABSENT' THEN 'Ab'
    WHEN 'CONGE' THEN 'Co'
    WHEN 'MALADIE' THEN 'Ma'
    WHEN 'FERIE' THEN 'Fe'
    WHEN 'ARRET' THEN 'Ar'
    ELSE jour_31
  END
WHERE 
  jour_01 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_02 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_03 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_04 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_05 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_06 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_07 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_08 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_09 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_10 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_11 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_12 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_13 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_14 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_15 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_16 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_17 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_18 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_19 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_20 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_21 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_22 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_23 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_24 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_25 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_26 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_27 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_28 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_29 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_30 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET') OR
  jour_31 IN ('TRAVAILLE', 'ABSENT', 'CONGE', 'MALADIE', 'FERIE', 'ARRET');

SELECT 'Migration terminée' AS status, COUNT(*) AS lignes_modifiees FROM pointages;

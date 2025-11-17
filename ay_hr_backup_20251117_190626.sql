/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.6.22-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ay_hr
-- ------------------------------------------------------
-- Server version	10.6.22-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `avances`
--

DROP TABLE IF EXISTS `avances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `avances` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employe_id` int(11) NOT NULL,
  `date_avance` date NOT NULL,
  `montant` decimal(12,2) NOT NULL,
  `mois_deduction` int(11) NOT NULL,
  `annee_deduction` int(11) NOT NULL,
  `motif` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `employe_id` (`employe_id`),
  KEY `ix_avances_id` (`id`),
  KEY `ix_avances_mois_deduction` (`mois_deduction`),
  KEY `ix_avances_annee_deduction` (`annee_deduction`),
  KEY `ix_avances_date_avance` (`date_avance`),
  CONSTRAINT `avances_ibfk_1` FOREIGN KEY (`employe_id`) REFERENCES `employes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `avances`
--

LOCK TABLES `avances` WRITE;
/*!40000 ALTER TABLE `avances` DISABLE KEYS */;
/*!40000 ALTER TABLE `avances` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `distance` decimal(10,2) NOT NULL,
  `telephone` varchar(20) NOT NULL,
  `tarif_km` decimal(10,2) NOT NULL DEFAULT 3.00 COMMENT 'Tarif kilométrique spécifique au client (DA/km)',
  PRIMARY KEY (`id`),
  KEY `ix_clients_nom` (`nom`),
  KEY `ix_clients_prenom` (`prenom`),
  KEY `ix_clients_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clients`
--

LOCK TABLES `clients` WRITE;
/*!40000 ALTER TABLE `clients` DISABLE KEYS */;
/*!40000 ALTER TABLE `clients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conges`
--

DROP TABLE IF EXISTS `conges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `conges` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employe_id` int(11) NOT NULL,
  `annee` int(11) NOT NULL,
  `mois` int(11) NOT NULL,
  `jours_travailles` int(11) DEFAULT 0,
  `jours_conges_acquis` decimal(5,2) DEFAULT 0.00,
  `jours_conges_pris` decimal(5,2) DEFAULT 0.00,
  `jours_conges_restants` decimal(5,2) DEFAULT 0.00,
  `date_calcul` datetime DEFAULT current_timestamp(),
  `derniere_mise_a_jour` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_employe_mois` (`employe_id`,`annee`,`mois`),
  KEY `idx_employe` (`employe_id`),
  KEY `idx_periode` (`annee`,`mois`),
  CONSTRAINT `conges_ibfk_1` FOREIGN KEY (`employe_id`) REFERENCES `employes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conges`
--

LOCK TABLES `conges` WRITE;
/*!40000 ALTER TABLE `conges` DISABLE KEYS */;
/*!40000 ALTER TABLE `conges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credits`
--

DROP TABLE IF EXISTS `credits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `credits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employe_id` int(11) NOT NULL,
  `date_octroi` date NOT NULL,
  `montant_total` decimal(12,2) NOT NULL,
  `nombre_mensualites` int(11) NOT NULL,
  `montant_mensualite` decimal(12,2) NOT NULL,
  `montant_retenu` decimal(12,2) NOT NULL,
  `statut` enum('EN_COURS','SOLDE') NOT NULL,
  PRIMARY KEY (`id`),
  KEY `employe_id` (`employe_id`),
  KEY `ix_credits_id` (`id`),
  KEY `ix_credits_date_octroi` (`date_octroi`),
  CONSTRAINT `credits_ibfk_1` FOREIGN KEY (`employe_id`) REFERENCES `employes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credits`
--

LOCK TABLES `credits` WRITE;
/*!40000 ALTER TABLE `credits` DISABLE KEYS */;
/*!40000 ALTER TABLE `credits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `database_config`
--

DROP TABLE IF EXISTS `database_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `database_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) NOT NULL,
  `port` int(11) NOT NULL,
  `database_name` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `charset` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `date_creation` datetime DEFAULT NULL,
  `derniere_modification` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_database_config_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `database_config`
--

LOCK TABLES `database_config` WRITE;
/*!40000 ALTER TABLE `database_config` DISABLE KEYS */;
/*!40000 ALTER TABLE `database_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employes`
--

DROP TABLE IF EXISTS `employes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `employes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `date_naissance` date NOT NULL,
  `lieu_naissance` varchar(200) NOT NULL,
  `adresse` varchar(500) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `numero_secu_sociale` varchar(50) NOT NULL,
  `numero_compte_bancaire` varchar(50) NOT NULL,
  `numero_anem` varchar(50) DEFAULT NULL,
  `situation_familiale` enum('CELIBATAIRE','MARIE') NOT NULL,
  `femme_au_foyer` tinyint(1) NOT NULL,
  `date_recrutement` date NOT NULL,
  `date_fin_contrat` date DEFAULT NULL,
  `poste_travail` varchar(100) NOT NULL,
  `salaire_base` decimal(12,2) NOT NULL,
  `statut_contrat` enum('ACTIF','INACTIF') NOT NULL,
  `prime_nuit_agent_securite` tinyint(1) NOT NULL DEFAULT 0,
  `actif` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Employé actif dans le système (soft delete)',
  `duree_contrat` int(11) DEFAULT NULL COMMENT 'Duree du contrat en mois',
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_secu_sociale` (`numero_secu_sociale`),
  KEY `ix_employes_statut_contrat` (`statut_contrat`),
  KEY `ix_employes_prenom` (`prenom`),
  KEY `ix_employes_poste_travail` (`poste_travail`),
  KEY `ix_employes_id` (`id`),
  KEY `ix_employes_nom` (`nom`),
  KEY `idx_employes_numero_anem` (`numero_anem`),
  KEY `idx_employes_actif` (`actif`),
  KEY `idx_duree_contrat` (`duree_contrat`)
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employes`
--

LOCK TABLES `employes` WRITE;
/*!40000 ALTER TABLE `employes` DISABLE KEYS */;
INSERT INTO `employes` VALUES (29,'SAIFI','SALAH EDDINE','1991-09-01','CHELGHOUM LAID','CITE LES MARTYRS N°49-ZMALA TELEGHMA','770740615.0','911588007035','BDL 003210000001105',NULL,'MARIE',0,'2023-02-06','2026-02-05','RESPONSABLE PERSONNEL',30000.00,'ACTIF',0,1,NULL),(30,'ZERROUG','ABDELHALIM','1981-09-27','CHELGHOUM LAID','02 RUE MERBOUCHE MAKHLOUF - CH LAID','770763989.0','811767001745','CCP00799999001493073773',NULL,'MARIE',0,'2022-02-01','2025-01-31','DIRECTEUR COMMERCIAL',35000.00,'INACTIF',0,0,NULL),(31,'BERKANE','HOCINE','1976-06-16','CHELGHOUM LAID','CITE DJAMAA LAKHDAR - CH-LAID','772291078.0','760372021155','BDL 003210000001316-81',NULL,'MARIE',1,'2022-02-01','2025-01-31','RESPONSABLE ENT/MAINT',23000.00,'INACTIF',0,0,NULL),(32,'BENSAAD','ACHEREUF','1989-10-04','OUED ATHMANIA','BOUMALEK - OUED ATHMANIA','797453575.0','891192003540','BDL 003210000001109',NULL,'CELIBATAIRE',0,'2022-01-19','2025-01-18','CHEF EQUIPE',22000.00,'INACTIF',0,0,NULL),(33,'HAFDI','ABDERRAHMANE','1970-07-22','OUED ATHMANIA','CITE 1 NOV 1954 - OUED ATHMANIA','659221422.0','700445019247','BDL 003210000001102',NULL,'MARIE',1,'2022-02-01','2025-01-31','CHAUFFEUR',22000.00,'INACTIF',0,0,NULL),(34,'KENIDA','FARID','1976-09-29','CHELGHOUM LAID','CITE 1 NOV 1954 - OUED ATHMANIA','557467994.0','761239004844','BDL 003210000001113',NULL,'MARIE',1,'2022-02-01','2025-01-31','EMPLOYE',20000.00,'INACTIF',0,0,NULL),(35,'NADER','FOUAD','1990-07-09','CHELGHOUM LAID','CITE ABBANE RAMDANE - CH-LAID','781237205.0','901502007553','BDL 003210000001112',NULL,'CELIBATAIRE',0,'2022-02-01','2025-01-31','EMPLOYE',20000.00,'INACTIF',0,0,NULL),(36,'BOUDJENANA','KHALIL ERAH.','1991-07-11','CHELGHOUM LAID','CITE CHOUHADA 96 LOGTS - CH LAID','661695607.0','911258007143','CCP 00799999001492154407',NULL,'CELIBATAIRE',0,'2022-02-01','2025-01-31','AGENT ADMINISTRATIF',20000.00,'INACTIF',0,0,NULL),(37,'BENMAMERI','AZIZ','1977-01-01','CHELGHOUM LAID','CITE DJAMAA LEKHDER-CHELGHOUM LAID','771924978.0','770030032659','CCP 00799999001310922808',NULL,'MARIE',1,'2022-02-01','2025-01-31','ENT/MAINT',20000.00,'INACTIF',0,0,NULL),(38,'DJEBIR','FARID','1984-07-11','CHELGHOUM LAID','CITE AHMED YAHIA RACHID CHELGHOUM LAID','791374495.0','841551005744','CCP 00799999001372621986',NULL,'CELIBATAIRE',0,'2022-02-01','2025-01-31','AGENT DE SECURITE',20000.00,'INACTIF',0,0,NULL),(39,'ERREDIR','ZAKARYA','1988-04-20','CHELGHOUM LAID','CITE CHOHADA CHELGHOUM LAID','778107826.0','880883013437','CCP 00799999000621678929',NULL,'CELIBATAIRE',0,'2022-02-01','2025-01-31','AGENT ADMINISTRATIF',20000.00,'INACTIF',0,0,NULL),(40,'CHABBI','HAMID','1978-12-17','TEBESSA','CITE DJAMAA LEKHDER-CHELGHOUM LAID','664895483.0','783571001544','CCP 00799999002030677940',NULL,'MARIE',0,'2022-02-01','2025-01-31','CHAUFFEUR',22000.00,'INACTIF',0,0,NULL),(41,'GUENIFA','YACINE','1977-02-01','OUED ATHMANIA','CITE ABDELLAH BACHA - CHELGHOUM LAID','793241896.0','770105026454','BDL 003210000002132',NULL,'MARIE',1,'2022-02-01','2025-01-31','CHAUFFEUR',22000.00,'INACTIF',0,0,NULL),(42,'BENSACI','ZAKARIA','1989-10-10','CHELGHOUM LAID','RUE 01 NOVEMBRE 1954 CHELGHOUM LAID','792660817.0','892095000344','BDL 003210000001827',NULL,'MARIE',0,'2022-02-01','2025-01-31','AGENT DE CONTRÔLE',20000.00,'INACTIF',0,0,NULL),(43,'MEGHARZI','WALID','1982-11-08','OUED ATHMANIA','CITE NADJI SAID OUED ATHMANIA','797375123.0','820972000749','CCP 00799999001130482147',NULL,'MARIE',0,'2022-02-01','2025-01-31','VENDEUR',20000.00,'INACTIF',0,0,NULL),(44,'NEZZARI','HOUSSAM','1991-06-10','CHELGHOUM LAID','RUE DJAICHE TAHRIR CHELGHOUM LAID','779035647.0','911066001850','CCP 00799999001825228545',NULL,'MARIE',1,'2022-02-01','2025-01-31','VENDEUR',20000.00,'INACTIF',0,0,NULL),(45,'DJABLA','AHMED','1989-02-24','CHELGHOUM LAID','MECHTA BEN SAHLI - CHELGHOUM LAID','774372338.0','890452006145','CCP 00799999001232776795',NULL,'MARIE',1,'2022-02-01','2025-01-31','AIDE VENDEUR',20000.00,'INACTIF',0,0,NULL),(46,'BENHAMIMED','ABDELFETTAH','1993-11-28','OUED ATHMANIA','BLAD YOUCEF OUED ATHMANIA','698372860.0','930919011055','CCP 00799999001863068051',NULL,'MARIE',1,'2022-02-01','2025-01-31','EMPLOYE',20000.00,'INACTIF',0,0,NULL),(47,'KHANISSI','YASSINE','1983-09-24','SKIKDA','CITE MOHAMED BOUDIAF CHELGHOUM LAID','665793150.0','834598002136','BDL 003210000002127',NULL,'MARIE',0,'2022-02-01','2025-01-31','CHAUFFEUR',22000.00,'INACTIF',0,0,NULL),(48,'BAAZIZI','AHMED','1985-05-23','CHELGHOUM LAID','CITE BELLATAR SLIMANE - AIN MELOUK','779893627.0','851170001257','BDL 00321000000111602',NULL,'MARIE',1,'2022-02-01','2025-01-31','EMPLOYE',20000.00,'INACTIF',0,0,NULL),(49,'BOUSSENA','YASSINE','1988-04-25','CHELGHOUM LAID','CITE 20 AOUT 1955 CHELGHOUM LAID','774866945.0','880926007735','BDL 003210000002125',NULL,'MARIE',0,'2022-02-01','2025-01-31','AGENT DE SECURITE',20000.00,'INACTIF',0,0,NULL),(50,'LAHBATI','FAROUQ','1985-02-21','CHELGHOUM LAID','RUE 01 NOVEMBRE 1954 CHELGHOUM LAID','771795119.0','850476008929','0000000000000000',NULL,'MARIE',1,'2022-02-01','2025-01-31','AIDE VENDEUR',20000.00,'INACTIF',0,0,NULL),(51,'CHANTI','ABDALLAH','1993-04-02','CHELGHOUM LAID','CITE CHOUHADA N°96 -CHELGHOUM LAID','770992772.0','930600008155','CCP 00799999001907903876',NULL,'CELIBATAIRE',0,'2022-02-01','2025-01-31','AGENT ADMINISTRATIF',20000.00,'INACTIF',0,0,NULL),(52,'LASSED','KHEIREDDINE','1970-08-01','CHELGHOUM LAID','CITE ABDELLAH BACHA - CHELGHOUM LAID','557975254.0','700828004552','BDL 003210000002257',NULL,'MARIE',0,'2022-02-01','2025-01-31','COMPTABLE',22000.00,'INACTIF',0,0,NULL),(53,'ZAIDI','ABDELGHANI','1985-05-11','OUED ATHMANIA','CITE BOUKHCHEM AHMED - OUED ATHMANIA','665944875.0','850608001260','CCP 00799999000802755522',NULL,'MARIE',1,'2022-06-01','2025-05-31','MECANICIEN',20000.00,'INACTIF',0,0,NULL),(54,'MENNOUR','MABROUK','1991-05-08','AIN MELOUK','MECHTA EL DOUH-AIN MELOUK','770708300.0','910063030656','BDL 003210000001114',NULL,'CELIBATAIRE',0,'2022-06-01','2025-05-31','EMPLOYE',20000.00,'INACTIF',0,0,NULL),(55,'MAMMERI','HAMZA','1987-11-28','BOUHATEM','RUE BOUZIDI KHALIFA CHELGHOUM LAID','796318180.0','870401010169','CCP 00799999001425235562',NULL,'MARIE',1,'2022-09-26','2025-09-25','AIDE VENDEUR',20000.00,'INACTIF',0,0,NULL),(56,'BENABDELKADER','ZINE EL ABIDINE','1988-06-07','CHELGHOUM LAID','RUE MADI MOUSSA CHELGHOUM LAID','774775663.0','881271000947','CCP 00799999000637242094',NULL,'MARIE',1,'2022-12-11','2025-03-01','CHAUFFEUR',22000.00,'INACTIF',0,0,NULL),(57,'FEZZANI','ELBAHI','1970-05-10','CHELGHOUM LAID','CITE MOUHAMED BOUDIAF CHELGHOUM LAID','776390226.0','70 05 57 001 457','BNA 00843020000060087',NULL,'MARIE',1,'2023-06-07','2026-06-06','CHAUFFEUR',22000.00,'ACTIF',0,1,NULL),(58,'CHABBI','RAOUF','1988-10-12','OUED ATHMANIA','CITE GUENIFA MOUHAMED OUED ATHMANIA','796288704.0','88 12 79 007 826','CCP 00799999001384466074',NULL,'MARIE',1,'2023-06-07','2026-06-06','CHAUFFEUR',22000.00,'ACTIF',0,1,NULL),(59,'KHELLAF','FOUAD','1976-06-10','CHELGHOUM LAID','CITE DJAMAA LAKHDER CHELGHOUM LAID','676438843.0','760812004752','CCP 00799999001494997016',NULL,'MARIE',0,'2023-06-12','2026-06-11','CHAUFFEUR',22000.00,'ACTIF',0,1,NULL),(60,'BENATITALLAH','ABDELMALEK','1991-12-24','CHELGHOUM LAID','RUE AHMED YAHIA RACHID CHELGHOUM LAID','0000000000','0-20899007741','CCP 00000000000000000000',NULL,'CELIBATAIRE',0,'2023-08-28','2026-08-27','EMPLOYE',20000.00,'ACTIF',0,1,NULL),(61,'LAMOURI','ADEL','1977-10-04','OUED ZENATI','CITE HOUARI BOUMADIANE CHELGHOUM LAID','658163867.0','771323007349','CCP 00799999000627853173',NULL,'MARIE',0,'2023-10-11','2026-10-10','CHAUFFEUR',22000.00,'ACTIF',0,1,NULL),(62,'NASRI','TAYIB','1982-07-30','CHELGHOUM LAID','CITE ABDALLAH BACHA CHELGHOUM LAID','772997295.0','821447000753','CCP 0079999900658540444',NULL,'MARIE',1,'2024-01-08','2027-01-07','EMPLOYE',20000.00,'ACTIF',0,1,NULL),(63,'BELALA','SABER','1989-04-02','CONSTANTINE','CITE ABDALLAH BACHA CHELGHOUM LAID','773585215.0','894206001056','CCP 00799999001436256217',NULL,'MARIE',1,'2024-05-16','2027-05-16','CHAUFFEUR',22000.00,'ACTIF',0,1,NULL),(64,'ALI KHELLAF','AMAR','1973-06-21','CONSTANTINE','CITE FRERE HAIFI CHELGHOUM LAID','776464429.0','737547000345','CCP 00799999002830844423',NULL,'MARIE',1,'2024-05-16','2027-05-16','CHAUFFEUR',22000.00,'ACTIF',0,1,NULL),(65,'DJADLI','HOUSSEM','1991-08-19','AIN MLILA','CITE ZMALA TELEGHMA','663779716.0','912189000743','CCP 00799999001901538445',NULL,'CELIBATAIRE',0,'2024-05-16','2027-05-16','EMPLOYE',20000.00,'ACTIF',0,1,NULL),(66,'SAADA','ABDELWAHAB','1976-04-22','BIR CHOUHADA','CITE DJAMAA LAKHDER CHELGHOUM LAID','658295655.0','760265019140','CCP 00799999000619352093',NULL,'MARIE',0,'2024-05-16','2027-05-16','CHAUFFEUR',22000.00,'ACTIF',0,1,NULL),(67,'GHELLAM','ABDERREZZAQ','1982-06-26','CHELGHOUM LAID','26 AVENUE 1ER NOVEMBRE 1954 - CH LAID','770319768.0','821246001952','BDL 3210000001107',NULL,'MARIE',0,'2024-06-30','2027-06-30','AGENT ADMINISTRATIF',20000.00,'ACTIF',0,1,NULL),(68,'CHOUAIB','OUSSAMA','1990-02-02','CHELGHOUM LAID','CITE FRERE FEDALI -AIN MELOUK','0000000000','900263029044','CCP 007999990001349150506',NULL,'MARIE',1,'2024-07-08','2027-07-08','CUISINIER',20000.00,'ACTIF',0,1,NULL),(69,'BOUFAGHES','YASSER','1993-11-28','SETIF','CITE CHOUHADA N22-CHELGHOUM LAID','0000000000','938442000345','CCP 00799999001857822582',NULL,'CELIBATAIRE',0,'2024-10-08','2027-10-08','AGENT ADMINISTRATIF',20000.00,'ACTIF',0,1,NULL),(70,'BOULTIF','HEYTHEM','1990-07-25','CHELGHOUM LAID','CITE DJAMAA LAKHDER CHELGHOUM LAID','797342421.0','901612010761','CCP 00799999001487443505',NULL,'MARIE',0,'2024-10-08','2027-10-08','EMPLOYE',20000.00,'ACTIF',0,1,NULL),(71,'MEZDOURA','MOHAMED','1988-02-28','OUED ATHMANIA','CITE MEZDOURA RABIE OUED ATHMANIA','797058412.0','880257033542','CCP 00799999002668142041',NULL,'MARIE',0,'2025-03-18','2028-03-17','CHAUFFEUR',22000.00,'ACTIF',0,1,NULL),(72,'KHELIF','NADJELA','1998-07-06','CHELGHOUM LAID','RUE FRERE BORNI-CHELGHOUM LAID','0000000000','981135006443','0000000000000000',NULL,'MARIE',0,'2025-09-01','2028-08-31','SEC',20000.00,'ACTIF',0,1,NULL),(73,'GUELLIB','MOHAMED SALAH','2025-10-14','CHELGHOUM LAID','CITE 20 AOUT 1955 CHELGHOUM LAID','0000000000','921917000455','0000000000000000',NULL,'CELIBATAIRE',0,'2025-10-01','2028-09-30','EMPLOYE',20000.00,'ACTIF',0,1,NULL),(74,'MANSOURI','SOUHAIB','1994-11-19','CHELGHOUM LAID','CITE 130 LOGTS CHELGHOUM LAID','0000000000','942085006040','CCP 00799999001876743305',NULL,'CELIBATAIRE',0,'2025-10-01','2028-09-30','EMPLOYE',20000.00,'ACTIF',0,1,NULL);
/*!40000 ALTER TABLE `employes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logging`
--

DROP TABLE IF EXISTS `logging`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `logging` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `user_email` varchar(255) DEFAULT NULL,
  `module_name` varchar(100) NOT NULL,
  `action_type` enum('CREATE','UPDATE','DELETE') NOT NULL,
  `record_id` int(11) DEFAULT NULL,
  `old_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`old_data`)),
  `new_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`new_data`)),
  `description` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_logging_module_name` (`module_name`),
  KEY `ix_logging_timestamp` (`timestamp`),
  KEY `ix_logging_id` (`id`),
  KEY `ix_logging_record_id` (`record_id`),
  KEY `ix_logging_action_type` (`action_type`),
  KEY `ix_logging_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logging`
--

LOCK TABLES `logging` WRITE;
/*!40000 ALTER TABLE `logging` DISABLE KEYS */;
INSERT INTO `logging` VALUES (1,'2025-11-13 11:40:27',1,'admin@ayhr.dz','employes','CREATE',24,'null','{\"lieu_naissance\": \"Constantine\", \"date_recrutement\": \"2025-02-01\", \"adresse\": \"Rue Debug 456\", \"date_fin_contrat\": \"2026-02-01\", \"mobile\": \"0666114022\", \"poste_travail\": \"Chauffeur\", \"numero_secu_sociale\": \"DEBUG114022655\", \"salaire_base\": 25000.0, \"id\": 24, \"numero_compte_bancaire\": \"002114022655\", \"prime_nuit_agent_securite\": false, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"statut_contrat\": \"Actif\", \"nom\": \"DEBUG114022655\", \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"actif\": true, \"femme_au_foyer\": true}','Création employé: DEBUG114022655 Test','127.0.0.1'),(2,'2025-11-13 11:42:08',1,'admin@ayhr.dz','employes','CREATE',25,'null','{\"adresse\": \"Rue Debug 456\", \"date_fin_contrat\": \"2026-02-01\", \"mobile\": \"0666114204\", \"poste_travail\": \"Chauffeur\", \"numero_secu_sociale\": \"DEBUG114204021\", \"salaire_base\": 25000.0, \"id\": 25, \"numero_compte_bancaire\": \"002114204021\", \"prime_nuit_agent_securite\": false, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"statut_contrat\": \"Actif\", \"nom\": \"DEBUG114204021\", \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"actif\": true, \"lieu_naissance\": \"Constantine\", \"femme_au_foyer\": true, \"date_recrutement\": \"2025-02-01\"}','Création employé: DEBUG114204021 Test','127.0.0.1'),(3,'2025-11-13 18:55:01',2,'sghellam@gmail.com','postes_travail','DELETE',3,'{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T11:14:57\", \"libelle\": \"Gardien\", \"id\": 3, \"modifiable\": true, \"created_at\": \"2025-11-13T11:14:57\"}','null','Suppression poste: Gardien','127.0.0.1'),(4,'2025-11-13 18:55:45',2,'sghellam@gmail.com','postes_travail','CREATE',5,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:55:46\", \"libelle\": \"Administrateur\", \"id\": 5, \"modifiable\": true, \"created_at\": \"2025-11-13T17:55:46\"}','Création poste: Administrateur','127.0.0.1'),(5,'2025-11-13 18:55:58',2,'sghellam@gmail.com','postes_travail','CREATE',6,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:55:59\", \"libelle\": \"Agent Administratif\", \"id\": 6, \"modifiable\": true, \"created_at\": \"2025-11-13T17:55:59\"}','Création poste: Agent Administratif','127.0.0.1'),(6,'2025-11-13 18:56:12',2,'sghellam@gmail.com','postes_travail','CREATE',7,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:56:13\", \"libelle\": \"Agent Commercial\", \"id\": 7, \"modifiable\": true, \"created_at\": \"2025-11-13T17:56:13\"}','Création poste: Agent Commercial','127.0.0.1'),(7,'2025-11-13 18:56:25',2,'sghellam@gmail.com','postes_travail','CREATE',8,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:56:26\", \"libelle\": \"Agent Polyvalent\", \"id\": 8, \"modifiable\": true, \"created_at\": \"2025-11-13T17:56:26\"}','Création poste: Agent Polyvalent','127.0.0.1'),(8,'2025-11-13 18:56:39',2,'sghellam@gmail.com','postes_travail','UPDATE',4,'{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T11:14:57\", \"libelle\": \"Technicien\", \"id\": 4, \"modifiable\": true, \"created_at\": \"2025-11-13T11:14:57\"}','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T11:14:57\", \"libelle\": \"Technicien\", \"id\": 4, \"modifiable\": true, \"created_at\": \"2025-11-13T11:14:57\"}','Modification poste: Technicien','127.0.0.1'),(9,'2025-11-13 18:56:53',2,'sghellam@gmail.com','postes_travail','CREATE',9,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:56:54\", \"libelle\": \"Directeur Commercial\", \"id\": 9, \"modifiable\": true, \"created_at\": \"2025-11-13T17:56:54\"}','Création poste: Directeur Commercial','127.0.0.1'),(10,'2025-11-13 18:57:08',2,'sghellam@gmail.com','postes_travail','CREATE',10,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:57:09\", \"libelle\": \"Responsable Administration\", \"id\": 10, \"modifiable\": true, \"created_at\": \"2025-11-13T17:57:09\"}','Création poste: Responsable Administration','127.0.0.1'),(11,'2025-11-13 18:57:32',2,'sghellam@gmail.com','postes_travail','CREATE',11,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:57:33\", \"libelle\": \"Responsable Maintenance et Entretien\", \"id\": 11, \"modifiable\": true, \"created_at\": \"2025-11-13T17:57:33\"}','Création poste: Responsable Maintenance et Entretien','127.0.0.1'),(12,'2025-11-13 18:57:46',2,'sghellam@gmail.com','postes_travail','CREATE',12,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:57:47\", \"libelle\": \"Caissier\", \"id\": 12, \"modifiable\": true, \"created_at\": \"2025-11-13T17:57:47\"}','Création poste: Caissier','127.0.0.1'),(13,'2025-11-13 18:57:57',2,'sghellam@gmail.com','postes_travail','CREATE',13,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:57:58\", \"libelle\": \"Magasinier\", \"id\": 13, \"modifiable\": true, \"created_at\": \"2025-11-13T17:57:58\"}','Création poste: Magasinier','127.0.0.1'),(14,'2025-11-13 18:58:21',2,'sghellam@gmail.com','postes_travail','CREATE',14,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:58:17\", \"libelle\": \"Agent de Nettoyage et Entretien\", \"id\": 14, \"modifiable\": true, \"created_at\": \"2025-11-13T17:58:17\"}','Création poste: Agent de Nettoyage et Entretien','127.0.0.1'),(15,'2025-11-13 18:58:40',2,'sghellam@gmail.com','postes_travail','CREATE',15,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:58:41\", \"libelle\": \"Agent Manutention\", \"id\": 15, \"modifiable\": true, \"created_at\": \"2025-11-13T17:58:41\"}','Création poste: Agent Manutention','127.0.0.1'),(16,'2025-11-13 18:58:47',2,'sghellam@gmail.com','postes_travail','CREATE',16,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:58:49\", \"libelle\": \"Agent de Bureau\", \"id\": 16, \"modifiable\": true, \"created_at\": \"2025-11-13T17:58:49\"}','Création poste: Agent de Bureau','127.0.0.1'),(17,'2025-11-13 18:59:18',2,'sghellam@gmail.com','postes_travail','CREATE',17,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:59:19\", \"libelle\": \"Responsable Facturation\", \"id\": 17, \"modifiable\": true, \"created_at\": \"2025-11-13T17:59:19\"}','Création poste: Responsable Facturation','127.0.0.1'),(18,'2025-11-13 18:59:29',2,'sghellam@gmail.com','postes_travail','CREATE',18,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:59:30\", \"libelle\": \"Directeur Administration\", \"id\": 18, \"modifiable\": true, \"created_at\": \"2025-11-13T17:59:30\"}','Création poste: Directeur Administration','127.0.0.1'),(19,'2025-11-13 18:59:41',2,'sghellam@gmail.com','postes_travail','CREATE',19,'null','{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:59:42\", \"libelle\": \"Vendeur\", \"id\": 19, \"modifiable\": true, \"created_at\": \"2025-11-13T17:59:42\"}','Création poste: Vendeur','127.0.0.1'),(20,'2025-11-13 18:59:49',2,'sghellam@gmail.com','postes_travail','UPDATE',19,'{\"est_chauffeur\": false, \"actif\": true, \"updated_at\": \"2025-11-13T17:59:42\", \"libelle\": \"Vendeur\", \"id\": 19, \"modifiable\": true, \"created_at\": \"2025-11-13T17:59:42\"}','{\"est_chauffeur\": true, \"actif\": true, \"updated_at\": \"2025-11-13T17:59:50\", \"libelle\": \"Vendeur\", \"id\": 19, \"modifiable\": true, \"created_at\": \"2025-11-13T17:59:42\"}','Modification poste: Vendeur','127.0.0.1'),(21,'2025-11-13 19:00:01',2,'sghellam@gmail.com','postes_travail','CREATE',20,'null','{\"est_chauffeur\": true, \"actif\": true, \"updated_at\": \"2025-11-13T18:00:02\", \"libelle\": \"Aide Vendeur\", \"id\": 20, \"modifiable\": true, \"created_at\": \"2025-11-13T18:00:02\"}','Création poste: Aide Vendeur','127.0.0.1'),(22,'2025-11-13 19:00:30',2,'sghellam@gmail.com','postes_travail','CREATE',21,'null','{\"est_chauffeur\": true, \"actif\": true, \"updated_at\": \"2025-11-13T18:00:31\", \"libelle\": \"Chauffeur Lourd\", \"id\": 21, \"modifiable\": true, \"created_at\": \"2025-11-13T18:00:31\"}','Création poste: Chauffeur Lourd','127.0.0.1'),(23,'2025-11-14 00:46:38',2,'sghellam@gmail.com','employes','UPDATE',4,'{\"numero_secu_sociale\": \"82600124502255\", \"poste_travail\": \"test\", \"numero_compte_bancaire\": \"1234567897897789\", \"salaire_base\": 30000.0, \"id\": 4, \"numero_anem\": \"2025/22255/022\", \"prime_nuit_agent_securite\": false, \"prenom\": \"Abderrezzaq\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Actif\", \"nom\": \"Ghellam\", \"date_naissance\": \"1982-06-26\", \"femme_au_foyer\": true, \"actif\": true, \"lieu_naissance\": \"chelghoum laid\", \"date_recrutement\": \"2020-01-01\", \"adresse\": \"Cit\\u00e9 des Fr\\u00e8res Borni N\\u00b0166\", \"duree_contrat\": null, \"mobile\": \"0775646557\", \"date_fin_contrat\": \"2027-12-31\"}','{\"numero_secu_sociale\": \"82600124502255\", \"poste_travail\": \"test\", \"numero_compte_bancaire\": \"1234567897897789\", \"salaire_base\": 25000.0, \"id\": 4, \"numero_anem\": \"2025/22255/022\", \"prime_nuit_agent_securite\": false, \"prenom\": \"Abderrezzaq\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Actif\", \"nom\": \"Ghellam\", \"date_naissance\": \"1982-06-26\", \"femme_au_foyer\": true, \"actif\": true, \"lieu_naissance\": \"chelghoum laid\", \"date_recrutement\": \"2020-01-01\", \"adresse\": \"Cit\\u00e9 des Fr\\u00e8res Borni N\\u00b0166\", \"duree_contrat\": null, \"mobile\": \"0775646557\", \"date_fin_contrat\": \"2027-12-31\"}','Modification employé: Ghellam Abderrezzaq','127.0.0.1'),(24,'2025-11-14 12:10:18',2,'sghellam@gmail.com','employes','CREATE',26,'null','{\"numero_secu_sociale\": \"0215245556\", \"poste_travail\": \"Agent Commercial\", \"numero_compte_bancaire\": \"125545\", \"salaire_base\": 20000.0, \"id\": 26, \"numero_anem\": \"12554555\", \"prime_nuit_agent_securite\": false, \"prenom\": \"test\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Actif\", \"nom\": \"tes\", \"date_naissance\": \"2000-01-01\", \"femme_au_foyer\": false, \"actif\": true, \"lieu_naissance\": \"chelghoum laid\", \"date_recrutement\": \"2025-11-01\", \"adresse\": \"ici\", \"duree_contrat\": 12, \"mobile\": \"08855445522\", \"date_fin_contrat\": \"2026-11-01\"}','Création employé: tes test','127.0.0.1'),(25,'2025-11-14 12:24:53',2,'sghellam@gmail.com','employes','CREATE',27,'null','{\"numero_secu_sociale\": \"215558896\", \"poste_travail\": \"Agent de Nettoyage et Entretien\", \"numero_compte_bancaire\": \"556668855\", \"salaire_base\": 25000.0, \"id\": 27, \"numero_anem\": \"222588552\", \"prime_nuit_agent_securite\": false, \"prenom\": \"123\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Actif\", \"nom\": \"123\", \"date_naissance\": \"2000-01-01\", \"femme_au_foyer\": false, \"actif\": true, \"lieu_naissance\": \"chelghoum laid\", \"date_recrutement\": \"2025-11-01\", \"adresse\": \"dff\", \"duree_contrat\": 12, \"mobile\": \"0556225511\", \"date_fin_contrat\": \"2026-11-01\"}','Création employé: 123 123','127.0.0.1'),(26,'2025-11-14 14:40:37',2,'sghellam@gmail.com','employes','DELETE',27,'{\"nom\": \"123\", \"date_naissance\": \"2000-01-01\", \"femme_au_foyer\": false, \"actif\": true, \"lieu_naissance\": \"chelghoum laid\", \"date_recrutement\": \"2025-11-01\", \"adresse\": \"dff\", \"duree_contrat\": 12, \"mobile\": \"0556225511\", \"date_fin_contrat\": \"2026-11-01\", \"numero_secu_sociale\": \"215558896\", \"poste_travail\": \"Agent de Nettoyage et Entretien\", \"numero_compte_bancaire\": \"556668855\", \"salaire_base\": 25000.0, \"id\": 27, \"numero_anem\": \"222588552\", \"prime_nuit_agent_securite\": false, \"prenom\": \"123\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Actif\"}','null','Suppression définitive employé: 123 123','127.0.0.1'),(27,'2025-11-14 14:41:04',2,'sghellam@gmail.com','employes','UPDATE',19,'{\"nom\": \"DEBUG112319636\", \"date_naissance\": \"1995-05-15\", \"femme_au_foyer\": true, \"actif\": true, \"lieu_naissance\": \"Constantine\", \"date_recrutement\": \"2025-02-01\", \"adresse\": \"Rue Debug 456\", \"duree_contrat\": null, \"mobile\": \"0666112319\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG112319636\", \"poste_travail\": \"Chauffeur\", \"numero_compte_bancaire\": \"002112319636\", \"salaire_base\": 25000.0, \"id\": 19, \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false, \"prenom\": \"Test\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Actif\"}','{\"nom\": \"DEBUG112319636\", \"date_naissance\": \"1995-05-15\", \"femme_au_foyer\": true, \"actif\": false, \"lieu_naissance\": \"Constantine\", \"date_recrutement\": \"2025-02-01\", \"adresse\": \"Rue Debug 456\", \"duree_contrat\": null, \"mobile\": \"0666112319\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG112319636\", \"poste_travail\": \"Chauffeur\", \"numero_compte_bancaire\": \"002112319636\", \"salaire_base\": 25000.0, \"id\": 19, \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false, \"prenom\": \"Test\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Inactif\"}','Désactivation employé: DEBUG112319636 Test','127.0.0.1'),(28,'2025-11-14 15:40:01',2,'sghellam@gmail.com','employes','UPDATE',26,'{\"numero_secu_sociale\": \"0215245556\", \"poste_travail\": \"Agent Commercial\", \"id\": 26, \"numero_compte_bancaire\": \"125545\", \"salaire_base\": 20000.0, \"prenom\": \"test\", \"numero_anem\": \"12554555\", \"prime_nuit_agent_securite\": false, \"nom\": \"tes\", \"date_naissance\": \"2000-01-01\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Actif\", \"lieu_naissance\": \"chelghoum laid\", \"femme_au_foyer\": false, \"actif\": true, \"adresse\": \"ici\", \"date_recrutement\": \"2025-11-01\", \"mobile\": \"08855445522\", \"duree_contrat\": 12, \"date_fin_contrat\": \"2026-11-01\"}','{\"numero_secu_sociale\": \"0215245556\", \"poste_travail\": \"Agent Commercial\", \"id\": 26, \"numero_compte_bancaire\": \"125545\", \"salaire_base\": 20000.0, \"prenom\": \"test\", \"numero_anem\": \"12554555\", \"prime_nuit_agent_securite\": false, \"nom\": \"tes\", \"date_naissance\": \"2000-01-01\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Inactif\", \"lieu_naissance\": \"chelghoum laid\", \"femme_au_foyer\": false, \"actif\": false, \"adresse\": \"ici\", \"date_recrutement\": \"2025-11-01\", \"mobile\": \"08855445522\", \"duree_contrat\": 12, \"date_fin_contrat\": \"2026-11-01\"}','Désactivation employé: tes test','127.0.0.1'),(29,'2025-11-14 15:52:13',2,'sghellam@gmail.com','employes','UPDATE',16,'{\"mobile\": \"0666112005\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG112005088\", \"poste_travail\": \"Chauffeur\", \"id\": 16, \"numero_compte_bancaire\": \"002112005088\", \"salaire_base\": 25000.0, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false, \"nom\": \"DEBUG112005088\", \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Actif\", \"lieu_naissance\": \"Constantine\", \"femme_au_foyer\": true, \"actif\": true, \"adresse\": \"Rue Debug 456\", \"date_recrutement\": \"2025-02-01\", \"duree_contrat\": null}','{\"mobile\": \"0666112005\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG112005088\", \"poste_travail\": \"Chauffeur\", \"id\": 16, \"numero_compte_bancaire\": \"002112005088\", \"salaire_base\": 30000.0, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false, \"nom\": \"DEBUG112005088\", \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Actif\", \"lieu_naissance\": \"Constantine\", \"femme_au_foyer\": true, \"actif\": true, \"adresse\": \"Rue Debug 456\", \"date_recrutement\": \"2025-02-01\", \"duree_contrat\": null}','Modification employé: DEBUG112005088 Test','127.0.0.1'),(30,'2025-11-14 16:24:56',2,'sghellam@gmail.com','employes','UPDATE',19,'{\"mobile\": \"0666112319\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG112319636\", \"poste_travail\": \"Chauffeur\", \"id\": 19, \"numero_compte_bancaire\": \"002112319636\", \"salaire_base\": 25000.0, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false, \"nom\": \"DEBUG112319636\", \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Inactif\", \"lieu_naissance\": \"Constantine\", \"femme_au_foyer\": true, \"actif\": false, \"adresse\": \"Rue Debug 456\", \"date_recrutement\": \"2025-02-01\", \"duree_contrat\": null}','{\"mobile\": \"0666112319\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG112319636\", \"poste_travail\": \"Chauffeur\", \"id\": 19, \"numero_compte_bancaire\": \"002112319636\", \"salaire_base\": 35000.0, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false, \"nom\": \"DEBUG112319636\", \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Inactif\", \"lieu_naissance\": \"Constantine\", \"femme_au_foyer\": true, \"actif\": false, \"adresse\": \"Rue Debug 456\", \"date_recrutement\": \"2025-02-01\", \"duree_contrat\": null}','Modification employé: DEBUG112319636 Test','127.0.0.1'),(31,'2025-11-14 16:25:10',2,'sghellam@gmail.com','employes','UPDATE',19,'{\"mobile\": \"0666112319\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG112319636\", \"poste_travail\": \"Chauffeur\", \"id\": 19, \"numero_compte_bancaire\": \"002112319636\", \"salaire_base\": 35000.0, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false, \"nom\": \"DEBUG112319636\", \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Inactif\", \"lieu_naissance\": \"Constantine\", \"femme_au_foyer\": true, \"actif\": false, \"adresse\": \"Rue Debug 456\", \"date_recrutement\": \"2025-02-01\", \"duree_contrat\": null}','{\"mobile\": \"0666112319\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG112319636\", \"poste_travail\": \"Chauffeur\", \"id\": 19, \"numero_compte_bancaire\": \"002112319636\", \"salaire_base\": 35000.0, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false, \"nom\": \"DEBUG112319636\", \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Actif\", \"lieu_naissance\": \"Constantine\", \"femme_au_foyer\": true, \"actif\": true, \"adresse\": \"Rue Debug 456\", \"date_recrutement\": \"2025-02-01\", \"duree_contrat\": null}','Réactivation employé: DEBUG112319636 Test','127.0.0.1'),(32,'2025-11-16 15:04:05',2,'sghellam@gmail.com','employes','UPDATE',7,'{\"id\": 7, \"date_naissance\": \"1980-02-01\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Actif\", \"nom\": \"test\", \"femme_au_foyer\": false, \"actif\": true, \"lieu_naissance\": \"chelghoum laid\", \"date_recrutement\": \"2025-11-10\", \"adresse\": \"Cit\\u00e9 des Fr\\u00e8res Borni N\\u00b0166\", \"duree_contrat\": null, \"mobile\": \"0775646557\", \"date_fin_contrat\": \"2026-11-09\", \"numero_secu_sociale\": \"82600124502255556\", \"poste_travail\": \"chauffeur\", \"numero_compte_bancaire\": \"12345678978977894\", \"salaire_base\": 25000.0, \"prenom\": \"test\", \"numero_anem\": \"1234567897897789\", \"prime_nuit_agent_securite\": false}','{\"id\": 7, \"date_naissance\": \"1980-02-01\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Inactif\", \"nom\": \"test\", \"femme_au_foyer\": false, \"actif\": false, \"lieu_naissance\": \"chelghoum laid\", \"date_recrutement\": \"2025-11-10\", \"adresse\": \"Cit\\u00e9 des Fr\\u00e8res Borni N\\u00b0166\", \"duree_contrat\": null, \"mobile\": \"0775646557\", \"date_fin_contrat\": \"2026-11-09\", \"numero_secu_sociale\": \"82600124502255556\", \"poste_travail\": \"chauffeur\", \"numero_compte_bancaire\": \"12345678978977894\", \"salaire_base\": 25000.0, \"prenom\": \"test\", \"numero_anem\": \"1234567897897789\", \"prime_nuit_agent_securite\": false}','Désactivation employé: test test','127.0.0.1'),(33,'2025-11-16 15:04:13',2,'sghellam@gmail.com','employes','UPDATE',25,'{\"id\": 25, \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Actif\", \"nom\": \"DEBUG114204021\", \"femme_au_foyer\": true, \"actif\": true, \"lieu_naissance\": \"Constantine\", \"date_recrutement\": \"2025-02-01\", \"adresse\": \"Rue Debug 456\", \"duree_contrat\": null, \"mobile\": \"0666114204\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG114204021\", \"poste_travail\": \"Chauffeur\", \"numero_compte_bancaire\": \"002114204021\", \"salaire_base\": 25000.0, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false}','{\"id\": 25, \"date_naissance\": \"1995-05-15\", \"situation_familiale\": \"Mari\\u00e9\", \"statut_contrat\": \"Inactif\", \"nom\": \"DEBUG114204021\", \"femme_au_foyer\": true, \"actif\": false, \"lieu_naissance\": \"Constantine\", \"date_recrutement\": \"2025-02-01\", \"adresse\": \"Rue Debug 456\", \"duree_contrat\": null, \"mobile\": \"0666114204\", \"date_fin_contrat\": \"2026-02-01\", \"numero_secu_sociale\": \"DEBUG114204021\", \"poste_travail\": \"Chauffeur\", \"numero_compte_bancaire\": \"002114204021\", \"salaire_base\": 25000.0, \"prenom\": \"Test\", \"numero_anem\": \"ANEM123\", \"prime_nuit_agent_securite\": false}','Désactivation employé: DEBUG114204021 Test','127.0.0.1'),(34,'2025-11-16 15:07:22',2,'sghellam@gmail.com','employes','CREATE',28,'null','{\"id\": 28, \"date_naissance\": \"2000-02-01\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Actif\", \"nom\": \"titi\", \"femme_au_foyer\": false, \"actif\": true, \"lieu_naissance\": \"Constantine\", \"date_recrutement\": \"2025-11-16\", \"adresse\": \"tete\", \"duree_contrat\": 12, \"mobile\": \"0552252526\", \"date_fin_contrat\": \"2026-11-16\", \"numero_secu_sociale\": \"02555522\", \"poste_travail\": \"Agent de Nettoyage et Entretien\", \"numero_compte_bancaire\": \"0222544\", \"salaire_base\": 25000.0, \"prenom\": \"titi\", \"numero_anem\": \"2555\", \"prime_nuit_agent_securite\": false}','Création employé: titi titi','127.0.0.1'),(35,'2025-11-16 15:25:31',2,'sghellam@gmail.com','employes','UPDATE',28,'{\"id\": 28, \"date_naissance\": \"2000-02-01\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Actif\", \"nom\": \"titi\", \"femme_au_foyer\": false, \"actif\": true, \"lieu_naissance\": \"Constantine\", \"date_recrutement\": \"2025-11-16\", \"adresse\": \"tete\", \"duree_contrat\": 12, \"mobile\": \"0552252526\", \"date_fin_contrat\": \"2026-11-16\", \"numero_secu_sociale\": \"02555522\", \"poste_travail\": \"Agent de Nettoyage et Entretien\", \"numero_compte_bancaire\": \"0222544\", \"salaire_base\": 25000.0, \"prenom\": \"titi\", \"numero_anem\": \"2555\", \"prime_nuit_agent_securite\": false}','{\"id\": 28, \"date_naissance\": \"2000-02-01\", \"situation_familiale\": \"C\\u00e9libataire\", \"statut_contrat\": \"Actif\", \"nom\": \"titi\", \"femme_au_foyer\": false, \"actif\": true, \"lieu_naissance\": \"Constantine\", \"date_recrutement\": \"2025-01-01\", \"adresse\": \"tete\", \"duree_contrat\": 12, \"mobile\": \"0552252526\", \"date_fin_contrat\": \"2026-01-01\", \"numero_secu_sociale\": \"02555522\", \"poste_travail\": \"Agent de Nettoyage et Entretien\", \"numero_compte_bancaire\": \"0222544\", \"salaire_base\": 30000.0, \"prenom\": \"titi\", \"numero_anem\": \"2555\", \"prime_nuit_agent_securite\": false}','Modification employé: titi titi','127.0.0.1');
/*!40000 ALTER TABLE `logging` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `missions`
--

DROP TABLE IF EXISTS `missions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `missions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_mission` date NOT NULL,
  `chauffeur_id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `distance` decimal(10,2) NOT NULL,
  `tarif_km` decimal(10,2) NOT NULL,
  `prime_calculee` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `chauffeur_id` (`chauffeur_id`),
  KEY `client_id` (`client_id`),
  KEY `ix_missions_id` (`id`),
  KEY `ix_missions_date_mission` (`date_mission`),
  CONSTRAINT `missions_ibfk_1` FOREIGN KEY (`chauffeur_id`) REFERENCES `employes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `missions_ibfk_2` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `missions`
--

LOCK TABLES `missions` WRITE;
/*!40000 ALTER TABLE `missions` DISABLE KEYS */;
/*!40000 ALTER TABLE `missions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parametres`
--

DROP TABLE IF EXISTS `parametres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `parametres` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cle` varchar(50) NOT NULL,
  `valeur` varchar(200) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_parametres_cle` (`cle`),
  KEY `ix_parametres_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parametres`
--

LOCK TABLES `parametres` WRITE;
/*!40000 ALTER TABLE `parametres` DISABLE KEYS */;
INSERT INTO `parametres` VALUES (1,'tarif_km','3.00','Tarif kilométrique pour les missions (DA/km)');
/*!40000 ALTER TABLE `parametres` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parametres_entreprise`
--

DROP TABLE IF EXISTS `parametres_entreprise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `parametres_entreprise` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `raison_sociale` varchar(255) DEFAULT NULL,
  `nom_entreprise` varchar(255) DEFAULT NULL,
  `adresse` varchar(500) DEFAULT NULL,
  `rc` varchar(100) DEFAULT NULL,
  `nif` varchar(100) DEFAULT NULL,
  `nis` varchar(100) DEFAULT NULL,
  `art` varchar(100) DEFAULT NULL,
  `numero_secu_employeur` varchar(100) DEFAULT NULL,
  `telephone` varchar(100) DEFAULT NULL,
  `compte_bancaire` varchar(255) DEFAULT NULL,
  `banque` varchar(255) DEFAULT NULL,
  `date_creation` datetime DEFAULT current_timestamp(),
  `derniere_mise_a_jour` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parametres_entreprise`
--

LOCK TABLES `parametres_entreprise` WRITE;
/*!40000 ALTER TABLE `parametres_entreprise` DISABLE KEYS */;
INSERT INTO `parametres_entreprise` VALUES (1,'ABDELKAHAR YOURT','ABDELKAHAR YOURT','Douar Lemghalsa, Chelghoum Laid, Wilaya de Mila','21B123456','52552255225522','2255225522552255','125445566','5246688554422','0555123456','0012345678901234','CPA','2025-11-12 16:59:00','2025-11-13 11:51:42');
/*!40000 ALTER TABLE `parametres_entreprise` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pointages`
--

DROP TABLE IF EXISTS `pointages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `pointages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employe_id` int(11) NOT NULL,
  `annee` int(11) NOT NULL,
  `mois` int(11) NOT NULL,
  `jour_01` tinyint(1) DEFAULT NULL,
  `jour_02` tinyint(1) DEFAULT NULL,
  `jour_03` tinyint(1) DEFAULT NULL,
  `jour_04` tinyint(1) DEFAULT NULL,
  `jour_05` tinyint(1) DEFAULT NULL,
  `jour_06` tinyint(1) DEFAULT NULL,
  `jour_07` tinyint(1) DEFAULT NULL,
  `jour_08` tinyint(1) DEFAULT NULL,
  `jour_09` tinyint(1) DEFAULT NULL,
  `jour_10` tinyint(1) DEFAULT NULL,
  `jour_11` tinyint(1) DEFAULT NULL,
  `jour_12` tinyint(1) DEFAULT NULL,
  `jour_13` tinyint(1) DEFAULT NULL,
  `jour_14` tinyint(1) DEFAULT NULL,
  `jour_15` tinyint(1) DEFAULT NULL,
  `jour_16` tinyint(1) DEFAULT NULL,
  `jour_17` tinyint(1) DEFAULT NULL,
  `jour_18` tinyint(1) DEFAULT NULL,
  `jour_19` tinyint(1) DEFAULT NULL,
  `jour_20` tinyint(1) DEFAULT NULL,
  `jour_21` tinyint(1) DEFAULT NULL,
  `jour_22` tinyint(1) DEFAULT NULL,
  `jour_23` tinyint(1) DEFAULT NULL,
  `jour_24` tinyint(1) DEFAULT NULL,
  `jour_25` tinyint(1) DEFAULT NULL,
  `jour_26` tinyint(1) DEFAULT NULL,
  `jour_27` tinyint(1) DEFAULT NULL,
  `jour_28` tinyint(1) DEFAULT NULL,
  `jour_29` tinyint(1) DEFAULT NULL,
  `jour_30` tinyint(1) DEFAULT NULL,
  `jour_31` tinyint(1) DEFAULT NULL,
  `verrouille` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `employe_id` (`employe_id`),
  KEY `ix_pointages_mois` (`mois`),
  KEY `ix_pointages_annee` (`annee`),
  KEY `ix_pointages_id` (`id`),
  CONSTRAINT `pointages_ibfk_1` FOREIGN KEY (`employe_id`) REFERENCES `employes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pointages`
--

LOCK TABLES `pointages` WRITE;
/*!40000 ALTER TABLE `pointages` DISABLE KEYS */;
/*!40000 ALTER TABLE `pointages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `postes_travail`
--

DROP TABLE IF EXISTS `postes_travail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `postes_travail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `libelle` varchar(100) NOT NULL COMMENT 'Nom du poste',
  `est_chauffeur` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si le poste est chauffeur',
  `modifiable` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Indique si le poste peut être modifié/supprimé',
  `actif` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Soft delete',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `libelle` (`libelle`),
  KEY `idx_actif` (`actif`),
  KEY `idx_est_chauffeur` (`est_chauffeur`),
  KEY `idx_libelle` (`libelle`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Table des postes de travail avec gestion des chauffeurs et soft delete';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `postes_travail`
--

LOCK TABLES `postes_travail` WRITE;
/*!40000 ALTER TABLE `postes_travail` DISABLE KEYS */;
INSERT INTO `postes_travail` VALUES (1,'Chauffeur',1,0,1,'2025-11-13 11:14:57','2025-11-13 11:14:57'),(19,'Vendeur',1,1,1,'2025-11-13 17:59:42','2025-11-13 17:59:50'),(20,'Aide Vendeur',1,1,1,'2025-11-13 18:00:02','2025-11-13 18:00:02'),(21,'Chauffeur Lourd',1,1,1,'2025-11-13 18:00:31','2025-11-13 18:00:31'),(22,'AGENT ADMINISTRATIF',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(23,'AGENT DE CONTRÔLE',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(24,'AGENT DE SECURITE',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(25,'CHEF EQUIPE',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(26,'COMPTABLE',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(27,'CUISINIER',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(28,'DIRECTEUR COMMERCIAL',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(29,'EMPLOYE',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(30,'ENT/MAINT',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(31,'MECANICIEN',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(32,'RESPONSABLE ENT/MAINT',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(33,'RESPONSABLE PERSONNEL',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41'),(34,'SEC',0,1,1,'2025-11-17 18:03:41','2025-11-17 18:03:41');
/*!40000 ALTER TABLE `postes_travail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prorogations_credit`
--

DROP TABLE IF EXISTS `prorogations_credit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `prorogations_credit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `credit_id` int(11) NOT NULL,
  `date_prorogation` date NOT NULL,
  `mois_initial` int(11) NOT NULL,
  `annee_initiale` int(11) NOT NULL,
  `mois_reporte` int(11) NOT NULL,
  `annee_reportee` int(11) NOT NULL,
  `motif` varchar(500) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `credit_id` (`credit_id`),
  KEY `ix_prorogations_credit_id` (`id`),
  KEY `ix_prorogations_credit_date_prorogation` (`date_prorogation`),
  CONSTRAINT `prorogations_credit_ibfk_1` FOREIGN KEY (`credit_id`) REFERENCES `credits` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prorogations_credit`
--

LOCK TABLES `prorogations_credit` WRITE;
/*!40000 ALTER TABLE `prorogations_credit` DISABLE KEYS */;
/*!40000 ALTER TABLE `prorogations_credit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `retenues_credit`
--

DROP TABLE IF EXISTS `retenues_credit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `retenues_credit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `credit_id` int(11) NOT NULL,
  `mois` int(11) NOT NULL,
  `annee` int(11) NOT NULL,
  `montant` decimal(12,2) NOT NULL,
  `date_retenue` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `credit_id` (`credit_id`),
  KEY `ix_retenues_credit_mois` (`mois`),
  KEY `ix_retenues_credit_annee` (`annee`),
  KEY `ix_retenues_credit_id` (`id`),
  CONSTRAINT `retenues_credit_ibfk_1` FOREIGN KEY (`credit_id`) REFERENCES `credits` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `retenues_credit`
--

LOCK TABLES `retenues_credit` WRITE;
/*!40000 ALTER TABLE `retenues_credit` DISABLE KEYS */;
/*!40000 ALTER TABLE `retenues_credit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('Admin','Utilisateur') NOT NULL DEFAULT 'Utilisateur',
  `actif` tinyint(1) DEFAULT 1,
  `date_creation` datetime DEFAULT current_timestamp(),
  `derniere_connexion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_email` (`email`),
  KEY `idx_role` (`role`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (2,'sghellam@gmail.com','Ghellam','Abderrezzaq','$2b$12$32TCf7/jKAImTrSZoSxOB.q7PdK5j9dmU7Kjo/a/r8gP4gR6gqqXe','Admin',1,'2025-11-12 17:09:26','2025-11-16 20:29:26');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-17 18:06:34

-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: greendiagnose
-- ------------------------------------------------------
-- Server version	26.7.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '408b8944-b7b5-11f1-87bd-c018508fb81f:1-131';

--
-- Table structure for table `diagnosis_session`
--

DROP TABLE IF EXISTS `diagnosis_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnosis_session` (
  `id` int NOT NULL AUTO_INCREMENT,
  `species_id` int NOT NULL,
  `image_path` varchar(255) NOT NULL COMMENT 'retained photo, pending horticulturist validation before any training use',
  `predicted_disease_id` int DEFAULT NULL COMMENT 'CNN''s top prediction, filled after classification',
  `predicted_confidence` decimal(5,4) DEFAULT NULL COMMENT 'e.g. 0.9134',
  `consent_for_training` tinyint(1) DEFAULT '0' COMMENT 'explicit separate consent, per RA 10173 requirement',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `species_id` (`species_id`),
  KEY `predicted_disease_id` (`predicted_disease_id`),
  CONSTRAINT `diagnosis_session_ibfk_1` FOREIGN KEY (`species_id`) REFERENCES `plant_species` (`id`),
  CONSTRAINT `diagnosis_session_ibfk_2` FOREIGN KEY (`predicted_disease_id`) REFERENCES `disease` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diagnosis_session`
--

LOCK TABLES `diagnosis_session` WRITE;
/*!40000 ALTER TABLE `diagnosis_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `diagnosis_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disease`
--

DROP TABLE IF EXISTS `disease`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disease` (
  `id` int NOT NULL AUTO_INCREMENT,
  `species_id` int NOT NULL,
  `name` varchar(150) NOT NULL COMMENT 'e.g. "Fungal Leaf Spot", specific to this species',
  `description` text,
  `severity_level` enum('low','moderate','high') DEFAULT 'moderate',
  PRIMARY KEY (`id`),
  KEY `species_id` (`species_id`),
  CONSTRAINT `disease_ibfk_1` FOREIGN KEY (`species_id`) REFERENCES `plant_species` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disease`
--

LOCK TABLES `disease` WRITE;
/*!40000 ALTER TABLE `disease` DISABLE KEYS */;
INSERT INTO `disease` VALUES (1,1,'Fungal Leaf Spot','A common fungal infection causing dark lesions.','moderate'),(2,1,'Healthy','The leaf appears healthy with no visible signs of disease.','moderate'),(5,3,'Dactylopius opuntia (cochineal scale)','White cottony clusters causing pest damage.','moderate'),(6,3,'Healthy','Firm green stems with no visible signs of damage.','moderate'),(7,4,'Bacterial Wilt Disease','Sudden wilting and dark streaks on stems and leaves.','high'),(8,4,'Manganese Toxicity','Brown/black leaf spots caused by nutrient imbalance.','moderate'),(9,4,'Healthy','Glossy green leaves.','moderate'),(10,5,'Anthracnose','Dark lesions on leaves caused by fungal infection.','moderate'),(11,5,'Leaf Withering','Drooping, drying leaves due to physiological stress.','moderate'),(12,5,'Healthy','Upright green leaves with no visible damage.','moderate'),(13,6,'Fungal Leaf Spot','Small black or brown spots on leaves.','moderate'),(14,6,'Leaf Tip Necrosis','Brown necrotic tips caused by physiological stress.','low'),(15,6,'Healthy','Green striped leaves in healthy condition.','moderate'),(16,7,'Mosaic Virus','Mottled yellow leaves caused by viral infection.','high'),(17,7,'Pest Damage','Holes and sticky residue on leaves.','moderate'),(18,7,'Botrytis Blight','Gray mold and necrotic spots on leaves/petals.','high'),(19,7,'Healthy','Normal green leaves with no visible damage.','moderate'),(20,8,'Alternaria Leaf Blight','Concentric brown spots caused by fungal infection.','moderate'),(21,8,'Pest Damage','Chewed leaves caused by insects.','moderate'),(22,8,'Healthy','Normal green leaves.','moderate'),(23,9,'Anthracnose','Dark sunken lesions caused by fungal infection.','moderate'),(24,9,'Bacterial Wilt','Sudden wilting of plant tissue.','high'),(25,9,'Black Rot','Black rotting tissue on leaves or pseudobulbs.','high'),(26,9,'Brown Spots','Brown circular spots on leaves.','moderate'),(27,9,'Mold','White fuzzy growth due to fungal presence.','moderate'),(28,9,'Soft Rot','Soft mushy tissue breakdown.','high'),(29,9,'Withered Yellow Root','Yellow shriveled roots from physiological stress.','moderate'),(30,9,'Healthy','Firm green leaves and healthy root system.','moderate'),(31,10,'Downy Mildew','Yellow patches with downy fungal growth on leaves.','moderate'),(32,10,'Gray Mold','Gray fuzzy mold infection.','high'),(33,10,'Leaf Scars','Scarring on leaves from damage or stress.','low'),(34,10,'Sclerotinia Rot','White cottony rot on stems or roots.','high'),(35,10,'Sunflower Rust','Orange pustules on leaves and stems.','moderate'),(36,10,'Fresh Leaf','Fresh green leaves in healthy condition.','moderate'),(42,2,'Anthracnose','Fungal infection causing dark sunken lesions.','moderate'),(43,2,'Leaf Spot','Brown or black circular spots on leaves.','moderate'),(44,2,'Rust','Orange pustules on the underside of leaves.','moderate'),(45,2,'Sunburn','Brown scorched patches due to excessive light.','low'),(46,2,'Healthy','Normal green leaves with no signs of damage.','low'),(47,9,'Oxidation','Oxidation damage and discoloration on leaves','moderate'),(48,9,'Virus','Viral infection causing mottling and distortion','high');
/*!40000 ALTER TABLE `disease` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disease_symptom_rule`
--

DROP TABLE IF EXISTS `disease_symptom_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disease_symptom_rule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `disease_id` int NOT NULL,
  `symptom_id` int NOT NULL,
  `certainty_weight` decimal(3,2) NOT NULL COMMENT 'e.g. 0.85',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_rule` (`disease_id`,`symptom_id`),
  KEY `symptom_id` (`symptom_id`),
  CONSTRAINT `disease_symptom_rule_ibfk_1` FOREIGN KEY (`disease_id`) REFERENCES `disease` (`id`) ON DELETE CASCADE,
  CONSTRAINT `disease_symptom_rule_ibfk_2` FOREIGN KEY (`symptom_id`) REFERENCES `symptom` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disease_symptom_rule`
--

LOCK TABLES `disease_symptom_rule` WRITE;
/*!40000 ALTER TABLE `disease_symptom_rule` DISABLE KEYS */;
INSERT INTO `disease_symptom_rule` VALUES (1,1,1,0.70),(2,1,2,0.30),(3,5,3,0.90),(4,7,4,0.85),(5,8,5,0.80),(6,10,6,0.85),(7,11,7,0.80),(8,13,8,0.85),(9,14,9,0.75),(10,16,10,0.90),(11,17,11,0.85),(12,18,12,0.90),(13,20,13,0.85),(14,21,14,0.80),(15,23,15,0.85),(16,24,16,0.90),(17,25,17,0.90),(18,26,18,0.80),(19,27,19,0.80),(20,28,20,0.90),(21,29,21,0.75),(22,31,22,0.85),(23,32,23,0.90),(24,33,24,0.70),(25,34,25,0.90),(26,35,26,0.85),(27,42,27,0.85),(28,43,28,0.80),(29,44,29,0.90),(30,45,30,0.75);
/*!40000 ALTER TABLE `disease_symptom_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `diseases`
--

DROP TABLE IF EXISTS `diseases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diseases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `species_id` int NOT NULL,
  `name` varchar(150) NOT NULL,
  `description` text,
  `severity` varchar(50) DEFAULT 'moderate',
  PRIMARY KEY (`id`),
  KEY `species_id` (`species_id`),
  CONSTRAINT `diseases_ibfk_1` FOREIGN KEY (`species_id`) REFERENCES `species` (`species_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diseases`
--

LOCK TABLES `diseases` WRITE;
/*!40000 ALTER TABLE `diseases` DISABLE KEYS */;
INSERT INTO `diseases` VALUES (1,7,'Botrytis Blight','Fungal infection causing gray mold and tissue rot','moderate'),(2,7,'Healthy','Normal healthy rose leaves','low'),(3,7,'Pest Damage','Chewed leaves caused by insects','moderate'),(4,7,'Mosaic Virus','Viral infection causing leaf mottling and yellow patterns','high'),(5,8,'Alternaria Leaf Blight','Dark spots and blighting on leaves','moderate'),(6,8,'Healthy','Normal green leaves with no signs of damage','low'),(7,8,'Pest Damage','Chewed leaves caused by insects','moderate'),(8,9,'Anthracnose','Dark sunken lesions caused by fungal infection','moderate'),(9,9,'Bacterial Wilt','Sudden wilting of plant tissue','high'),(10,9,'Black Rot','Black rotting tissue on leaves or pseudobulbs','high'),(11,9,'Brown Spots','Brown circular spots on leaves','moderate'),(12,9,'Mold','White fuzzy growth due to fungal presence','moderate'),(13,9,'Soft Rot','Soft mushy tissue breakdown','high'),(14,9,'Withered Yellow Root','Yellow shriveled roots from physiological stress','moderate'),(15,9,'Healthy','Firm green leaves and healthy root system','low'),(16,9,'Oxidation','Oxidation damage and discoloration on leaves','moderate'),(17,9,'Virus','Viral infection causing mottling and distortion','high');
/*!40000 ALTER TABLE `diseases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plant_species`
--

DROP TABLE IF EXISTS `plant_species`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plant_species` (
  `id` int NOT NULL AUTO_INCREMENT,
  `common_name` varchar(100) NOT NULL,
  `scientific_name` varchar(150) DEFAULT NULL,
  `dataset_source` varchar(150) DEFAULT NULL COMMENT 'e.g. Mendeley, Kaggle, Roboflow - for methodology documentation',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plant_species`
--

LOCK TABLES `plant_species` WRITE;
/*!40000 ALTER TABLE `plant_species` DISABLE KEYS */;
INSERT INTO `plant_species` VALUES (1,'Hibiscus','Hibiscus rosa-sinensis','Mendeley Data','2026-09-24 03:16:06'),(2,'Aloe Vera','Aloe vera','Kaggle - Indoor Plant Disease Detection Dataset','2026-09-24 03:16:06'),(3,'Cactus',NULL,'Kaggle - Indoor Plant Disease Detection Dataset','2026-09-24 03:16:06'),(4,'Money Plant','Epipremnum aureum','Kaggle - Indoor Plant Disease Detection Dataset','2026-09-24 03:16:06'),(5,'Snake Plant','Dracaena trifasciata','Kaggle - Indoor Plant Disease Detection Dataset','2026-09-24 03:16:06'),(6,'Spider Plant','Chlorophytum comosum','Kaggle - Indoor Plant Disease Detection Dataset','2026-09-24 03:16:06'),(7,'Rose','Rosa spp.','Mendeley Data','2026-09-24 03:16:06'),(8,'Marigold','Tagetes spp.','Mendeley Data','2026-09-24 03:16:06'),(9,'Orchid',NULL,'Roboflow','2026-09-24 03:16:06'),(10,'Sunflower','Helianthus annuus','Kaggle','2026-09-24 03:16:06');
/*!40000 ALTER TABLE `plant_species` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scan_logs`
--

DROP TABLE IF EXISTS `scan_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scan_logs` (
  `scan_id` int NOT NULL AUTO_INCREMENT,
  `species_id` int NOT NULL,
  `predicted_disease_id` int NOT NULL,
  `confidence_score` float NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `scanned_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`scan_id`),
  KEY `species_id` (`species_id`),
  KEY `predicted_disease_id` (`predicted_disease_id`),
  CONSTRAINT `scan_logs_ibfk_1` FOREIGN KEY (`species_id`) REFERENCES `species` (`species_id`),
  CONSTRAINT `scan_logs_ibfk_2` FOREIGN KEY (`predicted_disease_id`) REFERENCES `diseases` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scan_logs`
--

LOCK TABLES `scan_logs` WRITE;
/*!40000 ALTER TABLE `scan_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `scan_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session_answer`
--

DROP TABLE IF EXISTS `session_answer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `session_answer` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `symptom_id` int NOT NULL,
  `answer_value` varchar(20) NOT NULL COMMENT 'yes / no / unsure',
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  KEY `symptom_id` (`symptom_id`),
  CONSTRAINT `session_answer_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `diagnosis_session` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_answer_ibfk_2` FOREIGN KEY (`symptom_id`) REFERENCES `symptom` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_answer`
--

LOCK TABLES `session_answer` WRITE;
/*!40000 ALTER TABLE `session_answer` DISABLE KEYS */;
/*!40000 ALTER TABLE `session_answer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session_result`
--

DROP TABLE IF EXISTS `session_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `session_result` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `disease_id` int NOT NULL,
  `confidence_score` decimal(5,4) NOT NULL,
  `result_rank` int NOT NULL COMMENT '1 = top diagnosis, 2 = first alternative, etc.',
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  KEY `disease_id` (`disease_id`),
  CONSTRAINT `session_result_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `diagnosis_session` (`id`) ON DELETE CASCADE,
  CONSTRAINT `session_result_ibfk_2` FOREIGN KEY (`disease_id`) REFERENCES `disease` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_result`
--

LOCK TABLES `session_result` WRITE;
/*!40000 ALTER TABLE `session_result` DISABLE KEYS */;
/*!40000 ALTER TABLE `session_result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `species`
--

DROP TABLE IF EXISTS `species`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `species` (
  `species_id` int NOT NULL AUTO_INCREMENT,
  `species_name` varchar(100) NOT NULL,
  `scientific_name` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`species_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `species`
--

LOCK TABLES `species` WRITE;
/*!40000 ALTER TABLE `species` DISABLE KEYS */;
INSERT INTO `species` VALUES (7,'Rose','Rosa rubiginosa','2026-10-07 18:57:50'),(8,'Marigold','Tagetes spp.','2026-10-07 18:57:50'),(9,'Orchid','Orchidaceae spp.','2026-10-07 18:57:50');
/*!40000 ALTER TABLE `species` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `symptom`
--

DROP TABLE IF EXISTS `symptom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `symptom` (
  `id` int NOT NULL AUTO_INCREMENT,
  `species_id` int NOT NULL,
  `question_text` varchar(255) NOT NULL,
  `answer_type` enum('yes_no','yes_no_unsure','multiple_choice') DEFAULT 'yes_no_unsure',
  `display_order` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `species_id` (`species_id`),
  CONSTRAINT `symptom_ibfk_1` FOREIGN KEY (`species_id`) REFERENCES `plant_species` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `symptom`
--

LOCK TABLES `symptom` WRITE;
/*!40000 ALTER TABLE `symptom` DISABLE KEYS */;
INSERT INTO `symptom` VALUES (1,1,'Are there distinct brown or black spots on the leaves?','yes_no',1),(2,1,'Are the leaves starting to turn yellow at the edges?','yes_no',2),(3,3,'Are there white cottony clusters visible on the plant?','yes_no',1),(4,4,'Is there sudden wilting and dark streaks on the plant?','yes_no',1),(5,4,'Are there brown or black leaf spots present?','yes_no',2),(6,5,'Are there dark lesions visible on the leaves?','yes_no',1),(7,5,'Are the leaves drooping and drying out?','yes_no',2),(8,6,'Are there small black or brown spots on the leaves?','yes_no',1),(9,6,'Do the leaf tips look brown and necrotic?','yes_no',2),(10,7,'Are the leaves showing mottled yellow patterns?','yes_no',1),(11,7,'Are there visible holes or sticky residue on the plant?','yes_no',2),(12,7,'Is there gray mold or necrotic spots present?','yes_no',3),(13,8,'Are there concentric brown spots on the leaves?','yes_no',1),(14,8,'Do you see chewed leaves or insect damage?','yes_no',2),(15,9,'Are there dark sunken lesions on the plant?','yes_no',1),(16,9,'Is there sudden wilting of the plant?','yes_no',2),(17,9,'Do you see black rotting tissue?','yes_no',3),(18,9,'Are there brown circular spots on the leaves?','yes_no',4),(19,9,'Is there white fuzzy growth or mold present?','yes_no',5),(20,9,'Is there soft, mushy tissue breakdown?','yes_no',6),(21,9,'Are the roots yellow and shriveled?','yes_no',7),(22,10,'Are there yellow patches with downy growth on leaves?','yes_no',1),(23,10,'Is there gray fuzzy mold present?','yes_no',2),(24,10,'Are there physical scars on the leaves?','yes_no',3),(25,10,'Is there white cottony rot on the plant?','yes_no',4),(26,10,'Are there orange pustules on the leaves or stems?','yes_no',5),(27,2,'Are there dark sunken lesions on the leaves?','yes_no',1),(28,2,'Do you see brown or black circular spots?','yes_no',2),(29,2,'Are there orange pustules on the underside of the leaves?','yes_no',3),(30,2,'Are there brown scorched patches from excess sun exposure?','yes_no',4);
/*!40000 ALTER TABLE `symptom` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `treatment`
--

DROP TABLE IF EXISTS `treatment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `treatment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `disease_id` int NOT NULL,
  `recommendation_text` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `disease_id` (`disease_id`),
  CONSTRAINT `treatment_ibfk_1` FOREIGN KEY (`disease_id`) REFERENCES `disease` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treatment`
--

LOCK TABLES `treatment` WRITE;
/*!40000 ALTER TABLE `treatment` DISABLE KEYS */;
INSERT INTO `treatment` VALUES (1,1,'Isolate the plant immediately to prevent spreading. Remove and safely dispose of the affected leaves. Apply a copper-based fungicide to the remaining foliage. Improve air circulation and avoid overhead watering.'),(2,2,'No treatment needed! Continue your current watering and sunlight routine.'),(3,5,'Scrape pests, apply neem oil[cite: 3].'),(4,6,'Normal care[cite: 3].'),(5,7,'Remove plant, sterilize soil[cite: 3].'),(6,8,'Flush soil, adjust fertilizer[cite: 3].'),(7,9,'Balanced watering[cite: 3].'),(8,10,'Remove leaves, fungicide[cite: 3].'),(9,11,'Adjust watering, improve drainage[cite: 3].'),(10,12,'Proper care[cite: 3].'),(11,13,'Remove leaves, fungicide[cite: 3].'),(12,14,'Flush soil, reduce salts[cite: 3].'),(13,15,'Balanced watering[cite: 3].'),(14,16,'Remove infected plants[cite: 3].'),(15,17,'Insecticidal soap, neem oil[cite: 3].'),(16,18,'Prune, improve airflow, fungicide[cite: 3].'),(17,19,'Maintain care[cite: 3].'),(18,20,'Remove leaves, fungicide[cite: 3].'),(19,21,'Handpick insects, neem oil[cite: 3].'),(20,22,'Maintain care[cite: 3].'),(21,23,'Remove leaves, fungicide[cite: 3].'),(22,24,'Remove plant, sterilize soil[cite: 3].'),(23,25,'Remove infected tissue, fungicide[cite: 3].'),(24,26,'Prune leaves, fungicide[cite: 3].'),(25,27,'Improve airflow, fungicide[cite: 3].'),(26,28,'Remove infected tissue, bactericide[cite: 3].'),(27,29,'Repot, adjust watering[cite: 3].'),(28,30,'Maintain care[cite: 3].'),(29,31,'Remove leaves, fungicide[cite: 3].'),(30,32,'Prune, fungicide[cite: 3].'),(31,33,'Adjust care, prevent mechanical damage[cite: 3].'),(32,34,'Remove plants, fungicide[cite: 3].'),(33,35,'Remove leaves, sulfur spray[cite: 3].'),(34,36,'Maintain care[cite: 3].'),(35,42,'Remove infected leaves, apply fungicide.'),(36,43,'Prune leaves, apply copper fungicide.'),(37,44,'Remove leaves, apply sulfur spray.'),(38,45,'Move to indirect light.'),(39,46,'Maintain proper watering routine.');
/*!40000 ALTER TABLE `treatment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'greendiagnose'
--
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-08  3:37:01

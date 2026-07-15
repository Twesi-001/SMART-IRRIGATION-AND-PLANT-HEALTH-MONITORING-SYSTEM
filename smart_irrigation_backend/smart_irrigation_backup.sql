-- MySQL dump 10.13  Distrib 9.7.1, for Win64 (x86_64)
--
-- Host: localhost    Database: smart_irrigation
-- ------------------------------------------------------
-- Server version	9.7.1

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

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '04c51681-6b68-11f1-8b3a-507b9daff92b:1-2171';

--
-- Table structure for table `alerts`
--

DROP TABLE IF EXISTS `alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alerts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `node_id` int NOT NULL,
  `alert_type` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `severity` enum('INFO','WARNING','CRITICAL') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'WARNING',
  `resolved` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_alerts_node_resolved` (`node_id`,`resolved`),
  CONSTRAINT `fk_alerts_node` FOREIGN KEY (`node_id`) REFERENCES `sensor_nodes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerts`
--

LOCK TABLES `alerts` WRITE;
/*!40000 ALTER TABLE `alerts` DISABLE KEYS */;
INSERT INTO `alerts` VALUES (1,1,'LOW_MOISTURE','Soil moisture below 30%','WARNING',1,'2026-07-14 08:16:36','2026-07-14 08:16:39');
/*!40000 ALTER TABLE `alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `predictions`
--

DROP TABLE IF EXISTS `predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `predictions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `reading_id` bigint NOT NULL,
  `irrigation_needed` tinyint(1) NOT NULL,
  `recommended_action` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `confidence` decimal(5,4) DEFAULT NULL,
  `model_version` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_predictions_reading` (`reading_id`),
  CONSTRAINT `fk_predictions_reading` FOREIGN KEY (`reading_id`) REFERENCES `sensor_readings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `predictions`
--

LOCK TABLES `predictions` WRITE;
/*!40000 ALTER TABLE `predictions` DISABLE KEYS */;
INSERT INTO `predictions` VALUES (1,1,1,'Water now',0.8500,'v1.0','2026-07-14 08:06:25'),(2,1,1,'Water now',0.5500,'simple_threshold_v1','2026-07-14 08:07:59'),(3,1,0,'No irrigation needed',0.7500,'simple_threshold_v1','2026-07-14 08:08:25'),(4,2,1,'Water now',0.6000,'simple_threshold_v1','2026-07-14 08:25:17');
/*!40000 ALTER TABLE `predictions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pump_commands`
--

DROP TABLE IF EXISTS `pump_commands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pump_commands` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `node_id` int NOT NULL,
  `command` enum('ON','OFF') COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` enum('AUTO','MANUAL') COLLATE utf8mb4_unicode_ci NOT NULL,
  `issued_by` int DEFAULT NULL,
  `issued_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_pump_user` (`issued_by`),
  KEY `idx_pump_node_time` (`node_id`,`issued_at`),
  CONSTRAINT `fk_pump_node` FOREIGN KEY (`node_id`) REFERENCES `sensor_nodes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pump_user` FOREIGN KEY (`issued_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pump_commands`
--

LOCK TABLES `pump_commands` WRITE;
/*!40000 ALTER TABLE `pump_commands` DISABLE KEYS */;
INSERT INTO `pump_commands` VALUES (1,1,'ON','MANUAL',1,'2026-07-14 08:14:31'),(2,1,'OFF','MANUAL',1,'2026-07-14 08:14:33'),(3,1,'ON','MANUAL',1,'2026-07-14 08:28:39'),(4,1,'OFF','MANUAL',1,'2026-07-14 10:50:14'),(5,1,'OFF','MANUAL',1,'2026-07-14 10:50:15'),(6,1,'ON','MANUAL',1,'2026-07-14 10:50:19'),(7,1,'OFF','MANUAL',1,'2026-07-14 10:50:24'),(8,1,'ON','MANUAL',1,'2026-07-14 10:50:27'),(9,1,'OFF','MANUAL',1,'2026-07-14 10:50:32'),(10,1,'ON','MANUAL',1,'2026-07-14 10:50:49'),(11,1,'OFF','MANUAL',1,'2026-07-15 02:33:19'),(12,1,'ON','MANUAL',1,'2026-07-15 02:33:21');
/*!40000 ALTER TABLE `pump_commands` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_nodes`
--

DROP TABLE IF EXISTS `sensor_nodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_nodes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `node_name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `location` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `crop_type` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `moisture_threshold` decimal(5,2) DEFAULT '30.00',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_nodes`
--

LOCK TABLES `sensor_nodes` WRITE;
/*!40000 ALTER TABLE `sensor_nodes` DISABLE KEYS */;
INSERT INTO `sensor_nodes` VALUES (1,'Node-01-Updated','Avodah Innovations Training Facility, Kiyanja, Mbarara City','Maize',35.00,1,'2026-07-14 08:14:45');
/*!40000 ALTER TABLE `sensor_nodes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensor_readings`
--

DROP TABLE IF EXISTS `sensor_readings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensor_readings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `node_id` int NOT NULL,
  `soil_moisture` decimal(5,2) NOT NULL,
  `temperature` decimal(5,2) NOT NULL,
  `humidity` decimal(5,2) NOT NULL,
  `recorded_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_readings_node_time` (`node_id`,`recorded_at`),
  CONSTRAINT `fk_readings_node` FOREIGN KEY (`node_id`) REFERENCES `sensor_nodes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensor_readings`
--

LOCK TABLES `sensor_readings` WRITE;
/*!40000 ALTER TABLE `sensor_readings` DISABLE KEYS */;
INSERT INTO `sensor_readings` VALUES (1,1,45.20,28.50,65.00,'2026-07-14 07:43:52'),(2,1,25.00,30.00,60.00,'2026-07-14 08:25:15');
/*!40000 ALTER TABLE `sensor_readings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('farmer','extension_officer','admin') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'farmer',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'testuser',NULL,'scrypt:32768:8:1$k7VtppoHAW5nZ9Vz$c1ea302ceb2b4967140e948cc1ce631925753e433151c7ab77e05c731d13f98f7d654396cae355c2c2a8ecdf32013eac1c04319f6253b8b2ca644a9cf70cac0d','farmer','2026-07-14 07:38:22');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-15 13:51:09

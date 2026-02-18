-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: homedb
-- ------------------------------------------------------
-- Server version	9.5.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
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

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'e0cb5ac4-f060-11f0-89df-7f841af27262:1-295';

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  `rating` varchar(50) DEFAULT NULL,
  `description` text,
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `feedback_ibfk_2` (`product_id`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `content` (`id`),
  CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (1,NULL,NULL,'1-Terrible','          nottt good  ','2026-02-04 07:24:14'),(2,NULL,NULL,'5-Excellent','              good','2026-02-04 07:32:11'),(3,16,15,'5-Excellent','              mmm','2026-02-04 09:44:07'),(4,16,15,'5-Excellent','              mmm','2026-02-04 09:44:08'),(5,16,15,'5-Excellent','              mmm','2026-02-04 09:44:08'),(6,16,15,'5-Excellent','              mmm','2026-02-04 09:44:08'),(7,16,15,'5-Excellent','              mmm','2026-02-04 09:44:08'),(8,16,15,'5-Excellent','              mmm','2026-02-04 09:44:09'),(9,16,15,'5-Excellent','              mmm','2026-02-04 09:44:09'),(10,16,15,'5-Excellent','              mmm','2026-02-04 09:44:09'),(11,16,15,'5-Excellent','              mmm','2026-02-04 09:44:09'),(12,16,15,'5-Excellent','              mmm','2026-02-04 09:44:10'),(13,16,15,'5-Excellent','              mmm','2026-02-04 09:44:10'),(14,16,15,'5-Excellent','              mmm','2026-02-04 09:44:10'),(15,16,NULL,'5','good','2026-02-04 10:48:00'),(16,16,NULL,'5','good','2026-02-04 10:48:11'),(17,16,NULL,'5','good','2026-02-04 10:59:09'),(18,16,NULL,'3','not good','2026-02-04 10:59:58'),(26,19,NULL,'5','good','2026-02-09 06:48:55'),(27,19,NULL,'3','bad','2026-02-09 07:02:26'),(28,19,NULL,'5','good','2026-02-09 07:39:54'),(29,19,NULL,'4','Customer Happy.......','2026-02-09 07:42:10'),(30,19,NULL,'5','wow','2026-02-09 07:45:39'),(31,19,NULL,'4','not bad','2026-02-09 08:30:33'),(32,23,24,'4','good','2026-02-09 09:37:30'),(33,22,15,NULL,'good product','2026-02-09 10:20:31'),(34,22,29,NULL,'Worth of money','2026-02-09 10:29:25'),(35,22,23,NULL,'good product','2026-02-09 11:33:00'),(36,23,24,NULL,'good','2026-02-09 11:38:13'),(37,17,24,NULL,'Fresh vegtables\r\n','2026-02-10 13:37:04'),(38,17,25,NULL,'Fresh vegtable','2026-02-10 14:00:07'),(39,19,24,NULL,'Happy to purchase here.','2026-02-10 14:03:29'),(40,17,28,NULL,'Good place to buy vegtables','2026-02-10 14:52:03');
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
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

-- Dump completed on 2026-02-18 16:15:26

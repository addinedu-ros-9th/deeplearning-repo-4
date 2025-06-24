-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: GigachadDb
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.24.04.1

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

--
-- Current Database: `GigachadDb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `GigachadDb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `GigachadDb`;

--
-- Table structure for table `cctv`
--

DROP TABLE IF EXISTS `cctv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cctv` (
  `store_name` varchar(32) NOT NULL,
  `cctv_no` int NOT NULL,
  PRIMARY KEY (`store_name`,`cctv_no`),
  CONSTRAINT `storeRef` FOREIGN KEY (`store_name`) REFERENCES `store` (`store_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cctv`
--

LOCK TABLES `cctv` WRITE;
/*!40000 ALTER TABLE `cctv` DISABLE KEYS */;
INSERT INTO `cctv` VALUES ('아이스크림 할인점 가산점',1),('커피 무인매장 금천점',3),('편의점 무인매장 독산점',2);
/*!40000 ALTER TABLE `cctv` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cctv_data`
--

DROP TABLE IF EXISTS `cctv_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cctv_data` (
  `store_name` varchar(32) NOT NULL,
  `cctv_no` int NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `event_type` varchar(16) DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `person_count` int DEFAULT NULL,
  `is_checked` tinyint DEFAULT NULL,
  `video_url` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`store_name`,`cctv_no`,`time`),
  KEY `cctvRef_idx` (`store_name`,`cctv_no`),
  KEY `event_typeRef_idx` (`event_type`),
  CONSTRAINT `cctvRef` FOREIGN KEY (`store_name`, `cctv_no`) REFERENCES `cctv` (`store_name`, `cctv_no`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `event_typeRef` FOREIGN KEY (`event_type`) REFERENCES `event_type` (`type_name`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cctv_data`
--

LOCK TABLES `cctv_data` WRITE;
/*!40000 ALTER TABLE `cctv_data` DISABLE KEYS */;
INSERT INTO `cctv_data` VALUES ('아이스크림 할인점 가산점',1,'2025-06-01 00:12:34','broken',0.97,2,1,'video_1.mp4'),('아이스크림 할인점 가산점',1,'2025-06-01 01:12:34','theft',0.97,3,1,'video_31.mp4'),('아이스크림 할인점 가산점',1,'2025-06-01 02:12:34','theft',0.97,3,0,'video_61.mp4'),('아이스크림 할인점 가산점',1,'2025-06-04 03:34:56','light_off',0.95,2,1,'video_4.mp4'),('아이스크림 할인점 가산점',1,'2025-06-04 04:34:56','abandon',0.95,3,1,'video_34.mp4'),('아이스크림 할인점 가산점',1,'2025-06-04 05:34:56','light_off',0.95,2,1,'video_64.mp4'),('아이스크림 할인점 가산점',1,'2025-06-07 06:33:27','theft',0.96,3,0,'video_7.mp4'),('아이스크림 할인점 가산점',1,'2025-06-07 07:33:27','broken',0.96,3,0,'video_37.mp4'),('아이스크림 할인점 가산점',1,'2025-06-07 08:33:27','theft',0.96,2,0,'video_67.mp4'),('아이스크림 할인점 가산점',1,'2025-06-10 01:00:00','light_off',0.98,3,1,'video_40.mp4'),('아이스크림 할인점 가산점',1,'2025-06-10 02:00:00','abandon',0.98,2,1,'video_70.mp4'),('아이스크림 할인점 가산점',1,'2025-06-10 09:00:00','abandon',0.98,3,1,'video_10.mp4'),('아이스크림 할인점 가산점',1,'2025-06-13 02:23:34','broken',0.99,3,0,'video_13.mp4'),('아이스크림 할인점 가산점',1,'2025-06-13 04:23:34','theft',0.99,3,0,'video_43.mp4'),('아이스크림 할인점 가산점',1,'2025-06-16 04:50:07','light_off',0.97,3,1,'video_16.mp4'),('아이스크림 할인점 가산점',1,'2025-06-16 06:50:07','abandon',0.97,3,1,'video_46.mp4'),('아이스크림 할인점 가산점',1,'2025-06-19 00:17:40','broken',0.95,3,0,'video_49.mp4'),('아이스크림 할인점 가산점',1,'2025-06-19 07:17:40','theft',0.95,3,0,'video_19.mp4'),('아이스크림 할인점 가산점',1,'2025-06-22 01:44:13','abandon',0.96,3,1,'video_22.mp4'),('아이스크림 할인점 가산점',1,'2025-06-22 03:44:13','light_off',0.96,3,1,'video_52.mp4'),('아이스크림 할인점 가산점',1,'2025-06-23 07:00:00','broken',0.97,2,1,'video_201.mp4'),('아이스크림 할인점 가산점',1,'2025-06-23 09:30:00','theft',0.95,3,0,'video_202.mp4'),('아이스크림 할인점 가산점',1,'2025-06-23 13:45:00','abandon',0.96,2,1,'video_203.mp4'),('아이스크림 할인점 가산점',1,'2025-06-23 18:15:00','light_off',0.98,3,1,'video_204.mp4'),('아이스크림 할인점 가산점',1,'2025-06-24 00:00:00','broken',0.99,2,0,'video_205.mp4'),('아이스크림 할인점 가산점',1,'2025-06-24 03:30:00','theft',0.97,3,1,'video_206.mp4'),('아이스크림 할인점 가산점',1,'2025-06-24 06:00:00','abandon',0.95,2,0,'video_207.mp4'),('아이스크림 할인점 가산점',1,'2025-06-25 04:11:46','theft',1,3,0,'video_25.mp4'),('아이스크림 할인점 가산점',1,'2025-06-25 06:11:46','theft',1,3,1,'video_55.mp4'),('아이스크림 할인점 가산점',1,'2025-06-28 06:39:19','light_off',0.99,3,1,'video_28.mp4'),('아이스크림 할인점 가산점',1,'2025-06-28 08:39:19','abandon',0.99,3,1,'video_58.mp4'),('커피 무인매장 금천점',3,'2025-06-03 02:23:45','theft',0.99,3,1,'video_3.mp4'),('커피 무인매장 금천점',3,'2025-06-03 03:23:45','broken',0.99,2,0,'video_33.mp4'),('커피 무인매장 금천점',3,'2025-06-03 04:23:45','theft',0.99,1,0,'video_63.mp4'),('커피 무인매장 금천점',3,'2025-06-06 05:44:11','abandon',0.97,2,1,'video_6.mp4'),('커피 무인매장 금천점',3,'2025-06-06 06:44:11','light_off',0.97,2,1,'video_36.mp4'),('커피 무인매장 금천점',3,'2025-06-06 07:44:11','abandon',0.97,1,1,'video_66.mp4'),('커피 무인매장 금천점',3,'2025-06-09 00:11:09','theft',0.95,2,0,'video_39.mp4'),('커피 무인매장 금천점',3,'2025-06-09 01:11:09','broken',0.95,1,0,'video_69.mp4'),('커피 무인매장 금천점',3,'2025-06-09 08:11:09','broken',0.95,2,0,'video_9.mp4'),('커피 무인매장 금천점',3,'2025-06-12 01:34:23','light_off',0.96,2,1,'video_12.mp4'),('커피 무인매장 금천점',3,'2025-06-12 03:34:23','abandon',0.96,2,1,'video_42.mp4'),('커피 무인매장 금천점',3,'2025-06-15 04:01:56','theft',0.98,2,0,'video_15.mp4'),('커피 무인매장 금천점',3,'2025-06-15 06:01:56','broken',0.98,2,0,'video_45.mp4'),('커피 무인매장 금천점',3,'2025-06-18 06:28:29','abandon',0.99,2,1,'video_18.mp4'),('커피 무인매장 금천점',3,'2025-06-18 08:28:29','light_off',0.99,2,1,'video_48.mp4'),('커피 무인매장 금천점',3,'2025-06-21 00:55:02','broken',0.97,2,0,'video_21.mp4'),('커피 무인매장 금천점',3,'2025-06-21 02:55:02','theft',0.97,2,0,'video_51.mp4'),('커피 무인매장 금천점',3,'2025-06-24 03:22:35','light_off',0.95,2,1,'video_24.mp4'),('커피 무인매장 금천점',3,'2025-06-24 05:22:35','abandon',0.95,2,1,'video_54.mp4'),('커피 무인매장 금천점',3,'2025-06-27 05:50:08','theft',0.96,2,0,'video_27.mp4'),('커피 무인매장 금천점',3,'2025-06-27 07:50:08','broken',0.96,2,0,'video_57.mp4'),('커피 무인매장 금천점',3,'2025-06-30 01:17:41','light_off',0.98,2,1,'video_60.mp4'),('커피 무인매장 금천점',3,'2025-06-30 08:17:41','abandon',0.98,2,1,'video_30.mp4'),('편의점 무인매장 독산점',2,'2025-06-02 01:45:21','abandon',0.96,1,0,'video_2.mp4'),('편의점 무인매장 독산점',2,'2025-06-02 02:45:21','light_off',0.96,1,1,'video_32.mp4'),('편의점 무인매장 독산점',2,'2025-06-02 03:45:21','abandon',0.96,2,1,'video_62.mp4'),('편의점 무인매장 독산점',2,'2025-06-05 04:15:22','broken',0.98,1,0,'video_5.mp4'),('편의점 무인매장 독산점',2,'2025-06-05 05:15:22','theft',0.98,1,0,'video_35.mp4'),('편의점 무인매장 독산점',2,'2025-06-05 06:15:22','broken',0.98,3,0,'video_65.mp4'),('편의점 무인매장 독산점',2,'2025-06-08 00:22:18','light_off',0.99,3,1,'video_68.mp4'),('편의점 무인매장 독산점',2,'2025-06-08 07:22:18','light_off',0.99,1,1,'video_8.mp4'),('편의점 무인매장 독산점',2,'2025-06-08 08:22:18','abandon',0.99,1,1,'video_38.mp4'),('편의점 무인매장 독산점',2,'2025-06-11 00:45:12','theft',0.97,1,0,'video_11.mp4'),('편의점 무인매장 독산점',2,'2025-06-11 02:45:12','broken',0.97,1,0,'video_41.mp4'),('편의점 무인매장 독산점',2,'2025-06-14 03:12:45','abandon',0.95,1,1,'video_14.mp4'),('편의점 무인매장 독산점',2,'2025-06-14 05:12:45','light_off',0.95,1,1,'video_44.mp4'),('편의점 무인매장 독산점',2,'2025-06-17 05:39:18','broken',0.96,1,0,'video_17.mp4'),('편의점 무인매장 독산점',2,'2025-06-17 07:39:18','theft',0.96,1,0,'video_47.mp4'),('편의점 무인매장 독산점',2,'2025-06-20 01:06:51','abandon',0.98,1,1,'video_50.mp4'),('편의점 무인매장 독산점',2,'2025-06-20 08:06:51','light_off',0.98,1,1,'video_20.mp4'),('편의점 무인매장 독산점',2,'2025-06-23 02:33:24','theft',0.99,1,0,'video_23.mp4'),('편의점 무인매장 독산점',2,'2025-06-23 04:33:24','broken',0.99,1,0,'video_53.mp4'),('편의점 무인매장 독산점',2,'2025-06-26 05:00:57','abandon',0.97,1,1,'video_26.mp4'),('편의점 무인매장 독산점',2,'2025-06-26 07:00:57','light_off',0.97,1,1,'video_56.mp4'),('편의점 무인매장 독산점',2,'2025-06-29 00:28:30','theft',0.95,1,0,'video_59.mp4'),('편의점 무인매장 독산점',2,'2025-06-29 07:28:30','broken',0.95,1,0,'video_29.mp4');
/*!40000 ALTER TABLE `cctv_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_type`
--

DROP TABLE IF EXISTS `event_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_type` (
  `type_name` varchar(16) NOT NULL,
  PRIMARY KEY (`type_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_type`
--

LOCK TABLES `event_type` WRITE;
/*!40000 ALTER TABLE `event_type` DISABLE KEYS */;
INSERT INTO `event_type` VALUES ('abandon'),('broken'),('light_off'),('theft');
/*!40000 ALTER TABLE `event_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `store`
--

DROP TABLE IF EXISTS `store`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `store` (
  `store_name` varchar(32) NOT NULL,
  `user_id` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`store_name`),
  KEY `userRef_idx` (`user_id`),
  CONSTRAINT `userRef` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `store`
--

LOCK TABLES `store` WRITE;
/*!40000 ALTER TABLE `store` DISABLE KEYS */;
INSERT INTO `store` VALUES ('아이스크림 할인점 가산점','user01'),('편의점 무인매장 독산점','user02'),('커피 무인매장 금천점','user03');
/*!40000 ALTER TABLE `store` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `user_id` varchar(16) NOT NULL,
  `password` varchar(16) NOT NULL,
  `name` varchar(16) DEFAULT NULL,
  `email` varchar(16) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('user01','user01','최기가','user01@email.com','2025-06-16 08:00:00'),('user02','user02','김채드','user02@email.com','2025-06-16 09:00:00'),('user03','user03','이에듀','user03@email.com','2025-06-16 10:00:00');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-24 16:19:45

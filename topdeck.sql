-- MariaDB dump 10.19  Distrib 10.5.13-MariaDB, for FreeBSD13.0 (amd64)
--
-- Host: localhost    Database: topdeck
-- ------------------------------------------------------
-- Server version	10.5.13-MariaDB

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
-- Table structure for table `container`
--

DROP TABLE IF EXISTS `container`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `container` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(64) NOT NULL,
  `ipaddress` varchar(24) NOT NULL,
  `ethernet` varchar(16) NOT NULL,
  `options` varchar(255) DEFAULT NULL,
  `state` varchar(24) DEFAULT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `container`
--

LOCK TABLES `container` WRITE;
/*!40000 ALTER TABLE `container` DISABLE KEYS */;
/*!40000 ALTER TABLE `container` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `containerservice`
--

DROP TABLE IF EXISTS `containerservice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containerservice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contservice` varchar(64) NOT NULL,
  `contsvcstatus` varchar(64) NOT NULL,
  `date` datetime NOT NULL,
  `contid` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `contid` (`contid`),
  CONSTRAINT `containerservice_ibfk_1` FOREIGN KEY (`contid`) REFERENCES `container` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `containerservice`
--

LOCK TABLES `containerservice` WRITE;
/*!40000 ALTER TABLE `containerservice` DISABLE KEYS */;
/*!40000 ALTER TABLE `containerservice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `containeruser`
--

DROP TABLE IF EXISTS `containeruser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `containeruser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contuser` varchar(64) NOT NULL,
  `usrstatus` varchar(64) NOT NULL,
  `date` datetime NOT NULL,
  `contid` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `contid` (`contid`),
  CONSTRAINT `containeruser_ibfk_1` FOREIGN KEY (`contid`) REFERENCES `container` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `containeruser`
--

LOCK TABLES `containeruser` WRITE;
/*!40000 ALTER TABLE `containeruser` DISABLE KEYS */;
/*!40000 ALTER TABLE `containeruser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `server`
--

DROP TABLE IF EXISTS `server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(64) NOT NULL,
  `daship` varchar(32) NOT NULL,
  `dashport` varchar(8) NOT NULL,
  `basedir` varchar(128) NOT NULL,
  `logdir` varchar(128) NOT NULL,
  `contdir` varchar(128) NOT NULL,
  `dnsip` varchar(32) NOT NULL,
  `domain` varchar(128) NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server`
--

LOCK TABLES `server` WRITE;
/*!40000 ALTER TABLE `server` DISABLE KEYS */;
INSERT INTO `server` VALUES (1,'fbsdtopdeck1','192.168.1.10','8001','/usr/jails','/var/log','container','192.168.1.1','topdeck.loc','2022-01-01 22:00:00');
/*!40000 ALTER TABLE `server` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `password` varchar(128) NOT NULL,
  `email` varchar(128) DEFAULT NULL,
  `admin` varchar(8) NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','$2b$12$OVyyuXQ8rmHlF70wgioAruvtZ7E7/lyZnbMO9LQb2yCUnq/q/9GY.','admin@topdeck.loc','Yes','2022-01-01 22:00:00');
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

-- Dump completed on 2022-01-01 18:00:00

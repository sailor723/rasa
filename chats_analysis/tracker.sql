/*
 Navicat Premium Data Transfer

 Source Server         : 172.16.11.59
 Source Server Type    : MySQL
 Source Server Version : 80028
 Source Host           : 172.16.11.59:3306
 Source Schema         : dl04_db

 Target Server Type    : MySQL
 Target Server Version : 80028
 File Encoding         : 65001

 Date: 16/05/2022 22:48:44
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tracker
-- ----------------------------
DROP TABLE IF EXISTS `tracker`;
CREATE TABLE `tracker`  (
  `tracker_id` longtext CHARACTER SET utf8 COLLATE utf8_bin NULL,
  `value` longtext CHARACTER SET utf8 COLLATE utf8_bin NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;

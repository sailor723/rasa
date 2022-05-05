DROP TABLE IF EXISTS `tracker`;
CREATE TABLE `tracker`  (
  `tracker_id` varchar(200) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
  `value` text CHARACTER SET utf8 COLLATE utf8_bin NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;

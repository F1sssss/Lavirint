INSERT INTO `soap_user` (`username`, `password`, `is_active`)
VALUES ('jaffa', '$pbkdf2-sha256$29000$vbdWyvm/F6IU4nxvrbXWGg$g1MoFVbUbhQfaFgeBLQQOFMMwu4RUq1L6I5ymX.SdOw', 1);

SET @soap_user_id = LAST_INSERT_ID();

INSERT INTO `soap_permission` (`company_id`, `soap_user_id`)
VALUES (1238, @soap_user_id);
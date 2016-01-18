-- structure of db


DROP TABLE IF EXISTS Forum, Post, Subscription, Thread, User, Follower;

CREATE TABLE IF NOT EXISTS `Forum` (
	`forum` INT NOT NULL AUTO_INCREMENT, 			
	`name` VARCHAR (50) NOT NULL,						
	`short_name` VARCHAR (50) NOT NULL,					
	`user` VARCHAR (50) NOT NULL, 					
	-- any keys

	PRIMARY KEY (`forum`),
	UNIQUE KEY (`name`), 
	UNIQUE KEY (`short_name`)

) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `User` (
	`user` INT NOT NULL AUTO_INCREMENT,  			
	`email` VARCHAR (50) NOT NULL, 						
	`name` VARCHAR (50) NULL,						
	`username` VARCHAR (50) NULL,					
	`isAnonymous` BOOLEAN NOT NULL DEFAULT 0,			
	`about` TEXT NULL,									

	-- any keys

	PRIMARY KEY (`user`),
	UNIQUE KEY (`email`),
	UNIQUE KEY name_email (name, email)

) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Post` (
	`post` INT NOT NULL AUTO_INCREMENT, 			
	`user` VARCHAR(50) NOT NULL, 				
	`thread` INT NOT NULL, 							 
	`forum` VARCHAR(50) NOT NULL, 					
	`message` TEXT NOT NULL,
	`parent` INT NULL DEFAULT NULL, 				
	`date` DATETIME NOT NULL DEFAULT '2000-01-01 00:00:00',
	`likes` INT NOT NULL DEFAULT 0,
	`dislikes` INT NOT NULL DEFAULT 0,
	`points` INT NOT NULL DEFAULT 0,
	`isSpam` BOOLEAN NOT NULL DEFAULT 0,
	`isEdited` BOOLEAN NOT NULL DEFAULT 0,
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isHighlighted` BOOLEAN NOT NULL DEFAULT 0,
	`isApproved` BOOLEAN NOT NULL DEFAULT 0,			

	-- any keys

	PRIMARY KEY (`post`),
	UNIQUE KEY `user_date` (`user`, `date`),
	KEY (`forum`, `date`),
	KEY `thread_date` (`thread`, `date`)

	
) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Thread` (
	`thread` INT NOT NULL AUTO_INCREMENT, 		
	`title` VARCHAR(50) NOT NULL, 				
	`user` VARCHAR(50) NOT NULL, 				
	`message` TEXT NOT NULL,
	`forum` VARCHAR(50) NOT NULL, 				
	`isDeleted` BOOLEAN NOT NULL DEFAULT 0,
	`isClosed` BOOLEAN NOT NULL DEFAULT 0,
	`date` DATETIME NOT NULL DEFAULT '2000-01-01 00:00:00',
	`slug` VARCHAR(50) NOT NULL, 				
	`likes` INT NOT NULL DEFAULT 0,
	`dislikes` INT NOT NULL DEFAULT 0,
	`points` INT NOT NULL DEFAULT 0,
	`posts` INT NOT NULL DEFAULT 0,	

	-- any keys

	PRIMARY KEY (`thread`),
	UNIQUE KEY (`title`),
	KEY (user)

) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `Subscription` (
	`subscriber` VARCHAR(50) NOT NULL, 					
	`thread` INT NOT NULL, 								

	PRIMARY KEY (`subscriber`, `thread`)
) DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS `Follower` (
	`follower` VARCHAR(50) NOT NULL, 					
	`following` VARCHAR(50) NOT NULL 					

) DEFAULT CHARSET=utf8;


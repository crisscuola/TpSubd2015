-- structure of db

CREATE TABLE IF NOT EXIST 'Forum' (
	'forum_id' INT NOT NULL AUTO_INCREMENT, 			-- forum id
	'name' VARCHAR (50) NOT NULL,						-- forum name
	'short_name' VARCHAR (50) NOT NULL,					-- forum short name
	'user_e' VARCHAR (50) NOT NULL, 					-- user email address

	-- any keys

) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXIST 'User' (
	'user_id' INT NOT NULL AUTO_INCREMENT,  			-- user id
	'email' VARCHAR (50) NOT NULL, 						-- user email address
	'name' VARCHAR (50) NOT NULL,						-- user name
	'user_name' VARCHAR (50) NOT NULL,					-- user nickname
	'isAnonimus' BOOLEAN NOT NULL DEFAULT 0,			-- anonimus
	'about' TEXT NULL,									--info about user

	-- any keys

) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXIST 'Post' (
	'post_id' INT NOT NULL AUTO_INCREMENT,  			-- post id
	'user_e' VARCHAR (50) NOT NULL, 					-- user email address
	'thread_id' INT NOT NULL, 							--thread id
	'forum_s' VARCHAR (50) NOT NULL,					-- forum short name
	'message' TEXT NOT NULL,							-- message
	'parrent' INT NULL DEFAULT NULL, 					-- parent post id
	'date' DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, --date of post released
	'likes' INT NOT NULL DEFAULT 0,						--likes 
	'dislikes' 	INT NOT NULL DEFAULT 0,					--dislikes
	'points' INT NOT NULL DEFAULT 0,					--points
	'isSpam' BOOLEAN NOT NULL DEFAULT 0,				--spam mark
	'isEdited' BOOLEAN NOT NULL DEFAULT 0,				--edited mark
	'isDelited' BOOLEAN NOT NULL DEFAULT 0,				--delited mark
	'isHighlighted' BOOLEAN NOT NULL DEFAULT 0,         --highlighted mark
	'isApproved' BOOLEAN NOT NULL DEFAULT 0,			--approved mark

	-- any keys

) DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXIST 'Thread' (
	'thread_id' INT NOT NULL AUTO_INCREMENT,  			-- thread id
	'title' VARCHAR (50) NOT NULL, 						-- thread title 
	'user_e' VARCHAR (50) NOT NULL, 					-- user email address
	'message' TEXT NOT NULL,							-- message
	'forum_s' VARCHAR (50) NOT NULL,					-- forum short name
	'isDelited' BOOLEAN NOT NULL DEFAULT 0,				--delited mark
	'isClose' BOOLEAN NOT NULL DEFAULT 0,				--close mark
	'date' DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, --date of thread released
	'slug' VARCHAR (50) NOT NULL,						-- slug
	'likes' INT NOT NULL DEFAULT 0,						--likes 
	'dislikes' 	INT NOT NULL DEFAULT 0,					--dislikes
	'points' NT NOT NULL DEFAULT 0,						--points
	`posts` INT NOT NULL DEFAULT 0,						--posts 

	-- any keys

) DEFAULT CHARSET=utf8;
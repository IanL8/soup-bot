CREATE DATABASE soupbot;
use soupbot;

CREATE TABLE Guilds(
    gid VARCHAR(100) NOT NULL,
    flag VARCHAR(10) DEFAULT '!',
    general_chat VARCHAR(100),
    owner_id VARCHAR(100) NOT NULL,
    PRIMARY KEY (gid)
);

CREATE TABLE Users(
    uid VARCHAR(100) NOT NULL,
    gid VARCHAR(100) NOT NULL,
    FOREIGN KEY(gid) REFERENCES Guilds(gid),
    PRIMARY KEY (uid, gid)
);

CREATE TABLE UserTimers(
    tid VARCHAR(100) NOT NULL,
    uid VARCHAR(100) NOT NULL,
    start_time INT DEFAULT 0,
    FOREIGN KEY(uid) REFERENCES Users(uid),
    PRIMARY KEY (tid, uid)
);

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
    FOREIGN KEY(gid) REFERENCES Guilds(gid) ON DELETE CASCADE,
    PRIMARY KEY (uid, gid)
);

CREATE TABLE UserTimers(
    tid VARCHAR(100) NOT NULL,
    uid VARCHAR(100) NOT NULL,
    start_time INT DEFAULT 0,
    FOREIGN KEY(uid) REFERENCES Users(uid) ON DELETE CASCADE,
    PRIMARY KEY (tid, uid)
);

CREATE TABLE MovieLists(
    gid VARCHAR(100),
    PRIMARY KEY (gid),
    FOREIGN KEY (gid) REFERENCES Guilds(gid) ON DELETE CASCADE
);

CREATE TABLE Movies(
    name VARCHAR(150),
    gid VARCHAR(100),
    priority INT DEFAULT 0,
    PRIMARY KEY (name, gid),
    FOREIGN KEY (gid) REFERENCES Guilds(gid) ON DELETE CASCADE
);
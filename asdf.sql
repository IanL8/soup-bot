CREATE DATABASE soupbot;
use soupbot;

CREATE TABLE UserTimers(
    timer_name VARCHAR(100) NOT NULL,
    user_id VARCHAR(200) NOT NULL,
    start_time INT DEFAULT 0,
    PRIMARY KEY (user_id)
);


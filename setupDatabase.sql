CREATE DATABASE IF NOT EXISTS bio_metric_database;
USE bio_metric_database;

CREATE TABLE IF NOT EXISTS `user` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    age INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bpm_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userID INT NOT NULL,
    bpm INT NOT NULL,
    time_stamp TIME NOT NULL,
    FOREIGN KEY (userID) REFERENCES user(id)
);

CREATE TABLE oxygen_level_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userID INT NOT NULL,
    oxygen_level INT NOT NULL,
    time_stamp TIME NOT NULL,
    FOREIGN KEY (userID) REFERENCES user(id)
);
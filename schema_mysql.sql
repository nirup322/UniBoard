-- UniBoard v1 Schema (MySQL)
-- Run with: mysql -u root -p < schema_mysql.sql

CREATE DATABASE IF NOT EXISTS uniboard;
USE uniboard;

CREATE TABLE IF NOT EXISTS students (
    usn         VARCHAR(20) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    dob         DATE NOT NULL,              -- used as login password
    semester    INT NOT NULL,               -- current semester (1-8)
    branch      VARCHAR(10) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subjects (
    subject_code VARCHAR(20) PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    semester     INT NOT NULL,
    branch       VARCHAR(10) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS attendance (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usn                 VARCHAR(20) NOT NULL,
    subject_code        VARCHAR(20) NOT NULL,
    classes_held        INT NOT NULL DEFAULT 0,
    classes_attended    INT NOT NULL DEFAULT 0,
    FOREIGN KEY (usn) REFERENCES students(usn) ON DELETE CASCADE,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE,
    UNIQUE KEY unique_usn_subject (usn, subject_code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS results (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usn             VARCHAR(20) NOT NULL,
    semester        INT NOT NULL,
    subject_code    VARCHAR(20) NOT NULL,
    marks           INT,
    grade           VARCHAR(5),
    FOREIGN KEY (usn) REFERENCES students(usn) ON DELETE CASCADE,
    FOREIGN KEY (subject_code) REFERENCES subjects(subject_code) ON DELETE CASCADE
) ENGINE=InnoDB;

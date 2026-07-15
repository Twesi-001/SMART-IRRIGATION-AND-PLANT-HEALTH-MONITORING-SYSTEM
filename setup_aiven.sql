-- Create database if not exists
CREATE DATABASE IF NOT EXISTS smart_irrigation;
USE smart_irrigation;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'extension_officer', 'admin') DEFAULT 'farmer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create sensor_nodes table
CREATE TABLE IF NOT EXISTS sensor_nodes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_name VARCHAR(80) NOT NULL,
    location VARCHAR(120),
    crop_type VARCHAR(80),
    moisture_threshold DECIMAL(5,2) DEFAULT 30.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create sensor_readings table
CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_id INT NOT NULL,
    soil_moisture DECIMAL(5,2) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    humidity DECIMAL(5,2) NOT NULL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES sensor_nodes(id)
);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    reading_id BIGINT NOT NULL,
    irrigation_needed BOOLEAN NOT NULL,
    recommended_action VARCHAR(120),
    confidence DECIMAL(5,4),
    model_version VARCHAR(40) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reading_id) REFERENCES sensor_readings(id)
);

-- Create pump_commands table
CREATE TABLE IF NOT EXISTS pump_commands (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_id INT NOT NULL,
    command ENUM('ON', 'OFF') NOT NULL,
    source ENUM('AUTO', 'MANUAL') NOT NULL,
    issued_by INT,
    issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (node_id) REFERENCES sensor_nodes(id),
    FOREIGN KEY (issued_by) REFERENCES users(id)
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_id INT NOT NULL,
    alert_type VARCHAR(60) NOT NULL,
    message VARCHAR(255) NOT NULL,
    severity ENUM('INFO', 'WARNING', 'CRITICAL') DEFAULT 'WARNING',
    resolved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (node_id) REFERENCES sensor_nodes(id)
);

-- Insert seed data
INSERT INTO sensor_nodes (node_name, location, crop_type, moisture_threshold) 
VALUES ('Node-01', 'Avodah Innovations Training Facility, Kiyanja, Mbarara City', 'Maize', 30.00);
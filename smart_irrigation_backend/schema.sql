-- ============================================================
-- Smart Irrigation and Plant Health Monitoring System
-- MySQL schema (3rd Normal Form)
-- Avodah Innovations Capstone Project
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_irrigation
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smart_irrigation;

-- ------------------------------------------------------------
-- users: farmers / extension officers who can log in to the
-- dashboard and issue manual pump commands
-- ------------------------------------------------------------
CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(120) UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('farmer', 'extension_officer', 'admin') NOT NULL DEFAULT 'farmer',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- sensor_nodes: one row per physical Arduino node. There is
-- only one node in the prototype, but this keeps the schema
-- ready for a multi-zone deployment without redesign.
-- ------------------------------------------------------------
CREATE TABLE sensor_nodes (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    node_name       VARCHAR(80)  NOT NULL,
    location        VARCHAR(120),
    crop_type       VARCHAR(80),
    moisture_threshold DECIMAL(5,2) DEFAULT 30.00, -- % below which irrigation is considered needed
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- sensor_readings: raw timestamped readings coming from the
-- serial/USB (or later MQTT) data pipeline
-- ------------------------------------------------------------
CREATE TABLE sensor_readings (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_id         INT NOT NULL,
    soil_moisture   DECIMAL(5,2) NOT NULL,   -- percentage
    temperature     DECIMAL(5,2) NOT NULL,   -- degrees Celsius
    humidity        DECIMAL(5,2) NOT NULL,   -- percentage
    recorded_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_readings_node FOREIGN KEY (node_id) REFERENCES sensor_nodes(id)
        ON DELETE CASCADE,
    INDEX idx_readings_node_time (node_id, recorded_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- predictions: ML model output, linked to the specific reading
-- that produced it so the training/inference trail is auditable
-- ------------------------------------------------------------
CREATE TABLE predictions (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    reading_id          BIGINT NOT NULL,
    irrigation_needed   BOOLEAN NOT NULL,
    recommended_action  VARCHAR(120),
    confidence          DECIMAL(5,4),        -- 0.0000 - 1.0000
    model_version       VARCHAR(40) NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_predictions_reading FOREIGN KEY (reading_id) REFERENCES sensor_readings(id)
        ON DELETE CASCADE,
    INDEX idx_predictions_reading (reading_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- pump_commands: every pump action, whether triggered
-- automatically by the ML/threshold logic or manually by a user
-- ------------------------------------------------------------
CREATE TABLE pump_commands (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_id         INT NOT NULL,
    command         ENUM('ON', 'OFF') NOT NULL,
    source          ENUM('AUTO', 'MANUAL') NOT NULL,
    issued_by       INT NULL,                -- NULL when source = AUTO
    issued_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pump_node FOREIGN KEY (node_id) REFERENCES sensor_nodes(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pump_user FOREIGN KEY (issued_by) REFERENCES users(id)
        ON DELETE SET NULL,
    INDEX idx_pump_node_time (node_id, issued_at)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- alerts: dry-spell, sensor-fault, or low-water alerts surfaced
-- on the dashboard
-- ------------------------------------------------------------
CREATE TABLE alerts (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    node_id         INT NOT NULL,
    alert_type      VARCHAR(60) NOT NULL,    -- e.g. 'LOW_MOISTURE', 'SENSOR_FAULT'
    message         VARCHAR(255) NOT NULL,
    severity        ENUM('INFO', 'WARNING', 'CRITICAL') NOT NULL DEFAULT 'WARNING',
    resolved        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TIMESTAMP NULL,
    CONSTRAINT fk_alerts_node FOREIGN KEY (node_id) REFERENCES sensor_nodes(id)
        ON DELETE CASCADE,
    INDEX idx_alerts_node_resolved (node_id, resolved)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Seed the single prototype node so the API has something to
-- write readings against out of the box
-- ------------------------------------------------------------
INSERT INTO sensor_nodes (node_name, location, crop_type, moisture_threshold, is_active)
VALUES ('Node-01', 'Avodah Innovations Training Facility, Kiyanja, Mbarara City', 'Maize', 30.00, TRUE);

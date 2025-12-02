
-- Script: create_agg_database.sql
-- Version: 1.0
-- Description: Creates aggregation database tables for pre-computed metrics
-- Usage: psql machine_monitoring_agg -f create_agg_database.sql

-- Table: agg_machine_activity_daily
-- Purpose: Stores daily machine state aggregations

CREATE TABLE IF NOT EXISTS agg_machine_activity_daily (
    dt DATE PRIMARY KEY,
    state_planned_down INT NOT NULL DEFAULT 0,
    state_running INT NOT NULL DEFAULT 0,
    state_unplanned_down INT NOT NULL DEFAULT 0,
    last_updated_at TIMESTAMP DEFAULT NOW()
);


-- Table: agg_sensor_stats
-- Purpose: Stores hourly aggregated sensor readings (temperature, pressure, etc.)
-- Example: For TEMPERATURE_BASE, we average all readings within each hour

CREATE TABLE IF NOT EXISTS agg_sensor_stats (
    sensor_name VARCHAR(100),                
    dt TIMESTAMP,                            
    min_value FLOAT,                         -- Minimum value during the hour
    avg_value FLOAT,                         -- Average value during the hour
    max_value FLOAT,                         -- Maximum value during the hour
    std_dev   FLOAT,                         -- Needed for the Nivo BoxPlot
    readings_count INT,                      -- Number of raw readings aggregated
    last_updated_at TIMESTAMP DEFAULT NOW(), -- Timestamp of last aggregation
    PRIMARY KEY (sensor_name, dt)
);

-- TABLE alerts
-- Purpose: Store daily alerts (only the ones of importance)

CREATE TABLE IF NOT EXISTS alerts(
    id SERIAL PRIMARY KEY, -- SERIAL for automatic IDs 
    dt TIMESTAMP NOT NULL,
    alert_type VARCHAR(20) NOT NULL
        CHECK(alert_type in ('emergency', 'error', 'warning')),
    description VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS machine_utilization(
    id SERIAL PRIMARY KEY,
    
    machine_state VARCHAR(20) NOT NULL
        CHECK(machine_state in ('down', 'running')),
    state_start_time TIMESTAMP NOT NULL,
    state_end_time TIMESTAMP NOT NULL,
    
    dt DATE GENERATED ALWAYS AS (state_start_time::DATE) STORED,

    duration INTERVAL
        GENERATED ALWAYS AS (state_end_time - state_start_time) STORED
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- B-Tree indexes for fast date-based lookups
-- Tailored for our request: GET sensor X's data for date Y
CREATE INDEX IF NOT EXISTS idx_sensor_date ON agg_sensor_stats(sensor_name, CAST(dt AS DATE));

-- =============================================================================
-- VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- View: v_data_status
-- Purpose: Quick overview of data availability. Gives summary of available data
-- -----------------------------------------------------------------------------

DROP VIEW IF EXISTS v_data_status;

CREATE OR REPLACE VIEW v_data_status AS
SELECT 
    'agg_sensor_stats' as table_name,
    MIN(dt) as first_date,
    MAX(dt) as last_date,
    COUNT(*) as total_records,
    COUNT(DISTINCT sensor_name) as number_of_sensors,
    MAX(last_updated_at) as last_updated
FROM agg_sensor_stats;


-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Aggregation database setup complete!';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - agg_machine_activity_daily';
    RAISE NOTICE '  - agg_sensor_stats';
END $$;


-- =============================================================================
-- Script: create_agg_database.sql
-- Version: 1.0
-- Description: Creates aggregation database tables for pre-computed metrics
-- Usage: psql machine_monitoring_agg -f create_agg_database.sql
-- =============================================================================

-- =============================================================================
-- TABLE DEFINITIONS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: agg_machine_activity_daily
-- Purpose: Stores daily machine state aggregations
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agg_machine_activity_daily (
    date DATE PRIMARY KEY,
    state_planned_down INT NOT NULL DEFAULT 0,
    state_running INT NOT NULL DEFAULT 0,
    state_unplanned_down INT NOT NULL DEFAULT 0,
    last_updated_at TIMESTAMP DEFAULT NOW()
);


-- -----------------------------------------------------------------------------
-- Table: agg_sensor_stats
-- Purpose: Stores hourly aggregated sensor readings (temperature, pressure, etc.)
-- Example: For TEMPERATURE_BASE, we average all readings within each hour
--          Result: 24 rows per day (one per hour) instead of thousands
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agg_sensor_stats (
    sensor_name VARCHAR(100),                -- Sensor identifier (e.g., 'TEMPERATURE_BASE')
    datetime TIMESTAMP,                               -- Date of the reading
    min_value FLOAT,                         -- Minimum value during the hour
    avg_value FLOAT,                         -- Average value during the hour
    max_value FLOAT,                         -- Maximum value during the hour
    readings_count INT,                      -- Number of raw readings aggregated
    last_updated_at TIMESTAMP DEFAULT NOW(), -- Timestamp of last aggregation
    PRIMARY KEY (sensor_name, datetime)
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- B-Tree indexes for fast date-based lookups
-- Get sensor X's data for date Y
CREATE INDEX IF NOT EXISTS idx_sensor_date ON agg_sensor_stats(sensor_name, CAST(datetime AS DATE));

-- =============================================================================
-- VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- View: v_data_status
-- Purpose: Quick overview of data availability and freshness
-- Gives summary of data available
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_data_status AS
SELECT 
    'agg_machine_activity_daily' as table_name,
    MIN(date) as first_date,
    MAX(date) as last_date,
    COUNT(*) as total_records,
    MAX(last_updated_at) as last_updated
FROM agg_machine_activity_daily;

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


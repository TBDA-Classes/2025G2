
-- Script: create_agg_database.sql
-- Version: 1.0
-- Description: Creates aggregation database tables for pre-computed metrics
-- Usage: psql machine_monitoring_agg -f create_agg_database.sql

-- Table: agg_machine_activity_daily
-- Purpose: Stores daily machine state aggregations

CREATE TABLE IF NOT EXISTS agg_machine_activity_daily (
    dt DATE PRIMARY KEY,
    state_planned_down NUMERIC DEFAULT 0,
    state_running NUMERIC DEFAULT 0,
    state_unplanned_down NUMERIC DEFAULT 0,
    running_percentage NUMERIC
        GENERATED ALWAYS AS (
            ROUND((state_running / 24) * 100, 2)
        ) STORED,
    down_percentage NUMERIC
        GENERATED ALWAYS AS (
            ROUND((state_planned_down / 24) * 100, 2)
        ) STORED,     
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

-- B-Tree indexes for fast date-based lookups
-- Tailored for our request: GET sensor X's data for date Y
CREATE INDEX IF NOT EXISTS idx_sensor_date ON agg_sensor_stats(sensor_name, CAST(dt AS DATE));

-- Table: alerts_daily_count
-- Purpose: Daily summary of alerts by category (used for the alerts summary box)

CREATE TABLE IF NOT EXISTS alerts_daily_count(
    day DATE NOT NULL,
    alert_type VARCHAR(20) NOT NULL
        CHECK(alert_type in ('emergency', 'error', 'warning', 'other')),
    amount INT NOT NULL,
    PRIMARY KEY (day, alert_type)
);


-- Table: alerts_detail
-- Purpose: Individual alert records with timestamps (used for the alerts list)

CREATE TABLE IF NOT EXISTS alerts_detail(
    id SERIAL PRIMARY KEY,
    dt TIMESTAMP NOT NULL,
    day DATE GENERATED ALWAYS AS (dt::date) STORED,
    alert_type VARCHAR(20) NOT NULL
        CHECK(alert_type in ('emergency', 'error', 'warning', 'other')),
    alarm_code TEXT,
    alarm_description TEXT,
    raw_elem_json JSONB
);

CREATE INDEX idx_alerts_detail_day_type ON alerts_detail (day, alert_type);

-- Table: machine_program_data
-- Purpose: Program usage per day (P0, P1, etc. and their run duration)

CREATE TABLE IF NOT EXISTS machine_program_data(
    id SERIAL PRIMARY KEY,
    dt DATE,
    program INT,
    duration_seconds BIGINT NOT NULL CHECK (duration_seconds >= 0)
);

-- Table: energy_consumption_hourly
-- Purpose: Estimated hourly energy consumption based on motor utilization

CREATE TABLE IF NOT EXISTS energy_consumption_hourly (
    hour_ts TIMESTAMP PRIMARY KEY,
    energy_kwh NUMERIC NOT NULL
);


-- =============================================================================
-- VIEWS
-- =============================================================================


DROP VIEW IF EXISTS v_data_status;

-- Purpose: Quick overview of data availability across all aggregated tables
-- Uses UNION ALL for efficient min/max scans on each table's date column
CREATE OR REPLACE VIEW v_data_status AS
WITH all_dates AS (
    SELECT dt::date AS dt FROM agg_sensor_stats
    UNION ALL
    SELECT dt FROM agg_machine_activity_daily
    UNION ALL
    SELECT day FROM alerts_daily_count
    UNION ALL
    SELECT dt::date FROM alerts_detail
    UNION ALL
    SELECT dt FROM machine_program_data
    UNION ALL
    SELECT hour_ts::date FROM energy_consumption_hourly
)
SELECT 
    MIN(dt) as first_date,
    MAX(dt) as last_date,
    (SELECT COUNT(*) FROM agg_sensor_stats) as sensor_records,
    (SELECT COUNT(*) FROM agg_machine_activity_daily) as utilization_records,
    (SELECT COUNT(*) FROM alerts_detail) as alert_records,
    (SELECT COUNT(*) FROM machine_program_data) as program_records,
    (SELECT COUNT(*) FROM energy_consumption_hourly) as energy_records
FROM all_dates;


-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Aggregation database setup complete!';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - agg_machine_activity_daily';
    RAISE NOTICE '  - agg_sensor_stats';
    RAISE NOTICE '  - alerts_daily_count';
    RAISE NOTICE '  - alerts_detail';
    RAISE NOTICE '  - machine_program_data';
    RAISE NOTICE '  - energy_consumption_hourly';
    RAISE NOTICE 'Views created:';
    RAISE NOTICE '  - v_data_status';
END $$;


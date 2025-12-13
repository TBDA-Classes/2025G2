'''
ETL (Extract, Transform and Load) script for hourly energy consumption.
Calculates estimated energy usage based on motor utilization percentages and nominal power ratings.

The calculation: energy_kwh = (utilization% / 100) * nominal_kw * hours

Usage:
    python -m backend.scripts.etl_agg_energy_daily                       # Full backfill
    python -m backend.scripts.etl_agg_energy_daily 2022-02-23            # Single day
    python -m backend.scripts.etl_agg_energy_daily 2022-02-01 2022-02-28 # Date range

Args:
    start_date: Start date (optional). If missing, processes all available data.
    end_date:   End date (optional). If missing, processes single day (start_date).
'''

import logging
import sys
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database import prod_engine, agg_engine
from backend.models import EnergyConsumptionHourly

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_date_range():
    '''
    Query the source DB for the min and max dates when no dates are provided.
    Used for full backfill.
    '''
    try:
        with prod_engine.connect() as conn:
            query = '''
            SELECT 
                MIN(to_timestamp(date / 1000))::date AS min_date,
                MAX(to_timestamp(date / 1000))::date AS max_date
            FROM variable_log_float
            WHERE id_var IN (
                SELECT id FROM variable 
                WHERE name IN ('AXIS_X_MOTOR_UTILIZACION', 'AXIS_Y_MOTOR_UTILIZATION', 
                               'AXIS_Z_MOTOR_UTILIZACION', 'SPINDLE_LOAD_1')
            )
            '''
            result = conn.execute(text(query))
            row = result.fetchone()
            if row and row.min_date and row.max_date:
                return str(row.min_date), str(row.max_date)
            return None, None
    except Exception as e:
        logger.error(f"Failed to get date range: {str(e)}")
        raise


def extract_data(target_date):
    '''
    Extract hourly energy consumption for a single day.
    
    Params:
        target_date: Date string, e.g. "2022-02-23"
    
    Returns:
        List of dicts with hour_ts and energy_kwh.
    '''
    try:
        with prod_engine.connect() as conn:
            query = '''
            WITH params AS (
                SELECT
                    CAST(:start_ts AS TIMESTAMPTZ) AS start_ts,
                    CAST(:end_ts AS TIMESTAMPTZ) AS end_ts,
                    (EXTRACT(EPOCH FROM CAST(:start_ts AS TIMESTAMPTZ)) * 1000)::bigint AS start_ms,
                    (EXTRACT(EPOCH FROM CAST(:end_ts AS TIMESTAMPTZ)) * 1000)::bigint AS end_ms
            ),

            motor_cfg AS (
                SELECT
                    v.id AS id_var,
                    cfg.motor,
                    cfg.nominal_kw
                FROM (
                    VALUES
                        ('AXIS_X_MOTOR_UTILIZACION', 15.1::float8),
                        ('AXIS_Y_MOTOR_UTILIZATION', 15.1::float8),
                        ('AXIS_Z_MOTOR_UTILIZACION', 15.71::float8),
                        ('SPINDLE_LOAD_1',           37.0::float8)
                ) AS cfg(motor, nominal_kw)
                JOIN variable v ON v.name = cfg.motor
            ),

            raw AS (
                SELECT
                    mc.motor,
                    to_timestamp(f.date / 1000.0) AS ts,
                    f.value::float8               AS util_pct,
                    mc.nominal_kw
                FROM variable_log_float f
                JOIN motor_cfg mc ON mc.id_var = f.id_var
                CROSS JOIN params p
                WHERE f.date >= p.start_ms
                    AND f.date <  p.end_ms
                    AND f.value IS NOT NULL
                    AND f.value = f.value
                    AND f.value NOT IN ('Infinity'::real, '-Infinity'::real)
            ),

            seg AS (
                SELECT
                    motor,
                    ts,
                    LEAD(ts) OVER (PARTITION BY motor ORDER BY ts) AS ts_next,
                    util_pct,
                    nominal_kw
                FROM raw
            ),

            seg_clamped AS (
                SELECT
                    s.motor,
                    s.ts,
                    CASE
                        WHEN s.ts_next IS NULL OR s.ts_next > p.end_ts THEN p.end_ts
                        ELSE s.ts_next
                    END AS ts_next,
                    s.util_pct,
                    s.nominal_kw
                FROM seg s
                CROSS JOIN params p
            ),

            segments_energy AS (
                SELECT
                    motor,
                    ts,
                    ts_next,
                    (util_pct / 100.0 * nominal_kw)
                        * EXTRACT(EPOCH FROM (ts_next - ts)) / 3600.0 AS energy_kwh
                FROM seg_clamped
                WHERE ts_next > ts
            )

            SELECT
                date_trunc('hour', ts)             AS hour_ts,
                ROUND(SUM(energy_kwh)::numeric, 3) AS energy_kwh
            FROM segments_energy
            GROUP BY 1
            ORDER BY 1;
            '''
            
            # Build timestamp strings for the day
            start_ts = f"{target_date} 00:00:00+00"
            end_ts_date = datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)
            end_ts = f"{end_ts_date.strftime('%Y-%m-%d')} 00:00:00+00"
            
            result = conn.execute(text(query), {
                'start_ts': start_ts,
                'end_ts': end_ts
            })
            rows = result.fetchall()
            
            if not rows:
                return []
            
            return [
                {
                    'hour_ts': row.hour_ts,
                    'energy_kwh': float(row.energy_kwh)
                }
                for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Extraction failed for {target_date}: {str(e)}")
        raise


def load_data(data):
    '''
    Load energy records into the aggregated database.
    Uses merge to upsert (update if exists, insert if not).
    
    Params:
        data: List of dicts from extract_data()
    '''
    if not data:
        logger.warning("No data to load")
        return
        
    session = Session(agg_engine)
    try:
        for record in data:
            energy_record = EnergyConsumptionHourly(
                hour_ts=record['hour_ts'],
                energy_kwh=record['energy_kwh']
            )
            session.merge(energy_record)
        
        session.commit()
        logger.info(f"Loaded {len(data)} hourly records")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Load failed: {str(e)}")
        raise
    finally:
        session.close()


def run_etl(start_date=None, end_date=None):
    '''
    Main orchestration function.
    '''
    # Determine date range
    if start_date is None:
        logger.info("No dates provided, fetching full date range...")
        start_date, end_date = get_date_range()
        if not start_date:
            logger.error("Could not determine date range from database")
            return
        logger.info(f"Full backfill from {start_date} to {end_date}")
    elif end_date is None:
        logger.info(f"Processing single day: {start_date}")
        end_date = start_date
    else:
        logger.info(f"Processing range: {start_date} to {end_date}")
    
    # Process each day
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    total_records = 0
    
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        try:
            data = extract_data(date_str)
            if data:
                load_data(data)
                total_records += len(data)
            else:
                logger.info(f"No data for {date_str}")
        except Exception as e:
            logger.error(f"Failed for {date_str}: {str(e)}")
        
        current += timedelta(days=1)
    
    logger.info(f"ETL complete. Total records loaded: {total_records}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_etl(sys.argv[1])
    elif len(sys.argv) == 3:
        run_etl(sys.argv[1], sys.argv[2])
    else:
        run_etl()

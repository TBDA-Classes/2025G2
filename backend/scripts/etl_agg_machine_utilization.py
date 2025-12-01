

'''
ETL (Extract, Transform and Load) script for machine utilization tracking

Args:
    None - Too complex of a query 
'''

# IMPORTS
import logging
import sys

from backend.database import prod_engine, agg_engine
from backend.models import MachineUtilization
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime


# DATA EXTRACTION
def extract_data():
    '''
    Query source DB for machine operation and stop events
    Note: To properly calculate overnight stops, we query +/- 1 day of buffer
    and filter in the final SELECT
    '''
    try:
        with prod_engine.connect() as conn:
            
            
            # Build dynamic query that processes all available dates in the database
            query = '''
        WITH changes AS (
            -- 1. Combine float and string logs (all dates)
            SELECT to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
            FROM variable_log_float a

            UNION ALL

            SELECT to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
            FROM variable_log_string a

            ORDER BY 1
        ),

        DateRange AS (
            -- 2. Generate a calendar table for each day based on actual data range
            SELECT DISTINCT date(dt) AS calendar_date
            FROM changes
        ),

        sorted AS (
            -- 3. Sort and identify previous/next timestamps within each day
            SELECT
                dt,
                date(dt) AS date,
                LAG(dt)  OVER (PARTITION BY date(dt) ORDER BY dt) AS prev_dt,
                LEAD(dt) OVER (PARTITION BY date(dt) ORDER BY dt) AS next_dt
            FROM changes
        ),

        GlobalEvents AS (
            -- 4. Detect the next global event (not partitioned by day)
            SELECT
                dt,
                date(dt) AS date,
                LEAD(dt, 1) OVER (ORDER BY dt) AS next_global_dt
            FROM changes
        ),

        -- Operation block logic
        mark_ops AS (
            SELECT
                date,
                dt,
                CASE
                    WHEN prev_dt IS NULL
                    OR EXTRACT(EPOCH FROM (dt - prev_dt)) > 600
                    THEN 1 ELSE 0
                END AS new_session
            FROM sorted
        ),

        op_blocks AS (
            SELECT
                date,
                dt,
                SUM(new_session) OVER (PARTITION BY date ORDER BY dt) AS block_id
            FROM mark_ops
        ),

        final_operations AS (
            SELECT
                'OPERATION' AS event_type,
                date,
                MIN(dt) AS start_time,
                MAX(dt) AS end_time,
                ROUND(EXTRACT(EPOCH FROM (MAX(dt) - MIN(dt))) / 3600.0, 2)
                    AS duration_hours
            FROM op_blocks
            GROUP BY date, block_id
        ),

        -- Midnight transition logic
        overnight_stops AS (
            -- Events where the next timestamp belongs to a different day
            SELECT
                dt,
                next_global_dt,
                EXTRACT(EPOCH FROM (next_global_dt - dt)) AS gap_seconds
            FROM GlobalEvents
            WHERE date(dt) <> date(next_global_dt)
        ),

        split_overnight_stops AS (
            -- Split midnight transitions into two separate events
            SELECT
                'STOP' AS event_type,
                date(dt) AS date,
                dt AS start_time,
                date(dt) + interval '1 day' - interval '1 second' AS end_time,
                ROUND(
                    EXTRACT(EPOCH FROM (
                        (date(dt) + interval '1 day' - interval '1 second') - dt
                    )) / 3600.0, 2
                ) AS duration_hours
            FROM overnight_stops
            WHERE gap_seconds > 600

            UNION ALL

            SELECT
                'STOP' AS event_type,
                date(next_global_dt) AS date,
                date(next_global_dt) AS start_time,
                next_global_dt AS end_time,
                ROUND(
                    EXTRACT(EPOCH FROM (
                        next_global_dt - date(next_global_dt)
                    )) / 3600.0, 2
                ) AS duration_hours
            FROM overnight_stops
            WHERE gap_seconds > 600
        ),

        -- Intraday STOP logic (gaps > 10 minutes)
        intra_day_stops AS (
            SELECT
                'STOP' AS event_type,
                date,
                dt AS start_time,
                next_dt AS end_time,
                ROUND(EXTRACT(EPOCH FROM (next_dt - dt)) / 3600.0, 2)
                    AS duration_hours
            FROM sorted
            WHERE next_dt IS NOT NULL
            AND EXTRACT(EPOCH FROM (next_dt - dt)) > 600
        ),

        -- Combine all event types
        all_events AS (
            SELECT event_type, date, start_time, end_time, duration_hours FROM final_operations
            UNION ALL
            SELECT event_type, date, start_time, end_time, duration_hours FROM intra_day_stops
            UNION ALL
            SELECT event_type, date, start_time, end_time, duration_hours FROM split_overnight_stops
        )

        -- Final output
        SELECT
            COALESCE(e.event_type, 'STOP') AS event_type,
            r.calendar_date AS date,
            CASE EXTRACT(DOW FROM r.calendar_date)
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                WHEN 6 THEN 'Saturday'
            END AS weekday,
            COALESCE(e.start_time, r.calendar_date::timestamp) AS start_time,
            COALESCE(e.end_time,
                (r.calendar_date + interval '1 day' - interval '1 second')::timestamp
            ) AS end_time,
            COALESCE(e.duration_hours, 24.00) AS duration_hours

        FROM DateRange r
        LEFT JOIN all_events e ON r.calendar_date = e.date
        ORDER BY r.calendar_date, start_time;
            '''

            result = conn.execute(text(query))
            rows = result.fetchall()
            
            if not rows:
                logger.warning(f"Result is nonexistent")
                return []
            
            # Return list of dicts for transformation step
            return [
                {
                    'machine_state': row.event_type,
                    'state_start_time': row.start_time,
                    'state_end_time': row.end_time
                } 
                for row in rows
            ]

            
    except Exception as e:
        logger.error(f"Connection failed when extracting data: {str(e)}")
        raise


# DATA TRANSFORMATION
def transform_data(raw_data):
    '''
    Process data - Map event types to machine states
    Args: 
        raw_data: List of dicts with machine_state, state_start_time, state_end_time

    Returns:
        transformed_data: Array with machine states mapped correctly
            OPERATION -> running
            STOP -> down
    '''
    transformed_data = []
    
    for record in raw_data:
        # Map event types to machine states
        machine_state = 'running' if record['machine_state'] == 'OPERATION' else 'down'
        
        transformed_data.append({
            'machine_state': machine_state,
            'state_start_time': record['state_start_time'],
            'state_end_time': record['state_end_time']
        })
    
    return transformed_data


# DATA LOADING
def load_data(transformed_data):
    '''
    Store in destination DB
    Strategy: Delete existing records for the affected dates, then insert new ones
    This prevents duplicates when re-running the ETL for the same date range
    '''
    
    if not transformed_data:
        logger.warning("No data to load")
        return
    
    session = Session(agg_engine)
    try:
        # Find the date range covered by the new data
        dates_to_update = set()
        for record in transformed_data:
            # Use the generated 'dt' column (date from state_start_time)
            record_date = record['state_start_time'].date()
            dates_to_update.add(record_date)
        
        # Delete existing records for these dates
        min_date = min(dates_to_update)
        max_date = max(dates_to_update)
        
        delete_query = text("""
            DELETE FROM machine_utilization 
            WHERE dt BETWEEN :min_date AND :max_date
        """)
        result = session.execute(delete_query, {'min_date': min_date, 'max_date': max_date})
        deleted_count = result.rowcount
        
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} existing records for dates {min_date} to {max_date}")
        
        # Insert new records
        for record in transformed_data:
            # Note: dt and duration are generated columns, so we don't need to set them
            utilization = MachineUtilization(
                machine_state = record['machine_state'],
                state_start_time = record['state_start_time'],
                state_end_time = record['state_end_time']
            )
            session.add(utilization)
        
        session.commit()
        logger.info(f"Inserted {len(transformed_data)} new records")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Load of data failed: {str(e)}")
        raise
        
    finally:
        session.close()


# ORCHESTRATION
def run_etl():
    '''Main function which combines all steps'''
    
    # Determine date range description
    
    logger.info(f"Started ETL script for full backfill")
    
    try:
        raw_data = extract_data()
        if not raw_data:
            logger.warning(f"Could not find raw data.")
            return
        
        logger.info(f"Extracted raw data consisting of {len(raw_data)} records")
        
        transformed_data = transform_data(raw_data)
        logger.info(f"Transformed into {len(transformed_data)} utilization records.")
        
        load_data(transformed_data)
        logger.info(f"Successfully loaded data.")
    except Exception as e:
        logger.error(f"ETL failed with error: {str(e)}")
        raise


# When run directly from CLI
if __name__ == "__main__":
    
    # Logging setup
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    run_etl()
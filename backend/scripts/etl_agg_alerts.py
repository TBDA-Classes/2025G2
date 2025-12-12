'''
ETL (Extract, Transform and Load) script for alerts data.
Populates two tables: alerts_daily_count and alerts_detail

Use the Arguments to filter on date. If one data from one date is desired, use only one argument.
If data between an interval of two dates is desired, use two arguments, respectively start_date and end_date.

Tip: When running the script, run it as a module:
    
    EXAMPLE BELOW:
    python -m backend.scripts.etl_agg_alerts 2022-02-23
    python -m backend.scripts.etl_agg_alerts 2022-02-01 2022-02-28

Args:
    start_date : None by default (will do full backfill)
    end_date   : None by default
'''

# IMPORTS
import logging
import sys
import json

from backend.database import prod_engine, agg_engine
from backend.models import AlertsDailyCount, AlertsDetail
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


# Mapping from query categories to table values
ALERT_TYPE_MAP = {
    'Emergency': 'emergency',
    'Error': 'error',
    'Alert': 'warning',  # Alert category maps to warning
    'Other': 'other',
}


# HELPER FUNCTION
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
            FROM variable_log_string
            WHERE id_var = 447
            AND value IS NOT NULL
            AND value != '[]'
            '''
            result = conn.execute(text(query))
            row = result.fetchone()
            if row and row.min_date and row.max_date:
                return str(row.min_date), str(row.max_date)
            return None, None
    except Exception as e:
        logger.error(f"Failed to get date range: {str(e)}")
        raise


# EXTRACT FUNCTION FOR DAILY COUNT
def extract_daily_count(target_date):
    '''
    Query source DB for alert counts by type for a single date.
    Returns list of dicts with day, alert_type, and amount.
    '''
    try:
        with prod_engine.connect() as conn:
            query = '''
            WITH alarm_data AS (
                SELECT
                    to_timestamp(a.date / 1000) AS timestamp,
                    TRIM(elem ->> 0) AS alarm_code,
                    TRIM(elem ->> 1) AS alarm_description
                FROM variable_log_string a
                JOIN variable b ON a.id_var = b.id
                CROSS JOIN LATERAL jsonb_array_elements(a.value::jsonb) AS elem
                WHERE b.id = 447
                  AND a.value IS NOT NULL
                  AND a.value != '[]'
                  AND LENGTH(a.value) > 2
                  AND a.value ~ '^\\[.*\\]$'
                  AND to_timestamp(a.date / 1000)::date = CAST(:target_date AS date)
            ),
            categorized AS (
                SELECT
                    timestamp,
                    alarm_code,
                    alarm_description,
                    CASE
                        WHEN alarm_description ILIKE '%emerg%' THEN 'Emergency'
                        WHEN alarm_description ILIKE '%error%' OR 
                             alarm_description ILIKE '%err%' OR
                             alarm_description ILIKE '%fallo%' OR
                             alarm_description ILIKE '%fault%' THEN 'Error'
                        WHEN alarm_description ILIKE '%alert%' OR 
                             alarm_description ILIKE '%alarm%' OR 
                             alarm_description ILIKE '%warn%' OR
                             alarm_description ILIKE '%aviso%' OR
                             alarm_description ILIKE '%attention%' THEN 'Alert'
                        ELSE 'Other'
                    END AS alert_type
                FROM alarm_data
            )
            SELECT 
                alert_type,
                COUNT(*) AS total_occurrences
            FROM categorized
            WHERE alert_type IS NOT NULL
            GROUP BY alert_type
            ORDER BY alert_type;
            '''

            result = conn.execute(text(query), {'target_date': target_date})
            rows = result.fetchall()
            
            return [
                {
                    'day': target_date,
                    'alert_type': ALERT_TYPE_MAP.get(row.alert_type),
                    'amount': row.total_occurrences
                } 
                for row in rows
                if row.alert_type in ALERT_TYPE_MAP
            ]
            
    except Exception as e:
        logger.error(f"Failed to extract daily count: {str(e)}")
        raise


# EXTRACT FUNCTION FOR ALERT DETAILS
def extract_details(target_date):
    '''
    Query source DB for detailed alert records for a single date.
    Returns list of dicts with dt, alert_type, alarm_code, alarm_description, raw_elem_json.
    '''
    try:
        with prod_engine.connect() as conn:

            # Only querying for Emergencies and Errors, as these are the only ones we are interested
            # in showing details for.
            query = '''
            WITH alarm_data AS (
                SELECT
                    to_timestamp(a.date / 1000.0) AS ts,
                    elem AS raw_elem_jsonb,
                    NULLIF(TRIM(elem ->> 0), '') AS alarm_code,
                    NULLIF(TRIM(elem ->> 1), '') AS alarm_description
                FROM variable_log_string a
                JOIN variable b ON a.id_var = b.id
                CROSS JOIN LATERAL jsonb_array_elements(a.value::jsonb) AS elem
                WHERE b.id = 447
                  AND a.value IS NOT NULL
                  AND a.value <> '[]'
                  AND LENGTH(a.value) > 2
                  AND a.value ~ '^\\[.*\\]$'
                  AND to_timestamp(a.date / 1000.0)::date = CAST(:target_date AS date)
            ),
            categorized AS (
                SELECT
                    ts,
                    alarm_code,
                    alarm_description,
                    raw_elem_jsonb,
                    CASE
                        WHEN alarm_description ILIKE '%emerg%' THEN 'Emergency'
                        WHEN alarm_description ILIKE '%error%'
                          OR alarm_description ILIKE '%err%'
                          OR alarm_description ILIKE '%fallo%'
                          OR alarm_description ILIKE '%fault%' THEN 'Error'
                        ELSE NULL
                    END AS alert_type
                FROM alarm_data
            )
            SELECT
                ts,
                alert_type,
                alarm_code,
                alarm_description,
                raw_elem_jsonb::text AS raw_elem_json
            FROM categorized
            WHERE alert_type IS NOT NULL
            ORDER BY ts DESC;
            '''

            result = conn.execute(text(query), {'target_date': target_date})
            rows = result.fetchall()
            
            return [
                {
                    'dt': row.ts,
                    'alert_type': ALERT_TYPE_MAP.get(row.alert_type),
                    'alarm_code': row.alarm_code,
                    'alarm_description': row.alarm_description,
                    'raw_elem_json': json.loads(row.raw_elem_json) if row.raw_elem_json else None
                } 
                for row in rows
                if row.alert_type in ALERT_TYPE_MAP
            ]
            
    except Exception as e:
        logger.error(f"Failed to extract details: {str(e)}")
        raise


# LOAD FUNCTION FOR DAILY COUNT
def load_daily_count(data):
    '''Store daily count data in destination DB'''
    if not data:
        return 0
        
    session = Session(agg_engine)
    try:
        for record in data:
            alert_count = AlertsDailyCount(
                day=record['day'],
                alert_type=record['alert_type'],
                amount=record['amount']
            )
            session.merge(alert_count)  # Use merge for upsert behavior

        session.commit()
        return len(data)
            
    except Exception as e:
        session.rollback()
        logger.error(f"Load of daily count failed: {str(e)}")
        raise
        
    finally:
        session.close()


# LOAD FUNCTION FOR ALERT DETAILS
def load_details(data):
    '''Store detail data in destination DB'''
    if not data:
        return 0
        
    session = Session(agg_engine)
    try:
        for record in data:
            alert_detail = AlertsDetail(
                dt=record['dt'],
                alert_type=record['alert_type'],
                alarm_code=record['alarm_code'],
                alarm_description=record['alarm_description'],
                raw_elem_json=record['raw_elem_json']
            )
            session.add(alert_detail)

        session.commit()
        return len(data)
            
    except Exception as e:
        session.rollback()
        logger.error(f"Load of details failed: {str(e)}")
        raise
        
    finally:
        session.close()


# ORCHESTRATION
def run_etl(start_date=None, end_date=None):
    '''Main function which combines all steps'''

    # For full backfill, get min/max dates from source data
    if start_date is None and end_date is None:
        logger.info("No dates provided, querying date range for full backfill...")
        start_date, end_date = get_date_range()
        if not start_date or not end_date:
            logger.error("Could not determine date range for full backfill")
            return
        date_desc = f"full backfill from {start_date} to {end_date}"
    elif end_date is not None:
        date_desc = f"from {start_date} to {end_date}"
    else:
        end_date = start_date  # Single date
        date_desc = f"only {start_date}"
    
    logger.info(f"Started ETL script for {date_desc}")
    
    # Process each date in the range
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    total_daily_count = 0
    total_details = 0
    failed_dates = []
    
    while current_date <= end_dt:
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            # Extract and load daily count
            daily_count_data = extract_daily_count(date_str)
            if daily_count_data:
                loaded = load_daily_count(daily_count_data)
                total_daily_count += loaded
            
            # Extract and load details
            details_data = extract_details(date_str)
            if details_data:
                loaded = load_details(details_data)
                total_details += loaded
                
        except Exception as e:
            logger.warning(f"Failed to process {date_str}: {str(e)}")
            failed_dates.append(date_str)
        
        current_date += timedelta(days=1)
    
    logger.info(f"Successfully loaded {total_daily_count} daily count records")
    logger.info(f"Successfully loaded {total_details} detail records")
    
    if failed_dates:
        logger.warning(f"Failed to process {len(failed_dates)} dates: {failed_dates[:10]}{'...' if len(failed_dates) > 10 else ''}")


# When run directly from CLI
if __name__ == "__main__":

    # Logging - Tracks what happens at every step
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if len(sys.argv) == 2:
        start_date = sys.argv[1]
        run_etl(start_date)
    elif len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        run_etl(start_date, end_date)
    else:
        # Full backfill - no dates provided
        run_etl()

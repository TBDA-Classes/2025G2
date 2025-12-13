'''
ETL (Extract, Transform and Load) script for machine program history data.
Use the Arguments to filter on date. If one data from one date is desired, use only one argument.
If data between an interval of two dates is desired, use two arguments, respectively start_date and end_date.

Tip: When running the script, run it as a module, this way our imports are properly handled (sys.path):
    
    EXAMPLE BELOW:
    (venv) (base) atlesund@Atles-MacBook-Pro 2025G2 % python -m backend.scripts.etl_agg_program_history 2021-01-07
    INFO:__main__:Started ETL script for only 2021-01-07
    INFO:__main__:Extracted raw data consisting of 15 records
    INFO:__main__:Successfully loaded data.

Args:
    start_date : None by default. 
    end_date   : None by default
'''

# IMPORTS
import logging
import sys

from backend.database import prod_engine, agg_engine
from backend.models import MachineProgramData
from sqlalchemy import text
from sqlalchemy.orm import Session


# Using a  helper function to get the full range in case of a full backfill
def get_date_range():
    '''
    Query the source DB for the min and max dates when no dates are provided.
    Used for full backfill.
    '''
    try:
        with prod_engine.connect() as conn:
            query = '''
            SELECT 
                MIN(to_timestamp(trunc(cast(date AS bigint)/1000)))::date AS min_date,
                MAX(to_timestamp(trunc(cast(date AS bigint)/1000)))::date AS max_date
            FROM variable_log_float
            WHERE id_var = 581
            AND value >= 0 AND value < 1000
            '''
            result = conn.execute(text(query))
            row = result.fetchone()
            if row and row.min_date and row.max_date:
                return str(row.min_date), str(row.max_date)
            return None, None
    except Exception as e:
        logger.error(f"Failed to get date range: {str(e)}")
        raise


# EXTRACT FUNCTION
def extract_data(start_date=None, end_date=None):
    '''
    Query source DB for program history data.
    Returns list of dicts with dt, program, and duration_seconds.
    '''
    try:
        with prod_engine.connect() as conn:
            
            query = '''
            WITH RangoTiempo AS (
                SELECT
                    CAST(:start_date AS timestamp) AS inicio,
                    CAST(:end_date AS timestamp) + interval '1 day' AS fin
            ),

            EstadoPrevio AS (
                SELECT
                    (SELECT inicio FROM RangoTiempo) AS dt,
                    CAST(value AS integer) AS estado_numerico
                FROM variable_log_float
                WHERE id_var = 581
                AND to_timestamp(trunc(cast(date AS bigint)/1000)) < (SELECT inicio FROM RangoTiempo)
                AND value >= 0 AND value < 1000
                ORDER BY date DESC
                LIMIT 1
            ),

            LogsRango AS (
                SELECT
                    to_timestamp(trunc(cast(date AS bigint)/1000)) AS dt,
                    CAST(value AS integer) AS estado_numerico
                FROM variable_log_float
                WHERE id_var = 581
                AND to_timestamp(trunc(cast(date AS bigint)/1000)) BETWEEN (SELECT inicio FROM RangoTiempo) AND (SELECT fin FROM RangoTiempo)
                AND value >= 0 AND value < 1000
            ),

            LogsCompletos AS (
                SELECT dt, estado_numerico FROM EstadoPrevio
                UNION ALL
                SELECT dt, estado_numerico FROM LogsRango
            ),

            Intervalos AS (
                SELECT
                    dt AS hora_inicio,
                    LEAD(dt) OVER (ORDER BY dt) AS hora_fin_raw,
                    estado_numerico
                FROM LogsCompletos
            ),

            IntervalosCerrados AS (
                SELECT
                    hora_inicio,
                    COALESCE(hora_fin_raw, (SELECT fin FROM RangoTiempo)) AS hora_fin,
                    estado_numerico
                FROM Intervalos
            ),

            SerieDias AS (
                SELECT generate_series(
                    (SELECT date_trunc('day', inicio) FROM RangoTiempo),
                    (SELECT date_trunc('day', fin) FROM RangoTiempo),
                    '1 day'
                ) AS dia_referencia
            ),

            CortePorDias AS (
                SELECT
                    d.dia_referencia,
                    i.estado_numerico,
                    GREATEST(i.hora_inicio, d.dia_referencia) AS inicio_real,
                    LEAST(i.hora_fin, d.dia_referencia + interval '1 day') AS fin_real
                FROM IntervalosCerrados i
                JOIN SerieDias d ON
                    i.hora_inicio < (d.dia_referencia + interval '1 day') AND
                    i.hora_fin > d.dia_referencia
            )

            SELECT
                date(dia_referencia) AS fecha,
                estado_numerico,
                ROUND(SUM(EXTRACT(EPOCH FROM (fin_real - inicio_real))), 2) AS duracion_segundos
            FROM CortePorDias
            WHERE fin_real > inicio_real
              AND EXISTS (SELECT 1 FROM LogsRango)  -- Only return data if actual logs exist in range
            GROUP BY 1, 2
            ORDER BY fecha, duracion_segundos DESC;
            '''

            params = {
                'start_date': start_date,
                'end_date': end_date if end_date else start_date
            }

            result = conn.execute(text(query), params)
            rows = result.fetchall()
            
            if not rows:
                logger.warning("No data found for the specified date range")
                return []
            
            return [
                {
                    'dt': row.fecha,
                    'program': row.estado_numerico,
                    'duration_seconds': int(row.duracion_segundos)
                } 
                for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Connection failed when extracting data: {str(e)}")
        raise


# LOAD FUNCTION
def load_data(transformed_data):
    '''Store in destination DB'''
    session = Session(agg_engine)
    try:
        for record in transformed_data:
            program_data = MachineProgramData(
                dt=record['dt'],
                program=record['program'],
                duration_seconds=record['duration_seconds']
            )
            session.add(program_data)

        session.commit()
            
    except Exception as e:
        session.rollback()
        logger.error(f"Load of data failed: {str(e)}")
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
        date_desc = f"only {start_date}"
    
    logger.info(f"Started ETL script for {date_desc}")
    
    try:
        raw_data = extract_data(start_date, end_date)
        if not raw_data:
            logger.warning("Could not find raw data.")
            return

        logger.info(f"Extracted raw data consisting of {len(raw_data)} records")
        
        # No transformation needed - data is already in the correct format from the query
        load_data(raw_data)
        logger.info("Successfully loaded data.")
        
    except Exception as e:
        logger.error(f"ETL failed with error: {str(e)}")
        raise


# When run directly from CLI, __name__ = "__main__"
# Parametrized execution
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
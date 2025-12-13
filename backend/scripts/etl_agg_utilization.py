'''
ETL (Extract, Transform and Load) script for daily machine utilization.
Calculates running hours vs. downtime hours per day based on log activity gaps.

A gap of >10 minutes between log entries is considered downtime.

Usage:
    python -m backend.scripts.etl_agg_utilization                       # Full backfill
    python -m backend.scripts.etl_agg_utilization 2021-09-14            # Single day
    python -m backend.scripts.etl_agg_utilization 2021-09-01 2021-09-30 # Date range

Args:
    from_date: Start date (optional). If missing, processes all available data.
    to_date:   End date (optional). If missing, processes single day (from_date).
'''

import logging
import sys

from sqlalchemy.orm import Session
from backend.database import prod_engine, agg_engine
from sqlalchemy import text
from backend.models import AggMachineActivityDaily

logging.basicConfig(level=logging.INFO)

def extract_data(from_date=None, to_date=None):
    '''
    Extract running/downtime hours from production database.
    
    Params:
        from_date: Start date filter (optional)
        to_date:   End date filter (optional)
    
    Returns:
        List of dicts with dt, running_hours, and down_hours per day.
    '''
    try:
        with prod_engine.connect() as conn:
            query = '''WITH cambios AS (
            -- 1. Common database: Float and string union
            SELECT
                to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
            FROM variable_log_float a
            '''
            if(from_date):
                if(to_date):
                    query +='''
                    WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))::date
                    BETWEEN :from_date AND :to_date
                    '''
                else:
                    query +='''
                    WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))::date
                    = :from_date
                    '''
            query += '''
            UNION ALL

            SELECT
                to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
            FROM variable_log_string a
            '''
            if(from_date):
                if(to_date):
                    query += '''
                    WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))::date
                    BETWEEN :from_date AND :to_date
                    '''
                else:
                    query+='''
                    WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))::date
                        = :from_date
                    '''

            query +='''
            ),
            ordenado AS (
                -- 2. Sorting
                SELECT
                    dt,
                    date(dt) AS fecha,
                    LAG(dt) OVER (PARTITION BY date(dt) ORDER BY dt) AS dt_anterior
                FROM cambios
            ),

            -- Calculation of operations (running time)
            marcado_ops AS (
                SELECT fecha, dt, CASE WHEN dt_anterior IS NULL OR EXTRACT(EPOCH FROM (dt - dt_anterior)) > 600 THEN 1 ELSE 0 END AS nueva_sesion
                FROM ordenado
            ),
            bloques_ops AS (
                SELECT fecha, dt, SUM(nueva_sesion) OVER (PARTITION BY fecha ORDER BY dt) AS bloque_id
                FROM marcado_ops
            ),
            Duracion_Operacion AS (
                SELECT fecha, EXTRACT(EPOCH FROM (MAX(dt) - MIN(dt))) AS duracion_segundos
                FROM bloques_ops
                GROUP BY fecha, bloque_id
            ),
            Tiempo_Running AS (
                SELECT fecha, COALESCE(SUM(duracion_segundos), 0) AS running_segundos
                FROM Duracion_Operacion
                GROUP BY fecha
            )

            -- ==========================================
            -- Final format and percentages (24 hours = 86400 s)
            -- ==========================================
            SELECT
                r.fecha AS dia,
                
                -- Conversion to hours (Running)
                ROUND( (COALESCE(r.running_segundos, 0) / 3600.0), 2) AS running_horas,
                
                -- Conversion to hours (Down)
                ROUND( ((86400.0 - COALESCE(r.running_segundos, 0)) / 3600.0), 2) AS down_horas
            FROM (
                -- Select all dates with logs for coverage assurement
                SELECT DISTINCT fecha 
                FROM ordenado
            ) AS All_Dates
            LEFT JOIN Tiempo_Running r ON All_Dates.fecha = r.fecha

            ORDER BY dia;
            '''
            params = {
                'from_date' : from_date,
                'to_date' : to_date
            }
            results = conn.execute(text(query), params)
            
            return [
                {
                'dt' : r.dia,
                'running_hours' : r.running_horas,
                'down_hours' : r.down_horas
                }
            for r in results
            ]
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        raise
    
def load_data(transformed_data):
    '''
    Load records into the aggregated database.
    Uses merge to upsert (update if exists, insert if not).
    
    Params:
        transformed_data: List of dicts from extract_data()
    '''
    session = Session(agg_engine)
    try:
        
        for record in transformed_data:
            session_object = AggMachineActivityDaily(
                dt = record['dt'],
                state_planned_down = record['down_hours'],
                state_running = record['running_hours'], 
            )
            session.merge(session_object)
        
        session.commit()

    
    except Exception as e:
        logger.error(f"Error for loading data: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
    


def run_etl():
    '''
    Main orchestration function.
    '''
    if len(sys.argv) > 1:
        if len(sys.argv) == 3:
            raw_data = extract_data(sys.argv[1], sys.argv[2])
            logger.info(f"Started ETL script for dates between {sys.argv[1]} && {sys.argv[2]}")
        else:
            raw_data = extract_data(sys.argv[1])
            logger.info(f"Started ETL script for {sys.argv[1]}")
    else:
        raw_data = extract_data()
        logger.info(f"Started ETL script for full backfill")
        

    
    logger.info(f"Successfully loaded {len(raw_data)} rows")
    # Transformation not needed since it is sufficiently transformed in the load query
    load_data(raw_data)
    logger.info(f"Successfully loaded data")


if __name__ == "__main__":
    
    logger = logging.getLogger(__name__)
    run_etl()

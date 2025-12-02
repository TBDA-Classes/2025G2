'''
ETL (Extract, Transform and Load) script for tracking of TEMPERATURA BASE
Use the Arguments to filter on date. If one data from one date is desired, use only one argument.
If data between an interval of two dates is desired, use two arguments, respectively start_date and end_date.

Tip: When running the script, run it as a module, this way our imports are properly handled (sys.path):
    
    EXAMPLE BELOW:
    (venv) (base) atlesund@Atles-MacBook-Pro 2025G2 % python -m backend.scripts.etl_temperature 2021-01-07
    INFO:__main__:Started ETL script for only 2021-01-07
    INFO:__main__:Parameters start_date = True and end_date = False
    INFO:__main__:Extracted raw data consisting of 33410 records
    INFO:__main__:Transformed into 13 hourly records.
    INFO:__main__:Succesfully loaded data.

Args:
    start_date : None by default. 
    end_date   : None by default
'''

# IMPORTS


import logging
import statistics
import sys
import math

from backend.database import prod_engine, agg_engine
from backend.models import AggSensorStats
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
from collections import defaultdict

SENSOR_OF_CHOICE = 'TEMPERATURA_BASE'



# EXTRACT FUNCTION
def extract_data(start_date, end_date):
    '''
    Query source DB
    '''
    try:
        with prod_engine.connect() as conn:
            
            # Simplified the query to only the two values of interest, date and value

            query = f'''
            SELECT vlf.value, 
                TO_TIMESTAMP(vlf.date/1000) AS ts 
            FROM variable_log_float vlf
                LEFT JOIN variable v ON vlf.id_var = v.id
                WHERE v.name = :sensor_name
            '''

            params = {'sensor_name' : SENSOR_OF_CHOICE}

            if start_date is not None:
                
                if end_date is None:
                    logger.info(f"Parameters start_date = True and end_date = False")
                    query += " AND TO_TIMESTAMP(vlf.date/1000)::date = :start_date" 
                    params = {'sensor_name' : SENSOR_OF_CHOICE, 'start_date' : start_date}
                else:
                    logger.info(f"Parameters start_date = True and end_date = True")
                    #Can't use alias "ts" in WHERE clause
                    query += " AND TO_TIMESTAMP(vlf.date/1000)::date >= :start_date" 
                    query += " AND TO_TIMESTAMP(vlf.date/1000)::date <= :end_date"
                    params = {'sensor_name' : SENSOR_OF_CHOICE, 'start_date' : start_date, 'end_date': end_date}

            query += " ORDER BY ts DESC;"
            
            result = conn.execute(text(query), params)
            # Each row is an object with accessible column names
            rows = result.fetchall()
            if not rows:
                logger.warning(f"Result is nonexisting")
                return []
            
            # Returning a list of dicts, gives more freedom under transformation step
            
            return [
                {
                    'ts': row.ts,
                    'value': row.value
                } 
                for row in rows
            ]
            
    except Exception as e:
        logger.error(f"Connection failed when extracting data: + {str(e)}")
        raise



    

# TRANSFORM FUNCTION
def transform_data(raw_data):
    '''
    Process data
    Args: 
        raw_data: List of dicts
            Example: [{ts: '2022-02-23 18:59:59+00', value: 256 }, ...]

    Returns:
        transformed_data: Array of the following deatils for every hour:
            timestamp (manipulated to remove minutes and lower measures of time),
            min_value,
            max_value,
            avg_value,
            readings_count
    '''

    hourly_data = defaultdict(list)
    
    for record in raw_data:
        value = record['value']

        # Skip invalid values
        if value is None or value == 0 or not math.isfinite(value):
            continue

        # Appends all values to the appropriate hour
        hour = record['ts'].replace(minute=0, second=0, microsecond=0)
        hourly_data[hour].append(record['value']/100) # Divide by 100 to get the real value 

    transformed_data = []

    for hour, values in hourly_data.items():
        transformed_data.append({
            'dt': hour,
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': round(sum(values) / len(values),2),
            'std_dev'  : round(statistics.stdev(values), 2),
            'readings_count': len(values)
        })

    return transformed_data
 
# LOAD FUNCTION
def load_data(transformed_data):
    '''Store in destination DB'''

    # The session represents a "holding zone"
    session = Session(agg_engine)
    try:
        for record in transformed_data:
            # Creating an ORM object matching the model for each row
            sensor_stat = AggSensorStats(
                sensor_name = SENSOR_OF_CHOICE,
                dt = record['dt'],
                min_value = record['min_value'],
                avg_value = record['avg_value'],
                max_value = record['max_value'],
                std_dev = record['std_dev'],
                readings_count = record['readings_count'],
                last_updated_at = datetime.now()
            )

            session.merge(sensor_stat)

        session.commit()

            
    except Exception as e:
        # Undo everything if something went wrong
        session.rollback()
        logger.error(f"Load of data failed: {str(e)}")
        
    finally:
        session.close()


 

# ORCHESTRATION
def run_etl(start_date=None, end_date=None):
    '''main function which combines all steps'''

    # TernaDetermine date range description
    if start_date is None and end_date is None:
        date_desc = "full backfill"
    elif end_date is not None:
        date_desc = f"from {start_date} to {end_date}"
    else:
        date_desc = f"only {start_date}"
    
    logger.info(f"Started ETL script for {date_desc}")
    
    try :
        raw_data = extract_data(start_date, end_date)
        if not raw_data:
            logger.warning(f"Could not find raw data.")
            return

        logger.info(f"Extracted raw data consisting of {len(raw_data)} records")
        
        transformed_data = transform_data(raw_data)
        logger.info(f"Transformed into {len(transformed_data)} hourly records.")
        
        load_data(transformed_data)
        logger.info(f"Succesfully loaded data.")
    except Exception as e:
        logger.error(f"Couldn't find data Received error: {str(e)}")
        raise # Ensures that the failure is not being swallowed silently. The caller can detect it and act accordingly



# When run directly from CLI, __name__ = "__main__"
# Parametrized execution
if __name__ == "__main__":

    # Logging - Tracks what happens at every step
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__) # Built in name given by python (related to filename)

    if len(sys.argv) == 2:
        start_date = sys.argv[1]
        run_etl(start_date)
    elif len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        run_etl(start_date, end_date)
    else:
        run_etl()
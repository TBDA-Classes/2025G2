'''
ETL (Extract, Transform and Load) script for tracking of TEMPERATURA BASE
'''

# IMPORTS

from tracemalloc import start
from typing import Any
import logging
import sys

from fastapi import HTTPException
from pydantic import BaseModel
from backend.database import prod_engine, agg_engine
from backend.models import AggSensorStats
from sqlalchemy import ExceptionContext, text
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
            {f"AND ts >= :start_date AND ts <= :start_date" 
            if start_date and end_date == None 
            else f"AND ts > :start_date AND ts < :end_date"}
            ORDER BY ts DESC;
            '''

            params = {'sensor_name' : SENSOR_OF_CHOICE, 'start_date' : start_date, 'end_date': end_date}
            result = conn.execute(text(query), params)
            # Each row is an object with accessible column names
            rows = result.fetchall()
            if not rows:
                raise HTTPException(status_code=404, detail="Temperatures not found")
            
            # Returning a list of dicts, gives more freedom under transformation step
            
            return [
                {
                    'ts': row.ts,
                    'value': row.value
                } 
                for row in rows
            ]

    except Exception as e:
        return {"Exception error " + f"Connection failed {str(e)}"}



    return raw_data

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
        # Appends all values to the appropriate hour
        hour = record['ts'].replace(minute=0, second=0, microsecond=0)
        hourly_data[hour].append(record['value'])

    transformed_data = []

    for hour, values in hourly_data.items():
        transformed_data.append({
            'dt': hour,
            'min_value': min(values),
            'max_value': max(values),
            'avg_value': sum(values) / len(values),
            'readings_count': len(values)
        })

    return transformed_data
 
# LOAD FUNCTION
def load_data(transformed_data):
    '''Store in destination DB'''

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
                readings_count = record['readings_count'],
                last_updated_at = datetime.now()
            )

            session.merge(sensor_stat)

        session.commit()

            
    except Exception as e:
        return {f"Conection failed with error message: {str(e)}"}
 

# ORCHESTRATION
def run_etl(start_date=None, end_date=None):
    '''main function which combines all steps'''

    # Parametrized Execution

    # simple ternary
    logger.info(f"Started ETL script for {'full backfill' if (start_date==None and end_date == None) else f"for {start_date} -> {end_date}."} ")
    
    try :
        raw_data = extract_data(start_date, end_date)
        if not raw_data:
            logger.warning(f"Could not find raw data {'.' if (start_date==None and end_date == None) else f"for {start_date} -> {end_date}."} ")
            return

        logger.info(f"Extracted raw data consisting of {len(raw_data)} records")
        
        transformed_data = transform_data(raw_data)
        logger.info(f"Transformed into {len(transformed_data)} hourly records.")
        
        load_data(transformed_data)
        logger.info(f"Succesfully loaded data.")
    except Exception as e:
        logger.error(f"Couldn't find data {'.' if (start_date==None and end_date == None) else f"for {start_date} -> {end_date}."} Received error: {str(e)}")
        raise # Ensures that the failure is not being swallowed silently. The caller can detect it and act accordingly



# When run directly from CLI, __name__ = "__main__"
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

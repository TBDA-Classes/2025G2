'''
ETL (Extract, Transform and Load) script for tracking of TEMPERATURA BASE
'''

# IMPORTS

from typing import Any


from fastapi import HTTPException
from pydantic import BaseModel
from backend.database import prod_engine, agg_engine
from backend.models import AggSensorStats
from sqlalchemy import ExceptionContext, text
from sqlalchemy.orm import Session
from datetime import datetime
from collections import defaultdict

TEMPERATURE_SENSOR = 'TEMPERATURA_BASE'

# EXTRACT FUNCTION
def extract_data():
    '''
    Query source DB
    '''
    try:
        with prod_engine.connect() as conn:
            
            # Simplified the query to only the two values of interest, date and value
            result = conn.execute(text('''
            SELECT vlf.value, 
                TO_TIMESTAMP(vlf.date/1000) AS ts, 
            FROM variable_log_float vlf
                LEFT JOIN variable v ON vlf.id_var = v.id
                WHERE v.name = 'TEMPERATURA_BASE'
            ORDER BY ts DESC;
            '''))
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
        hour = record['timestamp'].replace(minute=0, second=0, microsecond=0)
        hourly_data[hour].append(record['value'])

    transformed_data = []

    for hour, values in hourly_data.items():
        transform_data.append({
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
        for record in transform_data:
            # Creating an ORM object matching the model for each row
            sensor_stat = AggSensorStats(
                sensor_name = TEMPERATURE_SENSOR,
                dt = record['dt'],
                min_value = record['min_value'],
                avg_value = record['avg_value'],
                max_value = record['max_value'],
                recordings_count = record['recording_count'],
                last_updated_at = datetime.now()
            )

            session.merge(sensor_stat)

        session.commit()

            
    except Exception as e:
        return {f"Conection failed with error message: {str(e)}"}
 
# ORCHESTRATION
def run_etl():
    '''main function which combines all steps'''

    # Parametrized Execution

    # Logging and Error Handling

    raw_data = extract_data()
    transformed_data = load_data(raw_data)
    load_data(transformed_data)

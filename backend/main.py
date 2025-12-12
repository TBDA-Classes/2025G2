# Import the libraries we need
from typing import List, Optional 
from fastapi import FastAPI, HTTPException, Depends   
from fastapi.middleware.cors import CORSMiddleware 
from database import prod_engine, agg_engine, get_prod_db, get_agg_db
from pydantic import BaseModel
from models import Period
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import date as DateType

# Create our API app instance, with versioning
app = FastAPI(title="Variable Monitoring API", version="1.0.0")

# Allows our backend to be called from another domain.
# CORS = Cross-Origin Resource Sharing (security feature)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React typically runs on port 3000
    allow_methods=["GET"],  # Allow HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# We use BaseModel from pydantic to enforce and shape the GET response
class MachineActivityOut(BaseModel):
    date: str
    state_idle: int
    state_active: int
    state_running: int

class SensorStatsOut(BaseModel):
    dt: str
    min_value: Optional[float]
    avg_value: Optional[float]
    max_value: Optional[float]
    std_dev:   Optional[float]
    readings_count: Optional[int]

class MachineUtilOut(BaseModel):
    dt: str
    state_running: Optional[float]
    state_planned_down: Optional[float]
    running_percentage: Optional[float]
    down_percentage : Optional[float]

class DataStatusOut(BaseModel):
    table_name: str
    first_date: str
    last_date: str
    total_records: Optional[int]
    number_of_sensors: Optional[int]

class AlertsOut(BaseModel):
    alert_type: str
    unique_alarms: int
    total_occurrences: int

class MachineChangeOut(BaseModel):
    ts: str
    value: int

class MachineProgramOut(BaseModel):
    dt: str
    program: int
    duration_seconds: int

# When you visit http://localhost:8000/ you'll see this message
@app.get("/")
def home():
    return {"message": "Hello! The API is working!"}


# Test endpoint to check database connection
@app.get("/api/status")
def status():
    try:
        with prod_engine.connect() as connection:
            # Simply gives us the version information of POSTgreSQL
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            return {"status": "API is running", "database": "Connected", "version": str(version)}
    except Exception as e:
        return {"status": "API is running", "database": f"Connection failed: {str(e)}"}


# Up for removal ...
@app.get("/api/v1/machine_activity", response_model=List[MachineActivityOut])
def get_machine_activity(
    target_date: DateType,
    db: Session = Depends(get_prod_db)
    ):
    """
    Get the number of hours of which machine was in each state on the given date.

    Args:
        db: Database Session
        target_date: The date of interest, format: "2021-01-15"
    Returns:
        List of MachineActivityOut objects
    """

    # Using the text() property of SQLAlchemy since it is too complicated to translate
    # the generate_series() function is inclusive, so the end time is 23.
    # We use SQLAlchemy's placeholder syntax, :parameter
    query = text("""
        WITH horas AS (
        SELECT dt
        FROM (
            SELECT generate_series(
                CAST(:target_date AS date) + interval '0 hours',
                CAST(:target_date AS date) + interval '23 hours',
                interval '1 hour'
            ) AS dt
        ) sub
        WHERE EXTRACT(DOW FROM dt) NOT IN (0, 6)  -- weekdays only
        ),
        cambios_por_hora AS (
            SELECT
                to_timestamp(
                    ROUND((TRUNC(CAST(date AS bigint) / 1000) / 3600)) * 3600
                ) AS dt,
                COUNT(DISTINCT id_var) AS total_variables
            FROM public.variable_log_float
            WHERE to_timestamp(TRUNC(CAST(date AS bigint) / 1000)) >= CAST(:target_date AS date)
            AND to_timestamp(TRUNC(CAST(date AS bigint) / 1000)) <  CAST(:target_date AS date) + interval '1 day'
            GROUP BY dt
        ),
        clasificado AS (
            SELECT
                h.dt,
                h.dt::date AS date,
                COALESCE(c.total_variables, 0) AS total_variables,
                CASE
                    WHEN COALESCE(c.total_variables, 0) = 0 THEN 'Máquina parada'
                    WHEN COALESCE(c.total_variables, 0) <= 80 THEN 'Actividad media'
                    ELSE 'Máquina en operación'
                END AS estado
            FROM horas h
            LEFT JOIN cambios_por_hora c ON h.dt = c.dt
        )
        SELECT
            date,
            COUNT(*) FILTER (WHERE estado = 'Actividad media')       AS active,
            COUNT(*) FILTER (WHERE estado = 'Máquina en operación')  AS operating,
            COUNT(*) FILTER (WHERE estado = 'Máquina parada')        AS idle
        FROM clasificado
        GROUP BY date
        ORDER BY date;
    """)

    try:
        # Executing with parameters prevents SQL injections because the input is treated as a data value, not SQL code.
        result = db.execute(query, {"target_date": str(target_date)})
        data = result.fetchall()

        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {target_date}")
        return[
            MachineActivityOut(
                date=str(row.date), 
                state_idle=row.idle, 
                state_active=row.active, 
                state_running=row.operating
            ) 
            for row in data
        ]
    except HTTPException: # Catch the 404 and re-raise
        raise
    except Exception as e: # Catches (almost) any other error
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    

@app.get("/api/v1/temperature", response_model=List[SensorStatsOut])
def get_temperature_stats(
    target_date: DateType,
    sensor_name: str = "",
    db: Session = Depends(get_agg_db)
):
    """
    Returns aggregated temperature statistics (min/avg/max/count) for a given sensor
    on a specific date. Uses the agg_sensor_stats materialized table.
    """

    query = text("""
        SELECT 
            dt,
            min_value,
            avg_value,
            max_value,
            std_dev,
            readings_count
        FROM agg_sensor_stats a
        WHERE a.dt::date = :target_date
        AND a.sensor_name = :sensor_name
        ORDER BY dt ASC
    """)

    try:
        rows = db.execute(query, {
            "target_date": str(target_date),
            "sensor_name": sensor_name
        }).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No temperature data found for {sensor_name} on {target_date}"
            )

        return [
            SensorStatsOut(
                dt=str(r.dt),
                min_value=r.min_value,
                avg_value=r.avg_value,
                max_value=r.max_value,
                std_dev  =r.std_dev,
                readings_count=r.readings_count
            )
            for r in rows
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@app.get('/api/v1/machine_util', response_model=List[MachineUtilOut])
def get_machine_util(
    target_date: DateType,
    db: Session = Depends(get_agg_db)
    ):

    params = {
        'target_date': target_date
        }
    query = text('''SELECT
    dt,
    state_planned_down,
    state_running,
    running_percentage,
    down_percentage
    FROM agg_machine_activity_daily
    WHERE dt = :target_date
    ORDER BY dt ASC;

    ''')

    try:
        
        rows = db.execute(query, params).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No temperature data found for machine utilization {target_date}"
            )
        return [
            MachineUtilOut(
            dt= str(row.dt),
            state_running = row.state_running,
            state_planned_down = row.state_planned_down,
            running_percentage = row.running_percentage,
            down_percentage = row.down_percentage,

            ) for row in rows
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")





@app.get("/api/v1/data_status", response_model=List[DataStatusOut])
def get_data_status(
db : Session = Depends(get_agg_db)
):
    query = '''
    SELECT
    table_name,
    first_date,
    last_date,
    total_records,
    number_of_sensors
    FROM v_data_status;
    '''
    try:

        rows = db.execute(text(query)).fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail=f"No data found")
        
        else:
            return[DataStatusOut(
                table_name= r.table_name,
                first_date= str(r.first_date),
                last_date= str(r.last_date),
                total_records= r.total_records,
                number_of_sensors= r.number_of_sensors
            ) for r in rows
            ]

    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/api/v1/alerts", response_model=List[AlertsOut])
def get_alerts(
    target_date: DateType,
    db: Session = Depends(get_prod_db)
):
    """
    Get alert counts categorized by type (Emergency, Error, Alert, Other) for a given date.

    Args:
        db: Database Session
        target_date: The date of interest, format: "2022-02-23"
    Returns:
        List of AlertsOut objects with alert_type, unique_alarms, and total_occurrences
    """

    query = text("""
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
              AND to_timestamp(a.date / 1000)::date = :target_date
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
            COUNT(DISTINCT alarm_code) AS unique_alarms,
            COUNT(*) AS total_occurrences
        FROM categorized
        GROUP BY alert_type
        ORDER BY alert_type;
    """)

    try:
        result = db.execute(query, {"target_date": str(target_date)})
        data = result.fetchall()

        if not data:
            raise HTTPException(status_code=404, detail=f"No alert data found for {target_date}")
        
        return [
            AlertsOut(
                alert_type=row.alert_type,
                unique_alarms=row.unique_alarms,
                total_occurrences=row.total_occurrences
            )
            for row in data
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@app.get("/api/v1/machine_changes", response_model=List[MachineChangeOut])
def get_machine_changes(
    start: str,
    end: str,
    db: Session = Depends(get_prod_db)
):
    """
    Returns only the timestamp where MACHINE_IN_OPERATION changes value.

    Params:
        start: datetime string, e.g. '2022-01-30 15:00:00'
        end:   datetime string, e.g. '2022-01-30 15:30:00'
    """

    query = text("""
    SELECT to_timestamp(vlf.date/1000) AS ts,
    vlf.value
    FROM variable_log_float vlf
    WHERE vlf.id_var=597
    AND to_timestamp(vlf.date/1000) BETWEEN CAST(:start AS timestamp) AND CAST(:end AS timestamp);
    """)
   

    try:
        rows = db.execute(query, {
            "start": start,
            "end": end
        }).fetchall()

        return [
            MachineChangeOut(
                ts=str(r.ts),
                value = r.value
            )
            for r in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/v1/machine_program", response_model=List[MachineProgramOut])
def get_machine_program(
    target_date: DateType,
    db: Session = Depends(get_agg_db)
):
    """
    Get machine program usage data for a given date.
    Returns program numbers and their duration in seconds.

    Args:
        target_date: The date of interest, format: "2021-01-15"
    Returns:
        List of MachineProgramOut objects with program and duration_seconds
    """

    query = text("""
        SELECT 
            dt,
            program,
            duration_seconds
        FROM machine_program_data
        WHERE dt = :target_date
        ORDER BY duration_seconds DESC;
    """)

    try:
        rows = db.execute(query, {"target_date": str(target_date)}).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No program data found for {target_date}"
            )

        return [
            MachineProgramOut(
                dt=str(r.dt),
                program=r.program,
                duration_seconds=r.duration_seconds
            )
            for r in rows
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

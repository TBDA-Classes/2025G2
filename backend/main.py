# Import the libraries we need
from typing import List, Optional 
from fastapi import FastAPI, HTTPException, Depends   
from fastapi.middleware.cors import CORSMiddleware 
from database import prod_engine, get_prod_db, get_agg_db
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    first_date: str
    last_date: str
    sensor_records: int
    utilization_records: int
    alert_records: int
    program_records: int
    energy_records: int


class MachineChangeOut(BaseModel):
    ts: str
    value: int

class MachineProgramOut(BaseModel):
    dt: str
    program: int
    duration_seconds: int

class AlertsDailyCountOut(BaseModel):
    day: str
    alert_type: str
    amount: int

class AlertsDetailOut(BaseModel):
    id: int
    dt: str
    alert_type: str
    alarm_code: Optional[str]
    alarm_description: Optional[str]


class EnergyConsumptionOut(BaseModel):
    hour_ts: str
    energy_kwh: float

# When you visit http://localhost:8000/ you'll see this message
@app.get("/")
def home():
    return {"message": "Hello! The API is working!"}


# Test endpoint to check database connection
@app.get("/api/status")
def status():
    """
    Health check endpoint for the API and database connection.
    
    Returns:
        Status message with database version if connected.
    """
    try:
        with prod_engine.connect() as connection:
            # Simply gives us the version information of POSTgreSQL
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            return {"status": "API is running", "database": "Connected", "version": str(version)}
    except Exception as e:
        return {"status": "API is running", "database": f"Connection failed: {str(e)}"}

@app.get("/api/v1/temperature", response_model=List[SensorStatsOut])
def get_temperature_stats(
    target_date: DateType,
    sensor_name: str = "",
    db: Session = Depends(get_agg_db)
):
    """
    Hourly temperature statistics for a sensor on a given day.
    
    Params:
        target_date: Date to query, e.g. "2021-09-14"
        sensor_name: Name of the sensor, e.g. "TEMPERATURA_BASE"
    
    Returns:
        List of hourly stats with min, avg, max, std_dev, and reading count.
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
    """
    Daily machine utilization summary showing running vs. downtime hours.
    
    Params:
        target_date: Date to query, e.g. "2021-09-14"
    
    Returns:
        Running hours, downtime hours, and their percentages for the day.
    """
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
                detail=f"No utilization data found for {target_date}"
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





@app.get("/api/v1/data_status", response_model=DataStatusOut)
def get_data_status(
    db: Session = Depends(get_agg_db)
):
    """
    Overview of available data across all aggregated tables.
    
    Returns:
        Global date range (min/max across all tables) and record counts per table.
    """
    query = '''
    SELECT
        first_date,
        last_date,
        sensor_records,
        utilization_records,
        alert_records,
        program_records,
        energy_records
    FROM v_data_status;
    '''
    try:
        row = db.execute(text(query)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="No data found")
        
        return DataStatusOut(
            first_date=str(row.first_date),
            last_date=str(row.last_date),
            sensor_records=row.sensor_records,
            utilization_records=row.utilization_records,
            alert_records=row.alert_records,
            program_records=row.program_records,
            energy_records=row.energy_records
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/api/v1/machine_changes", response_model=List[MachineChangeOut])
def get_machine_changes(
    start: str,
    end: str,
    db: Session = Depends(get_prod_db)
):
    """
    Machine operation state changes within a time window (variable id=597).
    Used to render the operational timeline chart.
    
    Params:
        start: Start of time window, e.g. "2022-01-30 15:00:00+00:00"
        end:   End of time window, e.g. "2022-01-30 15:30:00+00:00"
    
    Returns:
        Timestamps and values (255=running, 0=idle) for each state change.
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
    Program usage breakdown for a given day, sorted by duration.
    
    Params:
        target_date: Date to query, e.g. "2021-09-14"
    
    Returns:
        Each program number (P0, P1, etc.) and how long it ran in seconds.
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


@app.get("/api/v1/alerts_daily_count", response_model=List[AlertsDailyCountOut])
def get_alerts_daily_count(
    target_date: DateType,
    db: Session = Depends(get_agg_db)
):
    """
    Summary count of alerts by category for a given day.
    
    Params:
        target_date: Date to query, e.g. "2021-09-14"
    
    Returns:
        Count per alert type (emergency, error, warning, other).
    """

    query = text("""
        SELECT 
            day,
            alert_type,
            amount
        FROM alerts_daily_count
        WHERE day = :target_date
        ORDER BY amount DESC;
    """)

    try:
        rows = db.execute(query, {"target_date": str(target_date)}).fetchall()

        if not rows:
            return []  # Return empty list if no alerts for this date

        return [
            AlertsDailyCountOut(
                day=str(r.day),
                alert_type=r.alert_type,
                amount=r.amount
            )
            for r in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/v1/alerts_detail", response_model=List[AlertsDetailOut])
def get_alerts_detail(
    target_date: DateType,
    db: Session = Depends(get_agg_db)
):
    """
    Individual alert records for a given day, ordered chronologically.
    
    Params:
        target_date: Date to query, e.g. "2021-09-14"
    
    Returns:
        Each alert with timestamp, type, alarm code, and description.
    """

    query = text("""
        SELECT 
            id,
            dt,
            alert_type,
            alarm_code,
            alarm_description
        FROM alerts_detail
        WHERE day = :target_date
        ORDER BY dt ASC;
    """)

    try:
        rows = db.execute(query, {"target_date": str(target_date)}).fetchall()

        if not rows:
            return []  # Return empty list if no alerts for this date

        return [
            AlertsDetailOut(
                id=r.id,
                dt=str(r.dt),
                alert_type=r.alert_type,
                alarm_code=r.alarm_code,
                alarm_description=r.alarm_description
            )
            for r in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/v1/energy_consumption", response_model=List[EnergyConsumptionOut])
def get_energy_consumption(
    target_date: DateType,
    db: Session = Depends(get_agg_db)
):
    """
    Hourly energy consumption for a given day.
    
    Params:
        target_date: Date to query, e.g. "2022-02-23"
    
    Returns:
        List of hourly records with timestamp and energy in kWh.
    """

    query = text("""
        SELECT 
            hour_ts,
            energy_kwh
        FROM energy_consumption_hourly
        WHERE hour_ts::date = :target_date
        ORDER BY hour_ts ASC;
    """)

    try:
        rows = db.execute(query, {"target_date": str(target_date)}).fetchall()

        if not rows:
            return []

        return [
            EnergyConsumptionOut(
                hour_ts=str(r.hour_ts),
                energy_kwh=float(r.energy_kwh)
            )
            for r in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
# Import the libraries we need
from typing import List, Optional 
from fastapi import FastAPI, HTTPException, Depends   
from fastapi.middleware.cors import CORSMiddleware 
from database import engine, get_db
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
class PeriodOut(BaseModel):
    id: int
    name: str

class MachineActivityOut(BaseModel):
    date: str
    state_idle: int
    state_active: int
    state_running: int


# When you visit http://localhost:8000/ you'll see this message
@app.get("/")
def home():
    return {"message": "Hello! The API is working!"}


# Test endpoint to check database connection
@app.get("/api/status")
def status():
    try:
        with engine.connect() as connection:
            # Simply gives us the version information of POSTgreSQL
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            return {"status": "API is running", "database": "Connected", "version": str(version)}
    except Exception as e:
        return {"status": "API is running", "database": f"Connection failed: {str(e)}"}


# Our first realistic endpoint (for testing purposes)
@app.get("/api/v1/periods", response_model=List[PeriodOut])
def get_period(db: Session = Depends(get_db)):
    """
    Get all periods from the database using ORM

    Args:
        db: Database session (automatically provided by FastAPI via Depends)

    Returns:
        List of PeriodOut objects
    """
    # Using a Period object the SQL is abstracted away
    periods = db.query(Period).order_by(Period.id).all()
    if not periods:
        raise HTTPException(status_code=404, detail="Period(s) not found")
    return [PeriodOut(id=p.id, name=p.name) for p in periods]



@app.get("/api/v1/machine_activity", response_model=List[MachineActivityOut])
def get_machine_activity(
    target_date: DateType,
    db: Session = Depends(get_db)
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
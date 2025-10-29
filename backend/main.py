# Import the libraries we need
from typing import List, Optional 
from fastapi import FastAPI, HTTPException, Depends   
from fastapi.middleware.cors import CORSMiddleware 
from database import engine, text, get_db
from pydantic import BaseModel
from models import Period
from sqlalchemy.orm import Session
from sqlalchemy import func

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

# SELECT vf.value, TO_TIMESTAMP(vf.date/1000), v.name, v.datatype, units.prettyname 
# FROM variable_log_float vf 
# LEFT JOIN variable v ON vf.id_var = v.id 
# LEFT JOIN units ON units.name = v.name 
# WHERE v.name = 'MACHINE_IN_OPERATION';


class DateStatusOut(BaseModel):
    date: int
    running_hours: float
    planned_downtime: float
    unplanned_downtime: float



# Our first endpoint - just to test if the API is working
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
    periods = db.query(Period).order_by(Period.id).all()
    if not periods:
        raise HTTPException(status_code=404, detail="Period(s) not found")
    return [PeriodOut(id=p.id, name=p.name) for p in periods]


#@app.get("/api/v1/total_status", response_model=List[DateStatusOut])
#def get_date_status_out(db: Session = Depends(get_db)):
    """
    For each every date in a time interval, fetch
    1) The hours where the machine was executing a program (variable.name = MACHINE_IN_OPERATION)
    2) The unplanned downtime, when machine emergency pulsed (variable.name = MACHINE_EMERGENCY)
    3) The planned downtime, when the NC STOP active (variable.name = MACHINE_STOP_ACTIVE)

    Args:
        db: Database session
    Returns:
        List of DateStatusOut objects
        
    """

    #We need to:
    # Define from_ts and to_ts (either as parameters or hard coded in the query)
    # Normalize the signals to 0/1 for tracking true/false (some values contain 255, NaN etc.)
    # Build an event stream (track changes in the logs)
    # Compute duration
    # Sum hours to find total up- and downtime



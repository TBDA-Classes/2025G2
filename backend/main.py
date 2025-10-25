# Import the libraries we need
from typing import List, Optional 
from fastapi import FastAPI, HTTPException, Depends   
from fastapi.middleware.cors import CORSMiddleware 
from database import engine, text, get_db
from pydantic import BaseModel
from models import Period
from sqlalchemy.orm import Session

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
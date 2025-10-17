# Import the libraries we need
#from logging import raiseExceptions
#from sys import version
from typing import List, Optional 
from fastapi import FastAPI, HTTPException         
from fastapi.middleware.cors import CORSMiddleware 
from database import engine
from database import text
from pydantic import BaseModel

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
def get_period():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, name FROM public.periods ORDER BY id")
        )
        rows = result.mappings().all()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Period(s) not found")
        
        # **row Unpacks the dictionary (key becomes parameter, value becomes argument)
        return [PeriodOut(**row) for row in rows]

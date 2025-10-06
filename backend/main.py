# Import the libraries we need
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create our API application
# Think of this as creating a new website/service
app = FastAPI(title="Variable Monitoring API")

# Allow our React frontend to talk to this backend
# CORS = Cross-Origin Resource Sharing (security feature)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React typically runs on port 3000
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Our first endpoint - just to test if the API is working
# When you visit http://localhost:8000/ you'll see this message
@app.get("/")
def home():
    return {"message": "Hello! The API is working!"}


# Test endpoint to check database connection
@app.get("/api/status")
def status():
    return {"status": "API is running", "database": "Not connected yet"}


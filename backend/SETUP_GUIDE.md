# Setup Guide - Step by Step

Here is a quick tour to set up the application on your device.

## What We're Building
A web application with:
- **Backend (FastAPI)**: Python server that talks to the PostgreSQL database
- **Frontend (Next.js - React)**: User interface that runs in the browser

---

## Step 1: Backend Setup

### What we have so far:
1. **requirements.txt** - List of Python packages we need
2. **env_example.txt** - Database credentials template
3. **main.py** - A simple API with 2 test endpoints

### How to run it:

#### 1. Create a virtual environment (keeps packages organized)
```bash
cd backend
python3 -m venv venv
```

#### 2. Activate the virtual environment
**On Mac/Linux:**
```bash
source venv/bin/activate
```

#### 3. Install the required packages
```bash
pip install -r requirements.txt
```

#### 4. Create your .env file
```bash
cp env_example.txt .env
```

#### 5. Run the server
```bash
uvicorn main:app --reload
```

#### 6. Test it!
Open your browser and go to:
- http://localhost:8000 - Should see a welcome message
- http://localhost:8000/docs - Interactive API documentation (automatically generated!)

---


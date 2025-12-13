BACKEND OVERVIEW
================

Introduction
------------
The backend is implemented using **FastAPI** and relies on:

* SQLAlchemy as ORM (Object-Relational Mapper) 
* psycopg3 as PostgreSQL driver  
* python-dotenv for configuration  
* Custom ETL scripts for data aggregation

This layer provides the REST API consumed by the frontend and manages
communication with both the production database and the aggregation database.

Backend File Structure
----------------------
::

   backend/
   ├── main.py                             # FastAPI application and endpoints
   ├── models.py                           # SQLAlchemy ORM models
   ├── database.py                         # Database connection configuration
   ├── env_example.txt                     # Environment variables template
   ├── requirements.txt                    # Python dependencies
   ├── scripts/
   │   ├── create_agg_database.sql         # Schema for aggregation DB
   │   ├── etl_agg_utilization.py          # Temperature statistics
   │   └── etl_agg_sensor_stats.py         # Machine utilization
   │   └── etl_agg_program_history.py      # Program durations
   │   └── etl_agg_alerts.py               # Alert aggregation
   │   └── etl_agg_energy_daily.py         # Energy consumption
   │   └── etl_agg_daily_runner.py         # Orchestrates all ETLs
   └── README.md


Database Driver
---------------
The system uses psycopg3, a modern driver for PostgreSQL with support for both
synchronous and asynchronous execution. This allows:

* Better performance under concurrent requests  
* Compatibility with SQLAlchemy  
* Efficient ETL execution  


Environment Variables
---------------------
Sensitive configuration parameters (usernames, passwords, hosts, ports) are stored in
a `.env` file. A simplified example:

::

   DB_USER=atle
   DB_PASSWORD=secretpassword
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=mydatabase

The file is loaded via ``python-dotenv`` and accessed using ``os.getenv()``.


Running the Backend
-------------------
Step-by-step setup:

::

   cd backend
   python3 -m venv venv
   source venv/bin/activate         # macOS/Linux
   venv\Scripts\activate            # Windows
   pip install -r requirements.txt
   cp env_example.txt .env
   uvicorn main:app --reload

Testing:

* http://localhost:8000  
* http://localhost:8000/docs


API Endpoints
-------------------------
All endpoints are prefixed with `/api/v1/`:

* `/temperatures` - Temperature statistics by time bucket
* `/machine_util` - Daily utilization (running vs downtime)
* `/machine_changes` - State timeline for a time window
* `/machine_program` - Program durations per day
* `/energy_consumption` - Hourly energy data
* `/alerts_daily_count` - Alerts count by type
* `/alerts_detail` - Individual alert records
* `/data_status` - Available date range and record counts 

See also the :doc:`frontend` page for how the API integrates with the UI.
See also the :doc:`code` page for detailed backend code structure.
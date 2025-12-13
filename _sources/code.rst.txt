CODE REFERENCE
==============

This page centralizes the most relevant source code used in the project.  
The codebase is divided into two clearly differentiated categories:

- **Backend Scripts**: standalone scripts responsible for ETL processes and
  batch aggregation tasks.
- **Core Backend Code**: reusable infrastructure and data models used by the
  backend services and APIs.

This separation helps distinguish between *operational logic* (scripts) and
*structural logic* (core code).

---

Backend Scripts
---------------

This section documents backend scripts used to populate and maintain the
aggregation database. These scripts are typically executed manually or through
scheduled jobs and are not part of the request–response API flow.


Aggregation Database Creation Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**File:** ``create_agg_database.sql``

This script creates all tables, indexes, and views required for the aggregation
database.

**Execution example**:

.. code-block:: bash

   psql machine_monitoring_agg -f create_agg_database.sql

---

**Daily Machine Activity Aggregation**

.. code-block:: sql
   :linenos:

   CREATE TABLE IF NOT EXISTS agg_machine_activity_daily (
       dt DATE PRIMARY KEY,
       state_planned_down NUMERIC DEFAULT 0,
       state_running NUMERIC DEFAULT 0,
       state_unplanned_down NUMERIC DEFAULT 0,
       running_percentage NUMERIC
           GENERATED ALWAYS AS (
               ROUND((state_running / 24) * 100, 2)
           ) STORED,
       down_percentage NUMERIC
           GENERATED ALWAYS AS (
               ROUND((state_planned_down / 24) * 100, 2)
           ) STORED,
       last_updated_at TIMESTAMP DEFAULT NOW()
   );

---

**Aggregated Sensor Statistics**

.. code-block:: sql
   :linenos:

   CREATE TABLE IF NOT EXISTS agg_sensor_stats (
       sensor_name VARCHAR(100),
       dt TIMESTAMP,
       min_value FLOAT,
       avg_value FLOAT,
       max_value FLOAT,
       std_dev FLOAT,
       readings_count INT,
       last_updated_at TIMESTAMP DEFAULT NOW(),
       PRIMARY KEY (sensor_name, dt)
   );

---

**Alerts and Utilization Tables**

.. code-block:: sql
   :linenos:

   CREATE TABLE IF NOT EXISTS alerts_daily_count(
       day DATE NOT NULL,
       alert_type VARCHAR(20) NOT NULL
           CHECK(alert_type IN ('emergency', 'error', 'warning', 'other')),
       amount INT NOT NULL,
       PRIMARY KEY (day, alert_type)
   );

   CREATE TABLE IF NOT EXISTS alerts_detail(
       id SERIAL PRIMARY KEY,
       dt TIMESTAMP NOT NULL,
       day DATE GENERATED ALWAYS AS (dt::date) STORED,
       alert_type VARCHAR(20) NOT NULL
           CHECK(alert_type IN ('emergency', 'error', 'warning', 'other')),
       alarm_code TEXT,
       alarm_description TEXT,
       raw_elem_json JSONB
   );

---

**Views**

.. code-block:: sql
   :linenos:

   CREATE OR REPLACE VIEW v_data_status AS
   SELECT
       'agg_sensor_stats' AS table_name,
       MIN(dt) AS first_date,
       MAX(dt) AS last_date,
       COUNT(*) AS total_records,
       COUNT(DISTINCT sensor_name) AS number_of_sensors,
       MAX(last_updated_at) AS last_updated
   FROM agg_sensor_stats;

---
- Alerts Aggregation ETL Script**

**File:** ``etl_agg_alerts.py``

This script performs an **ETL (Extract, Transform, Load)** process for machine
alerts data. It extracts raw alert information from the production database,
processes and categorizes it, and loads both aggregated and detailed results
into the aggregation database.

It populates the following tables:

- ``alerts_daily_count`` – daily alert counts grouped by type
- ``alerts_detail`` – detailed records for critical alerts (emergency and error)

**Execution examples**:

.. code-block:: bash

   python -m backend.scripts.etl_agg_alerts 2022-02-23
   python -m backend.scripts.etl_agg_alerts 2022-02-01 2022-02-28

If no dates are provided, the script performs a full historical backfill.

---

**Alert Type Mapping**

Alert descriptions are normalized into standardized alert categories.

.. code-block:: python
   :linenos:

   ALERT_TYPE_MAP = {
       'Emergency': 'emergency',
       'Error': 'error',
       'Alert': 'warning',
       'Other': 'other',
   }

---

**Date Range Resolution (Full Backfill)**

When no dates are provided, the script queries the source database to determine
the minimum and maximum available dates.

.. code-block:: python
   :linenos:

   def get_date_range():
       with prod_engine.connect() as conn:
           query = '''
           SELECT 
               MIN(to_timestamp(date / 1000))::date AS min_date,
               MAX(to_timestamp(date / 1000))::date AS max_date
           FROM variable_log_string
           WHERE id_var = 447
             AND value IS NOT NULL
             AND value != '[]'
           '''
           result = conn.execute(text(query))
           row = result.fetchone()
           if row and row.min_date and row.max_date:
               return str(row.min_date), str(row.max_date)
           return None, None

---

**Daily Alert Count Extraction**

Extracts daily alert counts grouped by alert type from the production database.

.. code-block:: python
   :linenos:

   def extract_daily_count(target_date):
       with prod_engine.connect() as conn:
           query = ''' SQL QUERY OMITTED FOR BREVITY '''
           result = conn.execute(text(query), {'target_date': target_date})
           rows = result.fetchall()

           return [
               {
                   'day': target_date,
                   'alert_type': ALERT_TYPE_MAP.get(row.alert_type),
                   'amount': row.total_occurrences
               }
               for row in rows
               if row.alert_type in ALERT_TYPE_MAP
           ]

---

**Alert Details Extraction**

Extracts detailed alert records for **Emergency** and **Error** alerts only.

.. code-block:: python
   :linenos:

   def extract_details(target_date):
       with prod_engine.connect() as conn:
           query = ''' SQL QUERY OMITTED FOR BREVITY '''
           result = conn.execute(text(query), {'target_date': target_date})
           rows = result.fetchall()

           return [
               {
                   'dt': row.ts,
                   'alert_type': ALERT_TYPE_MAP.get(row.alert_type),
                   'alarm_code': row.alarm_code,
                   'alarm_description': row.alarm_description,
                   'raw_elem_json': json.loads(row.raw_elem_json)
                   if row.raw_elem_json else None
               }
               for row in rows
               if row.alert_type in ALERT_TYPE_MAP
           ]

---

**Load – Daily Alert Counts**

Stores aggregated daily alert counts in the destination database using
**upsert** semantics.

.. code-block:: python
   :linenos:

   def load_daily_count(data):
       session = Session(agg_engine)
       try:
           for record in data:
               session.merge(AlertsDailyCount(**record))
           session.commit()
           return len(data)
       finally:
           session.close()

---

**Load – Alert Details**

Stores detailed alert records in the aggregation database.

.. code-block:: python
   :linenos:

   def load_details(data):
       session = Session(agg_engine)
       try:
           for record in data:
               session.add(AlertsDetail(**record))
           session.commit()
           return len(data)
       finally:
           session.close()

---

**ETL Orchestration**

Coordinates extraction, transformation, and loading over a date range.

.. code-block:: python
   :linenos:

   def run_etl(start_date=None, end_date=None):
       # Determines date range
       # Iterates day by day
       # Executes extract + load steps
       # Logs progress and failures

---

**Command-Line Entry Point**

Allows execution as a standalone script or module.

.. code-block:: python
   :linenos:

   if __name__ == "__main__":
       logging.basicConfig(level=logging.INFO)
       logger = logging.getLogger(__name__)

       if len(sys.argv) == 2:
           run_etl(sys.argv[1])
       elif len(sys.argv) == 3:
           run_etl(sys.argv[1], sys.argv[2])
       else:
           run_etl()

---
Machine Program History ETL Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``etl_agg_program_history.py``

This script performs an **ETL (Extract, Transform, Load)** process to compute
machine program execution history. It extracts raw machine state changes from
the production database and calculates the execution duration of each program
per day.

The results are stored in the aggregation database table:

- ``machine_program_data`` 

The script supports single-day execution**, date ranges**, and full
historical backfills.

**Execution examples**:

.. code-block:: bash

   python -m backend.scripts.etl_agg_program_history 2021-01-07
   python -m backend.scripts.etl_agg_program_history 2021-01-01 2021-01-31

---

**Date Range Resolution (Full Backfill)**

When no dates are provided, the script determines the minimum and maximum
available dates directly from the source data.

.. code-block:: python
   :linenos:

   def get_date_range():
       with prod_engine.connect() as conn:
           query = '''
           SELECT 
               MIN(to_timestamp(trunc(cast(date AS bigint)/1000)))::date AS min_date,
               MAX(to_timestamp(trunc(cast(date AS bigint)/1000)))::date AS max_date
           FROM variable_log_float
           WHERE id_var = 581
             AND value >= 0 AND value < 1000
           '''
           result = conn.execute(text(query))
           row = result.fetchone()
           if row and row.min_date and row.max_date:
               return str(row.min_date), str(row.max_date)
           return None, None

---

**Program History Extraction**

Extracts machine program execution intervals and computes the total duration
(in seconds) of each program per day.

.. code-block:: python
   :linenos:

   def extract_data(start_date=None, end_date=None):
       with prod_engine.connect() as conn:
           query = ''' SQL QUERY OMITTED FOR BREVITY '''
           params = {
               'start_date': start_date,
               'end_date': end_date if end_date else start_date
           }
           result = conn.execute(text(query), params)
           rows = result.fetchall()

           return [
               {
                   'dt': row.fecha,
                   'program': row.estado_numerico,
                   'duration_seconds': int(row.duracion_segundos)
               }
               for row in rows
           ]

---

**Load – Machine Program Data**

Stores aggregated program execution durations into the aggregation database.

.. code-block:: python
   :linenos:

   def load_data(transformed_data):
       session = Session(agg_engine)
       try:
           for record in transformed_data:
               program_data = MachineProgramData(
                   dt=record['dt'],
                   program=record['program'],
                   duration_seconds=record['duration_seconds']
               )
               session.add(program_data)
           session.commit()
       finally:
           session.close()

---

**ETL Orchestration**

Coordinates extraction and loading steps for the selected date range.

.. code-block:: python
   :linenos:

   def run_etl(start_date=None, end_date=None):
       # Resolves date range
       # Extracts raw program history
       # Loads aggregated results
       # Logs progress and errors

---

**Command-Line Entry Point**

Allows execution as a standalone script or module.

.. code-block:: python
   :linenos:

   if __name__ == "__main__":
       logging.basicConfig(level=logging.INFO)
       logger = logging.getLogger(__name__)

       if len(sys.argv) == 2:
           run_etl(sys.argv[1])
       elif len(sys.argv) == 3:
           run_etl(sys.argv[1], sys.argv[2])
       else:
           run_etl()
---
Sensor Statistics ETL Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``etl_agg_sensor_stats.py``

This script performs an **ETL (Extract, Transform, Load)** process to compute
hourly statistics for a specific machine sensor, currently configured for
``TEMPERATURA_BASE``.

Raw high-frequency sensor readings are extracted from the production database,
aggregated on an hourly basis, and stored in the aggregation database table:

- ``agg_sensor_stats`` 

The script supports single-day execution, date ranges, and full
historical backfills.

**Execution examples**:

.. code-block:: bash

   python -m backend.scripts.etl_agg_sensor_stats 2021-01-07
   python -m backend.scripts.etl_agg_sensor_stats 2021-01-01 2021-01-31

---

**Sensor Configuration**

The ETL process is parameterized by a single sensor name. At present, the
script focuses on the base temperature sensor.

.. code-block:: python
   :linenos:

   SENSOR_OF_CHOICE = 'TEMPERATURA_BASE'

---

**Sensor Data Extraction**

Extracts raw sensor readings (timestamp and value) from the production
database, optionally filtered by date or date range.

.. code-block:: python
   :linenos:

   def extract_data(start_date, end_date):
       with prod_engine.connect() as conn:
           query = '''
           SELECT vlf.value,
                  TO_TIMESTAMP(vlf.date/1000) AS ts
           FROM variable_log_float vlf
           LEFT JOIN variable v ON vlf.id_var = v.id
           WHERE v.name = :sensor_name
           '''
           # Optional date filters applied dynamically

---

**Data Transformation (Hourly Aggregation)**

Groups raw sensor readings by hour and computes statistical metrics for each
hourly interval.

The following values are calculated:

- minimum value
- maximum value
- average value
- standard deviation
- number of valid readings

Invalid or non-finite sensor values are discarded.

.. code-block:: python
   :linenos:

   def transform_data(raw_data):
       hourly_data = defaultdict(list)

       for record in raw_data:
           value = record['value']
           if value is None or value == 0 or not math.isfinite(value):
               continue

           hour = record['ts'].replace(minute=0, second=0, microsecond=0)
           hourly_data[hour].append(record['value'] / 100)

---

**Load – Aggregated Sensor Statistics**

Stores the computed hourly statistics into the aggregation database using
**upsert semantics** to avoid duplicate entries.

.. code-block:: python
   :linenos:

   def load_data(transformed_data):
       session = Session(agg_engine)
       try:
           for record in transformed_data:
               sensor_stat = AggSensorStats(
                   sensor_name=SENSOR_OF_CHOICE,
                   dt=record['dt'],
                   min_value=record['min_value'],
                   avg_value=record['avg_value'],
                   max_value=record['max_value'],
                   std_dev=record['std_dev'],
                   readings_count=record['readings_count'],
                   last_updated_at=datetime.now()
               )
               session.merge(sensor_stat)
           session.commit()
       finally:
           session.close()

---

**ETL Orchestration**

Coordinates the extract, transform, and load steps for the selected date range
and logs progress and errors.

.. code-block:: python
   :linenos:

   def run_etl(start_date=None, end_date=None):
       # Determines date range description
       # Extracts raw sensor readings
       # Aggregates values per hour
       # Loads results into aggregation DB

---

**Command-Line Entry Point**

Allows execution as a standalone script or module.

.. code-block:: python
   :linenos:

   if __name__ == "__main__":
       logging.basicConfig(level=logging.INFO)
       logger = logging.getLogger(__name__)

       if len(sys.argv) == 2:
           run_etl(sys.argv[1])
       elif len(sys.argv) == 3:
           run_etl(sys.argv[1], sys.argv[2])
       else:
           run_etl()
---
Machine Utilization ETL Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``etl_agg_utilization.py``

This script performs an **ETL (Extract, Transform, Load)** process to calculate
daily machine utilization metrics. It analyzes machine activity logs to derive
the total number of **running hours** and **downtime hours** per day.

The computed metrics are stored in the aggregation database table:

- ``agg_machine_activity_daily``

The script supports single-day execution, date ranges, and full
historical backfills.

**Execution examples**:

.. code-block:: bash

   python -m backend.scripts.etl_agg_utilization 2021-01-15
   python -m backend.scripts.etl_agg_utilization 2021-01-01 2021-01-31

---

**Utilization Data Extraction**

Extracts raw machine activity timestamps from both numeric and string variable
logs, combines them into a unified timeline, and calculates daily operation
intervals.

Running time is derived by grouping activity into sessions, separated by
inactivity gaps greater than 10 minutes.

.. code-block:: python
   :linenos:

   def extract_data(from_date=None, to_date=None):
       with prod_engine.connect() as conn:
           query = ''' SQL QUERY OMITTED FOR BREVITY '''
           params = {
               'from_date': from_date,
               'to_date': to_date
           }
           results = conn.execute(text(query), params)

           return [
               {
                   'dt': r.dia,
                   'running_hours': r.running_horas,
                   'down_hours': r.down_horas
               }
               for r in results
           ]

---

**Load – Daily Machine Utilization**

Stores daily machine utilization metrics in the aggregation database. The script
uses **upsert semantics** to ensure idempotent execution.

.. code-block:: python
   :linenos:

   def load_data(transformed_data):
       session = Session(agg_engine)
       try:
           for record in transformed_data:
               session_object = AggMachineActivityDaily(
                   dt=record['dt'],
                   state_planned_down=record['down_hours'],
                   state_running=record['running_hours']
               )
               session.merge(session_object)
           session.commit()
       finally:
           session.close()

---

**ETL Orchestration**

Determines the execution mode (single date, date range, or full backfill),
coordinates extraction and loading steps, and logs execution progress.

.. code-block:: python
   :linenos:

   def run_etl():
       if len(sys.argv) > 1:
           if len(sys.argv) == 3:
               raw_data = extract_data(sys.argv[1], sys.argv[2])
           else:
               raw_data = extract_data(sys.argv[1])
       else:
           raw_data = extract_data()

       load_data(raw_data)

---

**Command-Line Entry Point**

Allows execution as a standalone script or module.

.. code-block:: python
   :linenos:

   if __name__ == "__main__":
       logger = logging.getLogger(__name__)
       run_etl()
---
Core Backend Code
-----------------

This section documents reusable backend modules that define database access,
ORM models, and shared infrastructure. These files are imported by API services
and backend scripts.

---

Database Connection Layer
~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``database.py``

This module centralizes all database connection logic used by the backend. It
manages connections to:

- A **production database** (read-only, raw data)
- An **aggregation database** (derived analytical data)

It is designed to be compatible with **FastAPI dependency injection**.

---

**Production Database Connection**

.. code-block:: python
   :linenos:

   import os
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   from dotenv import load_dotenv
   load_dotenv()

   db_user = os.getenv("DB_USER")
   db_password = os.getenv("DB_PASSWORD")
   db_host = os.getenv("DB_HOST")
   db_name = os.getenv("DB_NAME")
   db_port = os.getenv("DB_PORT", "2345")

   PROD_DATABASE_URL = (
       f"postgresql+psycopg://{db_user}:{db_password}"
       f"@{db_host}:{db_port}/{db_name}"
   )

   prod_engine = create_engine(
       PROD_DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True,
       pool_recycle=1800
   )

   ProductionSession = sessionmaker(
       autocommit=False,
       autoflush=False,
       bind=prod_engine
   )

   def get_prod_db():
       db = ProductionSession()
       try:
           yield db
       finally:
           db.close()

---

**Aggregation Database Connection**

.. code-block:: python
   :linenos:

   agg_db_name = os.getenv("AGG_DB_NAME")

   AGG_DATABASE_URL = (
       f"postgresql+psycopg://{db_user}:{db_password}"
       f"@{db_host}:{db_port}/{agg_db_name}"
   )

   agg_engine = create_engine(
       AGG_DATABASE_URL,
       pool_size=5,
       max_overflow=10,
       pool_pre_ping=True
   )

   AggregationSession = sessionmaker(
       autocommit=False,
       autoflush=False,
       bind=agg_engine
   )

   def get_agg_db():
       db = AggregationSession()
       try:
           yield db
       finally:
           db.close()

---

ORM Models
~~~~~~~~~~

**File:** ``models.py``

This module defines SQLAlchemy ORM models that map Python classes to database
tables and views, using SQLAlchemy 2.0 typed mappings.

---

**Declarative Base**

.. code-block:: python
   :linenos:

   from sqlalchemy.orm import DeclarativeBase

   class Base(DeclarativeBase):
       pass

---

**Production Database Models**

.. code-block:: python
   :linenos:

   class Variable(Base):
       __tablename__ = "variable"

       id: Mapped[int] = mapped_column(primary_key=True)
       name: Mapped[str]
       datatype: Mapped[str]

---

**Aggregation Database Models**

.. code-block:: python
   :linenos:

   class AggSensorStats(Base):
       __tablename__ = "agg_sensor_stats"

       sensor_name: Mapped[str] = mapped_column(primary_key=True)
       dt: Mapped[datetime] = mapped_column(primary_key=True)
       min_value: Mapped[Optional[float]]
       avg_value: Mapped[Optional[float]]
       max_value: Mapped[Optional[float]]
       readings_count: Mapped[Optional[int]]
---
API Application Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``main.py``

This module defines the **FastAPI application entry point** and exposes all
public REST endpoints used by the frontend and external consumers.

It is responsible for:

- Creating and configuring the FastAPI application
- Defining response schemas using **Pydantic**
- Registering API routes for analytics and monitoring
- Managing database dependencies through SQLAlchemy sessions
- Handling errors and HTTP responses consistently

The API provides read-only access to both the production database and the
aggregation database.

---

**Application Setup**

Initializes the FastAPI application with metadata and configures **CORS** to
allow requests from the frontend application.

.. code-block:: python
   :linenos:

   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   app = FastAPI(
       title="Variable Monitoring API",
       version="1.0.0"
   )

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_methods=["GET"],
       allow_headers=["*"],
   )

---

**Response Models (Pydantic Schemas)**

Defines response schemas used to validate and serialize API responses.

.. code-block:: python
   :linenos:

   from pydantic import BaseModel
   from typing import Optional

   class SensorStatsOut(BaseModel):
       dt: str
       min_value: Optional[float]
       avg_value: Optional[float]
       max_value: Optional[float]
       std_dev: Optional[float]
       readings_count: Optional[int]

---

**Health Check Endpoint**

Simple endpoint to verify that the API and database connection are operational.

.. code-block:: python
   :linenos:

   @app.get("/")
   def home():
       return {"message": "Hello! The API is working!"}

   @app.get("/api/status")
   def status():
       with prod_engine.connect() as connection:
           result = connection.execute(text("SELECT version()"))
           version = result.fetchone()
           return {
               "status": "API is running",
               "database": "Connected",
               "version": str(version)
           }

---

**Aggregated Sensor Statistics Endpoint**

Returns hourly aggregated sensor statistics for a given date and sensor.

.. code-block:: python
   :linenos:

   @app.get("/api/v1/temperature", response_model=List[SensorStatsOut])
   def get_temperature_stats(
       target_date: DateType,
       sensor_name: str = "",
       db: Session = Depends(get_agg_db)
   ):
       query = text("""
           SELECT
               dt,
               min_value,
               avg_value,
               max_value,
               std_dev,
               readings_count
           FROM agg_sensor_stats
           WHERE dt::date = :target_date
             AND sensor_name = :sensor_name
           ORDER BY dt ASC
       """)

---

**Machine Utilization Endpoint**

Exposes daily machine utilization metrics derived from the aggregation
database.

.. code-block:: python
   :linenos:

   @app.get("/api/v1/machine_util", response_model=List[MachineUtilOut])
   def get_machine_util(
       target_date: DateType,
       db: Session = Depends(get_agg_db)
   ):
       query = text("""
           SELECT
               dt,
               state_planned_down,
               state_running,
               running_percentage,
               down_percentage
           FROM agg_machine_activity_daily
           WHERE dt = :target_date
           ORDER BY dt ASC
       """)

---

**Alerts Endpoints**

Provides both **raw** and **aggregated** alert information.

- Aggregated daily counts
- Detailed alert records
- On-demand alert categorization from raw data

.. code-block:: python
   :linenos:

   @app.get("/api/v1/alerts_daily_count", response_model=List[AlertsDailyCountOut])
   def get_alerts_daily_count(
       target_date: DateType,
       db: Session = Depends(get_agg_db)
   ):
       query = text("""
           SELECT
               day,
               alert_type,
               amount
           FROM alerts_daily_count
           WHERE day = :target_date
           ORDER BY amount DESC
       """)

---

**Machine Program Usage Endpoint**

Returns program execution duration per day from the aggregation database.

.. code-block:: python
   :linenos:

   @app.get("/api/v1/machine_program", response_model=List[MachineProgramOut])
   def get_machine_program(
       target_date: DateType,
       db: Session = Depends(get_agg_db)
   ):
       query = text("""
           SELECT
               dt,
               program,
               duration_seconds
           FROM machine_program_data
           WHERE dt = :target_date
           ORDER BY duration_seconds DESC
       """)

---
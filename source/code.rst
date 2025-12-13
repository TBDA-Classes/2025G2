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

**Sample Aggregated Tables**

The following examples illustrate the structure of the aggregation tables.
All tables follow a similar pattern with date-based primary keys and
computed/derived metrics.

*Daily Machine Activity:*

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

*Aggregated Sensor Statistics:*

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

   CREATE INDEX IF NOT EXISTS idx_sensor_date 
       ON agg_sensor_stats(sensor_name, CAST(dt AS DATE));

Additional tables created by this script include: ``alerts_daily_count``,
``alerts_detail``, ``machine_program_data``, and ``energy_consumption_hourly``.

---


ETL Scripts Overview
~~~~~~~~~~~~~~~~~~~~

The project includes five ETL scripts, all following a consistent pattern:

1. **Extract**: Query raw data from the production database
2. **Transform**: Aggregate or reshape data as needed
3. **Load**: Store results in the aggregation database using upsert semantics

**Available ETL Scripts:**

- ``etl_agg_alerts.py`` – Aggregates daily alert counts and stores critical alert details
- ``etl_agg_program_history.py`` – Computes program execution durations per day
- ``etl_agg_sensor_stats.py`` – Calculates hourly sensor statistics (min, max, avg, std_dev)
- ``etl_agg_utilization.py`` – Derives daily machine running hours vs. downtime
- ``etl_agg_energy_daily.py`` – Calculates hourly energy consumption from motor utilization

All scripts support three execution modes:

.. code-block:: bash

   # Single day
   python -m backend.scripts.etl_agg_alerts 2022-02-23

   # Date range
   python -m backend.scripts.etl_agg_alerts 2022-02-01 2022-02-28

   # Full historical backfill (no arguments)
   python -m backend.scripts.etl_agg_alerts

---

**Representative ETL Example: Alerts Aggregation**

The following snippets from ``etl_agg_alerts.py`` illustrate the common ETL
pattern used across all scripts.

*Extraction – Daily Alert Counts:*

.. code-block:: python
   :linenos:

   def extract_daily_count(target_date):
       try:
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
       except Exception as e:
           logger.error(f"Failed to extract daily count: {str(e)}")
           raise

*Load – Using Upsert Semantics:*

.. code-block:: python
   :linenos:

   def load_daily_count(data):
       if not data:
           return 0

       session = Session(agg_engine)
       try:
           for record in data:
               alert_count = AlertsDailyCount(
                   day=record['day'],
                   alert_type=record['alert_type'],
                   amount=record['amount']
               )
               session.merge(alert_count)

           session.commit()
           return len(data)

       except Exception as e:
           session.rollback()
           logger.error(f"Load of daily count failed: {str(e)}")
           raise

       finally:
           session.close()

*ETL Orchestration:*

.. code-block:: python
   :linenos:

   def run_etl(start_date=None, end_date=None):
       # For full backfill, get min/max dates from source data
       if start_date is None and end_date is None:
           logger.info("No dates provided, querying date range for full backfill...")
           start_date, end_date = get_date_range()

       # Process each date in the range
       current_date = datetime.strptime(start_date, '%Y-%m-%d')
       end_dt = datetime.strptime(end_date, '%Y-%m-%d')

       while current_date <= end_dt:
           date_str = current_date.strftime('%Y-%m-%d')
           daily_count_data = extract_daily_count(date_str)
           if daily_count_data:
               load_daily_count(daily_count_data)
           current_date += timedelta(days=1)

---


Daily ETL Runner Script
~~~~~~~~~~~~~~~~~~~~~~~


**File:** ``etl_daily_runner.py``

This script orchestrates daily execution of all ETL scripts. It queries
``v_data_status`` for the latest processed date and runs all ETL scripts
from that date to the current date.

.. code-block:: python
   :linenos:

   ETL_MODULES = [
       "backend.scripts.etl_agg_sensor_stats",
       "backend.scripts.etl_agg_utilization",
       "backend.scripts.etl_agg_program_history",
       "backend.scripts.etl_agg_alerts",
       "backend.scripts.etl_agg_energy_daily",
   ]

   def run_all_etls(from_date: date, to_date: date):
       for module in ETL_MODULES:
           result = subprocess.run(["python", "-m", module, str(from_date), str(to_date)])
           if result.returncode == 0:
               print(f"✓ {module} completed")
           else:
               print(f"✗ {module} failed")

---


Core Backend Code
------------------


This section documents reusable backend modules that define database access,
ORM models, and shared infrastructure.

---


Database Connection Layer
~~~~~~~~~~~~~~~~~~~~~~~~~


**File:** ``database.py``

This module centralizes all database connection logic. It manages connections to
a **production database** (read-only, raw data) and an **aggregation database**
(derived analytical data), and is designed for **FastAPI dependency injection**.

.. code-block:: python
   :linenos:

   import os
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   from dotenv import load_dotenv
   load_dotenv()

   # Production Database
   PROD_DATABASE_URL = (
       f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
       f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '2345')}/{os.getenv('DB_NAME')}"
   )

   prod_engine = create_engine(
       PROD_DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True,
       pool_recycle=1800
   )

   ProductionSession = sessionmaker(autocommit=False, autoflush=False, bind=prod_engine)

   def get_prod_db():
       """Dependency for FastAPI endpoints that read from production database"""
       db = ProductionSession()
       try:
           yield db
       finally:
           db.close()

   # Aggregation Database follows the same pattern with AGG_DB_NAME

---


ORM Models
~~~~~~~~~~


**File:** ``models.py``

Defines SQLAlchemy ORM models using SQLAlchemy 2.0 typed mappings.

*Production Database Models:*

.. code-block:: python
   :linenos:

   class Variable(Base):
       __tablename__ = "variable"

       id: Mapped[int] = mapped_column(primary_key=True)
       name: Mapped[str]
       datatype: Mapped[str]

       variable_log_floats: Mapped[list["VariableLogFloat"]] = relationship(back_populates="variable")
       variable_log_strings: Mapped[list["VariableLogString"]] = relationship(back_populates="variable")

*Sample Aggregation Models:*

.. code-block:: python
   :linenos:

   class AggMachineActivityDaily(Base):
       """Daily machine utilization: running hours vs. downtime hours."""
       __tablename__ = "agg_machine_activity_daily"

       dt: Mapped[date] = mapped_column(primary_key=True)
       state_planned_down: Mapped[float]
       state_running: Mapped[float]
       state_unplanned_down: Mapped[float]
       last_updated_at: Mapped[Optional[datetime]]


   class AggSensorStats(Base):
       """Hourly aggregated sensor statistics."""
       __tablename__ = "agg_sensor_stats"

       sensor_name: Mapped[str] = mapped_column(primary_key=True)
       dt: Mapped[datetime] = mapped_column(primary_key=True)
       min_value: Mapped[Optional[float]]
       avg_value: Mapped[Optional[float]]
       max_value: Mapped[Optional[float]]
       std_dev: Mapped[Optional[float]]
       readings_count: Mapped[Optional[int]]
       last_updated_at: Mapped[Optional[datetime]]

Additional models include: ``MachineProgramData``, ``AlertsDailyCount``,
``AlertsDetail``, and ``EnergyConsumptionHourly``.

---


API Application Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~


**File:** ``main.py``

Defines the **FastAPI application** with REST endpoints for analytics and
monitoring. Provides read-only access to both the production and aggregation
databases.

*Application Setup:*

.. code-block:: python
   :linenos:

   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   app = FastAPI(title="Variable Monitoring API", version="1.0.0")

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_methods=["GET"],
       allow_headers=["*"],
   )

*Sample Response Models:*

.. code-block:: python
   :linenos:

   class SensorStatsOut(BaseModel):
       dt: str
       min_value: Optional[float]
       avg_value: Optional[float]
       max_value: Optional[float]
       std_dev: Optional[float]
       readings_count: Optional[int]

   class MachineUtilOut(BaseModel):
       dt: str
       state_running: Optional[float]
       state_planned_down: Optional[float]
       running_percentage: Optional[float]
       down_percentage: Optional[float]

*Sample Endpoint:*

.. code-block:: python
   :linenos:

   @app.get("/api/v1/temperature", response_model=List[SensorStatsOut])
   def get_temperature_stats(
       target_date: DateType,
       sensor_name: str = "",
       db: Session = Depends(get_agg_db)
   ):
       query = text("""
           SELECT dt, min_value, avg_value, max_value, std_dev, readings_count
           FROM agg_sensor_stats
           WHERE dt::date = :target_date AND sensor_name = :sensor_name
           ORDER BY dt ASC
       """)
       # ...

**Available API Endpoints:**

- ``GET /api/status`` – Health check and database connection status
- ``GET /api/v1/temperature`` – Hourly sensor statistics
- ``GET /api/v1/machine_util`` – Daily machine utilization metrics
- ``GET /api/v1/data_status`` – Overview of available data
- ``GET /api/v1/alerts_daily_count`` – Aggregated daily alert counts
- ``GET /api/v1/alerts_detail`` – Detailed alert records
- ``GET /api/v1/machine_program`` – Program execution durations
- ``GET /api/v1/energy_consumption`` – Hourly energy consumption

---
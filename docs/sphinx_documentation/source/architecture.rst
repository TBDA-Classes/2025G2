SYSTEM ARCHITECTURE
===================

Overview
--------
This project implements a complete monitoring solution for a CNC machine, combining
real-time data processing, aggregated analytics, interactive dashboards, and alert
management. The architecture is divided into four major components:

* **Frontend (Next.js + Tailwind CSS)**  
  Modern single-page application providing interactive dashboards, filtering tools,
  charts, and alert exploration.

* **Backend (FastAPI + SQLAlchemy + psycopg3)**  
  REST API responsible for database access and communication with both data sources.

* **Dual-Database Layer (Production DB + Aggregation DB)**  
  Large-scale sensor data (321M+ rows) processed into a smaller, query-optimized 
  aggregation database to achieve <50ms response times.

* **Data Engineering Layer (ETL Scripts)**  
  Python scripts for Extract–Transform–Load workflows that precomputed results which are then stored in the aggregation database. 
  One parent script (scripts/etl_daily_runner.py) is used for running all etl's as subscripts and is intended for daily data aggregation.
  

* **UI/UX Layer (Figma Prototyping)**  
  Human-centered interaction design guiding UI flow, dashboard hierarchy, and visual behavior.


System Architecture Diagram
---------------------------

.. graphviz::

   digraph architecture {
       rankdir=LR;
       ProductionDB [shape=cylinder];
       AggregationDB [shape=cylinder];
       ETL [shape=box];
       Backend [shape=box];
       Frontend [shape=box];

       ProductionDB -> ETL;
       ETL -> AggregationDB;
       AggregationDB -> Backend;
       Backend -> Frontend;
   }



Dual-Database Strategy
----------------------
Since real-time querying of the production database is impractical and, for the most part, slow the system uses:

1. **Production DB**
    * Read-only access.
    * Contains raw machine sensor data (timestamped events, temperatures, power usage, alerts).
    * Very large (over 321 million rows).

2. **Aggregation DB**
   Custom schema created via ``create_agg_database.sql``. ETL scripts populate:

   - Sensor statistics (temperature distributions)
   - Machine utilization (running vs downtime)
   - Program history (duration per program per day)
   - Alerts (daily counts and detailed records)
   - Energy consumption (hourly estimates)

3. **ETL Scripts** (``backend/scripts/``)

   * ``etl_agg_sensor_stats.py`` – Temperature statistics per time bucket
   * ``etl_agg_utilization.py`` – Daily running hours vs downtime
   * ``etl_agg_program_history.py`` – Program durations per day
   * ``etl_agg_alerts.py`` – Alert counts and details
   * ``etl_agg_energy_daily.py`` – Hourly energy consumption
   * ``etl_daily_runner.py`` – Orchestrates all ETLs for incremental updates
   * ``create_agg_database.sql`` – Schema initialization

This pre-aggregation strategy reduces query response times and enables interactive dashboards.


Frontend–Backend Interaction
----------------------------
The frontend communicates with the backend via API functions in ``frontend/src/lib/api.ts``.
All requests include a date parameter; the backend returns JSON from the aggregated database.


Dashboard Data Requirements
---------------------------
Each UI section maps to specific backend endpoints and aggregated tables:

* **Dashboard** (``/dashboard``)
  - Machine utilization (running vs downtime)
  - Operational timeline (30-minute window, selectable start time)
  - Temperature statistics (box plot)
  - Program history (duration per program)

* **Energy** (``/dashboard/energy``)
  - Hourly energy consumption (line chart)
  - Peak consumption hour
  - Daily total

* **Alerts** (``/dashboard/alerts``)
  - Summary counts by type (emergency, error, warning, other)
  - Filterable alert list
  - Detail panel for selected alert

The UI design is described in :doc:`ui_ux`.
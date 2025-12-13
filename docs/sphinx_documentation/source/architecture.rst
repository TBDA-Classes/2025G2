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
  Python scripts for Extract–Transform–Load workflows, with one mother script used for daily data aggregation.
  Precomputed results which are then stored in the aggregation database.

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
Since real-time querying of the production database is impractical, the system uses:

1. **Production DB**
    * Read-only access.
    * Contains raw machine sensor data (timestamped events, temperatures, power usage, alerts).
    * Very large (over 321 million rows).

2. **Aggregation DB**
    * Custom schema created via ``create_agg_database.sql``.
    * ETL processes populate tables with:

    - Machine utilization distributions  
    - Sensor state timelines  
    - Temperature history  
    - Energy consumption  
    - Alerts summarized by shift  

3. **ETL Scripts**
   Located in ``backend/scripts/``:

   * ``etl_agg_sensor_stats.py``  
     Generates aggregated machine state durations (RUN/IDLE/DOWN).

   * ``etl_agg_machine_utilization.py``  
     Computes 24-hour distributions and shift-based metrics.

   * ``create_agg_database.sql``  
     Initializes the aggregated database schema.

This strategy reduces response times drastically and enables the frontend to display
data interactively without delay.


Frontend–Backend Interaction
----------------------------
The frontend communicates with the backend via a single Axios wrapper located in
``src/lib/api.ts``. All components—including dashboards, charts, and alert lists—request
data using:

* Date parameters  
* Time-window selection  
* Shift filtering  
* Alert severity filtering  

The backend exposes endpoints that return JSON-structured responses optimized for the
frontend components.


User Interface Flow Integration
-------------------------------
The architecture was heavily shaped by the UI/UX design process:
* The Dashboard requires:
  - 24-hour machine utilization data
  - 10-minute time window timeline
  - Temperature history
  - Program execution history

* The Energy section requires:
  - Real-time power
  - Hourly consumption
  - Shift-based totals

* The Alerts section requires:
  - Alerts by type and shift
  - Filterable list of alerts
  - Details panel for selected alert

Backend endpoints and aggregation tables were designed specifically to support these
data flows efficiently.

The dashboard UI is described in detail in the :doc:`ui_ux` section.




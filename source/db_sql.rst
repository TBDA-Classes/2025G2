SQL DATABASE AND DATA ANALYSIS
==============================

Introduction
------------
The project relies on two PostgreSQL databases:

1. **Production Database:**  
   Large-scale raw CNC sensor dataset.  


2. **Aggregation Database:**  
   Lightweight, query-optimized database built via custom ETL processes.

The Data Analysis Team was responsible for understanding the production schema,
extracting relevant information, and enabling efficient querying through aggregation.


CNC Machine Status Semantics
----------------------------
A CNC machine can be in one of several states:

* **RUN** – actively processing a part  
* **IDLE** – powered on but not processing  
* **DOWN** – emergency stop or failure  
 

Raw data reflects:

* Status changes  
* Temperature samples  
* Program execution logs  
* Power usage  
* Alerts and timestamps  


Data Extraction Strategy
------------------------
The production database schema contains:

* ``machine_state``  
* ``temperature_readings``  
* ``alerts``  
* ``program_usage``  
* ``power_consumption``  

The Data Analysis Team ingested these tables to compute:

* 24-hour status distributions  
* Per-shift aggregations  
* Program history  
* Temperature history  
* Energy consumption patterns  
* Emergent alerts by severity  
* Coverage of available dates  


Aggregation Database Schema
---------------------------
Created using:

::

   scripts/create_agg_database.sql

The schema contains:

* ``agg_sensor_stats`` – summarized RUN/IDLE/DOWN durations  
* ``agg_machine_utilization`` – distributions by shift  
* ``agg_temperature_history`` – hourly temperature medians  
* ``agg_program_history`` – program execution blocks  
* ``agg_energy_consumption`` – energy curves and shift totals  
* ``agg_alerts`` – alerts grouped by type and shift  

Indexes include:

* ``timestamp``  
* ``shift``  
* ``status``  
* ``program_id``  
* ``alert_type``  


Shift-Based Interpretation
--------------------------
Production teams work in:

* **Shift 1** – 06:00–14:00  
* **Shift 2** – 14:00–22:00  
* **Shift 3** – 22:00–06:00  

Aggregations produce metrics for each shift, consumed by:

* Dashboard  
* Energy view  
* Alerts distribution  


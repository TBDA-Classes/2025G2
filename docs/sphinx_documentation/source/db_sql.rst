SQL DATABASE AND DATA ANALYSIS
==============================

Introduction
------------
The project relies on two PostgreSQL databases:

1. **Production Database:**  
   Large-scale raw CNC sensor dataset (321M+ rows).  
   Access is read-only and requires VPN.

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

Data Aggregation Strategy
-------------------------
The production database contains millions of rows. To ensure interactive
performance in the frontend:

* ETL scripts extract raw sensor data  
* Transform it through SQL and Python logic  
* Load computed summaries into the aggregation DB  

Indexing Strategy
~~~~~~~~~~~~~~~~~
B-Tree indexes are used for reducing lookup time significantly.

Views
~~~~~
The ``v_data_status`` view provides:

* Global first/last date across all aggregated tables
* Record counts per table (sensors, utilization, alerts, programs, energy)
* Used by the frontend datepicker to restrict selectable dates  


Connecting to PostgreSQL
------------------------
Example:

::

   psql -h 138.100.82.184 -U lectura -d <database> -p 2345

Useful psql commands:

* ``\l`` list databases  
* ``\dt`` list tables  
* ``\dv`` list views  
* ``\d table`` describe schema  
* ``\conninfo`` connection info  


JSON and SQL Operations
-----------------------
Relevant PostgreSQL operators used during analysis:

* ``->`` and ``->>``  
* ``jsonb_array_elements``  
* ``jsonb_object_keys``  
* Window functions (``PARTITION BY``)  
* ``GROUP BY``, ``HAVING``  

These allowed the team to transform nested or semi-structured sensor logs into usable
units for aggregation.


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


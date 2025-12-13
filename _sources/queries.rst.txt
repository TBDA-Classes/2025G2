MAIN QUERIES
============

This section documents a collection of key SQL queries used during the
analysis, exploration, and validation phases of the project.

These queries were used to:
- Understand raw machine behavior
- Validate ETL logic
- Derive utilization, energy, and alert metrics
- Prototype aggregations later implemented in ETL scripts

---

## Machine Utilization Queries

### Machine Utilization (Percentages)

This query calculates **daily machine utilization percentages** by classifying
10-minute activity blocks into operational states and aggregating them per day.

.. code-block:: sql
   :linenos:

   WITH RangoTiempo AS (
       SELECT 
           '2021-01-07 00:00:00'::timestamp AS inicio, 
           '2021-01-16 00:00:00'::timestamp AS fin
   ),
   ResumenFloat AS (
       SELECT 
           to_timestamp(
               floor(
                   extract(epoch from to_timestamp(TRUNC(CAST(date AS bigint)/1000))) / 600
               ) * 600
           ) AS inicio_bloque,
           COUNT(*) AS cnt,
           MIN(date) AS min_ms,
           MAX(date) AS max_ms
       FROM variable_log_float
       WHERE to_timestamp(TRUNC(CAST(date AS bigint)/1000))
             BETWEEN (SELECT inicio FROM RangoTiempo)
             AND (SELECT fin FROM RangoTiempo)
       GROUP BY 1
   ),
   ResumenString AS (
       SELECT 
           to_timestamp(
               floor(
                   extract(epoch from to_timestamp(TRUNC(CAST(date AS bigint)/1000))) / 600
               ) * 600
           ) AS inicio_bloque,
           COUNT(*) AS cnt,
           MIN(date) AS min_ms,
           MAX(date) AS max_ms
       FROM variable_log_string
       WHERE to_timestamp(TRUNC(CAST(date AS bigint)/1000))
             BETWEEN (SELECT inicio FROM RangoTiempo)
             AND (SELECT fin FROM RangoTiempo)
       GROUP BY 1
   ),
   TotalActivity AS (
       SELECT 
           COALESCE(f.inicio_bloque, s.inicio_bloque) AS inicio_bloque,
           (COALESCE(f.cnt, 0) + COALESCE(s.cnt, 0)) AS cambios_totales,
           LEAST(f.min_ms, s.min_ms) AS min_ts_real, 
           GREATEST(f.max_ms, s.max_ms) AS max_ts_real
       FROM ResumenFloat f
       FULL OUTER JOIN ResumenString s
           ON f.inicio_bloque = s.inicio_bloque
   ),
   GrillaBloques AS (
       SELECT generate_series(
           (SELECT inicio FROM RangoTiempo), 
           (SELECT fin FROM RangoTiempo) - interval '10 minutes', 
           '10 minutes'
       ) AS inicio_bloque
   ),
   Clasificacion AS (
       SELECT
           g.inicio_bloque,
           COALESCE(t.cambios_totales, 0) AS cambios,
           CASE
               WHEN COALESCE(t.cambios_totales, 0) = 0 THEN 'PARADA'
               WHEN COALESCE(t.cambios_totales, 0) <= 30 THEN 'IDLE'
               ELSE 'OPERACION'
           END AS estado,
           CASE 
               WHEN COALESCE(t.cambios_totales, 0) = 0
                    THEN g.inicio_bloque
               ELSE to_timestamp(t.min_ts_real / 1000.0)
           END AS start_ts,
           CASE 
               WHEN COALESCE(t.cambios_totales, 0) = 0
                    THEN g.inicio_bloque + interval '10 minutes'
               ELSE to_timestamp(t.max_ts_real / 1000.0)
           END AS end_ts
       FROM GrillaBloques g
       LEFT JOIN TotalActivity t
           ON g.inicio_bloque = t.inicio_bloque
   )
   SELECT
       date(dia_referencia) AS fecha,
       estado,
       ROUND(
           SUM(EXTRACT(EPOCH FROM (fin_corte - inicio_corte))) / 3600.0,
           2
       ) AS tiempo_horas,
       ROUND(
           (SUM(EXTRACT(EPOCH FROM (fin_corte - inicio_corte))) / 86400.0) * 100,
           2
       ) AS porcentaje_dia
   FROM Clasificacion;

---

## Program History Queries

### Program History (24 Hours)

Computes **daily program execution durations** by reconstructing program state
intervals and cutting them by calendar day.

.. code-block:: sql
   :linenos:

   WITH RangoTiempo AS (
       SELECT 
           '2021-01-07 00:00:00'::timestamp AS inicio, 
           '2021-01-16 00:00:00'::timestamp AS fin
   ),
   EstadoPrevio AS (
       SELECT 
           (SELECT inicio FROM RangoTiempo) AS dt,
           CAST(value AS integer) AS estado_numerico
       FROM variable_log_float
       WHERE id_var = 581
         AND to_timestamp(TRUNC(CAST(date AS bigint)/1000))
             < (SELECT inicio FROM RangoTiempo)
       ORDER BY date DESC
       LIMIT 1
   ),
   LogsRango AS (
       SELECT 
           to_timestamp(TRUNC(CAST(date AS bigint)/1000)) AS dt,
           CAST(value AS integer) AS estado_numerico
       FROM variable_log_float
       WHERE id_var = 581
         AND to_timestamp(TRUNC(CAST(date AS bigint)/1000))
             BETWEEN (SELECT inicio FROM RangoTiempo)
             AND (SELECT fin FROM RangoTiempo)
   )
   SELECT
       date(dia_referencia) AS fecha,
       estado_numerico,
       ROUND(
           SUM(EXTRACT(EPOCH FROM (fin_real - inicio_real))),
           2
       ) AS duracion_segundos
   FROM LogsRango
   GROUP BY fecha, estado_numerico;

---

## Temperature Queries

### Temperature History (24 Hours)

Retrieves **raw temperature sensor readings** for a set of temperature-related
variables over a given time window.

.. code-block:: sql
   :linenos:

   SELECT 
     b.name AS variable,
     to_timestamp(CAST(a.date AS bigint) / 1000) AS dt,
     a.value
   FROM variable_log_float a
   JOIN variable b ON a.id_var = b.id
   WHERE to_timestamp(CAST(a.date AS bigint) / 1000)
         BETWEEN '2021-01-04 13:39:30+01'
         AND '2021-01-05 22:00:00+01'
     AND b.name IN (
       'TEMPERATURE_BASE',
       'TEMPERATURA_BASE',
       'TEMPERATURE_HEAD'
     )
   ORDER BY variable, dt;

---

## Energy Consumption Queries

### Hourly Consumption

Computes **hourly energy consumption (kWh)** based on motor utilization
percentages and nominal power.

.. code-block:: sql
   :linenos:

   SELECT
     date_trunc('hour', ts) AS hour_ts,
     ROUND(SUM(energy_kwh)::numeric, 3) AS energy_kwh
   FROM segments_energy
   GROUP BY date_trunc('hour', ts)
   ORDER BY hour_ts;

---

### Energy by Shift

Aggregates energy consumption by **production shift** (Day, Swing, Night).

.. code-block:: sql
   :linenos:

   SELECT
     shift_name,
     ROUND(SUM(energy_kwh)::numeric, 3) AS energy_kwh
   FROM by_shift
   GROUP BY shift_name
   ORDER BY shift_name;

---

## Alarm Queries

### Alarm Count by Category

Counts alarms grouped by **severity category**.

.. code-block:: sql
   :linenos:

   SELECT 
       category,
       COUNT(*) AS total_alerts
   FROM categorized
   GROUP BY category;

---

### Alarm Count by Shift and Category

Counts alarms per **shift** and **severity category**.

.. code-block:: sql
   :linenos:

   SELECT 
       shift,
       COUNT(*) AS total_alerts
   FROM categorized
   GROUP BY shift
   ORDER BY shift;

---

### Full List of Alerts

Retrieves a **chronological list of alarms** with classification.

.. code-block:: sql
   :linenos:

   SELECT 
       category AS alert_type,
       alarm_code,
       timestamp
   FROM categorized
   ORDER BY timestamp DESC;

---

### Alarm Detail for a Specific Code

Filters alarms for a **specific alarm code and date**.

.. code-block:: sql
   :linenos:

   SELECT 
       alarm_code,
       timestamp,
       alarm_description
   FROM alarm_data
   WHERE alarm_code = :alarm_code
     AND timestamp::date = :target_date;

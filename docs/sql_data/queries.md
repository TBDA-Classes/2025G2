---
title: "SQL Queries for Data Analysis"
author: "Data analysis team"
output: html_document
---

# Clarification: The dates used for the queries can be changed depending on the needs,these are just reference dates to have usable queries


##### PERIOD IDENTIFYING QUERIES #####

### Query to identify the hours in which changes in variables are registered, based on the working day (in order to know possible start and end times for the machine)

```sql
WITH horas AS (  
  SELECT dt FROM (  
    SELECT generate_series(  
      '2021-01-07 00:00:00'::timestamp,  
      '2021-01-15 23:00:00'::timestamp,  
      interval '1 hour'  
    ) AS dt  
  ) sub  
  WHERE EXTRACT(DOW FROM dt) NOT IN (0,6)  
),  
cambios_por_hora AS (  
  SELECT   
    to_timestamp(ROUND((TRUNC(CAST(date AS bigint)/1000) / 3600))*3600) AS dt,  
    COUNT(DISTINCT id_var) AS total_variables  
  FROM public.variable_log_float  
  WHERE to_timestamp(TRUNC(CAST(date AS bigint)/1000)) >= '2021-01-07 00:00:00'  
    AND to_timestamp(TRUNC(CAST(date AS bigint)/1000)) < '2021-01-16 00:00:00'  
  GROUP BY dt  
)  
SELECT  
  h.dt,  
  TO_CHAR(h.dt, 'FMDay') AS dia_semana,  
  COALESCE(c.total_variables, 0) AS total_variables,  
  CASE   
    WHEN COALESCE(c.total_variables, 0) = 0 THEN 'Máquina parada'  
    WHEN COALESCE(c.total_variables, 0) < 30 THEN 'Parada probable'  
    WHEN COALESCE(c.total_variables, 0) BETWEEN 30 AND 80 THEN 'Actividad media'  
    ELSE 'Máquina en operación'  
  END AS estado_maquina  
FROM horas h  
LEFT JOIN cambios_por_hora c ON h.dt = c.dt  
ORDER BY h.dt;
```

### Query for detecting the exact timestamps in which variable changes are detected (also includes the days of the week)

WITH horas AS (
  SELECT generate_series(
      '2021-01-07 00:00:00'::timestamp,
      '2021-01-15 23:00:00'::timestamp,
      interval '1 hour'
  ) AS hora
),

cambios AS (
  SELECT
    to_timestamp(CAST(a.date AS bigint)/1000) AS dt,
    date_trunc('hour', to_timestamp(CAST(a.date AS bigint)/1000)) AS hora,
    a.id_var,
    b.name AS variable,
    a.value::float AS valor,
    LAG(a.value::float) OVER (
      PARTITION BY a.id_var 
      ORDER BY to_timestamp(CAST(a.date AS bigint)/1000)
    ) AS valor_anterior
  FROM variable_log_float a
  JOIN variable b ON a.id_var = b.id
  WHERE to_timestamp(CAST(a.date AS bigint)/1000)
        BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'
),

cambios_filtrados AS (
  SELECT *
  FROM cambios
  WHERE valor IS DISTINCT FROM valor_anterior
),

resumen_cambios AS (
  SELECT
    hora,
    COUNT(DISTINCT id_var) AS total_variables_que_cambiaron,
    MIN(dt) AS primer_cambio,
    MAX(dt) AS ultimo_cambio
  FROM cambios_filtrados
  GROUP BY hora
)

SELECT
  h.hora,
  COALESCE(r.total_variables_que_cambiaron, 0) AS total_variables_que_cambiaron,
  r.primer_cambio,
  r.ultimo_cambio,
  CASE
    WHEN COALESCE(r.total_variables_que_cambiaron, 0) = 0 THEN 'Máquina parada'
    WHEN COALESCE(r.total_variables_que_cambiaron, 0) < 30 THEN 'Parada probable'
    WHEN COALESCE(r.total_variables_que_cambiaron, 0) BETWEEN 30 AND 80 THEN 'Actividad media'
    ELSE 'Máquina en operación'
  END AS estado_maquina
FROM horas h
LEFT JOIN resumen_cambios r ON h.hora = r.hora
ORDER BY h.hora;





### Query for identifying NaNs in time intervals

WITH base_data AS (
    SELECT 
        to_timestamp(ROUND((TRUNC(CAST(a.date AS bigint)/1000) / 30))*30) AS dt
    FROM public.variable_log_float a
    JOIN variable b ON a.id_var = b.id
    WHERE b.name = 'TEMPERATURA_BASE' AND a.value::text = 'NaN'
),

grouped AS (
    SELECT 
        dt,
        dt - INTERVAL '30 seconds' * ROW_NUMBER() OVER (ORDER BY dt) AS grp
    FROM base_data
),

downtime_periods_raw AS (
    SELECT 
        MIN(dt) AS start_time,
        MAX(dt) + INTERVAL '30 seconds' AS end_time
    FROM grouped
    GROUP BY grp
)

SELECT 
    start_time,
    end_time,
    end_time - start_time AS duration,
    EXTRACT(EPOCH FROM (end_time - start_time)) / 60 AS duration_minutes
FROM downtime_periods_raw
ORDER BY start_time;


### Query for identifying the variables that have registered NaNs

WITH base_data AS (
    SELECT 
        id_var,
        to_timestamp(ROUND((TRUNC(CAST(a.date AS bigint)/1000) / 30))*30) AS dt
    FROM public.variable_log_float a
    WHERE a.value::text = 'NaN'
),

grouped AS (
    SELECT 
        id_var,
        dt,
        dt - INTERVAL '30 seconds' * ROW_NUMBER() OVER (ORDER BY dt) AS grp
    FROM base_data
),

downtime_periods_raw AS (
    SELECT 
        grp,
        MIN(dt) AS start_time,
        MAX(dt) + INTERVAL '30 seconds' AS end_time
    FROM grouped
    GROUP BY grp
),

variables_por_periodo AS (
    SELECT 
        d.start_time,
        d.end_time,
        d.end_time - d.start_time AS duration,
        EXTRACT(EPOCH FROM (d.end_time - d.start_time)) / 60 AS duration_minutes,
        array_agg(DISTINCT v.id_var) AS variables_nan
    FROM downtime_periods_raw d
    JOIN grouped v
      ON v.dt BETWEEN d.start_time AND d.end_time
      AND v.grp = d.grp
    GROUP BY d.start_time, d.end_time
)

SELECT
    vpp.start_time,
    vpp.end_time,
    vpp.duration,
    vpp.duration_minutes,
    vpp.variables_nan,
    -- Aquí obtenemos los nombres de variables usando un subquery
    (
      SELECT array_agg(DISTINCT var.name)
      FROM variable var
      WHERE var.id = ANY(vpp.variables_nan)
    ) AS nombres_variables
FROM variables_por_periodo vpp
ORDER BY vpp.start_time;



##### ALARM IDENTIFYING QUERIES #####

### Query to identify the different types of alarms

SELECT DISTINCT
    TRIM(jsonb_array_elements(value::jsonb)->>1) AS descripcion_alarma
FROM variable_log_string a
JOIN variable b ON a.id_var = b.id
WHERE b.name = 'ALARMS'
  AND value IS NOT NULL
  AND value LIKE '[%'
  AND value LIKE '%]'
ORDER BY descripcion_alarma;



##### QUERIES TO EXTRACT DATA #####

### Query to unite float and string data

SELECT 
    a.id_var,
    b.name,
    to_timestamp(ROUND((TRUNC(CAST(a.date AS bigint)/1000) / 30))*30) AS dt,
    a.value::text AS value
FROM "public"."variable_log_float" a
JOIN variable b 
    ON a.id_var = b.id

WHERE to_timestamp(ROUND((TRUNC(CAST(a.date AS bigint)/1000) / 30))*30) >= '2022-02-23 13:39:30+01'
  AND to_timestamp(ROUND((TRUNC(CAST(a.date AS bigint)/1000) / 30))*30) < '2022-02-23 15:00:00+01'

UNION ALL

SELECT 
    a.id_var,
    b.name,
    to_timestamp(ROUND((TRUNC(CAST(a.date AS bigint)/1000) / 30))*30) AS dt,
    a.value::text AS value
FROM "public"."variable_log_string" a
JOIN variable b 
    ON a.id_var = b.id

WHERE to_timestamp(ROUND((TRUNC(CAST(a.date AS bigint)/1000) / 30))*30) >= '2022-02-23 13:39:30+01'
  AND to_timestamp(ROUND((TRUNC(CAST(a.date AS bigint)/1000) / 30))*30) < '2022-02-23 15:00:00+01'

ORDER BY dt, name;

### Query to count the amount of variables that change during a time period (in this case, every hour)

SELECT count(distinct(id_var)) ,to_timestamp(ROUND((TRUNC(CAST(date as bigint)/1000) / 3600))*3600) 
as dt FROM "public"."variable_log_float" 
WHERE to_timestamp(TRUNC(CAST(date as bigint)/1000)) >= '2020-12-28 00:00:00+01' 
and to_timestamp(TRUNC(CAST(date as bigint)/1000)) < '2021-01-10 06:00:00+01'
group by dt

### Query to identify the minimum and maximum date present in the database

SELECT to_timestamp(cast(min(date) as bigint)/ 1000) AS min_date, 
to_timestamp(cast(max(date) as bigint)/ 1000) AS max_date 
FROM "public"."variable_log_string";

### Query for details of the values captured for every variable in a given timeframe (for string or float data)

SELECT 
    a.id_var,
    b.name,
    to_timestamp(ROUND((TRUNC(CAST(a.date as bigint)/1000) / 30))*30) as dt,
    a.value
FROM "public"."variable_log_float" a
JOIN variable b 
    ON a.id_var = b.id
WHERE to_timestamp(ROUND((TRUNC(CAST(a.date as bigint)/1000) / 30))*30) >= '2021-01-04 13:39:30+01'
  AND to_timestamp(ROUND((TRUNC(CAST(a.date as bigint)/1000) / 30))*30) < '2021-01-04 22:00:00+01'
ORDER BY dt;





```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
library(DBI)
library(RPostgres)

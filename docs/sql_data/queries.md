---
title: "SQL Queries for Data Analysis"
author: "Data analysis team"
output: html_document
---

# Clarification: The dates used for the queries can be changed depending on the needs,these are just reference dates to have usable queries


## PERIOD IDENTIFYING QUERIES ##

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

``` sql
WITH horas AS (
  SELECT dt AS hora
  FROM (
    SELECT generate_series(
      '2021-01-07 00:00:00'::timestamp,
      '2021-01-15 23:00:00'::timestamp,
      interval '1 hour'
    ) AS dt
  ) sub
),

cambios_float AS (
  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt,
    b.name AS variable
  FROM variable_log_float a
  JOIN variable b ON a.id_var = b.id
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'
),

cambios_string AS (
  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt,
    b.name AS variable
  FROM variable_log_string a
  JOIN variable b ON a.id_var = b.id
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'
),

-- Unir ambos tipos de cambios
todos_cambios AS (
  SELECT * FROM cambios_float
  UNION ALL
  SELECT * FROM cambios_string
),

-- Agrupar cambios por franja horaria
cambios_por_hora AS (
  SELECT
    date_trunc('hour', dt) AS hora,
    COUNT(DISTINCT variable) AS total_variables,
    MIN(dt) AS primer_cambio,
    MAX(dt) AS ultimo_cambio
  FROM todos_cambios
  GROUP BY date_trunc('hour', dt)
)

SELECT
  h.hora,
  CASE EXTRACT(DOW FROM h.hora)
    WHEN 0 THEN 'Domingo'
    WHEN 1 THEN 'Lunes'
    WHEN 2 THEN 'Martes'
    WHEN 3 THEN 'Miércoles'
    WHEN 4 THEN 'Jueves'
    WHEN 5 THEN 'Viernes'
    WHEN 6 THEN 'Sábado'
  END AS dia_semana,
  COALESCE(c.total_variables, 0) AS total_variables,
  c.primer_cambio,
  c.ultimo_cambio,
  CASE
    WHEN COALESCE(c.total_variables, 0) = 0 THEN 'Máquina parada'
    WHEN COALESCE(c.total_variables, 0) < 30 THEN 'Parada probable'
    WHEN COALESCE(c.total_variables, 0) BETWEEN 30 AND 80 THEN 'Actividad media'
    ELSE 'Máquina en operación'
  END AS estado_maquina
FROM horas h
LEFT JOIN cambios_por_hora c ON h.hora = c.hora
ORDER BY h.hora;
```


### Query to count the average working hours per day, by days counted

```sql
WITH cambios_float AS (
  SELECT
    to_timestamp(CAST(a.date AS bigint)/1000) AS dt
  FROM variable_log_float a
  WHERE to_timestamp(CAST(a.date AS bigint)/1000)
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'
),
cambios_string AS (
  SELECT
    to_timestamp(CAST(a.date AS bigint)/1000) AS dt
  FROM variable_log_string a
  WHERE to_timestamp(CAST(a.date AS bigint)/1000)
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'
),
todos_cambios AS (
  SELECT dt FROM cambios_float
  UNION ALL
  SELECT dt FROM cambios_string
),
diferencias AS (
  SELECT
    dt,
    LAG(dt) OVER (ORDER BY dt) AS dt_anterior
  FROM todos_cambios
),
duraciones AS (
  SELECT
    DATE(dt) AS dia,
    EXTRACT(DOW FROM dt) AS num_dia_semana, -- 0 = domingo, 1 = lunes...
    EXTRACT(EPOCH FROM (dt - dt_anterior)) / 3600 AS horas
  FROM diferencias
  WHERE dt_anterior IS NOT NULL
    AND EXTRACT(EPOCH FROM (dt - dt_anterior)) < 3600  -- ignorar huecos mayores a 1 hora
),
horas_por_dia AS (
  SELECT
    dia,
    num_dia_semana::int AS num_dia_semana,
    ROUND(SUM(horas)::numeric, 2) AS horas_trabajadas
  FROM duraciones
  GROUP BY dia, num_dia_semana
)

SELECT
  CASE num_dia_semana
    WHEN 1 THEN 'Lunes'
    WHEN 2 THEN 'Martes'
    WHEN 3 THEN 'Miércoles'
    WHEN 4 THEN 'Jueves'
    WHEN 5 THEN 'Viernes'
    WHEN 6 THEN 'Sábado'
    WHEN 0 THEN 'Domingo'
  END AS dia_semana,
  COUNT(*) AS dias_analizados,
  ROUND(AVG(horas_trabajadas)::numeric, 2) AS promedio_horas_trabajadas
FROM horas_por_dia
GROUP BY num_dia_semana
ORDER BY num_dia_semana;
```


### Query to know the average working hours of the entire database (note: for saturday and sunday the result means that, if the machine operates in these days, the average time of operation is the one shown in the result

```sql
WITH cambios_float AS (
  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_float a
),

cambios_string AS (
  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_string a
),

-- Unir todas las marcas de tiempo donde hubo algún cambio
todos_cambios AS (
  SELECT dt FROM cambios_float
  UNION ALL
  SELECT dt FROM cambios_string
),

-- Contar cuántas variables cambiaron por hora
cambios_por_hora AS (
  SELECT
    date_trunc('hour', dt) AS hora,
    COUNT(*) AS total_cambios
  FROM todos_cambios
  GROUP BY date_trunc('hour', dt)
),

-- Clasificar cada hora según la actividad de la máquina
estado_por_hora AS (
  SELECT
    hora,
    CASE
      WHEN total_cambios = 0 THEN 'Máquina parada'
      WHEN total_cambios < 30 THEN 'Parada probable'
      WHEN total_cambios BETWEEN 30 AND 80 THEN 'Actividad media'
      ELSE 'Máquina en operación'
    END AS estado
  FROM cambios_por_hora
),

-- Calcular las horas trabajadas por día
horas_por_dia AS (
  SELECT
    DATE(hora) AS dia,
    EXTRACT(DOW FROM hora) AS num_dia_semana,
    CASE EXTRACT(DOW FROM hora)
      WHEN 0 THEN 'Domingo'
      WHEN 1 THEN 'Lunes'
      WHEN 2 THEN 'Martes'
      WHEN 3 THEN 'Miércoles'
      WHEN 4 THEN 'Jueves'
      WHEN 5 THEN 'Viernes'
      WHEN 6 THEN 'Sábado'
    END AS dia_semana,
    COUNT(*) FILTER (WHERE estado IN ('Máquina en operación', 'Actividad media')) AS horas_trabajadas
  FROM estado_por_hora
  GROUP BY DATE(hora), EXTRACT(DOW FROM hora)
)

-- Promedio de horas trabajadas por día de la semana
SELECT
  dia_semana,
  ROUND(AVG(horas_trabajadas)::numeric, 2) AS promedio_horas_trabajadas
FROM horas_por_dia
GROUP BY dia_semana, num_dia_semana
ORDER BY num_dia_semana;
```


### Query to count the working hours each day

```sql
WITH cambios_float AS (
  SELECT
    to_timestamp(CAST(a.date AS bigint)/1000) AS dt
  FROM variable_log_float a
  WHERE to_timestamp(CAST(a.date AS bigint)/1000)
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'
),
cambios_string AS (
  SELECT
    to_timestamp(CAST(a.date AS bigint)/1000) AS dt
  FROM variable_log_string a
  WHERE to_timestamp(CAST(a.date AS bigint)/1000)
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'
),
todos_cambios AS (
  SELECT dt FROM cambios_float
  UNION ALL
  SELECT dt FROM cambios_string
),
diferencias AS (
  SELECT
    dt,
    LAG(dt) OVER (ORDER BY dt) AS dt_anterior
  FROM todos_cambios
),
duraciones AS (
  SELECT
    DATE(dt) AS dia,
    EXTRACT(EPOCH FROM (dt - dt_anterior)) / 3600 AS horas
  FROM diferencias
  WHERE dt_anterior IS NOT NULL
    AND EXTRACT(EPOCH FROM (dt - dt_anterior)) < 3600  -- ignorar huecos mayores a 1 hora
)
SELECT
  dia,
  CASE EXTRACT(DOW FROM dia)
    WHEN 0 THEN 'Domingo'
    WHEN 1 THEN 'Lunes'
    WHEN 2 THEN 'Martes'
    WHEN 3 THEN 'Miércoles'
    WHEN 4 THEN 'Jueves'
    WHEN 5 THEN 'Viernes'
    WHEN 6 THEN 'Sábado'
  END AS dia_semana,
  ROUND(SUM(horas)::numeric, 2) AS horas_trabajadas
FROM duraciones
GROUP BY dia
ORDER BY dia;
```

### Query for identifying NaNs in time intervals

```sql
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
```


## ALARM IDENTIFYING QUERIES ##

### Query to identify the different types of alarms

```sql
SELECT DISTINCT
    TRIM(jsonb_array_elements(value::jsonb)->>1) AS descripcion_alarma
FROM variable_log_string a
JOIN variable b ON a.id_var = b.id
WHERE b.name = 'ALARMS'
  AND value IS NOT NULL
  AND value LIKE '[%'
  AND value LIKE '%]'
ORDER BY descripcion_alarma;
```


## QUERIES TO EXTRACT DATA ##

### Query to unite float and string data

```sql
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
```


### Query to count the amount of variables that change during a time period (in this case, every hour)

```sql
SELECT count(distinct(id_var)) ,to_timestamp(ROUND((TRUNC(CAST(date as bigint)/1000) / 3600))*3600) 
as dt FROM "public"."variable_log_float" 
WHERE to_timestamp(TRUNC(CAST(date as bigint)/1000)) >= '2020-12-28 00:00:00+01' 
and to_timestamp(TRUNC(CAST(date as bigint)/1000)) < '2021-01-10 06:00:00+01'
group by dt
```

### Query to identify the minimum and maximum date present in the database

```sql
SELECT to_timestamp(cast(min(date) as bigint)/ 1000) AS min_date, 
to_timestamp(cast(max(date) as bigint)/ 1000) AS max_date 
FROM "public"."variable_log_string";
```

### Query for details of the values captured for every variable in a given timeframe (for string or float data)

```sql
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
```




```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
library(DBI)
library(RPostgres)

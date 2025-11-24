---
title: "SQL Queries for Data Analysis"
author: "Data analysis team"
output: html_document
---

# Clarification: The dates used for the queries can be changed depending on the needs,these are just reference dates to have usable queries (limited to 200 rows)

## COMPARISON ##

### CQ1: Query using the variable machine_in_operation vs. query to identify variable changes, to see if the data gathered by the two queries is the same.

```sql
WITH RangoEventos AS (
    -- 1. Capturar los primeros 200 segundos únicos con cualquier evento
    SELECT date_trunc('second', to_timestamp(a.date/1000)) AS segundo_evento
    FROM variable_log_float a
    WHERE to_timestamp(a.date/1000) BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'
    UNION
    SELECT date_trunc('second', to_timestamp(a.date/1000)) AS segundo_evento
    FROM variable_log_string a
    WHERE to_timestamp(a.date/1000) BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'
    ORDER BY segundo_evento
    LIMIT 200 -- Limita el número de segundos a analizar
),
-- 2. Conteo de Cambios (La métrica alternativa, optimizada)
ConteoCambios AS (
    SELECT
        date_trunc('second', dt) AS segundo_evento,
        COUNT(*) AS total_cambios
    FROM (
        SELECT to_timestamp(a.date/1000) AS dt
        FROM variable_log_float a
        JOIN variable b ON a.id_var = b.id
        WHERE b.name <> 'MACHINE_IN_OPERATION'
              AND to_timestamp(a.date/1000) BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'
        UNION ALL
        SELECT to_timestamp(a.date/1000) AS dt
        FROM variable_log_string a
        WHERE to_timestamp(a.date/1000) BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'
    ) AS TodosLosCambios
    GROUP BY 1
)

-- 3. COMPARACIÓN FINAL con LATERAL JOIN
SELECT
    re.segundo_evento,
    -- Estado Real (basado en MACHINE_IN_OPERATION)
    CASE
        WHEN estado_actual.value IS NULL THEN 'Estado Desconocido'
        WHEN estado_actual.value > 0 THEN 'Operación (Real)'
        ELSE 'Parada (Real)'
    END AS estado_real,
    
    -- Estado por Conteo de Cambios
    CASE
        WHEN cc.total_cambios IS NULL OR cc.total_cambios = 0 THEN 'Parada (Conteo)'
        ELSE 'Operación (Conteo)'
    END AS estado_conteo,
    
    -- Coincidencia
    CASE
        WHEN (estado_actual.value > 0) AND (cc.total_cambios IS NULL OR cc.total_cambios = 0) THEN 'NO COINCIDEN (Real ON, Conteo OFF)'
        WHEN (estado_actual.value IS NULL OR estado_actual.value <= 0) AND (cc.total_cambios IS NOT NULL AND cc.total_cambios > 0) THEN 'NO COINCIDEN (Real OFF, Conteo ON)'
        ELSE 'COINCIDEN'
    END AS coincidencia
FROM RangoEventos re
-- LATERAL JOIN optimizado para buscar el estado vigente en ese segundo
LEFT JOIN LATERAL (
    SELECT a.value
    FROM variable_log_float a
    JOIN variable b ON a.id_var = b.id
    WHERE b.name = 'MACHINE_IN_OPERATION'
      AND to_timestamp(a.date/1000) <= re.segundo_evento
    ORDER BY to_timestamp(a.date/1000) DESC
    LIMIT 1
) AS estado_actual ON TRUE
LEFT JOIN ConteoCambios cc ON re.segundo_evento = cc.segundo_evento
ORDER BY re.segundo_evento;
```
<img width="287" height="172" alt="image" src="https://github.com/user-attachments/assets/3cd72209-4367-4cf0-bf5a-68e1a7bfefea" />
<img width="402" height="202" alt="image" src="https://github.com/user-attachments/assets/56fca6f8-aa09-4a75-836e-b94ccaeacbce" />

### CQ2: Query to know when the status of the machine changes and which state is in (operating or stopped)

```sql
WITH RegistrosEstado AS (
    -- 1. Obtener todos los registros de la variable 'MACHINE_IN_OPERATION' ordenados por tiempo
    SELECT
        TO_TIMESTAMP(vf.date/1000) AS fecha_hora,
        vf.value -- Valor exacto (ej. 1.0 o 0.0)
    FROM
        variable_log_float vf
    LEFT JOIN
        variable v ON vf.id_var = v.id
    WHERE
        v.name = 'MACHINE_IN_OPERATION'
    ORDER BY
        vf.date
),
CambiosDetectados AS (
    -- 2. CTE para calcular el estado anterior y marcar el cambio
    SELECT
        fecha_hora,
        value,
        -- Usar LAG para obtener el valor anterior
        LAG(value) OVER (ORDER BY fecha_hora) AS valor_anterior
    FROM
        RegistrosEstado
)
SELECT
    cd.fecha_hora,
    -- Estado de la máquina en el momento exacto (actual)
    CASE
        WHEN cd.value > 0 THEN 'Operación'
        ELSE 'Parada'
    END AS estado_actual,
    -- Estado de la máquina en el registro anterior (LAG)
    CASE
        WHEN cd.valor_anterior > 0 THEN 'Operación'
        WHEN cd.valor_anterior IS NULL THEN 'Inicio' -- Primer registro
        ELSE 'Parada'
    END AS estado_anterior
FROM
    CambiosDetectados cd
WHERE
    -- 3. Aplicar el filtro de cambio de estado (excluye registros donde no hay cambio)
    cd.value IS DISTINCT FROM cd.valor_anterior
ORDER BY
    cd.fecha_hora
LIMIT 10;
```


## PERIOD IDENTIFYING QUERIES ##

### PQ1 - Query to identify the hours in which changes in variables are registered, based on the working day (in order to know possible start and end times for the machine)

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

### PQ2 - Query for detecting the exact timestamps in which variable changes are detected (also includes the days of the week)

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

-- Resultado final simplificado
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
    ELSE 'Máquina en operación'
  END AS estado_maquina
FROM horas h
LEFT JOIN cambios_por_hora c ON h.hora = c.hora
ORDER BY h.hora;
```

### PQ3 - Query to count the working hours in every interval in which the machine is working (IMPORTANT: we consider that the machine stops if there are no new variable changes after 10 minutes)

```sql
WITH cambios AS (
  -- Unir logs de tipo FLOAT
  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_float a
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'

  UNION ALL

  -- Unir logs de tipo STRING
  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_string a
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'
),

ordenado AS (
  SELECT
    dt,
    date(dt) AS fecha,
    LAG(dt) OVER (PARTITION BY date(dt) ORDER BY dt) AS dt_anterior
  FROM cambios
),

-- Detectar paradas: diferencia mayor a 10 minutos entre eventos
marcado AS (
  SELECT
    fecha,
    dt,
    dt_anterior,
    CASE
      WHEN dt_anterior IS NULL THEN 1
      WHEN EXTRACT(EPOCH FROM (dt - dt_anterior)) > 600 THEN 1  -- 600 segundos = 10 minutos
      ELSE 0
    END AS nueva_sesion
  FROM ordenado
),

-- Asignar un número de bloque de operación continuo
bloques AS (
  SELECT
    fecha,
    dt,
    SUM(nueva_sesion) OVER (PARTITION BY fecha ORDER BY dt) AS bloque_id
  FROM marcado
),

-- Determinar inicio, fin y duración de cada bloque
intervalos AS (
  SELECT
    fecha,
    MIN(dt) AS inicio_operacion,
    MAX(dt) AS fin_operacion,
    ROUND(EXTRACT(EPOCH FROM (MAX(dt) - MIN(dt)))/3600.0, 2) AS horas_operacion
  FROM bloques
  GROUP BY fecha, bloque_id
)

-- Resultado final ordenado
SELECT
  fecha,
  CASE EXTRACT(DOW FROM fecha)
    WHEN 0 THEN 'Domingo'
    WHEN 1 THEN 'Lunes'
    WHEN 2 THEN 'Martes'
    WHEN 3 THEN 'Miércoles'
    WHEN 4 THEN 'Jueves'
    WHEN 5 THEN 'Viernes'
    WHEN 6 THEN 'Sábado'
  END AS dia_semana,
  inicio_operacion,
  fin_operacion,
  horas_operacion
FROM intervalos
ORDER BY fecha, inicio_operacion;
```

### PQ4 - Query to identify the stoppage times during the day and for how long the stoppage lasted (IMPORTANT: same consideration as in PQ3 about the 10 minutes limit)

```sql
WITH cambios AS (
  -- Combinar los logs de float y string en una sola lista de timestamps
  SELECT to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_float a
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'

  UNION ALL

  SELECT to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_string a
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'
),

ordenado AS (
  SELECT
    dt,
    date(dt) AS fecha,
    LEAD(dt) OVER (PARTITION BY date(dt) ORDER BY dt) AS siguiente_dt
  FROM cambios
),

paradas AS (
  SELECT
    fecha,
    dt AS inicio_parada,
    siguiente_dt AS fin_parada,
    EXTRACT(EPOCH FROM (siguiente_dt - dt))/3600.0 AS horas_parada
  FROM ordenado
  WHERE siguiente_dt IS NOT NULL
    AND EXTRACT(EPOCH FROM (siguiente_dt - dt)) > 600  -- Umbral de 10 minutos
)

SELECT
  fecha,
  CASE EXTRACT(DOW FROM fecha)
    WHEN 0 THEN 'Domingo'
    WHEN 1 THEN 'Lunes'
    WHEN 2 THEN 'Martes'
    WHEN 3 THEN 'Miércoles'
    WHEN 4 THEN 'Jueves'
    WHEN 5 THEN 'Viernes'
    WHEN 6 THEN 'Sábado'
  END AS dia_semana,
  inicio_parada,
  fin_parada,
  ROUND(horas_parada, 2) AS horas_parada
FROM paradas
ORDER BY fecha, inicio_parada;
```

### PQ5 - Query to count the average working hours per day, by days counted

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


### PQ6 - Query to know the average working hours of the entire database (note: for saturday and sunday the result means that, if the machine operates in these days, the average time of operation is the one shown in the result

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
    COUNT(*) FILTER (WHERE estado IN ('Máquina en operación', 'Actividad media', 'Parada probable')) AS horas_trabajadas
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

### PQ7 - Query to count the working hours each day and the number of times the machine stopped working during the day

```sql
WITH cambios AS (
  -- Unimos logs de tipo FLOAT y STRING
  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_float a
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'

  UNION ALL

  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_string a
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-03-15 23:59:59'
),

ordenado AS (
  SELECT
    dt,
    date(dt) AS fecha,
    LAG(dt) OVER (PARTITION BY date(dt) ORDER BY dt) AS dt_anterior
  FROM cambios
),

-- Detectar pausas entre registros
intervalos AS (
  SELECT
    fecha,
    dt_anterior,
    dt,
    EXTRACT(EPOCH FROM (dt - dt_anterior)) / 60 AS minutos_diff,
    CASE
      WHEN dt_anterior IS NULL THEN 0
      WHEN EXTRACT(EPOCH FROM (dt - dt_anterior)) / 60 > 10 THEN 1
      ELSE 0
    END AS es_parada
  FROM ordenado
),

-- Agrupar intervalos continuos de actividad
bloques AS (
  SELECT
    fecha,
    MIN(dt_anterior) FILTER (WHERE es_parada = 0) AS inicio_bloque,
    MAX(dt) FILTER (WHERE es_parada = 0) AS fin_bloque,
    SUM(
      CASE WHEN es_parada = 0 THEN EXTRACT(EPOCH FROM (dt - dt_anterior)) ELSE 0 END
    ) / 3600.0 AS horas_operacion,
    SUM(es_parada) AS paradas
  FROM intervalos
  GROUP BY fecha
)

SELECT
  b.fecha,
  CASE EXTRACT(DOW FROM b.fecha)
    WHEN 0 THEN 'Domingo'
    WHEN 1 THEN 'Lunes'
    WHEN 2 THEN 'Martes'
    WHEN 3 THEN 'Miércoles'
    WHEN 4 THEN 'Jueves'
    WHEN 5 THEN 'Viernes'
    WHEN 6 THEN 'Sábado'
  END AS dia_semana,
  ROUND(SUM(b.horas_operacion), 2) AS horas_operacion,
  SUM(b.paradas) AS numero_paradas
FROM bloques b
GROUP BY b.fecha
ORDER BY b.fecha;
```


### PQ8 - Query to count the working hours each day

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

### PQ9 - Query for identifying NaNs in time intervals

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
```

### PQ10 - Query for identifying the variables that have registered NaNs

```sql
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

### AQ1 - Query to identify the different types of alarms

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

### QE1 - Query to unite float and string data

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


### QE2 - Query to count the amount of variables that change during a time period (in this case, every hour)

```sql
SELECT count(distinct(id_var)) ,to_timestamp(ROUND((TRUNC(CAST(date as bigint)/1000) / 3600))*3600) 
as dt FROM "public"."variable_log_float" 
WHERE to_timestamp(TRUNC(CAST(date as bigint)/1000)) >= '2020-12-28 00:00:00+01' 
and to_timestamp(TRUNC(CAST(date as bigint)/1000)) < '2021-01-10 06:00:00+01'
group by dt
```

### QE3 - Query to identify the minimum and maximum date present in the database

```sql
SELECT to_timestamp(cast(min(date) as bigint)/ 1000) AS min_date, 
to_timestamp(cast(max(date) as bigint)/ 1000) AS max_date 
FROM "public"."variable_log_string";
```

### QE4 - Query for details of the values captured for every variable in a given timeframe (for string or float data)

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

## UI/UX QUERIES ##

### UQ1: Basic statistical data for the temperature variables

```sql
SELECT
  v.name AS variable,
  ROUND(MIN(a.value)::numeric, 2) AS min_value,
  ROUND(AVG(a.value)::numeric, 2) AS avg_value,
  ROUND(MAX(a.value)::numeric, 2) AS max_value,
  ROUND(STDDEV(a.value)::numeric, 2) AS stddev_value
FROM variable_log_float a
JOIN variable v ON a.id_var = v.id
WHERE v.name ILIKE '%temp%'
  AND a.value IS NOT NULL
  AND a.value != 'NaN'
  AND a.value NOT IN ('Infinity', '-Infinity')
GROUP BY v.name
ORDER BY v.name;
```

### UQ2: Query to know the percentage of zeros that are stored in the temperature variables

```sql
SELECT
  v.name AS variable,
  COUNT(*) AS total_registros,

  -- Valores iguales a 0
  COUNT(*) FILTER (
    WHERE a.value::text = '0' OR a.value::text = '0.0'
  ) AS cantidad_ceros,
  ROUND(
    100.0 * COUNT(*) FILTER (
      WHERE a.value::text = '0' OR a.value::text = '0.0'
    ) / COUNT(*),
    2
  ) AS porcentaje_ceros,

  -- Valores que son NaN, inf, Infinity, -inf o NULL
  COUNT(*) FILTER (
    WHERE a.value::text ILIKE '%nan%'
       OR a.value::text ILIKE '%inf%'
       OR a.value IS NULL
  ) AS cantidad_nan,
  ROUND(
    100.0 * COUNT(*) FILTER (
      WHERE a.value::text ILIKE '%nan%'
         OR a.value::text ILIKE '%inf%'
         OR a.value IS NULL
    ) / COUNT(*),
    2
  ) AS porcentaje_nan

FROM variable_log_float a
JOIN variable v ON a.id_var = v.id
WHERE v.name ILIKE '%temp%'
GROUP BY v.name
ORDER BY porcentaje_nan DESC, porcentaje_ceros DESC;
```

<img width="539" height="291" alt="image" src="https://github.com/user-attachments/assets/f9059ed7-4bb4-4373-92d9-ebc8788e1097" />

###### Thanks to the UQ2 we know that these variables seem to be useless for determining the temperatures to measure the performance of the machine, and the variables to use would be the following ones:

<img width="538" height="241" alt="image" src="https://github.com/user-attachments/assets/5ddefb77-8f1d-46e5-aff0-44147dd9473e" />

```
TEMPERATURE_MOTOR_8
TEMPERATURE_MOTOR_5
TEMPERATURE_HEAD
TEMPERATURE_RAM_2
TEMPERATURE_RAM
TEMPERATURE_BASE
SPINDLE_1_TEMPERATURE
TEMPERATURE_MOTOR_Z
TEMPERATURE_MOTOR_Y
TEMPERATURA_MOTOR_8
TEMPERATURE_MOTOR_X
TEMPERATURE_SPINDLE_1
TEMPERATURA_MOTOR_5
SPINDLE_TEMP
TEMPERATURA_BASE
TEMPERATURA_CABEZAL
TEMPERATURA_CARNERO
TEMPERATURA_CARNERO_2
```

### UQ3: Values for the relevant temperature variables

```sql
SELECT 
  b.name AS variable,
  -- Convertimos el timestamp de milisegundos a segundos
  to_timestamp(CAST(a.date AS bigint) / 1000) AS dt,
  a.value
FROM "public"."variable_log_float" a
JOIN variable b ON a.id_var = b.id
WHERE 
  -- 1. Filtro de fecha y hora
  to_timestamp(CAST(a.date AS bigint) / 1000) >= '2021-01-04 13:39:30+01'
  AND to_timestamp(CAST(a.date AS bigint) / 1000) < '2021-01-05 22:00:00+01'
  
  -- 2. Filtro de los nombres de variable
  AND b.name IN (
    'TEMPERATURE_MOTOR_8', 'TEMPERATURE_MOTOR_5', 'TEMPERATURE_HEAD', 
    'TEMPERATURE_RAM_2', 'TEMPERATURE_RAM', 'TEMPERATURE_BASE', 
    'SPINDLE_1_TEMPERATURE', 'TEMPERATURE_MOTOR_Z', 'TEMPERATURE_MOTOR_Y', 
    'TEMPERATURA_MOTOR_8', 'TEMPERATURE_MOTOR_X', 'TEMPERATURE_SPINDLE_1', 
    'TEMPERATURA_MOTOR_5', 'SPINDLE_TEMP', 'TEMPERATURA_BASE', 
    'TEMPERATURA_CABEZAL', 'TEMPERATURA_CARNERO', 'TEMPERATURA_CARNERO_2'
  )
ORDER BY 
  variable, dt;
```




```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
library(DBI)
library(RPostgres)

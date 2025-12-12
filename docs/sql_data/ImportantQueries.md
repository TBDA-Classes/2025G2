# Important queries


### Machine Utilization (Percentages)

```sql
WITH RangoTiempo AS (
    SELECT 
        '2021-01-07 00:00:00'::timestamp AS inicio, 
        '2021-01-16 00:00:00'::timestamp AS fin
),
-- 1. Resumen Tabla FLOAT
ResumenFloat AS (
    SELECT 
        to_timestamp(floor(extract(epoch from to_timestamp(TRUNC(CAST(date AS bigint)/1000))) / 600) * 600) AS inicio_bloque,
        COUNT(*) AS cnt,
        MIN(date) AS min_ms,
        MAX(date) AS max_ms
    FROM variable_log_float
    WHERE to_timestamp(TRUNC(CAST(date AS bigint)/1000)) BETWEEN (SELECT inicio FROM RangoTiempo) AND (SELECT fin FROM RangoTiempo)
    GROUP BY 1
),
-- 2. Resumen Tabla STRING
ResumenString AS (
    SELECT 
        to_timestamp(floor(extract(epoch from to_timestamp(TRUNC(CAST(date AS bigint)/1000))) / 600) * 600) AS inicio_bloque,
        COUNT(*) AS cnt,
        MIN(date) AS min_ms,
        MAX(date) AS max_ms
    FROM variable_log_string
    WHERE to_timestamp(TRUNC(CAST(date AS bigint)/1000)) BETWEEN (SELECT inicio FROM RangoTiempo) AND (SELECT fin FROM RangoTiempo)
    GROUP BY 1
),
-- 3. Consolidar Totales
TotalActivity AS (
    SELECT 
        COALESCE(f.inicio_bloque, s.inicio_bloque) AS inicio_bloque,
        (COALESCE(f.cnt, 0) + COALESCE(s.cnt, 0)) AS cambios_totales,
        LEAST(f.min_ms, s.min_ms) AS min_ts_real, 
        GREATEST(f.max_ms, s.max_ms) AS max_ts_real
    FROM ResumenFloat f
    FULL OUTER JOIN ResumenString s ON f.inicio_bloque = s.inicio_bloque
),
-- 4. Grilla de Bloques de 10 min
GrillaBloques AS (
    SELECT generate_series(
        (SELECT inicio FROM RangoTiempo), 
        (SELECT fin FROM RangoTiempo) - interval '10 minutes', 
        '10 minutes'
    ) AS inicio_bloque
),
-- 5. Clasificar Estados
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
            WHEN COALESCE(t.cambios_totales, 0) = 0 THEN g.inicio_bloque
            ELSE to_timestamp(t.min_ts_real / 1000.0) 
        END AS start_ts,
        CASE 
            WHEN COALESCE(t.cambios_totales, 0) = 0 THEN (g.inicio_bloque + interval '10 minutes')
            ELSE to_timestamp(t.max_ts_real / 1000.0) 
        END AS end_ts
    FROM GrillaBloques g
    LEFT JOIN TotalActivity t ON g.inicio_bloque = t.inicio_bloque
),
-- 6. Fusión de Bloques Contiguos (Gantt General)
MarcadoGrupos AS (
    SELECT *, CASE WHEN estado = LAG(estado) OVER (ORDER BY inicio_bloque) THEN 0 ELSE 1 END AS es_nuevo_grupo
    FROM Clasificacion
),
AsignacionGrupos AS (
    SELECT *, SUM(es_nuevo_grupo) OVER (ORDER BY inicio_bloque) AS grupo_id
    FROM MarcadoGrupos
),
GruposColapsados AS (
    SELECT
        grupo_id, MAX(estado) AS estado, MIN(inicio_bloque) AS orden,
        MIN(start_ts) AS raw_start, MAX(end_ts) AS raw_end
    FROM AsignacionGrupos
    GROUP BY grupo_id
),
TimelineRaw AS (
    SELECT
        estado,
        COALESCE(raw_start, LAG(raw_end) OVER (ORDER BY orden), (SELECT inicio FROM RangoTiempo)) AS hora_inicio,
        COALESCE(raw_end, LEAD(raw_start) OVER (ORDER BY orden), (SELECT fin FROM RangoTiempo)) AS hora_fin
    FROM GruposColapsados
),
-- 7. GENERACIÓN DE DÍAS (Para no saltarnos ninguno)
SerieDias AS (
    SELECT generate_series(
        (SELECT inicio FROM RangoTiempo), 
        (SELECT fin FROM RangoTiempo) - interval '1 day', 
        '1 day'
    ) AS dia_referencia
),
-- 8. CORTE POR DÍAS (La magia para que sea exacto por día)
EventosPorDia AS (
    SELECT 
        d.dia_referencia,
        t.estado,
        -- Intersección del evento con el día actual
        GREATEST(t.hora_inicio, d.dia_referencia) AS inicio_corte,
        LEAST(t.hora_fin, d.dia_referencia + interval '1 day' - interval '1 second') AS fin_corte
    FROM TimelineRaw t
    JOIN SerieDias d ON 
        t.hora_inicio < (d.dia_referencia + interval '1 day') AND 
        t.hora_fin > d.dia_referencia
)
-- 9. SELECT FINAL RESUMIDO
SELECT
    date(dia_referencia) AS fecha,
    TO_CHAR(dia_referencia, 'Day') AS dia_semana,
    estado,
    -- Suma de duraciones exactas dentro de ese día
    ROUND(SUM(EXTRACT(EPOCH FROM (fin_corte - inicio_corte))) / 3600.0, 2) AS tiempo_horas,
    -- Porcentaje exacto del día
    ROUND((SUM(EXTRACT(EPOCH FROM (fin_corte - inicio_corte))) / 86400.0) * 100, 2) AS porcentaje_dia
FROM EventosPorDia
WHERE fin_corte > inicio_corte -- Filtrar segmentos inválidos mínimos
GROUP BY 1, 2, 3
ORDER BY fecha, estado;
```




### Program History (24 Hours)

```sql
WITH RangoTiempo AS (
    SELECT 
        '2021-01-07 00:00:00'::timestamp AS inicio, 
        '2021-01-16 00:00:00'::timestamp AS fin
),
-- 1. Buscar el estado inicial (el último log ANTES del rango para rellenar desde las 00:00)
EstadoPrevio AS (
    SELECT 
        (SELECT inicio FROM RangoTiempo) AS dt, -- Forzamos que empiece al inicio del rango
        CAST(value AS integer) AS estado_numerico
    FROM variable_log_float
    WHERE id_var = 581
      AND to_timestamp(TRUNC(CAST(date AS bigint)/1000)) < (SELECT inicio FROM RangoTiempo)
      AND value >= 0 AND value < 1000 -- Filtro de seguridad
    ORDER BY date DESC
    LIMIT 1
),
-- 2. Logs dentro del rango
LogsRango AS (
    SELECT 
        to_timestamp(TRUNC(CAST(date AS bigint)/1000)) AS dt,
        CAST(value AS integer) AS estado_numerico 
    FROM variable_log_float
    WHERE id_var = 581 
      AND to_timestamp(TRUNC(CAST(date AS bigint)/1000)) BETWEEN (SELECT inicio FROM RangoTiempo) AND (SELECT fin FROM RangoTiempo)
      AND value >= 0 AND value < 1000
),
-- 3. Unir: Estado Inicial + Logs del Rango
LogsCompletos AS (
    SELECT dt, estado_numerico FROM EstadoPrevio
    UNION ALL
    SELECT dt, estado_numerico FROM LogsRango
),
-- 4. Calcular Intervalos
Intervalos AS (
    SELECT 
        dt AS hora_inicio,
        LEAD(dt) OVER (ORDER BY dt) AS hora_fin_raw,
        estado_numerico
    FROM LogsCompletos
),
-- 5. Cerrar último intervalo
IntervalosCerrados AS (
    SELECT
        hora_inicio,
        COALESCE(hora_fin_raw, (SELECT fin FROM RangoTiempo)) AS hora_fin,
        estado_numerico
    FROM Intervalos
),
-- 6. Serie de Días
SerieDias AS (
    SELECT generate_series(
        (SELECT date_trunc('day', inicio) FROM RangoTiempo), 
        (SELECT date_trunc('day', fin) FROM RangoTiempo), 
        '1 day'
    ) AS dia_referencia
),
-- 7. Corte Diario
CortePorDias AS (
    SELECT 
        d.dia_referencia,
        i.estado_numerico,
        GREATEST(i.hora_inicio, d.dia_referencia) AS inicio_real,
        LEAST(i.hora_fin, d.dia_referencia + interval '1 day') AS fin_real
    FROM IntervalosCerrados i
    JOIN SerieDias d ON 
        i.hora_inicio < (d.dia_referencia + interval '1 day') AND 
        i.hora_fin > d.dia_referencia
)
-- 8. SELECT FINAL (Sin columna de texto)
SELECT
    date(dia_referencia) AS fecha,
    TO_CHAR(dia_referencia, 'Day') AS dia_semana,
    estado_numerico,
    -- Duración exacta en segundos
    ROUND(SUM(EXTRACT(EPOCH FROM (fin_real - inicio_real))), 2) AS duracion_segundos
FROM CortePorDias
WHERE fin_real > inicio_real
GROUP BY 1, 2, 3
ORDER BY fecha, duracion_segundos DESC;
```

### Temperature History (24 Hours)

```sql
SELECT 
  b.name AS variable,
  -- Miliseconds to seconds
  to_timestamp(CAST(a.date AS bigint) / 1000) AS dt,
  a.value
FROM "public"."variable_log_float" a
JOIN variable b ON a.id_var = b.id
WHERE 
  -- 1. Date and hour filter
  to_timestamp(CAST(a.date AS bigint) / 1000) >= '2021-01-04 13:39:30+01'
  AND to_timestamp(CAST(a.date AS bigint) / 1000) < '2021-01-05 22:00:00+01'
  
  -- 2. Variable names filter
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


### Hourly consumption

```sql
WITH params AS (
  SELECT
    TIMESTAMPTZ '2022-02-23 00:00:00+00' AS start_ts,
    TIMESTAMPTZ '2022-02-24 00:00:00+00' AS end_ts
),

motor_cfg AS (
  SELECT v.id, v.name, cfg.nominal_kw
  FROM (
    VALUES
      ('AXIS_X_MOTOR_UTILIZACION', 15.1::float8),
      ('AXIS_Y_MOTOR_UTILIZATION', 15.1::float8),
      ('AXIS_Z_MOTOR_UTILIZACION', 15.71::float8),
      ('SPINDLE_LOAD_1',          37.0::float8)
  ) AS cfg(var_name, nominal_kw)
  JOIN variable v ON v.name = cfg.var_name
),

raw AS (
  SELECT
    v.name                      AS motor,
    TO_TIMESTAMP(f.date/1000.0) AS ts,
    f.value::float8             AS util_pct,
    mc.nominal_kw
  FROM variable_log_float f
  JOIN motor_cfg mc ON mc.id = f.id_var
  JOIN variable   v ON v.id = f.id_var
  CROSS JOIN params p
  WHERE TO_TIMESTAMP(f.date/1000.0) >= p.start_ts
    AND TO_TIMESTAMP(f.date/1000.0) <  p.end_ts
    AND f.value IS NOT NULL
    AND f.value::text NOT ILIKE '%nan%'
    AND f.value::text NOT ILIKE '%inf%'
),

seg AS (
  SELECT
    motor,
    ts,
    LEAD(ts) OVER (PARTITION BY motor ORDER BY ts) AS ts_next,
    util_pct,
    nominal_kw
  FROM raw
),

seg_clamped AS (
  SELECT
    s.motor,
    s.ts,
    CASE
      WHEN s.ts_next IS NULL OR s.ts_next > p.end_ts THEN p.end_ts
      ELSE s.ts_next
    END AS ts_next,
    s.util_pct,
    s.nominal_kw
  FROM seg s
  CROSS JOIN params p
  WHERE s.ts < p.end_ts
),

segments_energy AS (
  SELECT
    motor,
    ts,
    ts_next,
    (util_pct/100.0 * nominal_kw)
      * EXTRACT(EPOCH FROM (ts_next - ts)) / 3600.0
      AS energy_kwh
  FROM seg_clamped
)

SELECT
  date_trunc('hour', ts)              AS hour_ts,
  ROUND(SUM(energy_kwh)::numeric, 3)  AS energy_kwh
FROM segments_energy
GROUP BY date_trunc('hour', ts)
ORDER BY hour_ts;
```



### Energy by Shift

```sql
WITH params AS (
  SELECT
    TIMESTAMPTZ '2022-02-23 00:00:00+00' AS start_ts,
    TIMESTAMPTZ '2022-02-24 00:00:00+00' AS end_ts
),

motor_cfg AS (
  SELECT v.id, v.name, cfg.nominal_kw
  FROM (
    VALUES
      ('AXIS_X_MOTOR_UTILIZACION', 15.1::float8),
      ('AXIS_Y_MOTOR_UTILIZATION', 15.1::float8),
      ('AXIS_Z_MOTOR_UTILIZACION', 15.71::float8),
      ('SPINDLE_LOAD_1',          37.0::float8)
  ) AS cfg(var_name, nominal_kw)
  JOIN variable v ON v.name = cfg.var_name
),

raw AS (
  SELECT
    v.name                      AS motor,
    TO_TIMESTAMP(f.date/1000.0) AS ts,
    f.value::float8             AS util_pct,
    mc.nominal_kw
  FROM variable_log_float f
  JOIN motor_cfg mc ON mc.id = f.id_var
  JOIN variable   v ON v.id = f.id_var
  CROSS JOIN params p
  WHERE TO_TIMESTAMP(f.date/1000.0) >= p.start_ts
    AND TO_TIMESTAMP(f.date/1000.0) <  p.end_ts
    AND f.value IS NOT NULL
    AND f.value::text NOT ILIKE '%nan%'
    AND f.value::text NOT ILIKE '%inf%'
),

seg AS (
  SELECT
    motor,
    ts,
    LEAD(ts) OVER (PARTITION BY motor ORDER BY ts) AS ts_next,
    util_pct,
    nominal_kw
  FROM raw
),

seg_clamped AS (
  SELECT
    s.motor,
    s.ts,
    CASE
      WHEN s.ts_next IS NULL OR s.ts_next > p.end_ts THEN p.end_ts
      ELSE s.ts_next
    END AS ts_next,
    s.util_pct,
    s.nominal_kw
  FROM seg s
  CROSS JOIN params p
  WHERE s.ts < p.end_ts
),

segments_energy AS (
  SELECT
    motor,
    ts,
    ts_next,
    (util_pct/100.0 * nominal_kw)
      * EXTRACT(EPOCH FROM (ts_next - ts)) / 3600.0
      AS energy_kwh
  FROM seg_clamped
),

by_shift AS (
  SELECT
    CASE
      WHEN EXTRACT(HOUR FROM ts) >= 6
       AND EXTRACT(HOUR FROM ts) < 14 THEN 'Day (06-14)'
      WHEN EXTRACT(HOUR FROM ts) >= 14
       AND EXTRACT(HOUR FROM ts) < 22 THEN 'Swing (14-22)'
      ELSE 'Night (22-06)'
    END AS shift_name,
    energy_kwh
  FROM segments_energy
)

SELECT
  shift_name,
  ROUND(SUM(energy_kwh)::numeric, 3) AS energy_kwh
FROM by_shift
GROUP BY shift_name
ORDER BY
  CASE shift_name
    WHEN 'Night (22-06)' THEN 1
    WHEN 'Day (06-14)'   THEN 2
    WHEN 'Swing (14-22)' THEN 3
  END;
```

### PQ1 - Initial query to identify the hours in which variable changes are registered

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


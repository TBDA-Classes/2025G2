# Important queries


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

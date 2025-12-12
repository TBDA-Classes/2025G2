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

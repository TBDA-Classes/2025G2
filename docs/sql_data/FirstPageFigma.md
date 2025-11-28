
---
SQL Queries for Figma Dashboard / Author: "Data analysis team"
---

### Machine Status Timeline (24 Hours)

```sql
WITH cambios AS (
  -- 1. BASE DE DATOS COMÚN: Unimos logs de FLOAT y STRING
  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_float a
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'

  UNION ALL

  SELECT
    to_timestamp(TRUNC(CAST(a.date AS bigint)/1000)) AS dt
  FROM variable_log_string a
  WHERE to_timestamp(TRUNC(CAST(a.date AS bigint)/1000))
        BETWEEN '2021-01-07 00:00:00' AND '2021-01-15 23:59:59'
),

ordenado AS (
  -- 2. ORDENAMIENTO PREVIO: Necesario para ambas lógicas
  SELECT
    dt,
    date(dt) AS fecha,
    -- LAG para detectar inicio de operaciones (mirar atrás)
    LAG(dt) OVER (PARTITION BY date(dt) ORDER BY dt) AS dt_anterior,
    -- LEAD para detectar huecos de paradas (mirar adelante)
    LEAD(dt) OVER (PARTITION BY date(dt) ORDER BY dt) AS dt_siguiente
  FROM cambios
),

-- ==========================================
-- LOGICA 1: CÁLCULO DE OPERACIONES (BLOQUES)
-- ==========================================
marcado_ops AS (
  SELECT
    fecha,
    dt,
    CASE
      WHEN dt_anterior IS NULL THEN 1
      WHEN EXTRACT(EPOCH FROM (dt - dt_anterior)) > 600 THEN 1
      ELSE 0
    END AS nueva_sesion
  FROM ordenado
),

bloques_ops AS (
  SELECT
    fecha,
    dt,
    SUM(nueva_sesion) OVER (PARTITION BY fecha ORDER BY dt) AS bloque_id
  FROM marcado_ops
),

final_operaciones AS (
  SELECT
    'OPERACION' AS tipo_evento,
    fecha,
    MIN(dt) AS inicio,
    MAX(dt) AS fin,
    ROUND(EXTRACT(EPOCH FROM (MAX(dt) - MIN(dt)))/3600.0, 2) AS horas
  FROM bloques_ops
  GROUP BY fecha, bloque_id
),

-- ==========================================
-- LOGICA 2: CÁLCULO DE PARADAS (HUECOS)
-- ==========================================
final_paradas AS (
  SELECT
    'PARADA' AS tipo_evento,
    fecha,
    dt AS inicio, -- La parada empieza en el registro actual
    dt_siguiente AS fin, -- y termina en el siguiente
    ROUND(EXTRACT(EPOCH FROM (dt_siguiente - dt))/3600.0, 2) AS horas
  FROM ordenado
  WHERE dt_siguiente IS NOT NULL
    AND EXTRACT(EPOCH FROM (dt_siguiente - dt)) > 600 -- Solo huecos > 10 min
)

-- ==========================================
-- UNIÓN Y FORMATO FINAL
-- ==========================================
SELECT
  tipo_evento,
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
  inicio AS hora_inicio,
  fin AS hora_fin,
  horas AS duracion_horas
FROM (
    SELECT * FROM final_operaciones
    UNION ALL
    SELECT * FROM final_paradas
) tabla_unificada
ORDER BY fecha, hora_inicio;
```



### Program History Graph 

#### (Note: 3 variables were detected that could be related to program history (Operating_mode and Prog_Status are enumeral, Prog_Line is a number and is described as the program block number)

```sql
SELECT
  b.name AS variable,
  -- Timestamp conversion from miliseconds to seconds
  TO_TIMESTAMP(CAST(a.date AS BIGINT) / 1000) AS dt,
  a.value
FROM
  "public"."variable_log_float" a
JOIN
  variable b ON a.id_var = b.id
WHERE
  -- 1. Date and hour filter (Custom date)
  TO_TIMESTAMP(CAST(a.date AS BIGINT) / 1000) >= '2021-01-04 13:39:30+01'
  AND TO_TIMESTAMP(CAST(a.date AS BIGINT) / 1000) < '2021-01-05 22:00:00+01'

  -- 2. Variables used to classify program history
  AND b.name IN (
    'OPERATING_MODE',
    'PROG_LINE',
    'PROG_STATUS'
  )
  
  -- 3. NaN/NULL values excluded
  AND a.value IS NOT NULL
  AND CAST(a.value AS TEXT) <> 'NaN'
  
ORDER BY
  variable,
  dt;
```



```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
library(DBI)
library(RPostgres)

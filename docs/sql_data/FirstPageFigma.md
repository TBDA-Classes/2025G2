
---

title: "SQL Queries for Figma Dashboard" 
author: "Data analysis team"
output: html_document

---


### Program History Graph

```sql
SELECT
  b.name AS variable,
  -- Convertimos el timestamp de milisegundos a segundos
  TO_TIMESTAMP(CAST(a.date AS BIGINT) / 1000) AS dt,
  a.value
FROM
  "public"."variable_log_float" a
JOIN
  variable b ON a.id_var = b.id
WHERE
  -- 1. Filtro de fecha y hora (Rango original)
  TO_TIMESTAMP(CAST(a.date AS BIGINT) / 1000) >= '2021-01-04 13:39:30+01'
  AND TO_TIMESTAMP(CAST(a.date AS BIGINT) / 1000) < '2021-01-05 22:00:00+01'

  -- 2. Filtro de los nombres de variable (solo las tres solicitadas)
  AND b.name IN (
    'OPERATING_MODE',
    'PROG_LINE',
    'PROG_STATUS'
  )
  
  -- 3. EXCLUSIÓN DE VALORES NULOS/NaN (Condiciones Agregadas)
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

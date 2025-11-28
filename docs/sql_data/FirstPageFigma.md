
---
SQL Queries for Figma Dashboard / Author: "Data analysis team"
---


### Program History Graph

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

### 1. Count per category (Emergency, Error, Alert)

```sql
WITH alarm_data AS (
    SELECT
        a.date,
        TRIM(elem ->> 0) AS alarm_code,
        TRIM(elem ->> 1) AS alarm_description,
        to_timestamp(a.date / 1000) as timestamp
    FROM variable_log_string a
    JOIN variable b ON a.id_var = b.id
    CROSS JOIN LATERAL jsonb_array_elements(a.value::jsonb) AS elem
    WHERE b.id = 447  -- ALARMS variable
      AND a.value IS NOT NULL
      AND a.value != '[]'
      AND to_timestamp(a.date / 1000)::date = '2022-02-23'::date
),
categorized AS (
    SELECT
        alarm_code,
        alarm_description,
        CASE
            WHEN alarm_description ILIKE '%emerg%' THEN 'Emergency'
            WHEN alarm_description ILIKE '%error%' OR 
                 alarm_description ILIKE '%err%' OR
                 alarm_description ILIKE '%fallo%' OR
                 alarm_description ILIKE '%fault%' THEN 'Error'
            WHEN alarm_description ILIKE '%alert%' OR 
                 alarm_description ILIKE '%alarm%' OR 
                 alarm_description ILIKE '%warn%' OR
                 alarm_description ILIKE '%aviso%' OR
                 alarm_description ILIKE '%attention%' THEN 'Alert'
            ELSE 'Other'
        END AS category
    FROM alarm_data
)
SELECT 
    COUNT(*) as total_alerts,
    SUM(CASE WHEN category = 'Emergency' THEN 1 ELSE 0 END) as emergency_count,
    SUM(CASE WHEN category = 'Error' THEN 1 ELSE 0 END) as error_count,
    SUM(CASE WHEN category = 'Alert' THEN 1 ELSE 0 END) as alert_count
FROM categorized
```

### COUNT BY SHIFT (06–14, 14–22, 22–06) AND CATEGORY

```sql
WITH alarm_data AS (
    SELECT
        a.date,
        TRIM(elem ->> 0) AS alarm_code,
        TRIM(elem ->> 1) AS alarm_description,
        to_timestamp(a.date / 1000) as timestamp
    FROM variable_log_string a
    JOIN variable b ON a.id_var = b.id
    CROSS JOIN LATERAL jsonb_array_elements(a.value::jsonb) AS elem
    WHERE b.id = 447
      AND a.value IS NOT NULL
      AND a.value != '[]'
      AND to_timestamp(a.date / 1000)::date = '2022-02-23'::date
),
categorized AS (
    SELECT
        timestamp,
        alarm_code,
        alarm_description,
        CASE
            WHEN alarm_description ILIKE '%emerg%' THEN 'Emergency'
            WHEN alarm_description ILIKE '%error%' OR 
                 alarm_description ILIKE '%err%' OR
                 alarm_description ILIKE '%fallo%' OR
                 alarm_description ILIKE '%fault%' THEN 'Error'
            WHEN alarm_description ILIKE '%alert%' OR 
                 alarm_description ILIKE '%alarm%' OR 
                 alarm_description ILIKE '%warn%' OR
                 alarm_description ILIKE '%aviso%' OR
                 alarm_description ILIKE '%attention%' THEN 'Alert'
            ELSE 'Other'
        END AS category,
        CASE 
            WHEN EXTRACT(HOUR FROM timestamp) >= 6 AND EXTRACT(HOUR FROM timestamp) < 14 THEN 'Shift 1 (06:00-14:00)'
            WHEN EXTRACT(HOUR FROM timestamp) >= 14 AND EXTRACT(HOUR FROM timestamp) < 22 THEN 'Shift 2 (14:00-22:00)'
            ELSE 'Shift 3 (22:00-06:00)'
        END as shift
    FROM alarm_data
)
SELECT 
    shift,
    COUNT(*) as total_alerts,
    SUM(CASE WHEN category = 'Emergency' THEN 1 ELSE 0 END) as emergency_count,
    SUM(CASE WHEN category = 'Error' THEN 1 ELSE 0 END) as error_count,
    SUM(CASE WHEN category = 'Alert' THEN 1 ELSE 0 END) as alert_count
FROM categorized
WHERE category != 'Other'
GROUP BY shift
ORDER BY 
    CASE shift
        WHEN 'Shift 1 (06:00-14:00)' THEN 1
        WHEN 'Shift 2 (14:00-22:00)' THEN 2
        ELSE 3
    END;
```

### Full list of alerts

```sql
WITH alarm_data AS (
    SELECT
        a.date,
        TRIM(elem ->> 0) AS alarm_code,
        TRIM(elem ->> 1) AS alarm_description,
        to_timestamp(a.date / 1000) as timestamp
    FROM variable_log_string a
    JOIN variable b ON a.id_var = b.id
    CROSS JOIN LATERAL jsonb_array_elements(a.value::jsonb) AS elem
    WHERE b.id = 447
      AND a.value IS NOT NULL
      AND a.value != '[]'
      AND to_timestamp(a.date / 1000)::date = '2022-02-23'::date
),
categorized AS (
    SELECT
        timestamp,
        alarm_code,
        alarm_description,
        CASE
            WHEN alarm_description ILIKE '%emerg%' THEN 'Emergency'
            WHEN alarm_description ILIKE '%error%' OR 
                 alarm_description ILIKE '%err%' OR
                 alarm_description ILIKE '%fallo%' OR
                 alarm_description ILIKE '%fault%' THEN 'Error'
            WHEN alarm_description ILIKE '%alert%' OR 
                 alarm_description ILIKE '%alarm%' OR 
                 alarm_description ILIKE '%warn%' OR
                 alarm_description ILIKE '%aviso%' OR
                 alarm_description ILIKE '%attention%' THEN 'Alert'
            ELSE 'Other'
        END AS category
    FROM alarm_data
)
SELECT 
    category as alert_type,
    alarm_code,
    to_char(timestamp, 'HH24:MI:SS') as time,
    timestamp as full_timestamp
FROM categorized
WHERE category != 'Other'
ORDER BY timestamp DESC;
```

#### 3.1 Queries to filter by shift and category 

```sql
WITH alarm_data AS (
    SELECT
        a.date,
        TRIM(elem ->> 0) AS alarm_code,
        TRIM(elem ->> 1) AS alarm_description,
        to_timestamp(a.date / 1000) as timestamp
    FROM variable_log_string a
    JOIN variable b ON a.id_var = b.id
    CROSS JOIN LATERAL jsonb_array_elements(a.value::jsonb) AS elem
    WHERE b.id = 447
      AND a.value IS NOT NULL
      AND a.value != '[]'
      AND to_timestamp(a.date / 1000)::date = '2022-02-23'::date
),
categorized AS (
    SELECT
        timestamp,
        alarm_code,
        alarm_description,
        CASE
            WHEN alarm_description ILIKE '%emerg%' THEN 'Emergency'
            WHEN alarm_description ILIKE '%error%' OR 
                 alarm_description ILIKE '%err%' OR
                 alarm_description ILIKE '%fallo%' OR
                 alarm_description ILIKE '%fault%' THEN 'Error'
            WHEN alarm_description ILIKE '%alert%' OR 
                 alarm_description ILIKE '%alarm%' OR 
                 alarm_description ILIKE '%warn%' OR
                 alarm_description ILIKE '%aviso%' OR
                 alarm_description ILIKE '%attention%' THEN 'Alert'
            ELSE 'Other'
        END AS category,
        CASE 
            WHEN EXTRACT(HOUR FROM timestamp) >= 6 AND EXTRACT(HOUR FROM timestamp) < 14 THEN 'Shift 1'
            WHEN EXTRACT(HOUR FROM timestamp) >= 14 AND EXTRACT(HOUR FROM timestamp) < 22 THEN 'Shift 2'
            ELSE 'Shift 3'
        END as shift
    FROM alarm_data
)
SELECT 
    category as alert_type,
    alarm_code,
    to_char(timestamp, 'HH24:MI:SS') as time,
    timestamp as full_timestamp
FROM categorized
WHERE category != 'Other'
  AND (category = ANY('{Emergency,Error,Alert}'))  -- Replace array with selected categories
  AND (shift = ANY('{Shift 1,Shift 2,Shift 3}'))   -- Replace array with selected shifts
ORDER BY timestamp DESC;
 ```sql

### 4. Detail for single alarm code

```sql
WITH alarm_data AS (
    SELECT
        a.date,
        TRIM(elem ->> 0) AS alarm_code,
        TRIM(elem ->> 1) AS alarm_description,
        to_timestamp(a.date / 1000) as timestamp
    FROM variable_log_string a
    JOIN variable b ON a.id_var = b.id
    CROSS JOIN LATERAL jsonb_array_elements(a.value::jsonb) AS elem
    WHERE b.id = 447
      AND a.value IS NOT NULL
      AND a.value != '[]'
      AND to_timestamp(a.date / 1000)::date = '2022-02-23'::date
)
SELECT 
    CASE
        WHEN alarm_description ILIKE '%emerg%' THEN 'Emergency'
        WHEN alarm_description ILIKE '%error%' OR 
             alarm_description ILIKE '%err%' OR
             alarm_description ILIKE '%fallo%' OR
             alarm_description ILIKE '%fault%' THEN 'Error'
        WHEN alarm_description ILIKE '%alert%' OR 
             alarm_description ILIKE '%alarm%' OR 
             alarm_description ILIKE '%warn%' OR
             alarm_description ILIKE '%aviso%' OR
             alarm_description ILIKE '%attention%' THEN 'Alert'
        ELSE 'Other'
    END AS alert_type,
    timestamp::date as alert_date,
    CASE 
        WHEN EXTRACT(HOUR FROM timestamp) >= 6 AND EXTRACT(HOUR FROM timestamp) < 14 THEN 'Shift 1 (06:00-14:00)'
        WHEN EXTRACT(HOUR FROM timestamp) >= 14 AND EXTRACT(HOUR FROM timestamp) < 22 THEN 'Shift 2 (14:00-22:00)'
        ELSE 'Shift 3 (22:00-06:00)'
    END as shift,
    timestamp,
    alarm_code,
    alarm_description
FROM alarm_data
WHERE alarm_code = ? AND date = ?  -- Replace with specific criteria
```



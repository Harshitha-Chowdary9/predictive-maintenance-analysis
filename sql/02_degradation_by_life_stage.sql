-- How sensors change as machines approach failure (bucketed by remaining life)
SELECT CASE WHEN rul > 100 THEN '1: >100 cycles left'
            WHEN rul > 50  THEN '2: 51-100'
            WHEN rul > 20  THEN '3: 21-50'
            ELSE                '4: <=20' END AS stage,
       COUNT(*)                    AS n,
       ROUND(AVG(temp), 2)         AS avg_temp,
       ROUND(AVG(vibration), 3)    AS avg_vibration,
       ROUND(AVG(pressure), 2)     AS avg_pressure,
       ROUND(AVG(rpm), 1)          AS avg_rpm
FROM readings
GROUP BY stage
ORDER BY stage;

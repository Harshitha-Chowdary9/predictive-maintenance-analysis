-- Does running at higher load run hotter in the last 30 cycles of life?
SELECT op_load,
       COUNT(*)                 AS n,
       ROUND(AVG(temp), 2)      AS avg_temp,
       ROUND(AVG(vibration), 3) AS avg_vibration
FROM readings
WHERE rul <= 30
GROUP BY op_load
ORDER BY op_load;

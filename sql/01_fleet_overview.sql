-- Fleet size and lifetime statistics by production line and model
SELECT line, model,
       COUNT(*)                       AS machines,
       ROUND(AVG(lifetime_cycles), 1) AS avg_life,
       MIN(lifetime_cycles)           AS min_life,
       MAX(lifetime_cycles)           AS max_life
FROM machines
GROUP BY line, model
ORDER BY line, model;

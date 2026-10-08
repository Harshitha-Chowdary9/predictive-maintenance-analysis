-- For each machine: first cycle where a 5-cycle moving average of vibration
-- exceeds 0.7, and how many cycles before failure that warning arrives.
WITH ma AS (
  SELECT machine_id, cycle, rul,
         AVG(vibration) OVER (PARTITION BY machine_id ORDER BY cycle
                              ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS vib_ma
  FROM readings
), first_alert AS (
  SELECT machine_id, MIN(cycle) AS alert_cycle
  FROM ma WHERE vib_ma > 0.7 GROUP BY machine_id
)
SELECT m.machine_id, m.line, m.lifetime_cycles, f.alert_cycle,
       m.lifetime_cycles - f.alert_cycle AS lead_time_cycles
FROM machines m LEFT JOIN first_alert f USING (machine_id)
ORDER BY lead_time_cycles DESC;

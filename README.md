# Predictive Maintenance Analysis (Python + SQL)

End-to-end analysis of run-to-failure sensor data for a fleet of industrial machines:
SQL exploration, feature engineering, and models that estimate **remaining useful life (RUL)**
and flag machines **likely to fail within 30 cycles**.

The dataset is simulated (`src/generate_data.py`) with degradation that accelerates near failure,
similar in structure to NASA C-MAPSS. The pipeline works the same on real data with columns
`machine_id, cycle, op_load, temp, vibration, pressure, rpm, rul`.

## Structure

```
src/generate_data.py   simulate machines + sensor readings (CSV)
src/load_db.py         load CSVs into SQLite (data/maintenance.db)
src/analysis.py        run SQL, build rolling features, train models, save figures
sql/                   four analytical queries (window functions, CTEs, bucketing)
reports/               query outputs, metrics and plots
```

## Setup and usage

```bash
pip install -r requirements.txt
python src/generate_data.py --machines 100 --seed 42
python src/load_db.py
python src/analysis.py
```

## SQL queries

| File | Question |
|------|----------|
| `01_fleet_overview.sql` | Lifetime statistics by line and model |
| `02_degradation_by_life_stage.sql` | How each sensor shifts as failure approaches |
| `03_vibration_alert_lead_time.sql` | Warning lead time from a 5-cycle vibration moving average |
| `04_load_impact.sql` | Does operating load affect temperature near end of life? |

## Findings (seed 42, 100 machines)

- Vibration is the strongest degradation signal: mean 0.35 early in life vs 1.09 in the last 20 cycles.
  Temperature rises about 9 C, pressure drops about 10 units.
- A simple vibration moving-average alert (> 0.7) gives machines roughly 70+ cycles of warning.
- Higher load raises temperature near end of life (76 C at 0.5 load vs 82 C at full load), while vibration is load-independent.
- Gradient boosting on 10-cycle rolling features predicts RUL with MAE of about 3.9 cycles (RUL capped at 125).
- A random forest flags machines failing within 30 cycles with F1 of about 0.94 on the positive class.
- Train/test split is grouped by machine, so no machine leaks across the split.

Because the data is simulated, absolute numbers reflect the simulator; the value of the repo is the pipeline.

## Next steps

- Swap in NASA C-MAPSS or another real dataset
- Add survival analysis or an LSTM baseline
- Power BI dashboard on top of `maintenance.db`

# Study guide - interview questions this project prepares you for

Read this alongside the code. Every answer points at the file where you can
see the idea working.

## Problem framing

**Q: What is remaining useful life (RUL) and why predict it?**
RUL is how many operating cycles a machine has left before failure. The
business point is lead time: if you know a machine will fail within ~30
cycles, you schedule maintenance instead of eating unplanned downtime. This
repo tackles it two ways at once (`src/analysis.py`): regression that
estimates the RUL number, and classification that flags "fails within 30
cycles" - regression for planning, classification for alerting.

**Q: Why cap RUL at 125?**
Early in life the sensors carry almost no information about whether failure
is 130 or 300 cycles away, and the business does not care either. Capping
(a standard C-MAPSS practice) stops the model wasting capacity on
unknowable long-range values and focuses it where the signal is: near
failure.

## SQL

**Q: Show me a window function doing real work.**
`sql/03_vibration_alert_lead_time.sql`: a 5-cycle moving average per
machine with `AVG(vibration) OVER (PARTITION BY machine_id ORDER BY cycle
ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)`, then `MIN(cycle)` where the
average crosses 0.7, joined back to compute warning lead time in cycles.
One query answers "how early does a vibration alert fire before failure?"

**Q: How do the four SQL queries fit together?**
They move from description to decision: fleet lifetime overview
(`01`), how each sensor shifts as failure approaches (`02`, life-stage
bucketing), an actionable alert rule with lead time (`03`), and a confound
check - does load, not age, drive temperature (`04`). That order is how an
analyst builds a case, not just a chart dump.

## Machine learning

**Q: How did you avoid data leakage?**
`GroupShuffleSplit` on `machine_id` (`src/analysis.py`) - rows from one
machine are highly correlated over time, so a random row split would put
near-identical readings in both train and test and inflate scores. Grouping
by machine means the model is tested on machines it has never seen.

**Q: What features did you engineer and why?**
Per-machine rolling statistics over a 10-cycle window: moving average
(level), rolling std (instability), and difference vs 10 cycles ago
(trend). Raw sensor values at one instant say little about degradation;
the trajectory does. See `add_features` in `src/analysis.py`.

**Q: Regression MAE ~3.9 cycles, classifier F1 ~0.94 - how do you present
those honestly?**
By saying what they are: results on SIMULATED data from
`src/generate_data.py` (degradation accelerates near failure, C-MAPSS-like
structure). The README says exactly this - the value demonstrated is the
pipeline: SQL, features, leakage-safe split, two model families, saved
metrics and plots. Swapping in real C-MAPSS data is a documented next step.

**Q: Why gradient boosting / random forest instead of deep learning?**
Tabular sensor features, small data, CPU-only: gradient-boosted trees are
the strong baseline here, they train in seconds, and feature importance
comes for free (`reports/feature_importance.png`). An LSTM on raw sequences
is listed as a next step, not a claim.

## Engineering

**Q: How is the analysis reproducible?**
Fixed seeds end to end (`--seed 42` data generation, `random_state=0`
splits and models), query outputs written to `reports/*.csv`, metrics to
`reports/metrics.csv`. Anyone can rerun the three commands in the README
and get the same numbers.

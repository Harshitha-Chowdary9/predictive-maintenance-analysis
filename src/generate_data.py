"""Generate a synthetic run-to-failure sensor dataset for a fleet of machines.

Each machine has a random lifetime. Sensors drift as the machine degrades, so
the data mimics benchmarks like NASA C-MAPSS without needing a download.
Output: data/sensor_readings.csv (machine_id, cycle, op_load, temp, vibration,
pressure, rpm, rul) and data/machines.csv.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def simulate(n_machines: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    rows, meta = [], []
    lines = ["Line-A", "Line-B", "Line-C"]
    models = ["M100", "M200", "M300"]
    for m in range(1, n_machines + 1):
        life = int(rng.integers(150, 320))
        meta.append({"machine_id": m, "line": rng.choice(lines),
                     "model": rng.choice(models), "lifetime_cycles": life})
        base = rng.normal(0, 1, 4)
        for c in range(1, life + 1):
            wear = (c / life) ** 3  # degradation accelerates near failure
            load = rng.choice([0.5, 0.75, 1.0])
            rows.append({
                "machine_id": m, "cycle": c, "op_load": load,
                "temp": 70 + base[0] + 15 * wear * load + rng.normal(0, 1.0),
                "vibration": 0.30 + 0.02 * base[1] + 0.9 * wear + rng.normal(0, 0.04),
                "pressure": 100 + base[2] - 12 * wear + rng.normal(0, 1.2),
                "rpm": 1500 + 10 * base[3] - 60 * wear * load + rng.normal(0, 8),
                "rul": life - c,
            })
    return pd.DataFrame(rows), pd.DataFrame(meta)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--machines", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(exist_ok=True)
    readings, machines = simulate(a.machines, a.seed)
    readings.to_csv(out / "sensor_readings.csv", index=False)
    machines.to_csv(out / "machines.csv", index=False)
    print(f"{len(readings)} readings for {len(machines)} machines -> {out}/")

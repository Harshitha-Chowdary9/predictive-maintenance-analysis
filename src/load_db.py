"""Load the CSVs into a SQLite database (data/maintenance.db)."""
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    db = ROOT / "data" / "maintenance.db"
    con = sqlite3.connect(db)
    pd.read_csv(ROOT / "data" / "machines.csv").to_sql("machines", con, if_exists="replace", index=False)
    pd.read_csv(ROOT / "data" / "sensor_readings.csv").to_sql("readings", con, if_exists="replace", index=False)
    con.execute("CREATE INDEX IF NOT EXISTS idx_readings ON readings(machine_id, cycle)")
    con.commit(); con.close()
    print("loaded", db)


if __name__ == "__main__":
    main()

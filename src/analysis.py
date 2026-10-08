"""Run the SQL queries, build features, train an RUL model, and save figures."""
import sqlite3
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, classification_report
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SENSORS = ["temp", "vibration", "pressure", "rpm"]
WINDOW = 10
FAIL_HORIZON = 30  # label "will fail within 30 cycles"


def run_queries(con):
    for q in sorted((ROOT / "sql").glob("*.sql")):
        df = pd.read_sql_query(q.read_text(), con)
        print(f"\n== {q.name} ==")
        print(df.head(10).to_string(index=False))
        df.to_csv(REPORTS / f"{q.stem}.csv", index=False)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["machine_id", "cycle"]).copy()
    g = df.groupby("machine_id")
    for s in SENSORS:
        df[f"{s}_ma"] = g[s].transform(lambda x: x.rolling(WINDOW, min_periods=1).mean())
        df[f"{s}_std"] = g[s].transform(lambda x: x.rolling(WINDOW, min_periods=2).std()).fillna(0)
        df[f"{s}_delta"] = g[s].transform(lambda x: x.diff(WINDOW)).fillna(0)
    return df


def main():
    REPORTS.mkdir(exist_ok=True)
    con = sqlite3.connect(ROOT / "data" / "maintenance.db")
    run_queries(con)
    df = add_features(pd.read_sql_query("SELECT * FROM readings", con))
    feats = [c for c in df.columns if c not in ("machine_id", "rul")]

    # split by machine so no machine appears in both train and test
    gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=0)
    tr, te = next(gss.split(df, groups=df["machine_id"]))
    train, test = df.iloc[tr], df.iloc[te]

    # RUL regression (cap RUL at 125 as is common for C-MAPSS)
    cap = lambda y: np.minimum(y, 125)
    reg = GradientBoostingRegressor(random_state=0).fit(train[feats], cap(train["rul"]))
    pred = reg.predict(test[feats])
    mae = mean_absolute_error(cap(test["rul"]), pred)
    rmse = mean_squared_error(cap(test["rul"]), pred) ** 0.5
    print(f"\nRUL regression: MAE={mae:.2f} cycles, RMSE={rmse:.2f} cycles")

    # Failure-within-horizon classification
    clf = RandomForestClassifier(n_estimators=200, random_state=0, n_jobs=-1)
    clf.fit(train[feats], train["rul"] <= FAIL_HORIZON)
    cpred = clf.predict(test[feats])
    print(f"\nFailure within {FAIL_HORIZON} cycles:")
    print(classification_report(test["rul"] <= FAIL_HORIZON, cpred, digits=3))

    # figures
    fig, ax = plt.subplots(figsize=(7, 4))
    for m in df["machine_id"].unique()[:6]:
        d = df[df.machine_id == m]
        ax.plot(d["rul"], d["vibration_ma"], alpha=.7)
    ax.invert_xaxis(); ax.set_xlabel("Remaining useful life (cycles)")
    ax.set_ylabel("Vibration (10-cycle mean)"); ax.set_title("Vibration rises before failure")
    fig.tight_layout(); fig.savefig(REPORTS / "vibration_vs_rul.png", dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(cap(test["rul"]), pred, s=3, alpha=.3)
    ax.plot([0, 125], [0, 125], "r--"); ax.set_xlabel("True RUL"); ax.set_ylabel("Predicted RUL")
    ax.set_title(f"RUL prediction (MAE {mae:.1f})")
    fig.tight_layout(); fig.savefig(REPORTS / "rul_pred_vs_true.png", dpi=130); plt.close(fig)

    imp = pd.Series(reg.feature_importances_, index=feats).sort_values().tail(10)
    fig, ax = plt.subplots(figsize=(6, 4)); imp.plot.barh(ax=ax)
    ax.set_title("Top feature importances"); fig.tight_layout()
    fig.savefig(REPORTS / "feature_importance.png", dpi=130); plt.close(fig)

    pd.DataFrame({"metric": ["MAE", "RMSE"], "value": [mae, rmse]}).to_csv(REPORTS / "metrics.csv", index=False)


if __name__ == "__main__":
    main()

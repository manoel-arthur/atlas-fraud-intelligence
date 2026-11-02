#!/usr/bin/env python3
"""ATLAS | dados sintéticos reproduzíveis com perfis, sazonalidade e ruído.
Não representa transações ou taxas de fraude reais. Python 3.10+ (stdlib).
"""
import csv
import json
import math
import random
import sqlite3
from calendar import monthrange
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
SEED = 73619
COUNT = 2400
STATES = ("SP", "RJ", "MG", "BA", "PR")
WEIGHTS = (0.40, 0.22, 0.19, 0.11, 0.08)
COLUMNS = ("id", "date", "month", "state", "amount", "device", "night", "velocity", "foreign", "risk", "fraud")


def weighted_state(rng):
    return rng.choices(STATES, weights=WEIGHTS, k=1)[0]


def generate(seed=SEED, count=COUNT):
    """Latent customer profiles generate correlated behavior; fraud labels are noisy."""
    rng = random.Random(seed)
    customers = []
    for _ in range(420):
        customers.append({
            "state": weighted_state(rng),
            "typical_amount": rng.lognormvariate(4.8, 0.78),
            "digital": rng.betavariate(2.3, 5.0),
            "risk_propensity": rng.betavariate(1.4, 12.0),
        })

    records = []
    for i in range(count):
        month = i // (count // 12)
        customer = rng.choice(customers)
        seasonal = 1.18 if month in (10, 11) else (0.92 if month in (1, 6) else 1.0)
        amount = round(min(25000.0, max(5.0, customer["typical_amount"] *
                         rng.lognormvariate(0.0, 0.92) * seasonal)), 2)
        # Independent hidden pressure creates a weakly correlated fraud mechanism,
        # without deriving labels directly from the displayed score.
        hidden = rng.random() < (0.025 + customer["risk_propensity"] * 0.20)
        device = rng.random() < min(0.8, 0.09 + customer["digital"] * 0.22 + (0.25 if hidden else 0))
        night = rng.random() < (0.12 + (0.19 if hidden else 0))
        velocity = rng.random() < (0.075 + (0.34 if hidden else 0))
        foreign = rng.random() < (0.045 + (0.29 if hidden else 0))
        # Visible heuristic uses observed signals; noise prevents perfect ranking.
        score = max(0, min(100, round(
            8 + (17 if amount > 1800 else 0) + (23 if device else 0) +
            (12 if night else 0) + (25 if velocity else 0) +
            (21 if foreign else 0) + rng.gauss(0, 10)
        )))
        # Separate stochastic outcome model: even low-risk transactions may be fraud.
        logit = (-5.4 + (1.55 if hidden else 0) + (0.65 if device else 0) +
                 (0.70 if velocity else 0) + (0.65 if foreign else 0) +
                 (0.25 if night else 0) + (0.30 if amount > 1800 else 0) +
                 rng.gauss(0, 0.35))
        fraud = rng.random() < 1 / (1 + math.exp(-logit))
        day = rng.randint(1, monthrange(2026, month + 1)[1])
        records.append(dict(
            id=f"TX-{i + 1:05d}", date=date(2026, month + 1, day).isoformat(),
            month=month, state=customer["state"], amount=amount,
            device=device, night=night, velocity=velocity, foreign=foreign,
            risk=int(score), fraud=bool(fraud),
        ))
    return records


def validate(rows):
    assert len(rows) == COUNT
    assert len({r["id"] for r in rows}) == COUNT
    assert all(tuple(r) == COLUMNS for r in rows)
    assert all(0 <= r["risk"] <= 100 and r["amount"] > 0 for r in rows)
    assert all(r["date"].startswith(f'2026-{r["month"] + 1:02d}-') for r in rows)
    assert all(r["state"] in STATES for r in rows)


def main():
    OUT.mkdir(exist_ok=True)
    rows = generate()
    validate(rows)
    (OUT / "transacoes.json").write_text(
        json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    with (OUT / "transacoes.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    db = OUT / "atlas.sqlite"
    if db.exists():
        db.unlink()
    with sqlite3.connect(db) as conn:
        conn.execute("""CREATE TABLE transacoes (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL CHECK(length(date) = 10),
            month INTEGER NOT NULL CHECK(month BETWEEN 0 AND 11),
            state TEXT NOT NULL CHECK(state IN ('SP','RJ','MG','BA','PR')),
            amount REAL NOT NULL CHECK(amount > 0),
            device INTEGER NOT NULL CHECK(device IN (0,1)),
            night INTEGER NOT NULL CHECK(night IN (0,1)),
            velocity INTEGER NOT NULL CHECK(velocity IN (0,1)),
            foreign_location INTEGER NOT NULL CHECK(foreign_location IN (0,1)),
            risk INTEGER NOT NULL CHECK(risk BETWEEN 0 AND 100),
            fraud INTEGER NOT NULL CHECK(fraud IN (0,1)))""")
        conn.executemany("INSERT INTO transacoes VALUES (?,?,?,?,?,?,?,?,?,?,?)", [
            (r["id"], r["date"], r["month"], r["state"], r["amount"],
             int(r["device"]), int(r["night"]), int(r["velocity"]),
             int(r["foreign"]), r["risk"], int(r["fraud"])) for r in rows])
        conn.execute("CREATE INDEX idx_transacoes_date ON transacoes(date)")
        conn.execute("CREATE INDEX idx_transacoes_risk ON transacoes(risk)")
        conn.execute("CREATE INDEX idx_transacoes_state_month ON transacoes(state, month)")
    for threshold in (40, 50, 60, 70, 80):
        tp = sum(r["risk"] >= threshold and r["fraud"] for r in rows)
        fp = sum(r["risk"] >= threshold and not r["fraud"] for r in rows)
        fn = sum(r["risk"] < threshold and r["fraud"] for r in rows)
        print(f"threshold={threshold} alerts={tp + fp} "
              f"precision={tp / (tp + fp) if tp + fp else 0:.3f} "
              f"recall={tp / (tp + fn) if tp + fn else 0:.3f}")
    print(f"Exported {len(rows)} synthetic records; synthetic fraud labels: "
          f"{sum(r['fraud'] for r in rows)}")


if __name__ == "__main__":
    main()

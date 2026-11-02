#!/usr/bin/env python3
"""ATLAS | pipeline reproduzível de dados sintéticos. Python 3.10+, stdlib."""
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)
SEED = 73619
UF = ("SP", "RJ", "MG", "BA", "PR")
state = SEED

def rand():
    global state
    state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
    return state / 4294967296

def generate():
    rows = []
    for i in range(2400):
        month = i // 200
        uf = UF[int(rand() * 5)]
        amount = int((30 + rand() ** 2 * 3400) * 100 + 0.5) / 100
        device = rand() < .18
        night = rand() < .14
        velocity = rand() < .12
        unusual = rand() < .07
        score = min(100, int((19 if amount > 1800 else 0) +
            (28 if device else 0) + (16 if night else 0) +
            (30 if velocity else 0) + (24 if unusual else 0) + rand() * 17 + .5))
        fraud = ((device and velocity and rand() < .42) or
                 (unusual and night and rand() < .25) or
                 (score > 78 and rand() < .14))
        day = 1 + int(rand() * 28)
        rows.append(dict(id=f"TX-{i+1:05d}", date=f"2026-{month+1:02d}-{day:02d}",
            month=month, state=uf, amount=amount, device=device, night=night,
            velocity=velocity, foreign=unusual, risk=score, fraud=bool(fraud)))
    return rows

def main():
    rows = generate()
    (OUT / "transacoes.json").write_text(
        json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    with (OUT / "transacoes.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    db = OUT / "atlas.sqlite"
    if db.exists():
        db.unlink()
    with sqlite3.connect(db) as conn:
        conn.execute("""CREATE TABLE transacoes (
            id TEXT PRIMARY KEY, date TEXT NOT NULL, month INTEGER NOT NULL,
            state TEXT NOT NULL, amount REAL NOT NULL,
            device INTEGER NOT NULL, night INTEGER NOT NULL,
            velocity INTEGER NOT NULL, foreign_location INTEGER NOT NULL,
            risk INTEGER NOT NULL, fraud INTEGER NOT NULL)""")
        conn.executemany("INSERT INTO transacoes VALUES (?,?,?,?,?,?,?,?,?,?,?)", [
            (r["id"],r["date"],r["month"],r["state"],r["amount"],
             int(r["device"]),int(r["night"]),int(r["velocity"]),
             int(r["foreign"]),r["risk"],int(r["fraud"])) for r in rows])
    for threshold in (40, 50, 60, 70, 80):
        tp = sum(r["risk"] >= threshold and r["fraud"] for r in rows)
        fp = sum(r["risk"] >= threshold and not r["fraud"] for r in rows)
        fn = sum(r["risk"] < threshold and r["fraud"] for r in rows)
        print(f"threshold={threshold} alerts={tp+fp} precision={tp/(tp+fp) if tp+fp else 0:.3f} recall={tp/(tp+fn) if tp+fn else 0:.3f}")
    print(f"Exported {len(rows)} synthetic records to {OUT}")

if __name__ == "__main__":
    main()

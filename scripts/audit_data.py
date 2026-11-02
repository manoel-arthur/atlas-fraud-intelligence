#!/usr/bin/env python3
"""Compara CSV, JSON, SQLite e os KPIs exibidos pelo dashboard ATLAS."""
import csv, json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
def require(condition,message):
    if not condition: raise AssertionError(message)
def metric(rows,threshold):
    tp=sum(x["risk"]>=threshold and x["fraud"] for x in rows)
    fp=sum(x["risk"]>=threshold and not x["fraud"] for x in rows)
    fn=sum(x["risk"]<threshold and x["fraud"] for x in rows)
    tn=len(rows)-tp-fp-fn
    return dict(volume=len(rows),alerts=tp+fp,tp=tp,fp=fp,fn=fn,tn=tn,
        precision=round(100*tp/(tp+fp),1) if tp+fp else 0,
        recall=round(100*tp/(tp+fn),1) if tp+fn else 0)
def main():
    j=json.loads((DATA/"transacoes.json").read_text(encoding="utf-8"))
    with (DATA/"transacoes.csv").open(encoding="utf-8",newline="") as f:
        c=list(csv.DictReader(f))
    with sqlite3.connect(DATA/"atlas.sqlite") as db:
        sql=db.execute("SELECT id,date,month,state,amount,device,night,velocity,foreign_location,risk,fraud FROM transacoes ORDER BY id").fetchall()
        integrity=db.execute("PRAGMA integrity_check").fetchone()[0]
    require(integrity=="ok","SQLite integrity check failed")
    require(len(j)==len(c)==len(sql)==2400,"Record counts differ")
    require(len({x["id"] for x in j})==len(j),"Duplicate transaction ID")
    for idx,(a,b,s) in enumerate(zip(j,c,sql)):
        normalized=(a["id"],a["date"],a["month"],a["state"],a["amount"],int(a["device"]),int(a["night"]),int(a["velocity"]),int(a["foreign"]),a["risk"],int(a["fraud"]))
        require(normalized==s,f"JSON vs SQLite mismatch row {idx}")
        require(a["id"]==b["id"] and a["date"]==b["date"] and a["state"]==b["state"],f"CSV identity mismatch row {idx}")
        require(abs(a["amount"]-float(b["amount"]))<1e-7 and a["risk"]==int(b["risk"]) and a["fraud"]==(b["fraud"]=="True"),f"CSV values mismatch row {idx}")
    results={str(t):metric(j,t) for t in (40,50,60,70,80)}
    with sqlite3.connect(DATA/"atlas.sqlite") as db:
        for t in (40,50,60,70,80):
            row=db.execute("""SELECT COUNT(*), SUM(CASE WHEN risk>=? THEN 1 ELSE 0 END),
            SUM(CASE WHEN risk>=? AND fraud=1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN risk>=? AND fraud=0 THEN 1 ELSE 0 END),
            SUM(CASE WHEN risk<? AND fraud=1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN risk<? AND fraud=0 THEN 1 ELSE 0 END)
            FROM transacoes""",(t,t,t,t,t)).fetchone()
            m=results[str(t)]
            require(tuple(row)==tuple(m[k] for k in ("volume","alerts","tp","fp","fn","tn")),f"SQL vs Python KPI mismatch threshold={t}")
    (DATA/"auditoria_metricas.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PASS: 2400 records consistent across JSON, CSV, SQLite; 5 thresholds; SQLite integrity OK")
    print(json.dumps(results["60"],ensure_ascii=False))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(f"FAIL: {exc}",file=sys.stderr);sys.exit(1)

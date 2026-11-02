#!/usr/bin/env python3
"""ATLAS: custo esperado de triagem para limiares de score. Valores hipotéticos."""
import csv, json, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"
# Hipóteses editáveis, NÃO custos reais de instituição financeira.
COST_REVIEW=12.0  # R$ por alerta investigado (TP ou FP)
COST_MISSED=900.0 # R$ por fraude simulada não detectada
THRESHOLDS=range(20,91,5)
def brl(value):return f"R$ {value:,.2f}".replace(",","X").replace(".",",").replace("X",".")
def main():
    with sqlite3.connect(OUT/"atlas.sqlite") as conn:
        rows=conn.execute("SELECT risk,fraud FROM transacoes").fetchall()
    assert len(rows)==2400
    results=[]
    for t in THRESHOLDS:
        tp=sum(r>=t and f==1 for r,f in rows)
        fp=sum(r>=t and f==0 for r,f in rows)
        fn=sum(r<t and f==1 for r,f in rows)
        tn=len(rows)-tp-fp-fn
        reviews=tp+fp
        cost=reviews*COST_REVIEW+fn*COST_MISSED
        results.append(dict(limiar=t,volume=len(rows),alertas=reviews,tp=tp,fp=fp,fn=fn,tn=tn,
          precisao_pct=round(100*tp/reviews,2) if reviews else 0,
          recall_pct=round(100*tp/(tp+fn),2) if tp+fn else 0,
          custo_revisao_brl=round(reviews*COST_REVIEW,2),
          custo_fraudes_nao_detectadas_brl=round(fn*COST_MISSED,2),
          custo_total_estimado_brl=round(cost,2)))
    winner=min(results,key=lambda r:(r["custo_total_estimado_brl"],r["limiar"]))
    with (OUT/"analise_custos.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]))
        writer.writeheader();writer.writerows(results)
    (OUT/"analise_custos.json").write_text(json.dumps(dict(
        premissas=dict(custo_por_alerta_brl=COST_REVIEW,custo_por_fraude_nao_detectada_brl=COST_MISSED,
            nota="Hipóteses ilustrativas; sem calibração com perdas reais."),
        resultados=results,melhor_cenario_hipotetico=winner),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    default=next(r for r in results if r["limiar"]==60)
    lines=["# ATLAS — Avaliação de custo operacional","",
      "> **Simulação educacional.** Os rótulos de fraude e as premissas de custo são artificiais. Não há estimativa de impacto financeiro real.","",
      "## Objetivo","",
      "Comparar o custo de investigar alertas com o custo hipotético de não detectar uma fraude, variando o limiar de score entre 20 e 90.","",
      "## Premissas declaradas","",
      f"- Custo por alerta investigado (verdadeiro ou falso positivo): **{brl(COST_REVIEW)}**.",
      f"- Custo por fraude não detectada (falso negativo): **{brl(COST_MISSED)}**.",
      "- Alertas têm custo de revisão mesmo quando a fraude é confirmada.",
      "- Não foram modelados bloqueios indevidos, perdas recuperadas, capacidade operacional, mudança de comportamento ou incerteza estatística.","",
      "**Equação:** custo total = (TP + FP) × custo de revisão + FN × custo de fraude não detectada.","",
      "## Comparação de limiares","",
      "| Limiar | Alertas | FP | FN | Precisão | Recall | Custo estimado |",
      "|---:|---:|---:|---:|---:|---:|---:|"]
    for r in results:
        lines.append(f'| {r["limiar"]} | {r["alertas"]} | {r["fp"]} | {r["fn"]} | {r["precisao_pct"]:.2f}% | {r["recall_pct"]:.2f}% | {brl(r["custo_total_estimado_brl"])} |')
    lines += ["","## Recomendação condicionada às premissas","",
      f'No cenário hipotético definido acima, o menor custo ocorre no **limiar {winner["limiar"]}**, com **{winner["alertas"]} alertas**, **{winner["fn"]} falsos negativos** e custo total de **{brl(winner["custo_total_estimado_brl"])}**.',
      f'O limiar inicial do dashboard (60) apresenta custo estimado de **{brl(default["custo_total_estimado_brl"])}** sob as mesmas hipóteses.',
      "Essa recomendação **não é aplicável em produção** sem estimar custos reais, avaliar subgrupos e validar os dados fora da amostra.","",
      "## Próximos testes","",
      "1. Fazer análise de sensibilidade para múltiplos valores de custo de falso negativo e custo de revisão.",
      "2. Medir capacidade diária da equipe e custos de bloqueio indevido.",
      "3. Validar em dados históricos reais, com aprovação e governança apropriadas.",""]
    (ROOT/"ANALISE_CUSTO_OPERACIONAL.md").write_text("\n".join(lines),encoding="utf-8")
    print("PASS: operational-cost scenario calculated; best hypothetical threshold:",winner["limiar"])
if __name__=="__main__":main()

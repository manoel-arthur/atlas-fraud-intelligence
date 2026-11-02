# ATLAS — Avaliação de custo operacional

> **Simulação educacional.** Os rótulos de fraude e as premissas de custo são artificiais. Não há estimativa de impacto financeiro real.

## Objetivo

Comparar o custo de investigar alertas com o custo hipotético de não detectar uma fraude, variando o limiar de score entre 20 e 90.

## Premissas declaradas

- Custo por alerta investigado (verdadeiro ou falso positivo): **R$ 12,00**.
- Custo por fraude não detectada (falso negativo): **R$ 900,00**.
- Alertas têm custo de revisão mesmo quando a fraude é confirmada.
- Não foram modelados bloqueios indevidos, perdas recuperadas, capacidade operacional, mudança de comportamento ou incerteza estatística.

**Equação:** custo total = (TP + FP) × custo de revisão + FN × custo de fraude não detectada.

## Comparação de limiares

| Limiar | Alertas | FP | FN | Precisão | Recall | Custo estimado |
|---:|---:|---:|---:|---:|---:|---:|
| 20 | 1372 | 1343 | 0 | 2.11% | 100.00% | R$ 16.464,00 |
| 25 | 1208 | 1179 | 0 | 2.40% | 100.00% | R$ 14.496,00 |
| 30 | 1030 | 1001 | 0 | 2.82% | 100.00% | R$ 12.360,00 |
| 35 | 786 | 757 | 0 | 3.69% | 100.00% | R$ 9.432,00 |
| 40 | 607 | 578 | 0 | 4.78% | 100.00% | R$ 7.284,00 |
| 45 | 448 | 420 | 1 | 6.25% | 96.55% | R$ 6.276,00 |
| 50 | 358 | 334 | 5 | 6.70% | 82.76% | R$ 8.796,00 |
| 55 | 252 | 230 | 7 | 8.73% | 75.86% | R$ 9.324,00 |
| 60 | 161 | 140 | 8 | 13.04% | 72.41% | R$ 9.132,00 |
| 65 | 97 | 79 | 11 | 18.56% | 62.07% | R$ 11.064,00 |
| 70 | 78 | 60 | 11 | 23.08% | 62.07% | R$ 10.836,00 |
| 75 | 59 | 45 | 15 | 23.73% | 48.28% | R$ 14.208,00 |
| 80 | 36 | 25 | 18 | 30.56% | 37.93% | R$ 16.632,00 |
| 85 | 23 | 16 | 22 | 30.43% | 24.14% | R$ 20.076,00 |
| 90 | 10 | 7 | 26 | 30.00% | 10.34% | R$ 23.520,00 |

## Recomendação condicionada às premissas

No cenário hipotético definido acima, o menor custo ocorre no **limiar 45**, com **448 alertas**, **1 falsos negativos** e custo total de **R$ 6.276,00**.
O limiar inicial do dashboard (60) apresenta custo estimado de **R$ 9.132,00** sob as mesmas hipóteses.
Essa recomendação **não é aplicável em produção** sem estimar custos reais, avaliar subgrupos e validar os dados fora da amostra.

## Próximos testes

1. Fazer análise de sensibilidade para múltiplos valores de custo de falso negativo e custo de revisão.
2. Medir capacidade diária da equipe e custos de bloqueio indevido.
3. Validar em dados históricos reais, com aprovação e governança apropriadas.

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
| 20 | 916 | 908 | 11 | 0.87% | 42.11% | R$ 20.892,00 |
| 25 | 691 | 684 | 12 | 1.01% | 36.84% | R$ 19.092,00 |
| 30 | 495 | 491 | 15 | 0.81% | 21.05% | R$ 19.440,00 |
| 35 | 353 | 349 | 15 | 1.13% | 21.05% | R$ 17.736,00 |
| 40 | 249 | 245 | 15 | 1.61% | 21.05% | R$ 16.488,00 |
| 45 | 169 | 166 | 16 | 1.78% | 15.79% | R$ 16.428,00 |
| 50 | 108 | 106 | 17 | 1.85% | 10.53% | R$ 16.596,00 |
| 55 | 68 | 66 | 17 | 2.94% | 10.53% | R$ 16.116,00 |
| 60 | 32 | 31 | 18 | 3.12% | 5.26% | R$ 16.584,00 |
| 65 | 21 | 20 | 18 | 4.76% | 5.26% | R$ 16.452,00 |
| 70 | 12 | 11 | 18 | 8.33% | 5.26% | R$ 16.344,00 |
| 75 | 8 | 7 | 18 | 12.50% | 5.26% | R$ 16.296,00 |
| 80 | 5 | 5 | 19 | 0.00% | 0.00% | R$ 17.160,00 |
| 85 | 1 | 1 | 19 | 0.00% | 0.00% | R$ 17.112,00 |
| 90 | 0 | 0 | 19 | 0.00% | 0.00% | R$ 17.100,00 |

## Recomendação condicionada às premissas

No cenário hipotético definido acima, o menor custo ocorre no **limiar 55**, com **68 alertas**, **17 falsos negativos** e custo total de **R$ 16.116,00**.
O limiar inicial do dashboard (60) apresenta custo estimado de **R$ 16.584,00** sob as mesmas hipóteses.
Essa recomendação **não é aplicável em produção** sem estimar custos reais, avaliar subgrupos e validar os dados fora da amostra.

## Próximos testes

1. Fazer análise de sensibilidade para múltiplos valores de custo de falso negativo e custo de revisão.
2. Medir capacidade diária da equipe e custos de bloqueio indevido.
3. Validar em dados históricos reais, com aprovação e governança apropriadas.

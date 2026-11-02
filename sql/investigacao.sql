-- ATLAS | investigação analítica SQLite
-- Dados sintéticos; rótulos artificiais, sem interpretação causal.
-- Execute: sqlite3 -header -column data/atlas.sqlite < sql/investigacao.sql

-- 1. Integridade e cobertura: 12 meses, 5 estados, sem duplicatas ou valores inválidos
SELECT COUNT(*) AS volume,
       COUNT(DISTINCT id) AS ids_unicos,
       COUNT(DISTINCT substr(date,1,7)) AS meses,
       COUNT(DISTINCT state) AS estados,
       SUM(CASE WHEN amount <= 0 OR risk NOT BETWEEN 0 AND 100
                 OR fraud NOT IN (0,1) OR date IS NULL THEN 1 ELSE 0 END) AS invalidos
FROM transacoes;

-- 2. Matriz de confusão + precisão, recall e taxa de alertas (limiar = 60)
WITH base AS (
  SELECT fraud, CASE WHEN risk >= 60 THEN 1 ELSE 0 END AS alert FROM transacoes
), matrix AS (
  SELECT COUNT(*) AS volume, SUM(alert) AS alerts,
    SUM(CASE WHEN alert=1 AND fraud=1 THEN 1 ELSE 0 END) AS tp,
    SUM(CASE WHEN alert=1 AND fraud=0 THEN 1 ELSE 0 END) AS fp,
    SUM(CASE WHEN alert=0 AND fraud=1 THEN 1 ELSE 0 END) AS fn,
    SUM(CASE WHEN alert=0 AND fraud=0 THEN 1 ELSE 0 END) AS tn
  FROM base
)
SELECT *, ROUND(100.0*tp/NULLIF(tp+fp,0),2) AS precision_pct,
          ROUND(100.0*tp/NULLIF(tp+fn,0),2) AS recall_pct,
          ROUND(100.0*alerts/NULLIF(volume,0),2) AS alert_rate_pct
FROM matrix;

-- 3. Evolução mensal, com taxas em vez de apenas contagens
SELECT substr(date,1,7) AS month, COUNT(*) AS transactions,
       SUM(CASE WHEN risk>=60 THEN 1 ELSE 0 END) AS alerts,
       SUM(fraud) AS synthetic_fraud,
       ROUND(AVG(amount),2) AS avg_amount,
       ROUND(100.0*AVG(CASE WHEN risk>=60 THEN 1.0 ELSE 0.0 END),2) AS alert_rate_pct,
       ROUND(100.0*AVG(fraud),2) AS synthetic_fraud_rate_pct
FROM transacoes GROUP BY substr(date,1,7) ORDER BY month;

-- 4. Comparação geográfica normalizada pelo volume de cada estado
SELECT state AS uf, COUNT(*) AS transactions,
       SUM(CASE WHEN risk>=60 THEN 1 ELSE 0 END) AS alerts,
       ROUND(100.0*AVG(CASE WHEN risk>=60 THEN 1.0 ELSE 0.0 END),2) AS alert_rate_pct,
       ROUND(AVG(risk),1) AS avg_score,
       ROUND(100.0*AVG(fraud),2) AS synthetic_fraud_rate_pct
FROM transacoes GROUP BY state ORDER BY alert_rate_pct DESC, transactions DESC;

-- 5. Segmentos por faixa de valor: risco e taxa de fraude sintética
WITH segments AS (
  SELECT CASE WHEN amount < 100 THEN '01 < R$100'
              WHEN amount < 500 THEN '02 R$100-499'
              WHEN amount < 1800 THEN '03 R$500-1799'
              ELSE '04 >= R$1800' END AS amount_band,
         risk, fraud FROM transacoes
)
SELECT amount_band, COUNT(*) AS transactions, ROUND(AVG(risk),1) AS avg_risk,
       ROUND(100.0*AVG(fraud),2) AS synthetic_fraud_rate_pct
FROM segments GROUP BY amount_band ORDER BY amount_band;

-- 6. Sinais de risco: associação descritiva, não causal
WITH signals AS (
  SELECT 'new_device' AS signal, device AS present, risk, fraud FROM transacoes
  UNION ALL SELECT 'night', night, risk, fraud FROM transacoes
  UNION ALL SELECT 'velocity', velocity, risk, fraud FROM transacoes
  UNION ALL SELECT 'foreign_location', foreign_location, risk, fraud FROM transacoes
)
SELECT signal, present, COUNT(*) AS transactions,
       ROUND(AVG(risk),1) AS avg_score,
       ROUND(100.0*AVG(fraud),2) AS synthetic_fraud_rate_pct
FROM signals GROUP BY signal,present ORDER BY signal,present DESC;

-- 7. Comparação de limiares com custos ilustrativos (R$ 12/alerta; R$ 900/FN)
WITH RECURSIVE thresholds(t) AS (
  SELECT 20 UNION ALL SELECT t+5 FROM thresholds WHERE t<90
), metrics AS (
  SELECT t, COUNT(*) AS volume,
    SUM(CASE WHEN risk>=t THEN 1 ELSE 0 END) AS alerts,
    SUM(CASE WHEN risk>=t AND fraud=1 THEN 1 ELSE 0 END) AS tp,
    SUM(CASE WHEN risk>=t AND fraud=0 THEN 1 ELSE 0 END) AS fp,
    SUM(CASE WHEN risk<t AND fraud=1 THEN 1 ELSE 0 END) AS fn
  FROM thresholds CROSS JOIN transacoes GROUP BY t
)
SELECT t AS threshold, volume, alerts, tp, fp, fn,
       ROUND(100.0*tp/NULLIF(alerts,0),2) AS precision_pct,
       ROUND(100.0*tp/NULLIF(tp+fn,0),2) AS recall_pct,
       (12*alerts + 900*fn) AS hypothetical_cost_brl
FROM metrics ORDER BY hypothetical_cost_brl, threshold;

-- 8. Fila de investigação com desempate determinístico
SELECT id,date,state,amount,risk,device,night,velocity,foreign_location
FROM transacoes WHERE risk>=60
ORDER BY risk DESC, amount DESC, date, id LIMIT 50;

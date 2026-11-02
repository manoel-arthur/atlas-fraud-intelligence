-- ATLAS | investigação em SQLite
-- Fonte: data/atlas.sqlite, gerada por scripts/build_data.py
-- Todos os dados e rótulos são sintéticos.
-- 1. Visão geral com limiar de 60 pontos
WITH classificacao AS (
  SELECT *, CASE WHEN risk >= 60 THEN 1 ELSE 0 END AS alerta
  FROM transacoes
)
SELECT COUNT(*) AS volume,
 SUM(alerta) AS alertas,
 SUM(CASE WHEN alerta = 1 AND fraud = 1 THEN 1 ELSE 0 END) AS tp,
 SUM(CASE WHEN alerta = 1 AND fraud = 0 THEN 1 ELSE 0 END) AS fp,
 SUM(CASE WHEN alerta = 0 AND fraud = 1 THEN 1 ELSE 0 END) AS fn,
 SUM(CASE WHEN alerta = 0 AND fraud = 0 THEN 1 ELSE 0 END) AS tn
FROM classificacao;

-- 2. Volume, alertas e fraudes simuladas por mês
SELECT substr(date,1,7) AS mes, COUNT(*) AS transacoes,
 SUM(CASE WHEN risk >= 60 THEN 1 ELSE 0 END) AS alertas,
 SUM(fraud) AS fraudes_simuladas
FROM transacoes GROUP BY 1 ORDER BY 1;

-- 3. Distribuição por estado
SELECT state AS uf, COUNT(*) AS transacoes,
 SUM(CASE WHEN risk >= 60 THEN 1 ELSE 0 END) AS alertas,
 ROUND(AVG(risk),1) AS score_medio
FROM transacoes GROUP BY state ORDER BY alertas DESC;

-- 4. Sinais comportamentais associados a rótulos sintéticos
SELECT device, velocity, foreign_location, COUNT(*) AS volume,
 ROUND(AVG(fraud)*100,2) AS taxa_fraude_simulada_pct
FROM transacoes GROUP BY device, velocity, foreign_location
ORDER BY taxa_fraude_simulada_pct DESC;

-- 5. Transações prioritárias para revisão
SELECT id,date,state,amount,risk,device,night,velocity,foreign_location
FROM transacoes WHERE risk >= 60 ORDER BY risk DESC, amount DESC LIMIT 50;

# ATLAS — Fraud Intelligence

Dashboard analítico de triagem de risco, com **Python + SQLite + JavaScript**. Dados e rótulos **100% sintéticos**; não é um motor de prevenção a fraudes real.

## Pipeline

1. `scripts/build_data.py` gera 2.400 transações reproduzíveis (gerador LCG de semente fixa), calcula score heurístico e exporta `data/transacoes.json`, `data/transacoes.csv` e `data/atlas.sqlite`.
2. `sql/investigacao.sql` contém consultas de matriz de classificação, alertas por mês, distribuição geográfica, sinais de risco e fila de investigação.
3. O site estático (`index.html`) carrega `data/transacoes.json` quando disponível; enquanto a automação não publicar esse arquivo, usa a amostra determinística embutida.
4. `.github/workflows/build-data.yml` automatiza a geração quando o script muda ou mediante execução manual em **Actions**.

## Rodar localmente

```bash
python scripts/build_data.py
python -m http.server 8000
```

Abra http://localhost:8000. Para investigar com SQL: `sqlite3 data/atlas.sqlite < sql/investigacao.sql`.

## Sobre a avaliação

Os rótulos são simulados. Precisão = TP/(TP+FP); recall = TP/(TP+FN). Um alerta indica somente necessidade de revisão. O dashboard não usa credenciais, APIs bancárias ou dados pessoais.

## Limitações

A aplicação é hospedada no GitHub Pages, que **não executa Python ou SQL no servidor**. O processamento acontece na etapa de geração e os dados são consumidos estaticamente pelo navegador. Não utilizar os resultados para decisões financeiras reais.

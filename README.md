<div align="center">

# ATLAS | Fraud Intelligence

### Transaction Risk Observatory · Estudo de caso em Análise de Dados e Inteligência Antifraude

**Python · SQL (SQLite) · JavaScript · GitHub Actions · Data Visualization**

[**Explorar dashboard**](https://manoel-arthur.github.io/atlas-fraud-intelligence/) · [**Análise de custos**](ANALISE_CUSTO_OPERACIONAL.md) · [**Notebook exploratório**](notebooks/ATLAS_analise_exploratoria.ipynb) · [**Pipeline automatizado**](../../actions)

</div>

> [!IMPORTANT]
> **Projeto demonstrativo para portfólio.** As 2.400 transações, os rótulos de fraude e os custos são **sintéticos/hipotéticos**. O ATLAS não processa transações bancárias reais, não utiliza dados pessoais e não deve orientar decisões financeiras reais.

## Visão geral

O ATLAS simula uma operação de monitoramento transacional. O desafio de negócio é **priorizar transações potencialmente suspeitas**, equilibrando a capacidade de investigação da equipe com o risco de não detectar uma fraude.

O projeto transforma esse problema em um fluxo analítico reproduzível: geração de dados, armazenamento, investigação SQL, validação de métricas, simulação de custos e visualização interativa.

**Pergunta central:** *qual limiar de risco minimiza o custo operacional estimado, considerando o preço de investigar alertas e o custo de fraudes não detectadas?*

## Dashboard ao vivo

**[Abrir ATLAS — Fraud Intelligence](https://manoel-arthur.github.io/atlas-fraud-intelligence/)**

O dashboard inclui KPIs, evolução mensal, distribuição por estado, indicadores de classificação, filtros, investigação de transações, exportação CSV e **gráfico interativo de custo por limiar**.

### Prévia do projeto

> **Visualização:** o link acima abre o dashboard real e interativo. Uma captura de tela estática poderá ser adicionada aqui posteriormente; não foi incluída uma imagem não verificada.

## Arquitetura e fluxo de dados

```mermaid
flowchart TD
    A["Python: geração de 2.400 transações sintéticas"] --> B["CSV + JSON + SQLite"]
    B --> C["Auditoria de integridade e métricas"]
    C --> D["SQL: investigação e segmentação"]
    C --> E["Python: simulação de custos por limiar"]
    B --> F["GitHub Pages: dashboard interativo"]
    E --> G["Relatório Markdown + CSV + JSON"]
    G --> F
    H["GitHub Actions"] --> A
    H --> C
    H --> E
```

| Camada | Tecnologia | Responsabilidade |
|---|---|---|
| Engenharia de dados | Python 3 | Geração determinística, score heurístico e exportações |
| Persistência | SQLite, CSV, JSON | Consulta analítica e intercâmbio de dados |
| Investigação | SQL | Matriz de classificação, evolução mensal, estados e sinais |
| Qualidade | Python + GitHub Actions | Conferência de registros, integridade e consistência dos KPIs |
| Simulação de negócio | Python | Custos, falsos positivos/negativos e escolha de limiar |
| Visualização | HTML, CSS, JavaScript | Dashboard responsivo publicado no GitHub Pages |

**Nota técnica:** o GitHub Pages serve arquivos estáticos; Python e SQLite são executados no pipeline, não no navegador ou em um backend de produção.

## Principais descobertas

Foram avaliados **15 limiares de risco**, de 20 a 90 pontos, com as seguintes premissas **ilustrativas**:

- **R$ 12** por alerta investigado, independentemente do resultado.
- **R$ 900** por fraude simulada não detectada.
- Custo total = (verdadeiros positivos + falsos positivos) × R$ 12 + falsos negativos × R$ 900.

| Indicador | Limiar padrão: 60 | Menor custo simulado: 45 |
|---|---:|---:|
| Alertas para revisão | 161 | 448 |
| Verdadeiros positivos | 21 | 28 |
| Falsos positivos | 140 | 420 |
| Falsos negativos | 8 | 1 |
| Precisão | 13,04% | 6,25% |
| Recall | 72,41% | 96,55% |
| **Custo total hipotético** | **R$ 9.132** | **R$ 6.276** |

**Resultado:** sob essas premissas, o limiar **45** reduz o custo simulado em **R$ 2.856 (31,3%)** em relação ao limiar 60. Porém, ele exige **287 investigações adicionais** e apresenta menor precisão.

**Interpretação de negócio:** a alternativa de menor custo estimado não é necessariamente a mais viável operacionalmente. A recomendação depende da capacidade da equipe, do custo real dos erros, da qualidade dos rótulos e da validação com dados independentes.

Os números completos são gerados automaticamente em [`data/analise_custos.json`](data/analise_custos.json) e documentados em [`ANALISE_CUSTO_OPERACIONAL.md`](ANALISE_CUSTO_OPERACIONAL.md).

## Como a qualidade dos dados é verificada

O script [`scripts/audit_data.py`](scripts/audit_data.py) valida:

1. Consistência dos **2.400 registros** entre JSON, CSV e SQLite.
2. Ausência de identificadores duplicados e integridade do banco SQLite.
3. Equivalência entre contagens de classificação calculadas em Python e SQL para os limiares 40, 50, 60, 70 e 80.
4. Exportação dos indicadores auditados em [`data/auditoria_metricas.json`](data/auditoria_metricas.json).

A rotina é executada automaticamente no [GitHub Actions](../../actions). Uma falha interrompe o fluxo antes da publicação dos resultados.

## Estrutura do repositório

```text
atlas-fraud-intelligence/
├── index.html                         # Dashboard responsivo
├── scripts/
│   ├── build_data.py                  # Geração sintética e exportações
│   ├── audit_data.py                  # Auditoria de consistência
│   └── analyze_costs.py               # Avaliação econômica dos limiares
├── sql/
│   └── investigacao.sql               # Consultas analíticas SQLite
├── notebooks/
│   └── ATLAS_analise_exploratoria.ipynb
├── data/
│   ├── transacoes.csv
│   ├── transacoes.json
│   ├── atlas.sqlite
│   ├── auditoria_metricas.json
│   ├── analise_custos.csv
│   └── analise_custos.json
├── .github/workflows/
│   └── build-data.yml                 # Pipeline CI
└── ANALISE_CUSTO_OPERACIONAL.md       # Relatório de decisão
```

## Executar localmente

**Pré-requisito:** Python 3.10 ou superior. Os três scripts principais utilizam apenas a biblioteca padrão.

```bash
git clone https://github.com/manoel-arthur/atlas-fraud-intelligence.git
cd atlas-fraud-intelligence

python scripts/build_data.py
python scripts/audit_data.py
python scripts/analyze_costs.py

python -m http.server 8000
```

Abra **http://localhost:8000** no navegador. Para executar a investigação SQL, utilize um cliente SQLite ou:

```bash
sqlite3 data/atlas.sqlite < sql/investigacao.sql
```

O notebook exploratório requer `pandas`, `matplotlib` e um ambiente Jupyter. Ele pode ser aberto no GitHub e executado em um ambiente Python configurado com essas dependências.

## Metodologia e limitações

- **Geração determinística:** os registros usam um gerador pseudoaleatório com semente fixa, permitindo reprodução dos dados.
- **Score heurístico:** o risco é calculado a partir de sinais simulados, como dispositivo novo, velocidade transacional, horário atípico e localização incomum.
- **Rótulos artificiais:** a variável de fraude é construída a partir de regras sintéticas; isso cria associações por construção e não comprova poder preditivo real.
- **Sem modelo treinado:** o projeto **não** utiliza machine learning supervisionado nem afirma desempenho em produção.
- **Custos ilustrativos:** os valores não incluem custos de bloqueio indevido, recuperação de perdas, capacidade operacional ou efeitos sobre clientes.
- **Sem validação externa:** resultados não são generalizáveis para transações reais.

## Possíveis evoluções

- Análise de sensibilidade das premissas financeiras e restrições de capacidade.
- Avaliação de fairness e estabilidade por segmentos.
- Testes com uma base pública devidamente documentada.
- Monitoramento de qualidade e documentação de decisões analíticas.

---

<div align="center">

**ATLAS | Fraud Intelligence** · Projeto de portfólio em análise de dados, BI e prevenção a fraudes.

[Dashboard](https://manoel-arthur.github.io/atlas-fraud-intelligence/) · [Código-fonte](https://github.com/manoel-arthur/atlas-fraud-intelligence) · [Relatório de custos](ANALISE_CUSTO_OPERACIONAL.md)

</div>

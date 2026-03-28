---
name: analise-dados
description: "Workflow de análise de dados, EDA, modelagem e visualizações do projeto MediaPipe Segurança. Use when: criar notebook, análise exploratória, EDA, estatística descritiva, correlação, visualização, gráfico, clusterização, classificação, treinar modelo, comparar modelos, gerar figuras, material de defesa, interpretar resultados, heatmap, boxplot, série temporal, distribuição, outlier, missing values."
argument-hint: "descreva a análise, notebook ou modelagem a ser realizada"
---

# Análise de Dados — Skill

Workflow padronizado para exploração de dados, análise estatística, modelagem e geração de visualizações no projeto MediaPipe Segurança.

## Quando Usar

- Criar ou executar notebooks de EDA
- Produzir análise estatística (distribuições, correlações, outliers, missing values)
- Gerar visualizações (heatmaps, boxplots, séries temporais)
- Treinar modelos não supervisionados (clusterização, detecção de anomalias)
- Treinar modelos supervisionados (classificação de eventos rotulados)
- Comparar e avaliar modelos (métricas, matrizes de confusão)
- Selecionar material para defesa acadêmica

## Fontes de Verdade

- **Dicionário de dados**: [docs/DICIONARIO_DE_DADOS.md](../../../docs/DICIONARIO_DE_DADOS.md)
- **Plano de notebooks**: [notebooks/README.md](../../../notebooks/README.md)
- **Arquitetura**: [docs/ARQUITETURA.md](../../../docs/ARQUITETURA.md)

## Dados Disponíveis

| Diretório | Conteúdo |
|---|---|
| `data/raw/` | Vídeos e insumos originais |
| `data/interim/` | Saídas parciais de extração |
| `data/processed/` | Features por frame e por janela — **usar como input principal** |
| `data/labels/` | Rótulos e anotações |

## Plano de Notebooks

| Notebook | Propósito | Fase |
|---|---|---|
| `01_ingestao.md` | Explorar dados de entrada | Fase 2 |
| `02_extracao_mediapipe.md` | Inspecionar saídas do MediaPipe | Fase 3 |
| `03_feature_engineering.md` | Validar features geradas | Fase 4 |
| `04_eda.md` | Análise exploratória completa | Fase 5 |
| `05_unsupervised.md` | Clusterização e anomalias | Fase 6 |
| `06_supervised.md` | Classificação supervisionada | Fase 7 |
| `07_visualizacoes.md` | Figuras finais para defesa | Fase 8 |

## Procedimento: EDA

1. **Verificar dados**: confirme que bases em `data/processed/` existem e têm conteúdo.
2. **Ler dicionário de dados**: consulte `docs/DICIONARIO_DE_DADOS.md` para entender variáveis.
3. **Carregar dataset**:
   ```python
   import pandas as pd
   df = pd.read_csv("data/processed/demo_window_features.csv")
   ```
4. **Estatística descritiva**: `df.describe()`, tipos, valores ausentes, cardinalidade.
5. **Distribuições**: histogramas e KDE para variáveis contínuas.
6. **Correlações**: heatmap de correlação entre features numéricas.
7. **Outliers**: boxplots, IQR, z-score.
8. **Segmentação por rótulo**: comparar distribuições por classe (`label`).
9. **Interpretar**: documentar achados principais — não apenas código/gráfico.
10. **Salvar artefatos**:
    - Figuras em `reports/figures/` com nomes descritivos (ex: `eda_correlacao_features.png`)
    - Síntese em `reports/eda/`

## Procedimento: Modelagem Não Supervisionada

1. **Verificar pré-requisitos**: EDA concluída, features disponíveis em `data/processed/`.
2. **Selecionar features**: usar features numéricas do dicionário de dados.
3. **Normalizar**: StandardScaler ou MinMaxScaler conforme distribuição.
4. **Clusterização**:
   - KMeans com análise de Elbow e Silhouette
   - DBSCAN se houver evidência de clusters não-convexos
5. **Detecção de anomalias**:
   - IsolationForest com contaminação estimada
   - Comparar com distribuição dos scores
6. **Avaliar**: silhouette score, calinski-harabasz, davies-bouldin.
7. **Visualizar**: scatter plots 2D (PCA ou t-SNE), perfis de clusters.
8. **Interpretar**: caracterizar cada cluster, relacionar com rótulos existentes.
9. **Salvar**: métricas em `reports/models/`, figuras em `reports/figures/`.

## Procedimento: Modelagem Supervisionada

1. **Verificar pré-requisitos**: rótulos disponíveis em `data/labels/` ou coluna `label`.
2. **Preparar dados**: train/test split estratificado por `label`.
3. **Baseline**: DummyClassifier (estratificado) para referência.
4. **Treinar modelos**:
   - RandomForest
   - LogisticRegression
   - SVM (se dataset não for muito grande)
   - GradientBoosting / XGBoost (se disponível)
5. **Avaliar**: accuracy, precision, recall, f1-score (macro e por classe).
6. **Matriz de confusão**: visualizar erros por classe.
7. **Feature importance**: identificar features mais discriminantes.
8. **Comparar modelos**: tabela comparativa com todas as métricas.
9. **Interpretar**: qual modelo é melhor e por quê, limitações.
10. **Salvar**: métricas em `reports/models/`, figuras em `reports/figures/`.

## Procedimento: Figuras para Defesa

1. **Selecionar**: escolher as visualizações mais impactantes de EDA e modelagem.
2. **Padronizar**: fontes legíveis, paleta consistente, títulos em português.
3. **Exportar**: alta resolução (300 dpi), formato PNG.
4. **Organizar**: salvar em `reports/figures/` com nomes padronizados.
5. **Documentar**: criar síntese em `reports/defesa/` explicando cada figura.

## Checklist de Qualidade

- [ ] Toda análise contém interpretação, não apenas código e gráficos
- [ ] Figuras relevantes salvas em `reports/figures/`
- [ ] Features de `data/processed/` usadas (nunca dados brutos diretamente para análise)
- [ ] Notebooks têm seções de Contexto, Análise e Conclusão
- [ ] Resultados reproduzíveis (seeds fixos, caminhos relativos)
- [ ] Limitações explicitamente mencionadas
- [ ] Material defensável em banca acadêmica

## Bibliotecas do Projeto

```python
# Stack de análise
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, silhouette_score
```

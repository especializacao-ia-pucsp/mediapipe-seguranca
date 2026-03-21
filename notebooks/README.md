# Notebooks planejados

Este diretório foi criado para receber os notebooks descritos no `README.md`.

- `01_ingestao.ipynb`: exploração inicial da leitura e estrutura dos vídeos.
- `02_extracao_mediapipe.ipynb`: teste das tasks e inspeção dos sinais extraídos.
- `03_feature_engineering.ipynb`: consolidação de atributos por frame e janela.
- `04_eda.ipynb`: análise exploratória, estatística descritiva e correlações.
- `05_unsupervised.ipynb`: clusterização, perfis de cena e anomalias.
- `06_supervised.ipynb`: classificação de eventos e comparação de métricas.
- `07_visualizacoes.ipynb`: material final de gráficos e apoio para defesa.

## Guias de planejamento

Enquanto os notebooks ainda não existem como `.ipynb`, cada um já possui um guia de escopo para orientar implementação, entradas esperadas e saídas finais:

- `01_ingestao.md`
- `02_extracao_mediapipe.md`
- `03_feature_engineering.md`
- `04_eda.md`
- `05_unsupervised.md`
- `06_supervised.md`
- `07_visualizacoes.md`

Enquanto a base do projeto é estruturada, o fluxo executável inicial fica centralizado no pacote Python em `src/mediapipe_seguranca/`.

## Diretriz de uso

- notebooks devem ser usados para exploração, análise e documentação visual;
- regras de negócio e lógica reutilizável devem permanecer em `src/mediapipe_seguranca/`;
- resultados importantes produzidos em notebooks devem ser exportados para `reports/` quando fizer sentido.

## Convenção sugerida

- cada notebook deve nascer a partir do respectivo arquivo `.md` desta pasta;
- o notebook final deve manter o mesmo prefixo numérico do guia correspondente;
- figuras finais devem ser exportadas para `reports/figures/`;
- conclusões relevantes devem ser consolidadas em `reports/eda/`, `reports/models/` ou `reports/defesa/`.



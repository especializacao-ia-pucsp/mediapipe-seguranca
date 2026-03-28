# MediaPipe Segurança

[![CI](https://github.com/especializacao-ia-pucsp/mediapipe-seguranca/actions/workflows/ci.yml/badge.svg)](https://github.com/especializacao-ia-pucsp/mediapipe-seguranca/actions/workflows/ci.yml)
[![CodeQL](https://github.com/especializacao-ia-pucsp/mediapipe-seguranca/actions/workflows/codeql.yml/badge.svg)](https://github.com/especializacao-ia-pucsp/mediapipe-seguranca/actions/workflows/codeql.yml)

Projeto acadêmico voltado à extração de indicadores comportamentais em filmagens de segurança com **MediaPipe** e técnicas de **aprendizado de máquina**. A proposta transforma vídeos de CFTV em dados estruturados para análise de padrões, detecção de anomalias e classificação de eventos de risco em um contexto acadêmico e reprodutível.

## Visão do projeto

Este repositório organiza o trabalho técnico e acadêmico do projeto integrador em torno de quatro eixos:

- **Pipeline de dados**: ingestão, leitura de vídeo, extração de sinais e consolidação de bases analíticas.
- **Análise exploratória**: construção de estatísticas, visualizações e interpretação dos dados derivados das filmagens.
- **Modelagem analítica**: aplicação de métodos supervisionados e não supervisionados para identificar padrões e eventos de risco.
- **Material de defesa**: organização de evidências, relatórios, figuras e estrutura de apresentação final.

## Navegação rápida

- [`README.md`](README.md): visão geral do projeto, escopo, objetivos e forma de execução.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): convenções para evolução do repositório e organização das contribuições.
- [`docs/DICIONARIO_DE_DADOS.md`](docs/DICIONARIO_DE_DADOS.md): definição das features, agregações e rótulos esperados.
- [`docs/ENTREGAVEIS.md`](docs/ENTREGAVEIS.md): detalhamento dos entregáveis, critérios de aceite e artefatos esperados.
- [`docs/PLANO_DE_EXECUCAO.md`](docs/PLANO_DE_EXECUCAO.md): plano operacional de evolução do projeto por etapas.
- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md): visão da arquitetura lógica, camadas da pipeline e responsabilidades.
- [`docs/ROADMAP.md`](docs/ROADMAP.md): fases, dependências, marcos e prioridades de evolução do projeto.
- [`data/README.md`](data/README.md): contrato de uso dos diretórios de dados.
- [`notebooks/README.md`](notebooks/README.md): planejamento dos notebooks e sua função no projeto.
- [`reports/README.md`](reports/README.md): organização das evidências analíticas e materiais de defesa.
- [`src/README.md`](src/README.md): visão da organização do código-fonte.
- [`tests/README.md`](tests/README.md): estratégia de testes e evolução da validação.

## Mapa por área

- **Documentação-base**: [`CONTRIBUTING.md`](CONTRIBUTING.md), [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md), [`docs/ROADMAP.md`](docs/ROADMAP.md)
- **Dados**: [`data/README.md`](data/README.md), [`data/raw/README.md`](data/raw/README.md), [`data/processed/README.md`](data/processed/README.md), [`data/labels/README.md`](data/labels/README.md)
- **Análise**: [`notebooks/README.md`](notebooks/README.md), [`reports/README.md`](reports/README.md), [`reports/eda/README.md`](reports/eda/README.md), [`reports/models/README.md`](reports/models/README.md)
- **Implementação**: [`src/README.md`](src/README.md), [`tests/README.md`](tests/README.md)

## Objetivo geral

Desenvolver um sistema em Python para processar filmagens de segurança, extrair informações com MediaPipe e aplicar técnicas de aprendizado supervisionado e não supervisionado para analisar comportamento e identificar eventos relevantes.

## Problema de pesquisa

Sistemas de vídeo monitoramento normalmente são usados de forma reativa, após a ocorrência de incidentes. Este projeto busca responder à seguinte pergunta:

> Como usar vídeos de segurança e tarefas prontas do MediaPipe para extrair atributos visuais e temporais que permitam identificar padrões de comportamento, detectar anomalias e classificar automaticamente eventos de risco?

## Hipótese

Um pipeline em Python, alimentado por vídeos de segurança e pelas saídas do MediaPipe, é capaz de gerar uma base analítica suficientemente rica para sustentar:

- descoberta de padrões por métodos não supervisionados;
- classificação de eventos por métodos supervisionados;
- resultados interpretáveis e úteis para apresentação acadêmica.

## Objetivos específicos

- Construir um pipeline de ingestão e processamento de vídeos em Python.
- Extrair atributos visuais com MediaPipe, como presença de pessoas, landmarks corporais e sinais de movimento.
- Transformar os resultados em uma base tabular com features por frame e por janela temporal.
- Realizar análise exploratória com estatística descritiva, correlação e visualizações.
- Aplicar algoritmos não supervisionados para clusterização e detecção de anomalias.
- Aplicar algoritmos supervisionados para classificar eventos como normal, aglomeração, corrida, queda e permanência suspeita.
- Comparar modelos por métricas apropriadas e consolidar visualizações para apresentação final.

## Escopo inicial

O escopo previsto contempla a análise de:

- detecção de pessoas;
- postura e landmarks corporais;
- movimentação e deslocamento;
- permanência em áreas monitoradas;
- aglomeração;
- anomalias comportamentais;
- classificação de eventos de risco.

## Abordagem técnica

### Camada de percepção

O projeto utiliza o **MediaPipe Solutions** como base de percepção visual, com foco inicial em:

- **Object Detector** para detecção e localização de pessoas e objetos;
- **Pose Landmarker** para extração de landmarks corporais, postura e dinâmica de movimento;
- **Image Classifier** como possibilidade futura para especializações adicionais de classificação.

### Camada analítica

Sobre os atributos extraídos do vídeo, serão aplicadas técnicas de ciência de dados e aprendizado de máquina em duas frentes:

- **Aprendizado não supervisionado** para identificar perfis de cena, agrupamentos e eventos fora do padrão.
- **Aprendizado supervisionado** para classificar eventos rotulados com base em indicadores derivados do vídeo.

## Pipeline proposto

1. **Ingestão**: leitura de vídeos MP4 ou fluxos gravados, extração de frames e organização por janelas temporais.
2. **Percepção**: uso de Object Detector e Pose Landmarker para localizar pessoas e coletar sinais corporais.
3. **Engenharia de atributos**: cálculo de contagem de pessoas, permanência, densidade, deslocamento, velocidade aproximada e ângulos de pose.
4. **EDA e estatística**: análise descritiva, correlação, distribuição, outliers e visualizações.
5. **Modelagem**: treinamento e comparação de algoritmos supervisionados e não supervisionados.
6. **Visualização**: geração de timelines, heatmaps, gráficos comparativos e material de apoio para defesa.

## Indicadores planejados

O sistema deverá produzir indicadores comportamentais e espaciais anonimizados, como:

- contagem de pessoas por frame;
- ocupação por zona;
- permanência;
- direção de deslocamento;
- densidade de cena;
- velocidade aproximada;
- frequência de mudança postural;
- score de movimento;
- indícios de corrida;
- possibilidade de queda;
- permanência acima do esperado em áreas sensíveis.

## Modelos e métricas

### Aprendizado não supervisionado

Modelos iniciais previstos:

- K-Means
- DBSCAN
- Isolation Forest

Métricas previstas:

- Silhouette Score
- Davies-Bouldin
- Calinski-Harabasz
- inspeção qualitativa dos agrupamentos

### Aprendizado supervisionado

Modelos candidatos:

- Regressão Logística
- Random Forest
- SVM
- XGBoost (conforme viabilidade do ambiente)

Métricas previstas:

- accuracy
- precision
- recall
- F1-score
- AUC-ROC
- matriz de confusão

## Base de dados e ética

O projeto prioriza vídeos próprios autorizados, bases públicas compatíveis com análise de movimento ou gravações simuladas para fins acadêmicos. O foco está em **atributos comportamentais e espaciais**, não em identificação individual.

Diretrizes principais:

- evitar reconhecimento facial como objetivo central;
- tratar eventos suspeitos como hipóteses analíticas, nunca como prova conclusiva;
- registrar limitações, possíveis vieses e contexto de uso dos modelos.

## Entregáveis planejados

- Repositório GitHub organizado com código Python modular, notebooks e documentação.
- Base processada com atributos extraídos dos vídeos.
- Análise exploratória com tabelas e visualizações.
- Resultados de clusterização e detecção de anomalias.
- Classificadores supervisionados com comparação de desempenho.
- Apresentação final com roteiro de defesa e demonstração dos resultados.

Os entregáveis foram refinados em trilhas separadas de execução, documentação e validação em `docs/ENTREGAVEIS.md`.

## Estrutura sugerida do repositório

```text
mediapipe-seguranca/
├── CONTRIBUTING.md
├── docs/
│   ├── ARQUITETURA.md
│   ├── DICIONARIO_DE_DADOS.md
│   ├── ENTREGAVEIS.md
│   ├── PLANO_DE_EXECUCAO.md
│   └── ROADMAP.md
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── labels/
├── notebooks/
│   ├── 01_ingestao.ipynb
│   ├── 02_extracao_mediapipe.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_unsupervised.ipynb
│   ├── 06_supervised.ipynb
│   └── 07_visualizacoes.ipynb
├── src/
│   ├── video_io.py
│   ├── mediapipe_extract.py
│   ├── tracking_features.py
│   ├── feature_engineering.py
│   ├── train_unsupervised.py
│   ├── train_supervised.py
│   └── evaluate.py
├── reports/
│   ├── eda/
│   ├── models/
│   ├── figures/
│   └── defesa/
├── requirements.txt
└── README.md
```

## Estrutura refinada para os entregáveis

### Entregáveis técnicos

- **Código-fonte** em `src/mediapipe_seguranca/` com módulos separados por responsabilidade.
- **Runner inicial** em `main.py` para execução da pipeline base.
- **Teste automatizado** em `tests/test_pipeline.py` para validar a base do projeto.

### Entregáveis de dados

- **Dados brutos** em `data/raw/`.
- **Saídas intermediárias** em `data/interim/`.
- **Bases processadas** em `data/processed/`.
- **Rótulos e anotações** em `data/labels/`.

### Entregáveis analíticos

- **Notebooks de exploração** em `notebooks/`.
- **Relatórios de EDA** em `reports/eda/`.
- **Resultados de modelagem** em `reports/models/`.
- **Figuras, heatmaps e gráficos** em `reports/figures/`.

### Entregáveis acadêmicos

- **Planejamento operacional** em `docs/PLANO_DE_EXECUCAO.md`.
- **Matriz de entregáveis** em `docs/ENTREGAVEIS.md`.
- **Material de defesa** em `reports/defesa/`.

## Cronograma resumido

| Semana | Foco principal | Resultado esperado |
| --- | --- | --- |
| 1 | Escopo e revisão | Tema delimitado, pergunta de pesquisa, repositório criado |
| 2 | Coleta e anotação | Vídeos selecionados e protocolo de rotulação definido |
| 3 | Extração com MediaPipe | Pipeline inicial com detecção e pose |
| 4 | Feature engineering | Base tabular consolidada por frame e janela |
| 5 | EDA e estatística | Visualizações, correlações e diagnóstico da base |
| 6 | Modelagem não supervisionada | Clusters, anomalias e interpretação inicial |
| 7 | Modelagem supervisionada | Comparação entre modelos e métricas |
| 8 | Consolidação final | Slides, texto final e preparação para defesa |

## Status do projeto

Atualmente o repositório está em fase inicial de estruturação, com base conceitual definida no pré-projeto. Os próximos passos naturais são:

1. substituir a extração simulada pela leitura real de vídeo;
2. integrar tasks reais do MediaPipe;
3. consolidar contrato de dados e rótulos;
4. produzir notebooks de EDA e modelagem;
5. transformar resultados em artefatos prontos para defesa.

## Estrutura inicial criada

Além da documentação, o repositório já conta com uma base executável em Python:

- `main.py`: ponto de entrada para rodar a pipeline demo.
- `src/mediapipe_seguranca/`: pacote com ingestão sintética, extração simulada, features e baselines.
- `tests/test_pipeline.py`: teste básico da pipeline inicial.
- `requirements.txt`: dependências mínimas para a base analítica.
- `data/`, `notebooks/` e `reports/`: diretórios preparados para evolução do projeto.

## Critérios de maturidade do repositório

Para que o projeto avance com qualidade, cada entrega deve atender a alguns critérios mínimos:

- **Reprodutibilidade**: scripts e notebooks devem ser executáveis a partir da estrutura do repositório.
- **Rastreabilidade**: todo artefato analítico deve indicar origem dos dados e etapa da pipeline.
- **Interpretabilidade**: modelos e visualizações devem ser explicáveis e defendáveis em contexto acadêmico.
- **Ética e escopo**: o foco deve permanecer em comportamento de cena, não em identificação pessoal.
- **Organização**: cada resultado deve ser salvo na pasta compatível com seu tipo de evidência.

## Como executar

1. Crie e ative um ambiente virtual Python.
2. Instale as dependências.
3. Rode a pipeline demo para gerar uma base inicial em `data/processed/`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Como testar

```powershell
python -m unittest discover -s tests -v
```

## Próximos incrementos sugeridos

- substituir a extração simulada por leitura real de vídeo com `opencv-python`;
- integrar detectores do MediaPipe conforme os modelos escolhidos;
- criar notebooks de EDA, clusterização e classificação;
- adicionar ingestão de rótulos reais em `data/labels/`.

## Convenções de evolução

- novas saídas analíticas devem ser registradas em `reports/`;
- novas bases geradas devem seguir a separação entre `interim` e `processed`;
- notebooks devem refletir a ordem da pipeline e manter numeração sequencial;
- mudanças estruturais devem atualizar o `README.md` e os arquivos em `docs/`.

## Referências iniciais

- Google AI Edge — MediaPipe Solutions Guide
- Google AI Edge — Object Detection Guide for Python
- Google AI Edge — Pose Landmarker Guide for Python
- Google AI Edge — Image Classification Guide for Python
- Google AI Edge — `mediapipe_model_maker`

## Observação

Este `README.md` foi elaborado com base no documento `pre_projeto_puc_mediapipe.docx`, consolidando os principais elementos acadêmicos e técnicos da proposta.

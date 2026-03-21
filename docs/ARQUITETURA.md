# Arquitetura do projeto

Este documento descreve a arquitetura lógica do projeto, conectando objetivos acadêmicos, organização do repositório e fluxo da pipeline.

## Visão geral

O projeto segue uma arquitetura orientada a pipeline, na qual vídeos de segurança são transformados em sinais visuais, depois em atributos analíticos, e por fim em evidências quantitativas e visuais para análise e defesa acadêmica.

## Camadas principais

### 1. Ingestão

Responsável por ler os dados de entrada e organizar a base temporal mínima do projeto.

- origem principal: `data/raw/`
- módulo relacionado: `src/mediapipe_seguranca/video_io.py`
- saídas típicas: metadados de vídeo, frames, janelas temporais

### 2. Percepção visual

Responsável por extrair sinais relevantes das imagens e vídeos.

- módulo relacionado: `src/mediapipe_seguranca/mediapipe_extract.py`
- tecnologia-alvo: MediaPipe
- saídas típicas: detecções, landmarks, presença de pessoas, sinais espaciais

### 3. Engenharia de atributos

Responsável por transformar sinais brutos em variáveis interpretáveis para EDA e modelagem.

- módulos relacionados:
  - `src/mediapipe_seguranca/tracking_features.py`
  - `src/mediapipe_seguranca/feature_engineering.py`
- saídas típicas: contagem, densidade, permanência, velocidade, score de risco, agregações por janela

### 4. Modelagem analítica

Responsável por descobrir padrões e classificar eventos.

- trilha não supervisionada: `src/mediapipe_seguranca/train_unsupervised.py`
- trilha supervisionada: `src/mediapipe_seguranca/train_supervised.py`
- avaliação: `src/mediapipe_seguranca/evaluate.py`

### 5. Evidências e comunicação

Responsável por transformar resultados em material utilizável para análise e defesa.

- notebooks: `notebooks/`
- relatórios: `reports/`
- planejamento: `docs/`

## Fluxo de dados

```text
data/raw/
  -> ingestão e leitura temporal
  -> percepção visual / MediaPipe
  -> data/interim/
  -> engenharia de atributos
  -> data/processed/
  -> EDA e modelagem
  -> reports/figures/, reports/eda/, reports/models/
  -> reports/defesa/
```

## Organização por responsabilidade

### Código-fonte

- concentra a lógica reutilizável e executável do projeto;
- deve permanecer independente de notebooks;
- organiza a pipeline em módulos com responsabilidade única.

### Dados

- separam origem, transformação intermediária, base final e rótulos;
- permitem rastreabilidade e defesa metodológica;
- evitam mistura entre insumo e artefato analítico.

### Notebooks

- concentram exploração, validação visual e experimentação analítica;
- servem como ponte entre pipeline e interpretação;
- não substituem módulos reutilizáveis em `src/`.

### Relatórios

- consolidam resultados em formato comunicável;
- organizam evidências para EDA, modelagem, figuras e defesa;
- reduzem dispersão de informação entre notebooks e documentação geral.

## Ponto de entrada atual

- `main.py`: runner principal da pipeline demo.
- `src/mediapipe_seguranca/pipeline.py`: orquestração das etapas da base inicial.

## Estado atual da arquitetura

No estado atual, a arquitetura já suporta:

- execução de uma pipeline demonstrativa;
- geração de base sintética para validar o fluxo;
- organização de diretórios alinhada aos entregáveis;
- documentação separada por responsabilidade.

Os próximos avanços esperados são:

1. substituir a extração simulada por leitura real de vídeo;
2. integrar tasks reais do MediaPipe;
3. consolidar contrato de rótulos e datasets finais;
4. transformar notebooks planejados em notebooks executáveis;
5. preencher `reports/` com evidências concretas.

## Decisões arquiteturais

- **Separação entre pipeline e exploração**: lógica estável em `src/`, exploração em `notebooks/`.
- **Separação entre tipos de dados**: bruto, intermediário, processado e rótulos ficam em diretórios diferentes.
- **Separação entre análise e apresentação**: relatórios e figuras servem como ponte entre experimento e defesa.
- **Prioridade para rastreabilidade**: cada artefato deve indicar sua origem, etapa e finalidade.

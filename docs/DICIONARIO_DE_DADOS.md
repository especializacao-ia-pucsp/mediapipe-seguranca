# Dicionário de dados

Este documento descreve os principais campos, métricas e rótulos previstos no projeto, com foco no estado atual da pipeline demo e na evolução esperada para a versão com vídeo real e MediaPipe.

## Navegação

- [Início](../README.md)
- [Contribuição](../CONTRIBUTING.md)
- [Arquitetura](ARQUITETURA.md)
- [Cronograma](CRONOGRAMA.md)
- [Entregáveis](ENTREGAVEIS.md)
- [Estratégia de dados e modelagem](ESTRATEGIA_DADOS_E_MODELAGEM.md)
- [Plano de execução](PLANO_DE_EXECUCAO.md)
- [Roadmap](ROADMAP.md)
- [Dados](../data/README.md)
- [Dados processados](../data/processed/README.md)
- [Rótulos](../data/labels/README.md)
- [Notebooks](../notebooks/README.md)
- [Relatórios](../reports/README.md)

## Objetivo

Padronizar a interpretação das variáveis analíticas do projeto, reduzir ambiguidades entre notebooks, código e relatórios, e apoiar a rastreabilidade das bases geradas em `data/interim/` e `data/processed/`.

## Níveis de granularidade

O projeto trabalha com dois níveis principais de observação:

- **Por frame**: variáveis extraídas ou derivadas para cada quadro do vídeo.
- **Por janela temporal**: agregações resumidas de múltiplos frames, usadas em EDA e modelagem.

## Esquema atual da pipeline demo

Atualmente, a pipeline base gera uma estrutura sintética que simula a futura base analítica do projeto. Ela é suficiente para validar o fluxo de transformação e para documentar a expectativa de colunas.

### Variáveis por frame

| Campo | Tipo esperado | Origem | Descrição |
| --- | --- | --- | --- |
| `frame_index` | inteiro | ingestão | Índice sequencial do frame dentro do vídeo processado. |
| `window_id` | inteiro | ingestão | Identificador da janela temporal à qual o frame pertence. |
| `people_count` | inteiro | percepção | Quantidade estimada de pessoas na cena. |
| `movement_score` | numérico contínuo | percepção | Score sintético de movimento observado no frame. |
| `posture_change_rate` | numérico contínuo | percepção | Indicador de variação postural no frame ou região analisada. |
| `estimated_speed` | numérico contínuo | percepção | Estimativa simplificada de velocidade de deslocamento. |
| `dense_scene` | binário inteiro | percepção | Indicador de alta densidade de pessoas na cena. |
| `fall_risk_score` | numérico contínuo | percepção | Score simplificado relacionado a indícios de queda ou instabilidade corporal. |
| `suspicious_loitering` | binário inteiro | percepção | Indicador de permanência suspeita ou acima do esperado. |
| `label` | categórico | anotação/demo | Classe associada ao frame no cenário sintético. |

### Variáveis derivadas por frame

| Campo | Tipo esperado | Origem | Descrição |
| --- | --- | --- | --- |
| `occupancy_score` | numérico contínuo | feature engineering | Score derivado da ocupação da cena, ponderado por densidade. |
| `risk_score` | numérico contínuo | feature engineering | Score composto de risco calculado a partir de movimento, velocidade, queda e permanência suspeita. |
| `motion_intensity` | numérico contínuo | feature engineering | Intensidade de movimento calculada pelo produto entre movimento e velocidade estimada. |

### Variáveis agregadas por janela

| Campo | Tipo esperado | Descrição |
| --- | --- | --- |
| `window_id` | inteiro | Identificador da janela temporal agregada. |
| `people_count_mean` | numérico contínuo | Média de pessoas observadas na janela. |
| `people_count_max` | inteiro | Máximo de pessoas observadas na janela. |
| `movement_score_mean` | numérico contínuo | Média do score de movimento. |
| `posture_change_rate_mean` | numérico contínuo | Média da variação postural. |
| `estimated_speed_mean` | numérico contínuo | Média da velocidade estimada. |
| `dense_scene_rate` | numérico contínuo | Proporção de frames com cena densa dentro da janela. |
| `suspicious_loitering_rate` | numérico contínuo | Proporção de frames com indício de permanência suspeita. |
| `fall_risk_score_mean` | numérico contínuo | Média do score de risco de queda. |
| `occupancy_score_mean` | numérico contínuo | Média do score de ocupação. |
| `risk_score_mean` | numérico contínuo | Média do score composto de risco. |
| `motion_intensity_mean` | numérico contínuo | Média da intensidade de movimento. |
| `label` | categórico | Classe dominante da janela. |
| `event_count` | inteiro | Contador de eventos agregados; na demo atual é fixado em `1`. |

### Variáveis auxiliares da modelagem demo

| Campo | Tipo esperado | Descrição |
| --- | --- | --- |
| `cluster_id` | inteiro categórico | Cluster atribuído pela baseline não supervisionada. |
| `anomaly_flag` | inteiro categórico | Indicador de anomalia, com `-1` para anômalo e `1` para padrão esperado. |
| `anomaly_score` | numérico contínuo | Distância relativa ao risco médio da base. |

## Rótulos atuais e rótulos planejados

### ShanghaiTech Campus Dataset

**Origem**: SVIP Lab, ShanghaiTech University via OneDrive official link
**Versão**: 2024-12 (extraído 2026-03-28)
**Tamanho**: 6.67 GB (comprimido), ~8.5 GB (descomprimido)
**Disponibilidade**: estrutura real suportada localmente via download/extração manual; repositório versiona apenas documentação e `SAMPLE/`

#### Contagem de Amostras

As contagens abaixo referem-se ao dataset real quando presente localmente em `data/raw/shanghaitech/`.

- **Training videos**: 330 (pasta `training/frames/`)
- **Test videos**: 109 (pasta `testing/frames/`)
- **Ground Truth masks**: 109 (pasta `testing/test_frame_mask/`, formato .npy)

#### Estrutura de Dados

- **Frames**: JPEG 640×480 (ou resolução nativa), índices 000.jpg, 001.jpg, ...
- **GT masks**: uint8 NumPy array (0=background, 1=foreground anomaly)
- **Localização no projeto**: `data/raw/shanghaitech/`

#### Variáveis Resultantes

| Nome | Tipo | Granularidade | Descrição |
| --- | --- | --- | --- |
| `video_id` | string | video | Identificador único (e.g., "01_001") |
| `frame_index` | int | frame | Índice sequencial do frame (0-based) |
| `frame_path` | string | frame | Caminho relativo ao frame JPEG |
| `has_gt_mask` | bool | video | Indica se vídeo tem GT mask correspondente |
| `gt_mask_path` | string | video | Caminho para .npy (se exists) |
| `frame_count` | int | video | Total de frames no vídeo |

---

### Rótulos e taxonomia

### Rótulos usados na demo

| Rótulo | Significado |
| --- | --- |
| `normal` | Cena com comportamento esperado e baixa intensidade de risco. |
| `aglomeracao` | Cena com maior densidade de pessoas e ocupação elevada. |
| `evento_risco` | Cena sintética genérica representando condição de risco. |

### Taxonomia planejada para o projeto

| Rótulo planejado | Significado |
| --- | --- |
| `normal` | Operação normal da cena. |
| `aglomeracao` | Concentração elevada de pessoas em um espaço ou intervalo curto. |
| `corrida` | Deslocamento acelerado incompatível com o padrão esperado. |
| `queda` | Indícios de perda de equilíbrio ou colapso postural. |
| `permanencia_suspeita` | Permanência acima do esperado em área sensível ou por tempo excessivo. |

## Features usadas atualmente nas baselines

As baselines da versão inicial usam as seguintes colunas como base analítica:

- `people_count_mean`
- `movement_score_mean`
- `estimated_speed_mean`
- `dense_scene_rate`
- `suspicious_loitering_rate`
- `risk_score_mean`

Essas colunas formam o núcleo mínimo do experimento atual e servem como ponto de partida para expansão futura.

## Origem lógica das variáveis

### Ingestão

- `frame_index`
- `window_id`

### Percepção

- `people_count`
- `movement_score`
- `posture_change_rate`
- `estimated_speed`
- `dense_scene`
- `fall_risk_score`
- `suspicious_loitering`

### Engenharia de atributos

- `occupancy_score`
- `risk_score`
- `motion_intensity`
- todas as colunas agregadas com sufixo `_mean`, `_max` ou `_rate`

### Modelagem

- `cluster_id`
- `anomaly_flag`
- `anomaly_score`

## Convenções recomendadas

- colunas por janela devem indicar a operação aplicada, como `_mean`, `_max` ou `_rate`;
- colunas binárias devem usar valores consistentes e bem documentados;
- campos categóricos devem ter taxonomia estável, especialmente em `label`;
- sempre que a estrutura do dataset mudar, este documento deve ser atualizado.

## Campos esperados em versões futuras

Conforme a integração com MediaPipe evoluir, o dicionário poderá incorporar colunas como:

- coordenadas normalizadas de landmarks;
- ângulos articulares;
- direção de deslocamento por trilha;
- ocupação por zona;
- permanência por área sensível;
- densidade espacial por região;
- score temporal de anomalia por segmento.

## Relação com o restante da documentação

- `data/README.md`: define a política de armazenamento das bases.
- `docs/ARQUITETURA.md`: explica onde as variáveis surgem na pipeline.
- `docs/ENTREGAVEIS.md`: conecta datasets e features aos entregáveis.
- `notebooks/`: usa este documento como referência para análise e visualização.

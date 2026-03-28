# Plano de execução

Este documento organiza o desenvolvimento do projeto em etapas práticas, conectando implementação, análise e material de apresentação. As etapas estão alinhadas ao [Cronograma do Projeto Integrador](CRONOGRAMA.md) e à metodologia CRISP-DM adaptada ao contexto acadêmico.

## Navegação

- [Início](../README.md)
- [Contribuição](../CONTRIBUTING.md)
- [Arquitetura](ARQUITETURA.md)
- [Cronograma](CRONOGRAMA.md)
- [Entregáveis](ENTREGAVEIS.md)
- [Roadmap](ROADMAP.md)
- [Dicionário de dados](DICIONARIO_DE_DADOS.md)
- [Dados](../data/README.md)
- [Notebooks](../notebooks/README.md)
- [Relatórios](../reports/README.md)

---

## Visão geral das etapas

O plano de execução está organizado em 8 etapas que cobrem as 8 macro-fases do Cronograma PI e as fases do CRISP-DM.

### Diagrama de fluxo de execução

O fluxo abaixo mostra a sequência de etapas com gates de validação entre elas. Cada gate verifica se as saídas mínimas da etapa anterior estão concluídas antes de avançar.

```mermaid
flowchart TD
    E1["Etapa 1<br/>Fundação"]
    G1{{"Gate 1<br/>Repositório operacional?"}}
    E2["Etapa 2<br/>Ingestão e Percepção"]
    G2{{"Gate 2<br/>Vídeos lidos com sucesso?"}}
    E3["Etapa 3<br/>Engenharia de Atributos"]
    G3{{"Gate 3<br/>Base analítica estável?"}}
    E4["Etapa 4<br/>EDA e Estatística"]
    G4{{"Gate 4<br/>Padrões identificados?"}}
    E5["Etapa 5<br/>Análise Diagnóstica"]
    G5{{"Gate 5<br/>Causas documentadas?"}}
    E6["Etapa 6<br/>Modelagem Analítica"]
    G6{{"Gate 6<br/>Modelos avaliados?"}}
    E7["Etapa 7<br/>Análise Prescritiva"]
    G7{{"Gate 7<br/>Recomendações formuladas?"}}
    E8["Etapa 8<br/>Consolidação de Defesa"]

    E1 --> G1 --> E2 --> G2 --> E3 --> G3 --> E4 --> G4 --> E5 --> G5 --> E6 --> G6 --> E7 --> G7 --> E8

    style E1 fill:#4CAF50,color:#fff
    style E2 fill:#FF9800,color:#fff
    style E3 fill:#78909C,color:#fff
    style E4 fill:#78909C,color:#fff
    style E5 fill:#78909C,color:#fff
    style E6 fill:#78909C,color:#fff
    style E7 fill:#78909C,color:#fff
    style E8 fill:#78909C,color:#fff
    style G1 fill:#E3F2FD,color:#333
    style G2 fill:#E3F2FD,color:#333
    style G3 fill:#E3F2FD,color:#333
    style G4 fill:#E3F2FD,color:#333
    style G5 fill:#E3F2FD,color:#333
    style G6 fill:#E3F2FD,color:#333
    style G7 fill:#E3F2FD,color:#333
```

### Diagrama de dependências

O diagrama abaixo mostra as dependências entre etapas, incluindo dependências paralelas e convergências.

```mermaid
flowchart TD
    subgraph fundacao["Fundação e Dados"]
        E1["Etapa 1<br/>Fundação"]
        E2["Etapa 2<br/>Ingestão e Percepção"]
        E3["Etapa 3<br/>Engenharia de Atributos"]
    end

    subgraph analise["Análise"]
        E4["Etapa 4<br/>EDA e Estatística"]
        E5["Etapa 5<br/>Análise Diagnóstica"]
    end

    subgraph modelagem["Modelagem"]
        E6["Etapa 6<br/>Modelagem Analítica"]
        E7["Etapa 7<br/>Análise Prescritiva"]
    end

    subgraph defesa["Defesa"]
        E8["Etapa 8<br/>Consolidação de Defesa"]
    end

    ROT["Rótulos<br/>data/labels/"]

    E1 --> E2 --> E3
    E3 --> E4 --> E5
    E3 --> E6
    ROT --> E6
    E5 --> E8
    E6 --> E7
    E7 --> E8

    style E1 fill:#4CAF50,color:#fff
    style E2 fill:#FF9800,color:#fff
    style E3 fill:#78909C,color:#fff
    style E4 fill:#78909C,color:#fff
    style E5 fill:#78909C,color:#fff
    style E6 fill:#78909C,color:#fff
    style E7 fill:#78909C,color:#fff
    style E8 fill:#78909C,color:#fff
    style ROT fill:#FFC107,color:#333
    style fundacao fill:#E8F5E9,stroke:#4CAF50
    style analise fill:#E3F2FD,stroke:#2196F3
    style modelagem fill:#F3E5F5,stroke:#9C27B0
    style defesa fill:#FFF3E0,stroke:#FF9800
```

### Mapeamento etapas vs. cronograma PI

| Etapa | Macro-fase do cronograma PI | Fase CRISP-DM |
| --- | --- | --- |
| Etapa 1 — Fundação | 1. Definição + 2. Setup Infra | Entendimento do Negócio |
| Etapa 2 — Ingestão e Percepção | 3. Pré-Processamento (Ingestão) | Entendimento dos Dados |
| Etapa 3 — Engenharia de Atributos | 3. Pré-Processamento (Tratamento, Pipeline, Governança) | Preparação dos Dados |
| Etapa 4 — EDA e Estatística | 4. Análise Descritiva/Exploratória | Preparação dos Dados / Modelagem |
| Etapa 5 — Análise Diagnóstica | 5. Análise Diagnóstica | Avaliação |
| Etapa 6 — Modelagem Analítica | 6. Análise Preditiva | Modelagem |
| Etapa 7 — Análise Prescritiva | 7. Análise Prescritiva | Avaliação / Implantação |
| Etapa 8 — Consolidação de Defesa | 8. Construção da Apresentação Final | Implantação / Defesa |

---

## Etapa 1: fundação

**Objetivo**: garantir uma base organizada, executável e com todas as definições necessárias para o projeto.

**Alinha com**: Cronograma PI — Seção 1 (Definição), atividades 4-30 + Seção 2 (Setup Infra), atividades 33-40
**Fases do roadmap**: Fase 1

### Itens de trabalho

- definir problema, hipótese e objetivos do projeto;
- definir ferramentas, arquitetura e metodologia (CRISP-DM);
- criar estrutura do repositório com diretórios padronizados;
- configurar ambiente Python (venv, requirements.txt);
- implementar pipeline demo executável;
- documentar entregáveis, arquitetura, dicionário de dados;
- definir estratégia de gerenciamento (GitHub Issues/Projects);
- definir governança básica: dicionário de dados, versionamento, convenções.

### Checklist de validação

| Item | Evidência esperada | Status |
| --- | --- | --- |
| Estrutura de diretórios | Pastas `data/`, `src/`, `notebooks/`, `reports/`, `docs/`, `tests/` criadas | Concluído |
| README consolidado | `README.md` com visão geral do projeto | Concluído |
| Package Python | `src/mediapipe_seguranca/` com `__init__.py` | Concluído |
| Pipeline demo | `main.py` executável sem erros | Concluído |
| Teste básico | `tests/test_pipeline.py` passando | Concluído |
| Documentação base | `docs/ARQUITETURA.md`, `ENTREGAVEIS.md`, `PLANO_DE_EXECUCAO.md`, `ROADMAP.md`, `CRONOGRAMA.md` | Concluído |
| Dicionário de dados | `docs/DICIONARIO_DE_DADOS.md` com variáveis iniciais | Concluído |
| Ambiente configurado | `requirements.txt` com dependências, `.venv/` funcional | Concluído |

---

## Etapa 2: ingestão e percepção

**Objetivo**: sair da simulação e entrar na leitura real de vídeo, integrando os detectores do MediaPipe.

**Alinha com**: Cronograma PI — Seção 3 (Pré-Processamento), atividades 49, 55, 58-60 (Ingestão) e 69-77 (Tratamento)
**Fases do roadmap**: Fase 2 + Fase 3

### Itens de trabalho

- definir formato e protocolo dos vídeos de entrada;
- implementar leitura real de vídeo quadro a quadro;
- definir volumetria e estratégia de amostragem;
- integrar tarefas reais do MediaPipe (detecção de pose, landmarks);
- validar detecção de pessoas e sinais visuais;
- salvar saídas intermediárias com rastreabilidade;
- documentar estrutura de colunas intermediária.

### Checklist de validação

| Item | Evidência esperada | Status |
| --- | --- | --- |
| Vídeos de teste | Amostras em `data/raw/` com metadados documentados | Planejado |
| Leitura de vídeo | `video_io.py` lendo vídeos reais sem erros | Planejado |
| Integração MediaPipe | `mediapipe_extract.py` extraindo sinais reais de pose | Planejado |
| Saídas intermediárias | Arquivos em `data/interim/` rastreáveis | Planejado |
| Notebook de ingestão | Notebook `01_ingestao` executável | Planejado |
| Notebook de extração | Notebook `02_extracao_mediapipe` executável | Planejado |
| Documentação de colunas | Estrutura de colunas documentada no dicionário | Planejado |

---

## Etapa 3: engenharia de atributos

**Objetivo**: transformar sinais visuais em variáveis úteis para análise, consolidando a base analítica.

**Alinha com**: Cronograma PI — Seção 3 (Pré-Processamento), atividades 72-77 (Tratamento), 80-83 (Processamento), 86-88 (Pipeline), 91-95 (Governança)
**Fases do roadmap**: Fase 4

### Itens de trabalho

- consolidar atributos por frame a partir dos sinais do MediaPipe;
- agregar atributos por janela temporal;
- implementar limpeza, integração e transformação de dados;
- definir e documentar variáveis e escalas no dicionário;
- estabilizar a base para EDA e modelagem;
- garantir governança: linhagem rastreável, qualidade verificável;
- revisar consistência dos dados com validações automáticas.

### Checklist de validação

| Item | Evidência esperada | Status |
| --- | --- | --- |
| Features por frame | `feature_engineering.py` gerando features por frame | Planejado |
| Features por janela | `tracking_features.py` gerando features por janela temporal | Planejado |
| Base processada | Arquivos em `data/processed/` prontos para análise | Planejado |
| Notebook de features | Notebook `03_feature_engineering` executável | Planejado |
| Dicionário atualizado | `docs/DICIONARIO_DE_DADOS.md` com todas as variáveis | Planejado |
| Pipeline integrada | `pipeline.py` executando fluxo completo de dados reais | Planejado |
| Qualidade de dados | Validações de completude, tipos e ranges aplicadas | Planejado |

---

## Etapa 4: EDA e estatística

**Objetivo**: entender comportamento, distribuição e padrões iniciais dos dados preparados.

**Alinha com**: Cronograma PI — Seção 4 (Análise Descritiva/Exploratória), atividades 106-118
**Fases do roadmap**: Fase 5

### Itens de trabalho

- calcular estatística descritiva: média, mediana, moda, desvio padrão, variância;
- analisar distribuição de frequência e classes;
- calcular medidas de posição relativa (percentis, quartis);
- analisar correlação e associação entre atributos;
- identificar e tratar outliers e valores ausentes;
- produzir gráficos temporais e de distribuição;
- gerar visualizações para a banca (heatmaps, boxplots, séries temporais);
- sintetizar achados em relatório interpretativo.

### Checklist de validação

| Item | Evidência esperada | Status |
| --- | --- | --- |
| Estatística descritiva | Medidas resumo calculadas para todas as variáveis | Planejado |
| Análise de correlação | Matriz de correlação e heatmap gerados | Planejado |
| Outliers e missing | Análise de valores atípicos e ausentes documentada | Planejado |
| Notebook de EDA | Notebook `04_eda` executável com interpretações | Planejado |
| Gráficos salvos | Figuras em `reports/figures/` reutilizáveis | Planejado |
| Relatório de EDA | Síntese em `reports/eda/` com achados principais | Planejado |
| Recomendações | Indicações para modelagem baseadas na EDA | Planejado |

---

## Etapa 5: análise diagnóstica

**Objetivo**: investigar causas dos padrões encontrados na EDA e formular plano de ação para modelagem.

**Alinha com**: Cronograma PI — Seção 5 (Análise Diagnóstica), atividades 122-125
**Fases do roadmap**: Fase 5b

### Itens de trabalho

- investigar causas dos fenômenos observados nos dados;
- analisar impactos dos padrões identificados no contexto de segurança;
- documentar desafios entre dados reais e dados observados;
- identificar limitações e vieses dos dados;
- formular plano de ação e recomendações para as fases de modelagem.

### Checklist de validação

| Item | Evidência esperada | Status |
| --- | --- | --- |
| Análise causal | Investigação de causas integrada à EDA | Planejado |
| Análise de impacto | Discussão dos impactos dos padrões observados | Planejado |
| Limitações documentadas | Vieses e restrições dos dados registrados | Planejado |
| Plano de ação | Recomendações para modelagem documentadas em `reports/eda/` | Planejado |
| Relatório diagnóstico | Seção de diagnóstico em `reports/eda/` | Planejado |

---

## Etapa 6: modelagem analítica

**Objetivo**: comparar abordagens supervisionadas e não supervisionadas para detecção de padrões e classificação de eventos.

**Alinha com**: Cronograma PI — Seção 6 (Análise Preditiva), atividades 130-141
**Fases do roadmap**: Fase 6 + Fase 7

### Itens de trabalho

- definir abordagens de IA: clusterização, detecção de anomalias, classificação;
- treinar modelos não supervisionados (perfis de cena, anomalias);
- treinar modelos supervisionados com eventos rotulados;
- validar balanceamento de classes e tratar viés;
- ajustar hiperparâmetros e otimizar modelos;
- calcular métricas de avaliação (acurácia, precision, recall, F1, silhouette);
- gerar matrizes de confusão e gráficos de comparação;
- analisar erros e limitações dos modelos;
- comparar desempenho entre abordagens.

### Checklist de validação

| Item | Evidência esperada | Status |
| --- | --- | --- |
| Modelos não supervisionados | Clusterização executada e interpretada | Planejado |
| Modelos supervisionados | Classificação treinada e avaliada | Planejado |
| Rótulos disponíveis | Anotações em `data/labels/` com convenção documentada | Planejado |
| Métricas registradas | Métricas de cada modelo salvas em `reports/models/` | Planejado |
| Notebook não supervisionado | Notebook `05_unsupervised` executável | Planejado |
| Notebook supervisionado | Notebook `06_supervised` executável | Planejado |
| Comparação de modelos | Tabela comparativa em `reports/models/` | Planejado |
| Análise de erros | Discussão de limitações e erros dos modelos | Planejado |

---

## Etapa 7: análise prescritiva

**Objetivo**: interpretar resultados dos modelos preditivos e formular recomendações baseadas em dados para o contexto de segurança.

**Alinha com**: Cronograma PI — Seção 7 (Análise Prescritiva), atividades 148-153
**Fases do roadmap**: Fase 7b

### Itens de trabalho

- interpretar resultados dos modelos preditivos em contexto de segurança;
- avaliar resolubilidade e viabilidade das recomendações;
- formular prescrições baseadas em dados (ações sugeridas);
- consolidar inferências e conclusões para a defesa;
- documentar resultado final e tomada de decisão baseada em dados.

### Checklist de validação

| Item | Evidência esperada | Status |
| --- | --- | --- |
| Estudo de resultados | Análise de resultados preditivos em `reports/models/` | Planejado |
| Recomendações formuladas | Prescrições documentadas com base em dados | Planejado |
| Inferências consolidadas | Síntese de inferências em `reports/defesa/` | Planejado |
| Notebook de visualizações | Notebook `07_visualizacoes` com resultados finais | Planejado |
| Tomada de decisão | Conclusões e recomendações finais documentadas | Planejado |

---

## Etapa 8: consolidação de defesa

**Objetivo**: transformar resultados em narrativa acadêmica e preparar todo o material para defesa oral do projeto.

**Alinha com**: Cronograma PI — Seção 8 (Construção da Apresentação Final), atividades 159-163
**Fases do roadmap**: Fase 8

### Itens de trabalho

- selecionar figuras-chave para a apresentação;
- organizar achados principais em narrativa coerente;
- registrar limitações e riscos metodológicos;
- garantir qualidade do código (linting, formatação, testes);
- verificar organização final do repositório;
- montar roteiro de defesa oral;
- estruturar slides de apresentação;
- documentar todo o processo de aprendizado.

### Checklist de validação

| Item | Evidência esperada | Status |
| --- | --- | --- |
| Figuras finais | Gráficos selecionados em `reports/figures/` | Planejado |
| Roteiro de defesa | Roteiro em `reports/defesa/` | Planejado |
| Slides | Estrutura de apresentação em `reports/defesa/` | Planejado |
| Qualidade de código | Linting (ruff), formatação (black/isort), testes (pytest) aprovados | Planejado |
| Repositório organizado | Estrutura limpa e navegável | Planejado |
| Narrativa técnica | Encadeamento hipótese-método-resultado-conclusão | Planejado |
| Documentação completa | Todos os docs atualizados e coerentes | Planejado |
| Limitações registradas | Seção de limitações e próximos passos documentada | Planejado |

---

## Definição de pronto por frente

- **Código**: executa sem ajustes manuais fora do fluxo documentado.
- **Dados**: possuem origem e etapa identificáveis.
- **Análise**: contém explicação, não apenas gráfico ou métrica.
- **Modelagem**: registra critérios de avaliação e interpretação.
- **Governança**: dicionário atualizado, linhagem rastreável, qualidade verificável.
- **Defesa**: conecta resultados ao objetivo do projeto.

## Relação com outros documentos

- [Cronograma PI](CRONOGRAMA.md): mapeamento detalhado das atividades do PI.
- [Roadmap](ROADMAP.md): fases do projeto e dependências.
- [Entregáveis](ENTREGAVEIS.md): matriz de artefatos e critérios de aceite.
- [Arquitetura](ARQUITETURA.md): camadas e módulos da pipeline.
- [Dicionário de dados](DICIONARIO_DE_DADOS.md): variáveis, tipos e granularidade.

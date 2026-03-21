# Roadmap do projeto

Este documento organiza a evolução do projeto em fases, marcos e dependências, conectando planejamento técnico, entregáveis acadêmicos e prioridades de implementação.

## Objetivo

Servir como visão executiva do progresso esperado do projeto, deixando claro:

- o que já está estruturado;
- o que vem a seguir;
- quais entregas dependem de outras;
- quais marcos são mais importantes para a defesa acadêmica.

## Estado atual

No momento, o projeto já possui:

- estrutura base do repositório em Python;
- pipeline demo executável;
- testes mínimos para a base inicial;
- documentação de arquitetura, entregáveis, dados, notebooks e relatórios;
- contrato inicial de organização do trabalho acadêmico e técnico.

## Fases do roadmap

### Fase 1: fundação documental e estrutural

**Status**: concluída

#### Objetivos

- consolidar a estrutura do repositório;
- registrar convenções de organização;
- documentar entregáveis, arquitetura e dicionário de dados;
- criar base inicial executável.

#### Principais saídas

- `README.md`
- `CONTRIBUTING.md`
- `docs/ENTREGAVEIS.md`
- `docs/PLANO_DE_EXECUCAO.md`
- `docs/ARQUITETURA.md`
- `docs/DICIONARIO_DE_DADOS.md`
- estrutura de `data/`, `notebooks/`, `reports/`, `src/` e `tests/`

### Fase 2: ingestão real de vídeo

**Status**: planejada

#### Objetivos

- substituir a ingestão sintética por leitura real de vídeo;
- validar formato, duração e metadados das amostras;
- definir estratégia de amostragem e janelamento.

#### Dependências

- disponibilidade de vídeos de teste em `data/raw/`;
- definição mínima de protocolo de entrada.

#### Principais saídas

- rotina real de leitura de vídeo;
- metadados por frame ou segmento;
- documentação do formato de entrada;
- notebook de ingestão executável.

### Fase 3: integração com MediaPipe

**Status**: planejada

#### Objetivos

- integrar tarefas reais do MediaPipe;
- validar detecção de pessoas e sinais de pose;
- definir quais saídas entram na engenharia de atributos.

#### Dependências

- Fase 2 concluída;
- seleção das tasks do MediaPipe mais compatíveis com o problema.

#### Principais saídas

- extração real de sinais visuais;
- amostras e inspeções qualitativas;
- estrutura intermediária de colunas;
- notebook de extração executável.

### Fase 4: consolidação da base analítica

**Status**: planejada

#### Objetivos

- transformar sinais visuais em features por frame e por janela;
- definir dicionário de variáveis consolidado;
- estabilizar a base para EDA e modelagem.

#### Dependências

- Fase 3 concluída;
- regras mínimas de agregação temporal definidas.

#### Principais saídas

- bases em `data/interim/` e `data/processed/`;
- features documentadas;
- notebook de feature engineering executável;
- atualização do `docs/DICIONARIO_DE_DADOS.md`.

### Fase 5: análise exploratória e estatística

**Status**: planejada

#### Objetivos

- entender distribuição, correlação e qualidade dos dados;
- identificar atributos relevantes;
- produzir evidências visuais e analíticas para a banca.

#### Dependências

- Fase 4 concluída.

#### Principais saídas

- notebook de EDA executável;
- gráficos em `reports/figures/`;
- sínteses em `reports/eda/`;
- recomendações para modelagem.

### Fase 6: modelagem não supervisionada

**Status**: planejada

#### Objetivos

- descobrir perfis de cena;
- detectar anomalias sem depender de rótulos;
- interpretar agrupamentos no contexto de segurança.

#### Dependências

- Fase 5 concluída ou suficientemente avançada;
- base processada estável.

#### Principais saídas

- notebook ou script de clusterização;
- resultados em `reports/models/`;
- figuras comparativas em `reports/figures/`.

### Fase 7: modelagem supervisionada

**Status**: planejada

#### Objetivos

- treinar classificadores com eventos rotulados;
- comparar desempenho entre modelos;
- analisar erros e limitações.

#### Dependências

- base processada consolidada;
- disponibilidade de rótulos em `data/labels/`.

#### Principais saídas

- notebook ou script supervisionado;
- métricas e matrizes de confusão;
- comparações em `reports/models/`.

### Fase 8: consolidação de defesa

**Status**: planejada

#### Objetivos

- transformar resultados em narrativa acadêmica;
- selecionar figuras-chave;
- estruturar a apresentação final.

#### Dependências

- Fases 5, 6 e 7 com material suficiente para síntese.

#### Principais saídas

- roteiro de defesa;
- estrutura de slides;
- gráficos finais selecionados;
- mensagens-chave e limitações do projeto.

## Dependências entre fases

```text
Fase 1
  -> Fase 2
  -> Fase 3
  -> Fase 4
  -> Fase 5
  -> Fase 6
  -> Fase 7
  -> Fase 8

Fase 2 -> Fase 3 -> Fase 4 -> Fase 5
Fase 4 -> Fase 6
Fase 4 + rótulos -> Fase 7
Fase 5 + Fase 6 + Fase 7 -> Fase 8
```

## Marcos principais

### Marco 1: pipeline real de ingestão

Quando o projeto sair totalmente da simulação e passar a ler vídeos reais.

### Marco 2: primeira base analítica consistente

Quando houver uma base processada com variáveis rastreáveis e utilizáveis em análise.

### Marco 3: primeiras evidências quantitativas

Quando EDA e modelagem já produzirem resultados com interpretação inicial.

### Marco 4: kit de defesa acadêmica

Quando o projeto tiver gráficos finais, narrativa consolidada e visão clara de limitações e contribuições.

## Prioridade de curto prazo

As prioridades imediatas recomendadas são:

1. preparar amostras reais em `data/raw/`;
2. implementar leitura real de vídeo;
3. conectar MediaPipe à pipeline;
4. gerar a primeira base processada não sintética;
5. transformar os notebooks planejados em notebooks executáveis.

## Critério de avanço entre fases

Uma fase deve avançar quando suas saídas mínimas estiverem documentadas, reproduzíveis e conectadas aos diretórios corretos do projeto.

## Relação com outros documentos

- `docs/PLANO_DE_EXECUCAO.md`: detalha as etapas operacionais.
- `docs/ENTREGAVEIS.md`: define o que cada fase precisa entregar.
- `docs/ARQUITETURA.md`: explica a lógica estrutural do projeto.
- `docs/DICIONARIO_DE_DADOS.md`: documenta as variáveis produzidas ao longo das fases.

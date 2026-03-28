---
name: planejamento-tarefas
description: "Workflow de planejamento e decomposição de tarefas do projeto MediaPipe Segurança. Use when: decompor tarefa complexa, planejar fase, definir steps ordenados, analisar dependências, criar plano de execução, quebrar em subtarefas, priorizar itens, estimar escopo, mapear pré-requisitos."
argument-hint: "descreva a tarefa ou fase que precisa ser decomposta em steps"
---

# Planejamento de Tarefas — Skill

Workflow padronizado para decomposição de tarefas complexas em steps atômicos, ordenados e com critérios de aceitação claros.

## Quando Usar

- Decompor uma fase do roadmap em tarefas executáveis
- Planejar implementação de módulo ou feature complexa
- Analisar dependências entre tarefas
- Priorizar backlog de tarefas
- Criar plano de execução para um entregável

## Fontes de Verdade

| Documento | Propósito |
|---|---|
| `docs/ROADMAP.md` | Fases, status e dependências do projeto |
| `docs/ENTREGAVEIS.md` | Entregáveis e critérios de aceite |
| `docs/PLANO_DE_EXECUCAO.md` | Etapas práticas e evidências esperadas |
| `docs/ARQUITETURA.md` | Camadas da pipeline e organização |
| `docs/DICIONARIO_DE_DADOS.md` | Variáveis e tipos disponíveis |

## Procedimento: Decompor Fase do Roadmap

1. **Ler o roadmap**: identificar a fase, status e dependências.
2. **Verificar pré-requisitos**: fases anteriores estão concluídas?
3. **Ler entregáveis**: quais artefatos são esperados para esta fase?
4. **Explorar repositório**: quais artefatos já existem parcialmente?
5. **Decompor em steps** atômicos seguindo o formato abaixo.
6. **Classificar cada step**:
   - Agente executor (Implementador, Analista, Documentador, Validador)
   - Dependências (steps anteriores, fases do roadmap)
   - Risco (baixo, médio, alto)
7. **Identificar tarefas do operador**: separar o que precisa de ação humana.
8. **Produzir plano** no formato YAML estruturado.

## Formato de Saída

```yaml
plano:
  tarefa: "descrição da tarefa original"
  fase_roadmap: "número e nome da fase"
  complexidade: "simples | moderada | complexa"
  pre_requisitos:
    - "fase ou artefato necessário"
  total_steps: N
  tarefas_operador:
    - "ações que só o humano pode fazer"
  steps:
    - id: 1
      titulo: "descrição curta do step"
      agente: "Implementador | Analista | Documentador | Validador | Operador"
      escopo:
        arquivos: ["lista de arquivos afetados"]
        modulos: ["módulos envolvidos"]
      dependencias: ["nenhuma" | "step X"]
      criterio_aceite: "condição verificável de conclusão"
      risco: "baixo | medio | alto"
    - id: 2
      # ...
```

## Procedimento: Planejar Implementação de Módulo

1. **Identificar o módulo**: consultar o Mapa de Módulos na arquitetura.
2. **Mapear interfaces**: entrada esperada (qual módulo alimenta) e saída (quem consome).
3. **Definir funções públicas** necessárias (assinatura, não implementação).
4. **Decompor em steps**:
   - Step 1: Criar esqueleto do módulo com assinaturas
   - Step 2: Implementar função principal com dados demo
   - Step 3: Escrever testes unitários
   - Step 4: Integrar no pipeline.py
   - Step 5: Validar execução end-to-end
   - Step 6: Documentar variáveis novas no dicionário
5. **Identificar riscos**: dependências externas, dados reais necessários, etc.

## Procedimento: Priorizar Backlog

1. **Listar todas as tarefas pendentes**.
2. **Para cada tarefa, avaliar**:
   - Impacto no avanço do projeto (alto/médio/baixo)
   - Esforço estimado (P/M/G)
   - Dependências bloqueantes
   - Fase do roadmap
3. **Priorizar**:
   - Primeiro: tarefas bloqueantes (sem elas, nada avança)
   - Segundo: tarefas de alto impacto e baixo esforço
   - Terceiro: tarefas da fase corrente do roadmap
   - Último: melhorias e refinamentos

## Regras de Planejamento

1. **Respeite o roadmap** — nunca planeje steps que dependam de fases não concluídas sem sinalizar como bloqueio
2. **Steps atômicos** — cada step deve ser independentemente executável e verificável
3. **Escopo explícito** — nenhum step deve ter escopo ambíguo
4. **Separe agente de operador** — deixe claro o que é automatizável e o que é manual
5. **Critérios verificáveis** — cada step deve ter critério de aceitação testável
6. **Máximo 10 steps** — se ultrapassar, agrupe em sub-planos

## Checklist de Qualidade

- [ ] Cada step tem agente executor definido
- [ ] Dependências entre steps estão explícitas
- [ ] Critérios de aceitação são verificáveis
- [ ] Tarefas do operador estão separadas
- [ ] Pré-requisitos de fases anteriores estão verificados
- [ ] Riscos identificados para steps críticos
- [ ] Plano é linearmente executável (sem ciclos)

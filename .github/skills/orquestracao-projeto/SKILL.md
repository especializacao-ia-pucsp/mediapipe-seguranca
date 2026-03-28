---
name: orquestracao-projeto
description: "Workflow de orquestração e coordenação do projeto MediaPipe Segurança. Use when: planejar próximo passo, verificar progresso, o que falta fazer, status do projeto, qual a próxima tarefa, avançar o projeto, coordenar fases, diagnosticar estado, rotear tarefa para agente correto, delegar implementação."
argument-hint: "descreva a tarefa, fase ou operação que precisa ser coordenada"
---

# Orquestração do Projeto — Skill

Workflow padronizado para diagnosticar estado do projeto, rotear tarefas para agentes corretos e coordenar fases do roadmap.

## Quando Usar

- Verificar progresso geral do projeto
- Identificar a próxima tarefa a executar
- Rotear uma solicitação para o agente correto
- Diagnosticar bloqueios entre fases
- Coordenar pipeline de agentes para tarefas complexas

## Fontes de Verdade

| Documento | Propósito |
|---|---|
| `docs/ROADMAP.md` | Fases, status, dependências — **sempre ler primeiro** |
| `docs/ENTREGAVEIS.md` | O que precisa ser produzido |
| `docs/PLANO_DE_EXECUCAO.md` | Etapas práticas |
| `docs/ARQUITETURA.md` | Organização da pipeline |

## Procedimento: Diagnosticar Estado

1. **Ler `docs/ROADMAP.md`**: identificar fase ativa e status.
2. **Cruzar com repositório**: verificar quais artefatos realmente existem.
3. **Produzir diagnóstico**:
   ```yaml
   diagnostico:
     fase_atual: "número e nome da fase ativa"
     status_fase: "concluída | em andamento | planejada"
     artefatos_existentes: ["lista de arquivos/módulos já criados"]
     artefatos_pendentes: ["lista do que falta"]
     bloqueios: ["dependências não atendidas"]
   ```
4. **Identificar próxima ação**: o que precisa acontecer para avançar?

## Procedimento: Rotear Solicitação

1. **Classificar a solicitação**:
   ```yaml
   classificacao:
     tipo: "implementar | analisar | revisar | documentar | explorar | corrigir | testar | planejar"
     complexidade: "simples | moderada | complexa"
     dominio: "ingestao | percepcao | features | eda | modelagem | defesa | docs | devops"
     cross_cutting: true | false
   ```
2. **Selecionar rota**:
   | Complexidade | Cross-cutting | Rota |
   |---|---|---|
   | simples | não | Direto para agente executor |
   | simples | sim | Planejador define escopo → agente executor |
   | moderada+ | qualquer | Planejador decompõe → agentes executam por step |
3. **Selecionar agente**:
   | Intent | Agente Primário | Apoio |
   |---|---|---|
   | Implementar código | Implementador | Validador, Revisor |
   | Análise/EDA/modelo | Analista | Revisor |
   | Revisar artefato | Revisor | — |
   | Rodar testes | Validador | — |
   | Atualizar docs | Documentador | — |
   | CI/CD, GitHub | GitHubOps | — |
   | Config VS Code | VSCodeConfig | — |
   | Planejar fase | Planejador | — |
   | Capability gap | MetaAgente | — |

## Procedimento: Coordenar Pipeline de Agentes

Para tarefas complexas que envolvem múltiplos agentes:

1. **Planejador decompõe** a tarefa em steps.
2. **Para cada step**:
   - Delegar ao agente executor (Implementador, Analista, etc.)
   - Após conclusão, delegar validação ao Validador
   - Se necessário, delegar revisão ao Revisor
3. **Ao final**: Documentador atualiza docs afetados.
4. **Verificar**: todos os critérios de aceitação foram atendidos?

## Fluxo de Fases do Roadmap

```
Fase 1 (Fundação) → Fase 2 (Ingestão) → Fase 3 (MediaPipe) → Fase 4 (Features)
                                                                      ↓
Fase 8 (Defesa) ← Fase 7 (Supervisionada) ← Fase 6 (Não-sup) ← Fase 5 (EDA)
```

## Checklist de Qualidade

- [ ] Diagnóstico baseado no estado real do repositório
- [ ] Classificação da solicitação é precisa
- [ ] Agente correto selecionado para o tipo de tarefa
- [ ] Tarefas complexas decompostas antes de executar
- [ ] Validação inclusa no pipeline quando há implementação
- [ ] Documentação atualizada ao final de tarefas que geram artefatos

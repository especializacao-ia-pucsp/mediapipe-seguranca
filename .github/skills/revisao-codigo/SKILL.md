---
name: revisao-codigo
description: "Workflow de revisão de código e qualidade do projeto MediaPipe Segurança. Use when: revisar código, code review, verificar qualidade, auditar arquitetura, revisar análise, checar padrões, avaliar interpretação, review multi-pass, pull request review, revisar notebook, avaliar modelagem."
argument-hint: "descreva o que precisa ser revisado e quais preocupações específicas"
---

# Revisão de Código — Skill

Workflow padronizado de revisão multi-pass para código, análises e artefatos do projeto MediaPipe Segurança.

## Quando Usar

- Revisar código implementado em `src/` ou `tests/`
- Fazer code review de PRs
- Auditar aderência à arquitetura
- Revisar notebooks e análises
- Avaliar interpretação de resultados de modelagem
- Verificar coerência entre código, dados e documentação

## Referências para Revisão

| Referência | Propósito |
|---|---|
| `docs/ARQUITETURA.md` | Verificar aderência à arquitetura de camadas |
| `docs/DICIONARIO_DE_DADOS.md` | Verificar coerência de variáveis |
| `docs/ENTREGAVEIS.md` | Verificar critérios de aceite |
| `src/mediapipe_seguranca/config.py` | Verificar uso de configuração centralizada |

## Protocolo de Revisão Multi-Pass

### Pass 1: Correção

Verificar se o código funciona corretamente.

| Check | O que verificar |
|---|---|
| Bugs lógicos | Condições invertidas, off-by-one, divisão por zero |
| Edge cases | Dados vazios, None, tipos inesperados |
| Imports | Módulos não encontrados, imports circulares |
| Tipos | Type hints presentes e consistentes |
| Runtime | Código executa sem exceções |

### Pass 2: Arquitetura

Verificar aderência à arquitetura do projeto.

| Check | O que verificar |
|---|---|
| Módulo correto | Código está no módulo certo conforme camada? |
| Fluxo de dados | Segue o fluxo Ingestão → Percepção → Features → Modelagem? |
| Separação | Pipeline (`src/`) separada de exploração (`notebooks/`)? |
| Dados | Dados no diretório correto (`raw/`, `interim/`, `processed/`, `labels/`)? |
| Config | Caminhos centralizados via `config.py`? |

### Pass 3: Qualidade

Verificar qualidade de engenharia.

| Check | O que verificar |
|---|---|
| Nomes | Descritivos, consistentes, snake_case |
| Responsabilidade | Cada função faz uma coisa |
| Code smells | Funções longas (>50 linhas), acoplamento excessivo |
| Type hints | Presentes em funções públicas |
| Testes | Existem testes para funcionalidades críticas |
| DRY | Sem duplicação significativa |

### Pass 4: Coerência Acadêmica (para análises)

Aplicar apenas quando revisando notebooks ou resultados de modelagem.

| Check | O que verificar |
|---|---|
| Interpretação | Resultados têm interpretação, não apenas código/gráfico |
| Limitações | Limitações dos métodos são reconhecidas |
| Defensável | Resultados são defensáveis em banca |
| Figuras | Gráficos salvos em `reports/figures/` |
| Métricas | Métricas registradas e comparáveis |
| Reprodutibilidade | Seeds fixos, caminhos relativos, dados disponíveis |

## Formato de Saída

```yaml
review_report:
  alvo: "arquivo(s) ou módulo(s) revisado(s)"
  status: "aprovado | aprovado com ressalvas | reprovado"
  passes:
    correcao:
      status: "pass | fail"
      issues:
        - "descrição do problema"
    arquitetura:
      status: "pass | fail"
      issues:
        - "descrição do problema"
    qualidade:
      status: "pass | fail"
      issues:
        - "descrição do problema"
    coerencia_academica:
      status: "pass | fail | n/a"
      issues:
        - "descrição do problema"
  acao_requerida:
    - descricao: "correção necessária"
      agente: "Implementador | Analista | Documentador"
  observacoes: "comentários gerais"
```

## Severidade de Issues

| Severidade | Critério | Ação |
|---|---|---|
| **Bloqueante** | Bug, crash, dados corrompidos, segurança | Reprovado — corrigir antes de avançar |
| **Alta** | Violação de arquitetura, falta de testes para funcionalidade crítica | Aprovado com ressalvas — corrigir em seguida |
| **Média** | Code smell, nomes ruins, falta type hint | Aprovado com ressalvas — corrigir quando conveniente |
| **Baixa** | Estilo, sugestão de melhoria | Aprovado — registrar para melhoria futura |

## Checklist de Qualidade da Revisão

- [ ] Todos os 4 passes foram executados (ou Pass 4 marcado como n/a)
- [ ] Issues categorizadas por severidade
- [ ] Ações requeridas têm agente recomendado
- [ ] Relatório é acionável (dá para agir com base nele)
- [ ] Referências foram consultadas (arquitetura, dicionário)

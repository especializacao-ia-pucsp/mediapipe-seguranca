---
name: gestao-skills
description: "Workflow de gestão de skills estruturadas do projeto MediaPipe Segurança. Use when: criar nova skill, auditar skills existentes, melhorar skill, avaliar cobertura de skills, skill gap, refatorar skill, otimizar description de skill, verificar skill discovery, listar skills, inventário de skills."
argument-hint: "descreva a skill a ser criada, auditada ou melhorada"
---

# Gestão de Skills — Skill

Workflow padronizado para criar, auditar, melhorar e manter as skills estruturadas consumidas pelos agentes do projeto MediaPipe Segurança.

## Quando Usar

- Criar uma nova skill para um agente ou domínio
- Auditar todas as skills existentes
- Melhorar uma skill com problemas de discovery ou eficácia
- Identificar gaps de skills (domínios sem skill)
- Verificar coerência entre skills e agentes

## Inventário de Skills

| Skill | Agente Primário | Domínio |
|---|---|---|
| `analise-dados` | Analista | EDA, modelagem, visualizações |
| `documentacao-projeto` | Documentador | Docs, roadmap, dicionário |
| `github-devops` | GitHubOps | CI/CD, GitHub Actions, templates |
| `implementacao-codigo` | Implementador | Código, módulos, testes |
| `planejamento-tarefas` | Planejador | Decomposição, dependências |
| `revisao-codigo` | Revisor | Code review, qualidade |
| `validacao-testes` | Validador | Testes, integridade, smoke test |
| `orquestracao-projeto` | Orquestrador | Coordenação, roteamento |
| `vscode-workspace` | VSCodeConfig | Editor, extensões, settings |
| `gestao-skills` | MetaAgente | Meta-operações sobre skills |

## Localização

Todas as skills ficam em `.github/skills/<nome>/SKILL.md`.

## Procedimento: Criar Nova Skill

1. **Identificar o gap**: qual domínio ou workflow não tem skill?
2. **Definir escopo**:
   - Para qual agente é a skill primária?
   - Quais triggers devem ativá-la? (keywords na description)
   - Qual é o workflow passo-a-passo?
3. **Criar a estrutura**:
   ```
   .github/skills/<nome-da-skill>/
   └── SKILL.md
   ```
4. **Escrever o SKILL.md** seguindo o template:
   ```yaml
   ---
   name: nome-da-skill          # Deve corresponder ao nome da pasta
   description: "Descrição keyword-rich com trigger phrases. Use when: ..."
   argument-hint: "dica de uso"
   ---
   ```
5. **Corpo obrigatório**:
   - `## Quando Usar` — lista de cenários de uso
   - `## Procedimento: <Nome>` — workflow passo-a-passo (pelo menos um)
   - `## Checklist de Qualidade` — verificações de completude
6. **Validar**:
   - Nome da pasta = campo `name` no frontmatter
   - Description tem keywords suficientes para discovery
   - Procedimentos são acionáveis (não vagos)
   - Checklist é verificável
7. **Atualizar o inventário** neste SKILL.md.
8. **Registrar no agente**: se o agente referencia skills no seu `.agent.md`.

## Procedimento: Auditar Skills

1. **Listar** todas as skills em `.github/skills/`.
2. **Para cada skill, avaliar**:

```yaml
auditoria_skill:
  skill: "nome"
  criterios:
    description_discovery:
      score: "1-5"
      problema: "keywords ausentes, vago, não ativa quando deveria"
    procedimentos_completude:
      score: "1-5"
      problema: "steps faltando, ordem incorreta"
    checklist_verificabilidade:
      score: "1-5"
      problema: "itens vagos, não testáveis"
    coerencia_com_agente:
      score: "1-5"
      problema: "skill desalinhada com responsibilities do agente"
    atualidade:
      score: "1-5"
      problema: "referências a artefatos que não existem mais"
  recomendacao: "nenhuma | ajuste menor | refatoração"
  detalhes: "descrição específica"
```

3. **Identificar padrões transversais**:
   - Skills com description ruim (discovery falha)
   - Skills desatualizadas (referenciam coisas que mudaram)
   - Gaps: domínios sem skill
   - Sobreposição: duas skills cobrindo o mesmo workflow

4. **Produzir relatório** com ações priorizadas.

## Procedimento: Melhorar Skill

1. **Ler a skill atual**: identificar o problema específico.
2. **Categorizar o problema**:
   - **Discovery**: description não ativa a skill quando deveria → adicionar keywords
   - **Procedimento incompleto**: faltam steps → adicionar steps
   - **Desatualização**: referências obsoletas → atualizar
   - **Vagueza**: procedimento genérico demais → ser mais específico ao projeto
3. **Aplicar a correção** mínima necessária.
4. **Validar**: o nome da pasta ainda corresponde ao `name`? Description < 1024 chars?

## Template de Skill

```markdown
---
name: nome-da-skill
description: "O que faz e quando usar. Use when: keyword1, keyword2, keyword3."
argument-hint: "dica de uso para invocação via slash command"
---

# Título da Skill

Descrição em uma linha do propósito.

## Quando Usar

- Cenário 1
- Cenário 2

## Referências

| Referência | Propósito |
|---|---|
| `docs/...` | ... |

## Procedimento: Nome do Workflow

1. **Step 1**: ação concreta.
2. **Step 2**: ação concreta.
3. **Resultado**: o que deve existir ao final.

## Checklist de Qualidade

- [ ] Item verificável 1
- [ ] Item verificável 2
```

## Regras de Ouro

1. **Nome da pasta = campo `name`** — mismatch causa falha silenciosa
2. **Description é o mecanismo de discovery** — keywords ricas e específicas
3. **Procedimentos acionáveis** — steps concretos, não genéricos
4. **SKILL.md < 500 linhas** — se maior, usar `references/` para detalhes
5. **Caminhos relativos** — usar `./` para assets dentro da skill
6. **Uma skill, um domínio** — não misturar domínios diferentes

## Checklist de Qualidade

- [ ] Todas as skills têm nome consistente (pasta = frontmatter)
- [ ] Descriptions têm keywords para discovery
- [ ] Cada skill tem pelo menos um procedimento com steps
- [ ] Checklists são verificáveis
- [ ] Inventário neste arquivo está atualizado
- [ ] Nenhuma skill referencia artefatos inexistentes
- [ ] Sem sobreposição significativa entre skills

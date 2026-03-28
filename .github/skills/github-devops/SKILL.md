---
name: github-devops
description: "Workflow de DevOps e automação GitHub do projeto MediaPipe Segurança. Use when: criar workflow CI/CD, configurar GitHub Actions, branch protection, PR template, issue template, release, code scanning, dependabot, automação GitHub, pipeline de deploy, validação automática, linting automático, testes automáticos no push, criar label, configurar labeler."
argument-hint: "descreva o fluxo DevOps, automação ou configuração GitHub que precisa ser criada ou ajustada"
---

# GitHub DevOps — Skill

Workflow padronizado para configurar e manter automação DevOps no GitHub para o projeto MediaPipe Segurança.

## Quando Usar

- Criar ou atualizar workflows de CI/CD (GitHub Actions)
- Configurar branch protection rules
- Criar templates de PR e issues
- Configurar Dependabot, CodeQL ou code scanning
- Automatizar labeling, releases ou notificações
- Configurar GitHub Pages para documentação

## Contexto do Repositório

- **Repositório**: `especializacao-ia-pucsp/mediapipe-seguranca`
- **Branch principal**: `main`
- **Stack**: Python 3.x, MediaPipe, OpenCV, pandas, scikit-learn
- **Requisitos**: `requirements.txt` na raiz
- **Testes**: `tests/` com pytest
- **Linting**: ruff, flake8
- **Formatação**: black, isort
- **Estrutura CI**: `.github/workflows/`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE/`

## Procedimento: Criar Workflow CI/CD

1. **Analisar contexto**:
   - Ler `requirements.txt` para dependências
   - Verificar `tests/` para a suíte de testes
   - Listar `.github/workflows/` para workflows existentes
2. **Definir triggers**: push para `main`, pull_request, schedule (se necessário).
3. **Projetar steps**:
   ```yaml
   # Ordem padrão dos steps
   - Checkout código
   - Setup Python (usar versão do projeto)
   - Cache pip dependencies
   - Instalar dependências
   - Lint (ruff check)
   - Format check (black --check, isort --check)
   - Testes (pytest com cobertura)
   - Upload de artefatos (se necessário)
   ```
4. **Criar arquivo** em `.github/workflows/<nome>.yml`.
5. **Validar sintaxe** YAML antes de salvar.

### Template de Workflow CI

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
          cache: pip
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov ruff black isort
      - name: Lint
        run: ruff check src/ tests/ --line-length=120
      - name: Format check
        run: |
          black --check src/ tests/ main.py --line-length=120
          isort --check src/ tests/ main.py --profile black --line-length=120
      - name: Tests
        run: pytest tests/ -v --tb=short --cov=src/mediapipe_seguranca --cov-report=term-missing
```

## Procedimento: Criar Issue Template

1. **Identificar tipo**: bug report, feature request, task/fase.
2. **Criar arquivo** em `.github/ISSUE_TEMPLATE/<tipo>.yml` (formato YAML form).
3. **Incluir campos obrigatórios**:
   - Título (name)
   - Descrição (description)
   - Labels automáticos
   - Body com campos estruturados

### Campos mínimos por tipo

| Tipo | Campos |
|---|---|
| Bug report | Descrição, steps to reproduce, comportamento esperado, ambiente |
| Feature request | Descrição, motivação, fase do roadmap |
| Task | Descrição, fase, critério de aceitação, agente responsável |

## Procedimento: Criar PR Template

1. **Criar** `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`.
2. **Incluir seções**:
   - Descrição da mudança
   - Tipo de mudança (bug fix, feature, docs, refactor)
   - Fase do roadmap relacionada
   - Checklist (testes passam, lint ok, docs atualizadas)
   - Screenshots/evidência (se visual)

## Procedimento: Configurar Branch Protection

1. **Verificar configuração atual** via GitHub API ou UI.
2. **Definir regras para `main`**:
   - Require PR reviews before merging
   - Require status checks to pass (CI workflow)
   - Require branch to be up to date
   - Block force pushes
3. **Documentar** as regras aplicadas.

## Procedimento: Configurar Dependabot

1. **Verificar** se `.github/dependabot.yml` existe.
2. **Configurar** atualizações para:
   - `pip` (package-ecosystem)
   - `github-actions` (manter actions atualizados)
3. **Definir frequência**: weekly ou monthly.
4. **Definir labels** automáticos para PRs do Dependabot.

## Procedimento: Configurar Labeler

1. **Verificar** `.github/labeler.yml`.
2. **Mapear labels por path**:
   - `src/` → `code`
   - `tests/` → `tests`
   - `docs/` → `documentation`
   - `notebooks/` → `analysis`
   - `.github/` → `devops`
   - `data/` → `data`

## Checklist de Qualidade

- [ ] Workflows YAML são válidos sintaticamente
- [ ] Actions usam versões fixas (v4, v5) e não `latest`
- [ ] Secrets não estão hardcoded nos workflows
- [ ] Cache de pip está configurado para performance
- [ ] Branch protection está ativo para `main`
- [ ] Templates de PR/issue incluem campos relevantes ao projeto
- [ ] Dependabot configurado para pip e github-actions

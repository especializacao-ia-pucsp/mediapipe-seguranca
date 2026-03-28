---
name: vscode-workspace
description: "Workflow de configuração do VS Code para o projeto MediaPipe Segurança. Use when: instalar extensão, configurar VS Code, otimizar editor, settings do workspace, configurar debugger, criar task, launch.json, keybinding, snippet, workspace recommendations, configurar linter, configurar formatter, configurar terminal, editorconfig."
argument-hint: "descreva a configuração, extensão ou otimização do VS Code que precisa ser feita"
---

# VS Code Workspace — Skill

Workflow padronizado para configurar e otimizar o VS Code Insiders para o projeto MediaPipe Segurança.

## Quando Usar

- Configurar extensões recomendadas
- Otimizar settings do workspace
- Criar ou atualizar tasks automatizadas
- Configurar debugger (launch.json)
- Configurar linting e formatação automática
- Setup do ambiente Python

## Arquivos de Configuração

| Arquivo | Propósito |
|---|---|
| `.vscode/settings.json` | Settings do workspace |
| `.vscode/tasks.json` | Tasks automatizadas |
| `.vscode/launch.json` | Configurações de debug |
| `.vscode/extensions.json` | Extensões recomendadas |
| `.editorconfig` | Consistência de formato |

## Procedimento: Configurar Extensões

1. **Verificar** `.vscode/extensions.json` existente.
2. **Extensões essenciais do projeto**:
   ```json
   {
     "recommendations": [
       "ms-python.python",
       "ms-python.vscode-pylance",
       "ms-python.debugpy",
       "ms-toolsai.jupyter",
       "ms-python.black-formatter",
       "ms-python.isort",
       "charliermarsh.ruff",
       "github.copilot",
       "github.copilot-chat",
       "gitkraken.gitlens",
       "github.vscode-pull-request-github",
       "sonarsource.sonarlint-vscode"
     ]
   }
   ```
3. **Instalar** extensões faltantes.

## Procedimento: Configurar Settings

1. **Ler** `.vscode/settings.json` atual.
2. **Settings essenciais**:
   ```json
   {
     "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "ms-python.black-formatter",
     "[python]": {
       "editor.defaultFormatter": "ms-python.black-formatter",
       "editor.codeActionsOnSave": {
         "source.organizeImports": "explicit"
       }
     },
     "black-formatter.args": ["--line-length=120"],
     "isort.args": ["--profile", "black", "--line-length=120"],
     "ruff.args": ["--line-length=120"],
     "files.exclude": {
       "**/__pycache__": true,
       "**/.pytest_cache": true,
       ".venv": true
     }
   }
   ```
3. **Mesclar** com settings existentes (preservar customizações do usuário).

## Procedimento: Criar/Atualizar Tasks

1. **Verificar** `.vscode/tasks.json` atual.
2. **Tasks padrão do projeto**:
   | Task | Comando | Grupo |
   |---|---|---|
   | Pipeline: Run | `python main.py` | build (default) |
   | Tests: Run All | `pytest tests/ -v --tb=short` | test (default) |
   | Tests: Run with Coverage | `pytest tests/ --cov=src/mediapipe_seguranca` | test |
   | Lint: Ruff Check | `ruff check src/ tests/` | build |
   | Lint: Ruff Fix | `ruff check src/ tests/ --fix` | build |
   | Format: Black | `black src/ tests/ main.py` | build |
   | Format: isort | `isort src/ tests/ main.py` | build |
   | Deps: Install | `pip install -r requirements.txt` | build |
   | Clean: Caches | Remove `__pycache__` e `.pytest_cache` | build |
3. **Preservar** tasks customizadas existentes.

## Procedimento: Configurar Debugger

1. **Verificar** `.vscode/launch.json` atual.
2. **Configurações recomendadas**:
   ```json
   {
     "configurations": [
       {
         "name": "Pipeline: Debug",
         "type": "debugpy",
         "request": "launch",
         "program": "${workspaceFolder}/main.py",
         "cwd": "${workspaceFolder}",
         "console": "integratedTerminal"
       },
       {
         "name": "Tests: Debug Current File",
         "type": "debugpy",
         "request": "launch",
         "module": "pytest",
         "args": ["${file}", "-v", "--tb=short"],
         "cwd": "${workspaceFolder}",
         "console": "integratedTerminal"
       }
     ]
   }
   ```

## Procedimento: Setup de Ambiente Python

1. **Verificar venv**: `.venv/` existe?
2. **Verificar interpreter**: apontando para `.venv/Scripts/python.exe`?
3. **Verificar dependências**: `pip list` inclui requirements.txt?
4. **Verificar Pylance**: configurado para o projeto?
5. **Verificar formatação on save**: black + isort ativos?

## Checklist de Qualidade

- [ ] Python interpreter aponta para `.venv`
- [ ] Extensões recomendadas configuradas em `.vscode/extensions.json`
- [ ] Format on save ativo (black + isort)
- [ ] Linting ativo (ruff)
- [ ] Tasks de pipeline, teste e lint definidas
- [ ] Debugger configurado para pipeline e testes
- [ ] Files.exclude configurado para esconder caches
- [ ] Terminal integrado usando o Python do venv

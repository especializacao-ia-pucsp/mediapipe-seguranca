---
name: implementacao-codigo
description: "Workflow de implementação de código do projeto MediaPipe Segurança. Use when: escrever código, criar módulo, implementar feature, corrigir bug, refatorar, modificar pipeline, atualizar src/, criar script, implementar ingestão, integrar MediaPipe, implementar feature engineering, adicionar dependência, escrever testes unitários."
argument-hint: "descreva o que precisa ser implementado, o módulo alvo e o critério de aceitação"
---

# Implementação de Código — Skill

Workflow padronizado para escrever, modificar e corrigir código no projeto MediaPipe Segurança.

## Quando Usar

- Implementar módulos da pipeline em `src/mediapipe_seguranca/`
- Corrigir bugs em código existente
- Escrever testes em `tests/`
- Refatorar para manter coesão
- Integrar dependências externas (MediaPipe, OpenCV)
- Atualizar `requirements.txt`

## Mapa de Módulos

| Módulo | Responsabilidade | Camada | Fase |
|---|---|---|---|
| `video_io.py` | Leitura e metadados de vídeo | Ingestão | Fase 2 |
| `mediapipe_extract.py` | Extração de sinais com MediaPipe | Percepção | Fase 3 |
| `tracking_features.py` | Features de rastreamento por frame | Percepção | Fase 4 |
| `feature_engineering.py` | Agregação e engenharia de atributos | Features | Fase 4 |
| `train_unsupervised.py` | Modelagem não supervisionada | Modelagem | Fase 6 |
| `train_supervised.py` | Modelagem supervisionada | Modelagem | Fase 7 |
| `evaluate.py` | Avaliação de modelos | Modelagem | Fases 6-7 |
| `pipeline.py` | Orquestração da pipeline completa | Todas | Todas |
| `config.py` | Configuração de caminhos e parâmetros | Todas | Todas |

## Diretórios de Trabalho

| Diretório | Conteúdo | Permissão |
|---|---|---|
| `src/mediapipe_seguranca/` | Código-fonte da pipeline | Leitura e escrita |
| `tests/` | Testes unitários e de integração | Leitura e escrita |
| `main.py` | Entry point da pipeline | Leitura e escrita |
| `requirements.txt` | Dependências Python | Leitura e escrita |
| `data/` | Dados processados | Apenas leitura (gerados via pipeline) |

## Procedimento: Implementar Módulo Novo

1. **Ler a arquitetura**: consultar `docs/ARQUITETURA.md` para entender a camada e posição no fluxo.
2. **Ler módulos relacionados**: entender interfaces upstream e downstream.
3. **Verificar `config.py`**: usar caminhos e parâmetros centralizados.
4. **Implementar seguindo os padrões do projeto**:
   ```python
   # Padrões obrigatórios
   # - Type hints em todas as funções públicas
   # - Imports organizados: stdlib → third-party → local
   # - Funções com responsabilidade única
   # - Nomes em inglês para código
   # - Dados demo/sintéticos para validação inicial
   ```
5. **Escrever testes**: criar `tests/test_<modulo>.py` com cobertura das funções públicas.
6. **Executar testes**: `pytest tests/ -v --tb=short`.
7. **Verificar integração**: confirmar que `python main.py` ainda executa sem erros.

## Procedimento: Corrigir Bug

1. **Reproduzir**: entender o bug e como reproduzir.
2. **Localizar**: identificar o módulo e a função afetada.
3. **Escrever teste**: criar teste que demonstra o bug (deve falhar antes do fix).
4. **Corrigir**: aplicar a correção mínima.
5. **Validar**: teste novo passa, testes existentes continuam passando.
6. **Verificar pipeline**: `python main.py` executa sem erros.

## Procedimento: Adicionar Dependência

1. **Verificar necessidade**: a dependência é realmente necessária?
2. **Verificar compatibilidade**: funciona com o Python e outras deps do projeto?
3. **Adicionar ao `requirements.txt`**: com versão fixada (ex: `mediapipe>=0.10.0`).
4. **Instalar**: `pip install -r requirements.txt`.
5. **Importar**: usar no módulo correto conforme a camada da arquitetura.

## Padrões de Código

### Estrutura de Módulo

```python
"""Breve descrição do módulo."""

from pathlib import Path

import numpy as np
import pandas as pd

from mediapipe_seguranca.config import PROCESSED_DIR


def funcao_publica(param: tipo) -> tipo_retorno:
    """Docstring apenas para funções públicas."""
    ...
```

### Estrutura de Teste

```python
"""Testes para <modulo>."""

import pytest

from mediapipe_seguranca.<modulo> import funcao_publica


class TestFuncaoPublica:
    def test_caso_basico(self):
        resultado = funcao_publica(input_valido)
        assert resultado == esperado

    def test_edge_case(self):
        ...
```

## Checklist de Qualidade

- [ ] Type hints em funções públicas
- [ ] Imports organizados (stdlib → third-party → local)
- [ ] Funções com responsabilidade única
- [ ] Testes escritos para funcionalidades novas
- [ ] `pytest tests/ -v` passa sem erros
- [ ] `python main.py` executa sem erros
- [ ] `requirements.txt` atualizado se nova dependência
- [ ] Sem código morto ou comentado
- [ ] Sem secrets ou paths hardcoded

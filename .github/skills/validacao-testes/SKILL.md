---
name: validacao-testes
description: "Workflow de validação e testes do projeto MediaPipe Segurança. Use when: rodar testes, validar pipeline, verificar integridade de dados, checar reprodutibilidade, validar output, testar módulo, conferir dados gerados, smoke test, validar critério de aceitação, cobertura de código, verificar schema."
argument-hint: "descreva o que precisa ser validado (módulo, pipeline, dados, critério de aceitação)"
---

# Validação e Testes — Skill

Workflow padronizado para execução de testes, validação de pipeline, verificação de integridade de dados e confirmação de critérios de aceitação.

## Quando Usar

- Executar suíte de testes unitários
- Validar pipeline end-to-end
- Verificar integridade de dados gerados
- Confirmar critérios de aceitação de um step/fase
- Fazer smoke test após implementação
- Verificar reprodutibilidade de resultados
- Analisar cobertura de código

## Comandos de Teste

| Comando | Propósito |
|---|---|
| `pytest tests/ -v --tb=short` | Testes unitários com detalhes |
| `pytest tests/ -v --cov=src/mediapipe_seguranca --cov-report=term-missing` | Testes com cobertura |
| `python main.py` | Pipeline end-to-end |
| `python -m mediapipe_seguranca` | Via __main__.py |
| `ruff check src/ tests/ --line-length=120` | Lint check |
| `black --check src/ tests/ main.py --line-length=120` | Format check |

## Procedimento: Validar Código

1. **Executar lint**: `ruff check src/ tests/ --line-length=120`.
2. **Verificar formatação**: `black --check src/ tests/ main.py --line-length=120`.
3. **Executar testes**: `pytest tests/ -v --tb=short`.
4. **Verificar imports**: confirmar que módulos importam sem erros.
5. **Pipeline demo**: `python main.py` executa sem exceções.
6. **Registrar resultados** no formato de relatório.

## Procedimento: Validar Dados

1. **Verificar existência**: arquivos esperados existem nos diretórios corretos.
2. **Verificar schema**: colunas conforme `docs/DICIONARIO_DE_DADOS.md`.
   ```python
   import pandas as pd
   df = pd.read_csv("data/processed/demo_window_features.csv")

   # Colunas esperadas (verificar contra dicionário)
   expected_columns = [
       "window_id", "people_count_mean", "people_count_max",
       "movement_score_mean", "posture_change_rate_mean",
       "estimated_speed_mean", "dense_scene_rate",
       "suspicious_loitering_rate", "fall_risk_score_mean",
       "occupancy_score_mean", "risk_score_mean",
       "motion_intensity_mean", "label", "event_count"
   ]
   missing = set(expected_columns) - set(df.columns)
   extra = set(df.columns) - set(expected_columns)
   ```
3. **Verificar tipos**: inteiros, numéricos, categóricos conforme esperado.
4. **Verificar nulos**: colunas obrigatórias não devem ter nulos.
5. **Verificar ranges**: valores dentro de faixas razoáveis.
6. **Verificar registros**: número de linhas dentro do esperado.

## Procedimento: Validar Critério de Aceitação

1. **Ler o critério**: entender exatamente o que deve ser verdadeiro.
2. **Definir checks**: traduzir o critério em verificações executáveis.
3. **Executar cada check**: registrar PASS ou FAIL com evidência.
4. **Produzir relatório** com resultado global.

## Procedimento: Smoke Test pós-Implementação

1. **Testes passam**: `pytest tests/ -v --tb=short` → zero failures.
2. **Pipeline executa**: `python main.py` → sem exceções.
3. **Output existe**: verificar que `data/processed/` tem arquivos atualizados.
4. **Imports ok**: `python -c "from mediapipe_seguranca import pipeline"` → sem erros.

## Formato de Saída

```yaml
validation_report:
  alvo: "pipeline | módulo | dados | critério de aceitação"
  status: "aprovado | reprovado"
  checks:
    - nome: "descrição do check"
      status: "pass | fail"
      evidencia: "output do comando ou observação"
  falhas:
    - descricao: "o que falhou"
      severidade: "bloqueante | aviso"
      acao_sugerida: "como corrigir"
      agente_recomendado: "Implementador | Analista | Documentador"
  resumo: "aprovado para avançar | bloqueado por N falhas"
```

## Checklist de Qualidade

- [ ] Testes pytest passam sem failures
- [ ] Pipeline demo executa sem exceções
- [ ] Lint e format checks passam
- [ ] Dados gerados têm schema correto
- [ ] Colunas obrigatórias sem valores nulos
- [ ] Critérios de aceitação verificados individualmente
- [ ] Relatório com evidência para cada check

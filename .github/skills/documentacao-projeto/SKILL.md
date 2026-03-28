---
name: documentacao-projeto
description: "Workflow de documentação do projeto MediaPipe Segurança. Use when: atualizar docs, atualizar roadmap, atualizar dicionário de dados, registrar entregável, atualizar ENTREGAVEIS, atualizar PLANO_DE_EXECUCAO, documentar variáveis, manter coerência documental, atualizar status de fase, atualizar README, registrar nova feature no dicionário."
argument-hint: "descreva o que precisa ser documentado ou atualizado e o contexto da mudança"
---

# Documentação do Projeto — Skill

Workflow padronizado para manter a documentação do projeto MediaPipe Segurança coerente, atualizada e alinhada com o estado real do repositório.

## Quando Usar

- Atualizar status de fases no roadmap
- Registrar novas variáveis no dicionário de dados
- Marcar entregáveis como concluídos
- Atualizar READMEs após mudanças estruturais
- Manter coerência entre documentação e repositório

## Mapa de Documentos

| Documento | O que rastreia | Quando atualizar |
|---|---|---|
| `docs/ROADMAP.md` | Status de fases e dependências | Quando uma fase muda de status |
| `docs/ENTREGAVEIS.md` | Entregáveis e critérios de aceite | Quando um entregável é concluído |
| `docs/PLANO_DE_EXECUCAO.md` | Etapas práticas e evidências | Quando uma etapa é concluída |
| `docs/ARQUITETURA.md` | Camadas e módulos da pipeline | Quando módulos são criados/reestruturados |
| `docs/DICIONARIO_DE_DADOS.md` | Variáveis, tipos, escalas | Quando novas features são criadas |
| `docs/CRONOGRAMA.md` | Cronograma acadêmico | Quando há mudanças de prazo |
| `README.md` | Visão geral do projeto | Quando há mudanças de escopo |
| `data/README.md` | Contrato de dados | Quando formato de dados muda |
| `notebooks/README.md` | Plano de notebooks | Quando notebooks são criados |
| `reports/README.md` | Organização de relatórios | Quando novos relatórios são gerados |
| `src/README.md` | Módulos da pipeline | Quando módulos são alterados |
| `tests/README.md` | Estratégia de testes | Quando cobertura muda significativamente |

## Procedimento: Atualizar Status de Fase

1. **Identificar a fase**: qual fase mudou de status no roadmap.
2. **Ler `docs/ROADMAP.md`**: verificar o status atual registrado.
3. **Validar no repositório**: confirmar que os artefatos da fase existem.
4. **Atualizar status**: mudar para o status correto:
   - `planejada` → fase ainda não iniciada
   - `em andamento` → fase com trabalho ativo
   - `concluída` → todos os artefatos e critérios satisfeitos
5. **Atualizar Gantt**: ajustar o diagrama mermaid se necessário.
6. **Cruzar com ENTREGAVEIS.md**: verificar se entregáveis da fase estão marcados.

## Procedimento: Registrar Variável no Dicionário

1. **Ler `docs/DICIONARIO_DE_DADOS.md`**: entender a estrutura existente.
2. **Identificar a tabela correta**:
   - Variáveis por frame → tabela "Variáveis por frame"
   - Variáveis derivadas → tabela "Variáveis derivadas por frame"
   - Variáveis por janela → tabela "Variáveis agregadas por janela"
   - Variáveis de modelagem → tabela "Variáveis auxiliares da modelagem"
3. **Adicionar a nova variável** com todos os campos obrigatórios:
   - Nome do campo (snake_case)
   - Tipo esperado (inteiro, numérico contínuo, binário, categórico)
   - Origem (ingestão, percepção, feature engineering, modelagem)
   - Descrição clara e concisa
4. **Verificar coerência**: nome da variável deve corresponder ao código em `src/`.

## Procedimento: Marcar Entregável Concluído

1. **Ler `docs/ENTREGAVEIS.md`**: localizar o entregável na matriz.
2. **Validar no repositório**: confirmar que o artefato existe no local previsto.
3. **Verificar critério de aceite**: garantir que o critério foi atendido.
4. **Marcar como concluído**: adicionar indicador de status (✅ ou equivalente).
5. **Atualizar `docs/PLANO_DE_EXECUCAO.md`**: marcar a etapa correspondente.

## Procedimento: Atualizar README de Diretório

1. **Identificar a mudança**: quais arquivos foram adicionados/removidos/renomeados.
2. **Ler o README atual**: entender o que está documentado.
3. **Listar o diretório real**: comparar com o que está registrado.
4. **Atualizar**: adicionar/remover referências conforme o estado real.
5. **Preservar estrutura**: manter o formato de tabela ou lista existente.

## Regras de Ouro

1. **Não crie documentos novos** — prefira atualizar os existentes
2. **Preserve a estrutura** — não mude headings, tabelas ou formato sem necessidade
3. **Atualize incrementalmente** — mude apenas o que corresponde à mudança real
4. **Mantenha navegação** — verifique que links entre docs ainda funcionam
5. **Use português** — toda documentação é em português
6. **Seja factual** — documente o que existe, não o que se espera que exista
7. **Rastreabilidade** — cada atualização deve ter justificativa clara

## Checklist de Qualidade

- [ ] Links entre documentos funcionam
- [ ] Status de fases reflete o estado real do repositório
- [ ] Variáveis no dicionário correspondem ao código em `src/`
- [ ] Entregáveis marcados como concluídos existem nos locais previstos
- [ ] READMEs refletem a estrutura real dos diretórios
- [ ] Nenhum documento referencia artefatos que não existem
- [ ] Formato de tabelas e headings preservado

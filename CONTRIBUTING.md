# Como contribuir

Este documento define convenções para evoluir o projeto de forma organizada, reprodutível e coerente com os entregáveis acadêmicos.

## Objetivo

Padronizar como novas contribuições entram no repositório, seja em código, documentação, dados, notebooks ou relatórios.

## Princípios do projeto

- manter foco em **indicadores comportamentais de cena**, e não em identificação individual;
- priorizar organização, rastreabilidade e interpretabilidade;
- separar claramente dados brutos, dados intermediários, dados processados e evidências analíticas;
- manter a documentação sincronizada com a estrutura do repositório.

## Onde cada contribuição deve entrar

- `src/mediapipe_seguranca/`: lógica reutilizável da pipeline.
- `tests/`: testes automatizados da base de código.
- `data/`: contrato de armazenamento de insumos, saídas intermediárias, bases finais e rótulos.
- `notebooks/`: exploração analítica e experimentação visual.
- `reports/`: sínteses, resultados, figuras e material de defesa.
- `docs/`: planejamento, arquitetura e documentos estruturantes.

## Regras para código

- funções e módulos devem ter responsabilidade clara;
- lógica central deve ficar em `src/`, não em notebooks;
- scripts e módulos devem ser reprodutíveis a partir da estrutura do projeto;
- mudanças estruturais devem ser acompanhadas de atualização de documentação.

## Regras para dados

- dados brutos não devem ser alterados manualmente após ingestão;
- saídas intermediárias e processadas devem ser reproduzíveis;
- artefatos gerados localmente devem respeitar o `.gitignore`;
- convenções de rótulos devem ser documentadas em `data/labels/`.

## Regras para notebooks

- notebooks devem seguir a ordem numérica já definida em `notebooks/`;
- cada notebook deve nascer do escopo descrito em seu arquivo `.md` correspondente;
- resultados relevantes devem ser exportados para `reports/` quando apropriado;
- o notebook não deve se tornar o único local onde a lógica existe.

## Regras para relatórios e defesa

- gráficos finais devem ir para `reports/figures/`;
- interpretações de EDA devem ir para `reports/eda/`;
- comparações de modelos devem ir para `reports/models/`;
- roteiro e narrativa final devem ir para `reports/defesa/`.

## Fluxo sugerido de contribuição

1. identificar a frente de trabalho;
2. localizar a pasta correta do artefato;
3. implementar a mudança com escopo pequeno e claro;
4. validar a saída gerada;
5. atualizar a documentação relacionada;
6. versionar apenas o que faz sentido para o repositório.

## Checklist antes de commitar

- a mudança respeita a estrutura do projeto;
- o artefato está na pasta correta;
- arquivos gerados localmente não foram incluídos por engano;
- a documentação relevante foi atualizada;
- o resultado é compreensível para uso em contexto acadêmico.

## Mensagens de commit sugeridas

- `docs: ...` para documentação, estrutura e convenções;
- `feat: ...` para novas capacidades da pipeline;
- `fix: ...` para correções de comportamento;
- `test: ...` para testes e validações automatizadas;
- `refactor: ...` para reorganização interna sem mudança funcional.

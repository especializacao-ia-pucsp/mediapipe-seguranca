# Dados processados

Este diretório deve armazenar as bases finais ou consolidadas, prontas para EDA, modelagem e avaliação.

## O que deve ficar aqui

- features por frame;
- agregações por janela temporal;
- datasets analíticos finais;
- versões consolidadas usadas em notebooks e relatórios.

## Diretriz de uso

- todo arquivo salvo aqui deve ter origem rastreável na pipeline;
- nomes de arquivos devem refletir granularidade, versão e recorte temporal;
- alterações na estrutura de colunas devem ser documentadas em `data/README.md` ou em `docs/` quando necessário.

## Exemplos esperados

- `features_por_frame_v1.parquet`
- `features_por_janela_v1.csv`
- `dataset_modelagem_v1.parquet`

## Observação sobre a demo

O arquivo `demo_window_features.csv`, quando gerado pela pipeline inicial, é apenas um **artefato local de demonstração**. Ele serve para validar o fluxo, mas **não deve ser versionado**.

## Versionamento

Somente a documentação da pasta deve ser versionada por padrão. Bases geradas devem permanecer ignoradas pelo `.gitignore`, salvo decisão explícita do projeto.

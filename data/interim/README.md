# Dados intermediários

Este diretório deve armazenar saídas temporárias ou parcialmente transformadas da pipeline.

## O que deve ficar aqui

- extrações parciais por frame;
- amostras de landmarks ou detecções;
- tabelas temporárias antes da consolidação final;
- arquivos de apoio para depuração de etapas intermediárias.

## Diretriz de uso

- todo arquivo salvo aqui deve ser reproduzível a partir de `data/raw/` e do código em `src/`;
- nomes de arquivos devem indicar a etapa da pipeline que os gerou;
- este diretório não deve concentrar artefatos finais de análise.

## Exemplos esperados

- `frames_indexados.parquet`
- `deteccoes_pose_amostra.csv`
- `tracking_temporario.parquet`

## Versionamento

Arquivos intermediários **não devem ser versionados** por padrão. O Git deve preservar apenas este guia e o placeholder da pasta.

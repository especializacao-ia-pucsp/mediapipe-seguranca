# `01_ingestao.ipynb`

## Objetivo

Validar a leitura dos vídeos, a organização dos frames e a estrutura temporal mínima para a pipeline.

## Entradas esperadas

- arquivos em `data/raw/`;
- metadados de vídeo, quando disponíveis;
- parâmetros iniciais de amostragem e janelamento.

## Saídas esperadas

- inspeção básica dos vídeos;
- tabela com metadados de frames ou segmentos;
- validação do esquema de janelas temporais;
- observações sobre qualidade e consistência dos insumos.

## Perguntas orientadoras

- quais vídeos estão disponíveis e em que formato?
- qual é a granularidade temporal ideal para a análise?
- há problemas de qualidade, duração ou padronização?

## Critério de pronto

O notebook está pronto quando demonstrar leitura reproduzível dos dados brutos e registrar a estratégia de segmentação temporal.

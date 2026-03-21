# Rótulos e anotações

Este diretório deve armazenar os rótulos e anotações usados para aprendizado supervisionado e validação analítica.

## O que deve ficar aqui

- taxonomias de eventos;
- arquivos de anotação por vídeo, frame ou janela;
- mapeamentos entre IDs de vídeo e classes;
- dicionários de classes e convenções de rotulagem.

## Diretriz de uso

- a convenção de rótulos deve ser consistente ao longo do projeto;
- mudanças de nomenclatura devem ser registradas para evitar quebra de comparação histórica;
- é importante indicar granularidade do rótulo: vídeo, frame, segmento ou janela.

## Exemplos esperados

- `rotulos_eventos.csv`
- `taxonomia_eventos.md`
- `anotacoes_por_janela.parquet`

## Classes inicialmente previstas

- `normal`
- `aglomeracao`
- `corrida`
- `queda`
- `permanencia_suspeita`

## Versionamento

Se os arquivos de rótulo forem leves e centrais para o experimento, eles podem ser versionados. Ainda assim, a pasta deve manter documentação clara sobre origem, critério de anotação e revisão.

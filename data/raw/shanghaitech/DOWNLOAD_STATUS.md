# Status de Download do ShanghaiTech

Este arquivo é apenas um marcador leve versionado no repositório.

Ele **não** deve ser tratado como snapshot confiável do estado local do dataset no ambiente de quem clonou o projeto.

## O que este arquivo representa

- referência documental sobre a estratégia de obtenção do dataset;
- lembrete de que o repositório mantém apenas artefatos leves;
- ponto de apoio para a validação descrita em `DOWNLOAD_INSTRUCTIONS.md`.

## Política resumida

- **Conteúdo versionado**: documentação leve e `SAMPLE/`
- **Dataset real**: download e extração locais
- **Diretórios locais esperados**: `training/` e `testing/`
- **Validação**: `scripts/validate_shanghaitech.py`

## Uso recomendado

Consulte `DOWNLOAD_INSTRUCTIONS.md` para preparar o dataset real no seu ambiente local ou use `SAMPLE/` enquanto essa preparação não for necessária.

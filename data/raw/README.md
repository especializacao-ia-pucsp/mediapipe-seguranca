# Dados brutos

Este diretório deve armazenar os **insumos originais** do projeto, sem transformação analítica.

## Navegação

- [Início](../../README.md)
- [Dados](../README.md)
- [Dados intermediários](../interim/README.md)
- [Dados processados](../processed/README.md)
- [Rótulos](../labels/README.md)
- [Arquitetura](../../docs/ARQUITETURA.md)
- [Dicionário de dados](../../docs/DICIONARIO_DE_DADOS.md)
- [Notebook de ingestão](../../notebooks/01_ingestao.md)

## O que deve ficar aqui

- vídeos originais de CFTV ou gravações simuladas;
- amostras de vídeo usadas para testes de ingestão;
- arquivos auxiliares que representem a origem do dado.

## Diretriz de uso

- os arquivos devem manter o formato original sempre que possível;
- renomeações devem preservar a identificação da origem;
- dados sensíveis só devem ser incluídos se houver autorização e finalidade acadêmica compatível.

## Exemplos esperados

- `camera_01_2026-03-21.mp4`
- `simulacao_corredor_bloco_a.mp4`
- `sessao_teste_entrada_principal.mp4`

## Versionamento

Arquivos reais de vídeo normalmente **não devem ser versionados** no repositório. O Git deve preservar apenas este guia e o placeholder da pasta.

---

## Dataset ShanghaiTech Campus (Fase 2)

O projeto usa o **ShanghaiTech Campus Dataset**, um benchmark de detecção de anomalias em vídeo de segurança pública.

- **Localização**: `data/raw/shanghaitech/`
- **Versionado no Git**: documentação leve e `SAMPLE/`
- **Dataset real**: download e extração locais, fora do versionamento do repositório
- **Como usar**: [Veja o guia completo](shanghaitech/DATASET_GUIDE.md)
- **Para informações técnicas**: [Repositório ShanghaiTech](https://svip-lab.github.io/dataset_campus.html)

### Estrutura

```
shanghaitech/
├── training/                # ignorado no git; extraído localmente
├── testing/                 # ignorado no git; extraído localmente
├── SAMPLE/                  # Mini-dataset sintético versionado para dev
├── README.md                # Descrição do dataset
├── DATASET_GUIDE.md         # Como usar a estrutura local
├── DOWNLOAD_INSTRUCTIONS.md # Como fazer download
├── DOWNLOAD_STATUS.md       # Marcador leve de referência
```

### Verificação rápida

Para validar a integridade do dataset real local, quando presente:

```bash
.venv\Scripts\python.exe scripts/validate_shanghaitech.py
```

Enquanto o dataset real não estiver disponível, o projeto pode ser explorado com `SAMPLE/`.

# Instruções de Download do ShanghaiTech Campus

Este documento descreve como preparar localmente o dataset real em `data/raw/shanghaitech/`.

O repositório **não** distribui o dataset real extraído. Ele versiona apenas documentação leve e `SAMPLE/`.

## Fonte oficial

- Página do dataset: <https://svip-lab.github.io/dataset/campus_dataset.html>
- Link oficial para download: <https://1drv.ms/u/s!AjjUqiJZsj8whLt-1ABerTT-9eH9Ag?e=eJbY6Y>

## Observação sobre o download automático

O script `scripts/download_shanghaitech.py` existe como apoio, mas o download automático pode falhar por depender de fontes externas, permissões e disponibilidade de hospedagem.

Quando isso acontecer, siga o procedimento manual abaixo.

## Passos manuais

1. Acesse a página oficial do ShanghaiTech Campus.
2. Baixe os arquivos do conjunto de treino e do conjunto de teste.
3. Extraia o conteúdo diretamente em `data/raw/shanghaitech/`.
4. Confirme que a estrutura local contém `training/`, `testing/` e, no caso do teste, `test_frame_mask/`.
5. Execute a validação local com `scripts/validate_shanghaitech.py`.

## Extração em `data/raw/shanghaitech/`

Exemplo com `tar`:

```bash
tar -xzf training.tar.gz -C data/raw/shanghaitech/
tar -xzf testing.tar.gz -C data/raw/shanghaitech/
```

Estrutura esperada após a extração local do dataset real:

```text
data/raw/shanghaitech/
├── training/
│   └── frames/
│       └── ...
├── testing/
│   ├── frames/
│   │   └── ...
│   └── test_frame_mask/
│       └── ...
├── SAMPLE/
└── documentação leve
```

## Validação

Após extrair o dataset real localmente, valide a estrutura com:

```bash
.venv\Scripts\python.exe scripts/validate_shanghaitech.py
```

Esse passo verifica a organização esperada e atualiza o marcador de referência em `data/raw/shanghaitech/DOWNLOAD_STATUS.md`.

## Uso de `SAMPLE/`

Enquanto o dataset real não estiver presente localmente, você pode usar `SAMPLE/` para desenvolvimento, exploração inicial e testes leves da pipeline.

Se necessário, o sample pode ser recriado com:

```bash
.venv\Scripts\python.exe scripts/create_sample_shanghaitech.py
```

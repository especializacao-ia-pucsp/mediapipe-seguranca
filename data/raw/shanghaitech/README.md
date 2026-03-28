# ShanghaiTech Campus Dataset

## Descrição

O **ShanghaiTech Campus Dataset** é um benchmark amplamente utilizado para
**Video Anomaly Detection (VAD)** em cenários de segurança pública. Consiste em
vídeos capturados em um campus universitário com câmeras fixas, cobrindo 13 cenas.

Neste repositório, a estrutura do dataset real é suportada para uso local após download e extração manuais. O versionamento inclui apenas documentação leve e `SAMPLE/`.

| Conjunto | Vídeos | Frames (aprox.) | Conteúdo |
| --- | --- | --- | --- |
| Treino | 330 | ~1.000.000 | Apenas comportamento normal |
| Teste | 109 | ~200.000 | Normal + anomalias anotadas |

Anomalias incluem: correr, brigar, veículos em área proibida, etc.

## Como Obter

### Download automático

```bash
.venv\Scripts\python.exe scripts/download_shanghaitech.py
```

O script tenta múltiplas fontes (Google Drive via gdown, Kaggle API) e cria
`DOWNLOAD_STATUS.md` com o resultado.

O download automático pode falhar por depender de fontes externas. O procedimento manual documentado em `DOWNLOAD_INSTRUCTIONS.md` é a referência principal.

### Download manual

1. Acesse a página oficial: <https://svip-lab.github.io/dataset/campus_dataset.html>
2. Baixe `training.tar.gz` e `testing.tar.gz`
3. Extraia em `data/raw/shanghaitech/`:

    ```bash
    tar xzf training.tar.gz -C data/raw/shanghaitech/
    tar xzf testing.tar.gz  -C data/raw/shanghaitech/
    ```

### Dataset sintético para desenvolvimento

Sem o dataset real, use o `SAMPLE/` versionado no repositório ou gere novamente um mini-dataset sintético compatível:

```bash
.venv\Scripts\python.exe scripts/create_sample_shanghaitech.py
```

O diretório `data/raw/shanghaitech/SAMPLE/` contém frames JPEG e GT masks `.npy` para desenvolvimento e testes leves.

## Estrutura de Diretórios

```text
data/raw/shanghaitech/
    training/               ← extraído localmente; ignorado no git
    testing/                ← extraído localmente; ignorado no git
    SAMPLE/                ← mini-dataset sintético versionado no repositório
        training/frames/
        testing/frames/
        testing/test_frame_mask/
```

## Como Usar com a Pipeline

```python
from src.mediapipe_seguranca.shanghaitech_loader import (
    get_train_videos,
    get_test_videos_with_gt,
    load_gt_mask,
    iter_frames,
)

# Listar vídeos de treino
train_videos = get_train_videos()
print(f"Treino: {len(train_videos)} vídeos")

# Iterar frames de treino
for video_dir in train_videos:
    for frame_idx, frame_path in iter_frames(video_dir):
        # processar frame_path com OpenCV / MediaPipe
        pass

# Listar vídeos de teste com GT
test_pairs = get_test_videos_with_gt()
for frames_dir, gt_path in test_pairs:
    gt_mask = load_gt_mask(gt_path)  # np.ndarray shape (n_frames,)
    for frame_idx, frame_path in iter_frames(frames_dir):
        label = gt_mask[frame_idx]  # 0 = normal, 1 = anomalia
```

O loader detecta automaticamente o dataset real ou o SAMPLE sintético.

---

## Política de Versionamento

| Aspecto | Status | Detalhes |
| --- | --- | --- |
| Documentação leve | ✅ Versionada | `README.md`, `DOWNLOAD_INSTRUCTIONS.md`, `DATASET_GUIDE.md`, `DOWNLOAD_STATUS.md` |
| SAMPLE | ✅ Versionado | Mini-dataset para desenvolvimento e testes leves |
| Dataset real extraído | 🚫 Não versionado | `training/` e `testing/` reais ficam apenas no ambiente local |
| Arquivos compactados | 🚫 Não versionados | `.zip`, `.tar`, `.tar.gz`, `.avi`, temporários |

**Histórico de atualização:**

- 2026-03-23: Fase 2 iniciada, mini-dataset SAMPLE criado
- 2026-03-28: política de versionamento ajustada para manter apenas artefatos leves

## Referência Bibliográfica

```bibtex
@inproceedings{liu2018future,
  title={Future Frame Prediction for Anomaly Detection -- A New Baseline},
  author={Liu, Wen and Luo, Weixin and Lian, Dongze and Gao, Shenghua},
  booktitle={Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  year={2018}
}
```

Dataset original (campus):
> W. Luo, W. Liu, S. Gao. *A revisit of sparse coding based anomaly detection in stacked RNN framework*. ICCV 2017.
> Homepage: <https://svip-lab.github.io/dataset/campus_dataset.html>

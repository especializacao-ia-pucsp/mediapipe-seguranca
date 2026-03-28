# ShanghaiTech Campus Dataset

## Descrição

O **ShanghaiTech Campus Dataset** é um benchmark amplamente utilizado para
**Video Anomaly Detection (VAD)** em cenários de segurança pública. Consiste em
vídeos capturados em um campus universitário com câmeras fixas, cobrindo 13 cenas.

| Conjunto | Vídeos | Frames (aprox.) | Conteúdo |
|---|---|---|---|
| Treino | 307 | ~1.000.000 | Apenas comportamento normal |
| Teste | 130 | ~200.000 | Normal + anomalias anotadas |

Anomalias incluem: correr, brigar, veículos em área proibida, etc.

## Como Obter

### Download automático

```bash
.venv\Scripts\python.exe scripts/download_shanghaitech.py
```

O script tenta múltiplas fontes (Google Drive via gdown, Kaggle API) e cria
`DOWNLOAD_STATUS.md` com o resultado.

### Download manual

1. Acesse: https://svip-lab.github.io/dataset/campus_dataset.html
2. Baixe `training.tar.gz` e `testing.tar.gz`
3. Extraia em `data/raw/shanghaitech/`:
   ```bash
   tar xzf training.tar.gz -C data/raw/shanghaitech/
   tar xzf testing.tar.gz  -C data/raw/shanghaitech/
   ```

### Dataset sintético para desenvolvimento

Sem o dataset real, gere um mini-dataset sintético compatível:
```bash
.venv\Scripts\python.exe scripts/create_sample_shanghaitech.py
```
Cria `data/raw/shanghaitech/SAMPLE/` com frames JPEG e GT masks `.npy`.

## Estrutura de Diretórios

```
data/raw/shanghaitech/
    training/
        frames/
            01_001/        ← frames de um vídeo de treino
                000.jpg
                001.jpg
                ...
            01_002/
            ...             (≈ 330 sub-pastas no dataset real)
    testing/
        frames/
            01_0014/       ← frames de um vídeo de teste
                ...
            ...             (≈ 107 sub-pastas no dataset real)
        test_frame_mask/
            01_0014.npy    ← GT binário frame-a-frame (0=normal, 1=anomalia)
            ...             (137 arquivos .npy no dataset real)
    SAMPLE/                ← mini-dataset sintético (gerado localmente)
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
> Homepage: https://svip-lab.github.io/dataset/campus_dataset.html

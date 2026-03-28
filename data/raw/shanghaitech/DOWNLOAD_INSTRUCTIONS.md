# ShanghaiTech Campus Dataset — Download Instructions

O download automático não conseguiu acessar os links — o dataset requer download manual via browser.
Use uma das opções abaixo. Para desenvolvimento imediato, use a Opção 4 (SAMPLE sintético).

## Opção 0 — OneDrive Oficial (RECOMENDADO) ★

Link direto obtido da página SVIP Lab (acessado via script em 2026-03-28):

**URL de download**: https://1drv.ms/u/s!AjjUqiJZsj8whLt-1ABerTT-9eH9Ag?e=eJbY6Y

### Passos

1. Abrir o link acima no browser
2. Fazer download dos arquivos:
   - `training.tar.gz` (training frames — apenas cenas normais)
   - `testing.tar.gz` (test frames + anotações frame-level)
3. Extrair em `data/raw/shanghaitech/`:
   ```
   # Windows PowerShell / WSL
   tar xzf training.tar.gz -C data/raw/shanghaitech/
   tar xzf testing.tar.gz  -C data/raw/shanghaitech/
   ```
4. Executar para validar:
   ```
   .venv\Scripts\python.exe scripts/validate_shanghaitech.py
   ```

> **Nota**: O link OneDrive pode requerer conta Microsoft para download. Caso necessite,
> use a Opção 1 (SVIP Lab) ou Opção 3 (Academic Torrents).

## Option 1 — Official Source

- Homepage: https://svip-lab.github.io/dataset/campus_dataset.html
- Paper: *A revisit of sparse coding based anomaly detection in stacked RNN framework* (Luo et al., ICCV 2017)

### Steps

1. Visit https://svip-lab.github.io/dataset/campus_dataset.html
2. Request or download:
   - `training.tar.gz` (~17 GB — training frames, normal only)
   - `testing.tar.gz` (~3 GB — test frames + frame-level GT masks)
3. Extract both archives into `data/raw/shanghaitech/`:
   ```bash
   tar xzf training.tar.gz -C data/raw/shanghaitech/
   tar xzf testing.tar.gz  -C data/raw/shanghaitech/
   ```

## Option 2 — Kaggle

Search Kaggle for "shanghaitech campus anomaly" or similar.
If you have `~/.kaggle/kaggle.json` configured, the download script will
attempt this automatically.

```bash
.venv\Scripts\python.exe scripts/download_shanghaitech.py
```

## Option 3 — Academic Torrents

Search https://academictorrents.com for "ShanghaiTech Campus".

## Option 4 — Synthetic Mini Dataset (Immediate Development)

No download required. Generate a compatible synthetic dataset:

```bash
.venv\Scripts\python.exe scripts/create_sample_shanghaitech.py
```

Creates `data/raw/shanghaitech/SAMPLE/` with:
- 5 training videos × 50 frames (normal synthetic scenes)
- 2 testing videos × 30 frames (with 20% anomaly frames)
- 2 GT `.npy` masks

The loader (`shanghaitech_loader.py`) auto-detects SAMPLE/ as a fallback.

## Expected Directory Structure After Real Download

```
data/raw/shanghaitech/
    training/
        frames/
            01_001/ ← ~2000 .jpg frames per video
            01_002/
            ... (≈ 330 sub-folders)
    testing/
        frames/
            01_0014/
            ... (≈ 107 sub-folders)
        test_frame_mask/
            01_0014.npy  ← binary GT array (0=normal, 1=anomaly)
            ...          (137 .npy files)
```

## Verifying the Dataset

```python
from src.mediapipe_seguranca.shanghaitech_loader import get_train_videos, get_test_videos_with_gt
train = get_train_videos()
test  = get_test_videos_with_gt()
print(f"Train: {len(train)} videos, Test: {len(test)} videos with GT")
```

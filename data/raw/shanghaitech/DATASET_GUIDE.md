# Como Usar o Dataset ShanghaiTech Campus

> Nota: este guia descreve a estrutura esperada do dataset real após download e extração locais em `data/raw/shanghaitech/`. O repositório versiona apenas documentação leve e `SAMPLE/`.

Os exemplos abaixo assumem que você já baixou e extraiu o dataset real localmente ou que está trabalhando com `SAMPLE/`, quando aplicável.

## Localização

Quando o dataset real está presente localmente, os arquivos ficam organizados de forma hierárquica em `data/raw/shanghaitech/`:

```text
data/raw/shanghaitech/
├── training/frames/              # Vídeos de treino (330)
│   ├── 01_001/                   # Video ID
│   │   ├── 000.jpg
│   │   ├── 001.jpg
│   │   ├── 002.jpg
│   │   └── ...
│   ├── 01_002/
│   ├── ...
│   └── 01_330/
├── testing/frames/               # Vídeos de teste (109)
│   ├── 01_0001/
│   ├── 01_0002/
│   └── ...
└── testing/test_frame_mask/      # Ground truth masks (109)
    ├── 01_0001.npy              # Máscara binária do vídeo
    ├── 01_0002.npy
    └── ...
```

### Intervalo de vídeos esperados

- **Training**: 330 diretórios de vídeo em `training/frames/`
- **Testing**: 109 diretórios de vídeo em `testing/frames/`
- **GT Masks**: 109 arquivos correspondentes aos vídeos de teste

## Carregar dados via Python

### Método 1: Usar o `ShanghaiTechLoader` (recomendado)

```python
from src.mediapipe_seguranca.shanghaitech_loader import ShanghaiTechLoader

# Inicializar o loader
loader = ShanghaiTechLoader(base_path="data/raw/shanghaitech")

# Listar todos os vídeos de treino do dataset real local
train_videos = loader.get_train_videos()
print(f"Total de vídeos de treino: {len(train_videos)}")  # Esperado: 330

# Listar vídeos de teste com ground truth
test_pairs = loader.get_test_videos_with_gt()
print(f"Total de vídeos de teste: {len(test_pairs)}")  # Esperado: 109

# Iterar frames de um vídeo de treino com processamento
for video_dir in train_videos[:5]:  # Primeiros 5 vídeos
    for frame_idx, frame_path in loader.iter_frames(video_dir):
        # frame_idx: índice sequencial (0, 1, 2, ...)
        # frame_path: caminho completo para o JPEG
        print(f"  Frame {frame_idx}: {frame_path}")

        # Processar com OpenCV/MediaPipe
        import cv2
        frame = cv2.imread(frame_path)
        # ... processar frame ...

# Carregar dados de teste com rótulos
for test_video_dir, gt_mask_path in test_pairs[:5]:  # Primeiros 5
    # Carregar máscara de ground truth
    gt_mask = loader.load_gt_mask(gt_mask_path)  # np.ndarray shape (n_frames,)
    print(f"GT mask shape: {gt_mask.shape}, type: {gt_mask.dtype}")

    # Iterar frames com seus rótulos ground truth
    for frame_idx, frame_path in loader.iter_frames(test_video_dir):
        label = gt_mask[frame_idx]  # 0 = normal, 1 = anomalia
        print(f"  Frame {frame_idx}: label={label}")
```

### Método 2: Carregar manualmente com OpenCV

Este fluxo assume que o dataset real já foi extraído localmente.

```python
import cv2
import numpy as np
from pathlib import Path

# Diretório base
shanghaitech_path = Path("data/raw/shanghaitech")

# Listar vídeos de treino
training_dirs = sorted((shanghaitech_path / "training" / "frames").glob("*/"))

for video_dir in training_dirs:
    # Listar frames em ordem numérica
    frame_files = sorted(video_dir.glob("*.jpg"), key=lambda x: int(x.stem))

    for frame_idx, frame_file in enumerate(frame_files):
        frame = cv2.imread(str(frame_file))
        print(f"{video_dir.name}/{frame_file.name}: shape={frame.shape}")

# Carregar ground truth
test_mask_dir = shanghaitech_path / "testing" / "test_frame_mask"
for mask_file in sorted(test_mask_dir.glob("*.npy")):
    gt_mask = np.load(mask_file)
    print(f"{mask_file.name}: shape={gt_mask.shape}, max={gt_mask.max()}")
```

## Formatos de dados

### Frames JPEG

- **Resolução**: 640 × 480 pixels
- **Formato**: RGB JPEG
- **Nomeação**: `000.jpg`, `001.jpg`, `002.jpg`, ... (índices sequenciais 0-based)
- **Quantidade por vídeo**: varia conforme a cena

### Ground Truth Masks (.npy)

- **Tipo**: NumPy array uint8
- **Forma**: `(n_frames,)` — vetor com um rótulo por frame
- **Valores**:
  - `0` = frame normal (sem anomalia)
  - `1` = frame com anomalia
- **Arquivo**: `01_XXXX.npy` correspondente a `testing/frames/01_XXXX/`

## Workflow típico: EDA e Feature Extraction

```python
import cv2
import numpy as np
from pathlib import Path
from src.mediapipe_seguranca.shanghaitech_loader import ShanghaiTechLoader

# Inicializar loader
loader = ShanghaiTechLoader()
test_videos = loader.get_test_videos_with_gt()

# Coleta estatísticas básicas
stats = {
    "n_videos": 0,
    "n_frames_total": 0,
    "n_anomalies": 0,
    "frame_shapes": set(),
}

for video_dir, gt_mask_path in test_videos[:10]:  # Amostra de 10 vídeos
    gt_mask = loader.load_gt_mask(gt_mask_path)
    stats["n_videos"] += 1
    stats["n_anomalies"] += gt_mask.sum()

    for frame_idx, frame_path in loader.iter_frames(video_dir):
        stats["n_frames_total"] += 1
        frame = cv2.imread(frame_path)
        stats["frame_shapes"].add(frame.shape)

print(f"Videos processados: {stats['n_videos']}")
print(f"Frames totais: {stats['n_frames_total']}")
print(f"Anomalias detectadas: {stats['n_anomalies']}")
print(f"Resoluções encontradas: {stats['frame_shapes']}")
```

## Diagnóstico: Validar dataset

Para verificar a integridade do dataset real local, execute:

```bash
# Terminal no root do projeto
.venv\Scripts\python.exe scripts/validate_shanghaitech.py
```

Este script:

- ✅ Verifica contagem de pastas (treino, teste)
- ✅ Valida frames JPEG (tipo, forma, legibilidade)
- ✅ Valida máscara GT (.npy, dtype, shape)
- ✅ Gera relatório em `data/raw/shanghaitech/DOWNLOAD_STATUS.md`

## Atualizar dataset manualmente

Se quiser refazer a preparação do dataset real no seu ambiente local:

### Opção 1: Tentar download automático

```bash
# Força nova tentativa (requer gdown ou Kaggle API e pode falhar)
.venv\Scripts\python.exe scripts/download_shanghaitech.py --force-real --skip-sample
```

### Opção 2: Download manual

1. Acesse o [link oficial](https://1drv.ms/u/s!AjjUqiJZsj8whLt-1ABerTT-9eH9Ag?e=eJbY6Y) do ShanghaiTech Campus
2. Baixe `training.tar.gz` e `testing.tar.gz`
3. Extraia em `data/raw/shanghaitech/`:
   ```bash
   # PowerShell/bash
   tar -xzf training.tar.gz -C data/raw/shanghaitech/
   tar -xzf testing.tar.gz -C data/raw/shanghaitech/
   ```
4. Valide a integridade:
   ```bash
   .venv\Scripts\python.exe scripts/validate_shanghaitech.py
   ```

## Dataset sintético para desenvolvimento local

Se você ainda não tiver o dataset real local, use o `SAMPLE/` versionado no repositório ou gere novamente um mini-dataset sintético compatível para desenvolvimento:

```bash
.venv\Scripts\python.exe scripts/create_sample_shanghaitech.py
```

Isto gera:

- `data/raw/shanghaitech/SAMPLE/training/frames/` — 5 vídeos × 50 frames
- `data/raw/shanghaitech/SAMPLE/testing/frames/` — 2 vídeos × 30 frames
- `data/raw/shanghaitech/SAMPLE/testing/test_frame_mask/` — 2 máscaras GT

O loader detecta automaticamente se você está usando `SAMPLE/` ou o dataset real local.

## Referência

- **Paper original**: [ShanghaiTech Campus](https://svip-lab.github.io/dataset_campus.html)
- **Link oficial**: [OneDrive SVIP Lab](https://1drv.ms/u/s!AjjUqiJZsj8whLt-1ABerTT-9eH9Ag?e=eJbY6Y)
- **Laboratório**: SVIP Lab, ShanghaiTech University
- **Licença**: Verificar no site oficial antes de usar em publicações
- **Contato**: Contribua com issues/PRs no repositório do projeto

## Próximos passos

Após confirmar que o dataset está funcionando no seu ambiente local:
1. **Fase 3**: Integrar com MediaPipe para extração de poses e sinais visuais
2. **Feature Engineering**: Gerar features por frame e por janela
3. **EDA**: Explorar padrões e distribuições de anomalias
4. **Modelagem**: Treinar modelos de detecção não supervisionados e supervisionados

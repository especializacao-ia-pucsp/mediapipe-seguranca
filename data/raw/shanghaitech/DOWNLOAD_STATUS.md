# ShanghaiTech Dataset — Status de Preparação

## Status: SAMPLE PRONTO — Dataset real requer download manual

**Data de criação**: 2026-03-28

---

### Dataset sintético (SAMPLE/) ✅
- **Finalidade**: desenvolvimento e testes end-to-end da pipeline
- **Training videos**: 5 pastas × 50 frames (`SAMPLE/training/frames/01_001` … `01_005`)
- **Testing videos**: 2 pastas × 30 frames (`SAMPLE/testing/frames/`)
- **GT masks**: 2 arquivos `.npy` (`SAMPLE/testing/test_frame_mask/`)
- **Frames gerados**: 310 JPEGs sintéticos
- **Status loader**: `shanghaitech_loader.py` auto-detecta SAMPLE/ como fallback

### Dataset real (ShanghaiTech Campus) ⚠️
- **Status**: Não baixado (download automático falhou — links restritos)
- **Tentativa SVIP Lab**: Google Drive link vazio (`href=" "`); OneDrive disponível em `https://1drv.ms/u/s!AjjUqiJZsj8whLt-1ABerTT-9eH9Ag?e=eJbY6Y` (requer browser)
- **Tentativa Hugging Face**: `huggingface_hub` não instalado; download automático não realizado
- **Download manual**: ver `DOWNLOAD_INSTRUCTIONS.md`
- **URL oficial**: https://svip-lab.github.io/dataset/campus_dataset.html
- **Tamanho estimado**: ~20 GB total (training + testing)
- **Estrutura esperada**: `training/frames/` (~330 vídeos), `testing/frames/` (~107 vídeos), `testing/test_frame_mask/` (~137 .npy)

---

### Próximos passos
1. Executar `python main.py` com SAMPLE/ para validar a pipeline end-to-end
2. Baixar o dataset real (ver `DOWNLOAD_INSTRUCTIONS.md`)
3. Avançar para Fase 3 — Integração com MediaPipe

# BSS WD14 Batch Tagger

Custom nodes for **ComfyUI** for automatic WD14 image tagging, batch workflows, tag postprocessing, caption export, and basic tag analytics.

## Features

- WD14 v3 model support (ViT / SwinV2 / EVA02 / ConvNeXT)
- Automatic model download from Hugging Face
- Single-image and batch tagging nodes
- Category-aware thresholds (`general`, `character`, `meta`, `rating`)
- Tag postprocessing (dedupe, sorting, include/exclude operations)
- Caption saving to `txt`, `json`, `csv`
- Tag frequency analytics (`top-k` + JSON stats)

## Installation

### Via ComfyUI Manager

1. Open ComfyUI Manager
2. Find **BSS WD14 Batch Tagger**
3. Install and restart ComfyUI

### Manual

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/BlackSnowSkill/wd14_batch_tagger.git
cd wd14_batch_tagger
pip install -r requirements.txt
```

## Included Nodes

- **BSS Load Images from Folder 📂** — loads folder images (`jpg`, `jpeg`, `png`, `webp`)
- **BSS WD14 Batch Tagger 🌿** — tags a single image and can save `.txt`
- **BSS WD14 Tagger Batch ⚡** — tags a list/batch and returns JSON scores
- **BSS Tags Postprocess 🧹** — cleanup/sort/dedupe/filter tag strings
- **BSS Save Captions 💾** — save captions in `txt/json/csv`
- **BSS Tag Analytics 📊** — compute top tag stats

## Usage (basic pipeline)

1. Load images with **BSS Load Images from Folder 📂**
2. Run tagging via:
   - **BSS WD14 Batch Tagger 🌿** (single), or
   - **BSS WD14 Tagger Batch ⚡** (batch)
3. (Optional) Clean results using **BSS Tags Postprocess 🧹**
4. (Optional) Save captions with **BSS Save Captions 💾**
5. (Optional) Inspect distribution using **BSS Tag Analytics 📊**

## Requirements

- Python 3.8+
- ComfyUI
- `onnxruntime>=1.18.0,<2.0.0`
- CUDA GPU (optional)

## Changelog

### v2.0.0

- Added batch node: **BSS WD14 Tagger Batch ⚡**
- Added postprocessing node: **BSS Tags Postprocess 🧹**
- Added caption writer node: **BSS Save Captions 💾**
- Added analytics node: **BSS Tag Analytics 📊**
- Added category-aware WD14 thresholds (`general/character/meta/rating`)
- Improved image normalization compatibility with ComfyUI `IMAGE`

### v1.0.1

- Stabilized `onnxruntime` handling and compatibility checks
- Improved model loading reliability

## License

MIT License

# BSS WD14 Batch Tagger v2.0

Custom nodes for **ComfyUI** for automatic WD14 image tagging, batch workflows, tag postprocessing, caption export, and basic tag analytics.
Набор нод для ComfyUI для WD14-теггинга, постобработки тегов, сохранения caption и базовой аналитики датасета.

## Что нового в v2.0

- ✅ Мультипорог по категориям: `general`, `character`, `meta`, `rating`
- ✅ Batch-in/Batch-out нода для массового теггинга
- ✅ Нода постобработки тегов (dedupe, сортировка, prepend/append/exclude)
- ✅ Нода сохранения caption в `txt/json/csv`
- ✅ Нода аналитики тегов (top-k + JSON статистика)

- WD14 v3 model support (ViT / SwinV2 / EVA02 / ConvNeXT)
- Automatic model download from Hugging Face
- Single-image and batch tagging nodes
- Category-aware thresholds (`general`, `character`, `meta`, `rating`)
- Tag postprocessing (dedupe, sorting, include/exclude operations)
- Caption saving to `txt`, `json`, `csv`
- Tag frequency analytics (`top-k` + JSON stats)
## Ноды
- **4 WD14 v3 Models**: ViT, SwinV2, EVA02, ConvNeXT
- **Auto Download**: Models download automatically from Hugging Face
- **GPU Support**: CUDA acceleration for faster processing
- **Batch Processing**: Process multiple images from folders
- **Format Support**: JPG, JPEG, PNG, WEBP
- **Custom Tags**: Add/remove tags as needed
- **ComfyUI IMAGE Compatibility**: Uses native tensor image format for modern ComfyUI builds

### 1) BSS Load Images from Folder 📂
Загружает изображения из папки (JPG/JPEG/PNG/WEBP) и отдает `IMAGE` + имена файлов.

### 2) BSS WD14 Batch Tagger 🌿
Теггинг одного изображения с сохранением `.txt`.

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
Параметры порогов:
- `general_threshold`
- `character_threshold`
- `meta_threshold`
- `rating_threshold`

### 3) BSS WD14 Tagger Batch ⚡
Теггинг списка изображений за один вызов.

Выходы:
- `tags` (список строк)
- `tags_json` (json с score/category)

### 4) BSS Tags Postprocess 🧹
Очистка и нормализация тегов:
- remove duplicates
- sort alphabetically
- prepend/append/exclude
- replace underscores

### 5) BSS Save Captions 💾
Сохраняет caption в `txt/json/csv`, есть `overwrite` и `suffix`.
1. Use **BSS Load Images from Folder** to load your images
2. Connect to **BSS WD14 Batch Tagger** for each image
3. Set output folder for tag files
4. Run the workflow

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
- **Model**: Choose WD14 model (auto-downloads if needed)
- **Threshold**: Tag confidence (0.35 default)
- **Character Threshold**: Separate threshold for character tags (WD category 4)
- **GPU**: Enable for faster processing
- **Prepend/Exclude**: Add custom tags or remove unwanted ones

## ComfyUI Compatibility

- Tested against current ComfyUI custom node API style (`NODE_CLASS_MAPPINGS`, `INPUT_TYPES`, `RETURN_TYPES`).
- Uses ComfyUI-native `IMAGE` tensors (`float32`, range `0..1`) in the loader node output.
- Tagger node accepts both tensor images (ComfyUI-native) and numpy arrays for backward compatibility.

## Models

Рекомендуемые стартовые параметры WD14:
- `general_threshold`: `0.35`
- `character_threshold`: `0.85`
- `meta_threshold`: `0.50`
- `rating_threshold`: `0.50`

## Требования

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
### 6) BSS Tag Analytics 📊
Считает top-k частых тегов и возвращает JSON статистику.

## Установка

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/BlackSnowSkill/wd14_batch_tagger.git
cd wd14_batch_tagger
pip install -r requirements.txt
```

## Совместимость

- Python 3.8+
- ComfyUI (актуальные сборки)
- onnxruntime `>=1.18.0,<2.0.0`

## License
MIT

MIT License
MIT License - see LICENSE file for details.

---

**Author**: Blacksnowskill

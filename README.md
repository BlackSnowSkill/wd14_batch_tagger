# BSS WD14 Batch Tagger v2.0

Набор нод для ComfyUI для WD14-теггинга, постобработки тегов, сохранения caption и базовой аналитики датасета.

## Что нового в v2.0

- ✅ Мультипорог по категориям: `general`, `character`, `meta`, `rating`
- ✅ Batch-in/Batch-out нода для массового теггинга
- ✅ Нода постобработки тегов (dedupe, сортировка, prepend/append/exclude)
- ✅ Нода сохранения caption в `txt/json/csv`
- ✅ Нода аналитики тегов (top-k + JSON статистика)

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

### Settings

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

- **WD ViT Tagger v3**: Fast, good quality (default)
- **WD SwinV2 Tagger v3**: Balanced speed/quality
- **WD EVA02 Large Tagger v3**: Best accuracy
- **WD ConvNeXT Tagger v3**: Modern architecture

Models download automatically on first use.

## Requirements

- Python 3.8+
- ComfyUI
- CUDA GPU (optional)

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

## Публикация v2.0 в ComfyUI Manager

1. Убедитесь, что версия обновлена в `pyproject.toml` и `package.json`.
2. Создайте git tag `v2.0.0` и push.
3. Опубликуйте через `comfy node publish` или ваш GitHub Action для registry.

## License
MIT

MIT License - see LICENSE file for details.

---

**Author**: Blacksnowskill

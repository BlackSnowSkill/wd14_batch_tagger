# BSS WD14 Batch Tagger v2.0

Набор нод для ComfyUI для WD14-теггинга, постобработки тегов, сохранения caption и базовой аналитики датасета.

## Что нового в v2.0

- ✅ Мультипорог по категориям: `general`, `character`, `meta`, `rating`
- ✅ Batch-in/Batch-out нода для массового теггинга
- ✅ Нода постобработки тегов (dedupe, сортировка, prepend/append/exclude)
- ✅ Нода сохранения caption в `txt/json/csv`
- ✅ Нода аналитики тегов (top-k + JSON статистика)

## Ноды

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

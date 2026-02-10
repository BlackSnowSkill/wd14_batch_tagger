# BSS WD14 Batch Tagger

Набор пользовательских нод для **ComfyUI** для автоматического теггинга изображений через WD14, пакетной обработки, постобработки тегов, сохранения подписей и базовой аналитики.

## Возможности

- Поддержка WD14 v3 моделей (ViT / SwinV2 / EVA02 / ConvNeXT)
- Автоматическая загрузка моделей с Hugging Face
- Ноды для одиночного и пакетного теггинга
- Пороги по категориям (`general`, `character`, `meta`, `rating`)
- Постобработка тегов (удаление дублей, сортировка, включение/исключение)
- Сохранение подписей в `txt`, `json`, `csv`
- Аналитика тегов (`top-k` + JSON статистика)

## Установка

### Через ComfyUI Manager

1. Откройте ComfyUI Manager
2. Найдите **BSS WD14 Batch Tagger**
3. Установите ноду и перезапустите ComfyUI

### Ручная установка

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/BlackSnowSkill/wd14_batch_tagger.git
cd wd14_batch_tagger
pip install -r requirements.txt
```

## Ноды в репозитории

- **BSS Load Images from Folder 📂** — загрузка изображений из папки (`jpg`, `jpeg`, `png`, `webp`)
- **BSS WD14 Batch Tagger 🌿** — теггинг одного изображения, при необходимости сохранение `.txt`
- **BSS WD14 Tagger Batch ⚡** — пакетный теггинг с возвратом JSON со score
- **BSS Tags Postprocess 🧹** — очистка/сортировка/дедупликация/фильтрация тегов
- **BSS Save Captions 💾** — сохранение подписей в `txt/json/csv`
- **BSS Tag Analytics 📊** — подсчёт частотности и топа тегов

## Использование

### Базовый сценарий

1. Загрузите изображения через **BSS Load Images from Folder 📂**
2. Выполните теггинг:
   - **BSS WD14 Batch Tagger 🌿** — для одиночного режима
   - **BSS WD14 Tagger Batch ⚡** — для пакетного режима
3. (Опционально) Очистите теги через **BSS Tags Postprocess 🧹**
4. (Опционально) Сохраните результат через **BSS Save Captions 💾**
5. (Опционально) Посмотрите статистику через **BSS Tag Analytics 📊**

### Пример графа (пакетный)

```text
BSS Load Images from Folder 📂
  ├─ images ───────► BSS WD14 Tagger Batch ⚡
  ├─ filenames ────► BSS WD14 Tagger Batch ⚡
  └─ folder_path ─► BSS WD14 Tagger Batch ⚡

BSS WD14 Tagger Batch ⚡ (tags)
  └───────────────► BSS Tags Postprocess 🧹
                       └──────────────► BSS Save Captions 💾

BSS WD14 Tagger Batch ⚡ (tags_json)
  └───────────────► BSS Tag Analytics 📊
```

Рекомендуемые стартовые параметры WD14:
- `general_threshold`: `0.35`
- `character_threshold`: `0.85`
- `meta_threshold`: `0.50`
- `rating_threshold`: `0.50`

## Требования

- Python 3.8+
- ComfyUI
- `onnxruntime>=1.18.0,<2.0.0`
- CUDA GPU (опционально)

## История изменений

Подробный список изменений находится в файле [CHANGELOG.md](./CHANGELOG.md).

Ключевые изменения версии `v2.0.0`:
- пакетный теггинг, постобработка, сохранение подписей и аналитика;
- пороги по категориям тегов (`general/character/meta/rating`);
- улучшенная совместимость с форматом ComfyUI `IMAGE`.

## Лицензия

MIT

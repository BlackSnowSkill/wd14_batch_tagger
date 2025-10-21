# Руководство по публикации в ComfyUI Registry

## Подготовленные файлы

Все необходимые файлы для публикации в [ComfyUI Registry](https://docs.comfy.org/registry/publishing) уже созданы:

### Основные файлы
- ✅ `pyproject.toml` - Конфигурация для ComfyUI Registry
- ✅ `LICENSE.txt` - Лицензия MIT
- ✅ `requirements.txt` - Зависимости Python
- ✅ `README.md` - Обновленная документация
- ✅ `install.py` - Скрипт автоматической установки

### Дополнительные файлы
- ✅ `node_list.json` - Справочная информация о нодах
- ✅ `package.json` - Метаданные (для совместимости)

## Секретный ключ

Ваш API ключ: `66ac3938-0c9c-42fc-b9c4-426d6729164d`

## Шаги для публикации

### 1. Настройка аккаунта в ComfyUI Registry

1. Перейдите на [ComfyUI Registry](https://registry.comfy.org/)
2. Создайте аккаунт Publisher с ID: `blacksnowskill`
3. Создайте API ключ для публикации
4. Сохраните API ключ: `66ac3938-0c9c-42fc-b9c4-426d6729164d`

### 2. Установка Comfy CLI

```bash
pip install comfy-cli
```

### 3. Подготовка репозитория

1. Убедитесь, что все файлы закоммичены в Git:
```bash
git add .
git commit -m "Prepare for ComfyUI Registry publication"
git push origin main
```

### 4. Публикация через Comfy CLI

```bash
comfy node publish
```

Введите ваш API ключ когда будет запрошен.

### 5. Автоматическая публикация через GitHub Actions

Создайте файл `.github/workflows/publish_action.yml`:

```yaml
name: Publish to Comfy registry
on:
  workflow_dispatch:
  push:
    branches:
      - main
    paths:
      - "pyproject.toml"

jobs:
  publish-node:
    name: Publish Custom Node to registry
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4
      - name: Publish Custom Node
        uses: Comfy-Org/publish-node-action@main
        with:
          personal_access_token: ${{ secrets.REGISTRY_ACCESS_TOKEN }}
```

### 6. Настройка GitHub Secret

1. Перейдите в Settings → Secrets and Variables → Actions
2. Создайте новый секрет: `REGISTRY_ACCESS_TOKEN`
3. Вставьте ваш API ключ: `66ac3938-0c9c-42fc-b9c4-426d6729164d`

### 7. После публикации

1. Нода будет доступна по адресу: `https://registry.comfy.org/blacksnowskill/wd14-batch-tagger`
2. Пользователи смогут установить через ComfyUI Manager
3. Обновления будут публиковаться автоматически при изменении `pyproject.toml`

## Структура файлов

```
wd14_batch_tagger/
├── __init__.py              # Основной модуль
├── nodes.py                 # Реализация нод
├── package.json             # Метаданные для ComfyUI Manager
├── pyproject.toml           # Конфигурация для comfyregistry
├── node_list.json           # Справочная информация о нодах
├── install.py               # Скрипт установки
├── requirements.txt         # Python зависимости
├── README.md                # Документация
├── LICENSE                  # Лицензия MIT
├── models/                  # Папка для моделей (создается автоматически)
└── custom-node-list-entry.json # Пример записи для PR
```

## Тестирование

После публикации протестируйте установку:

1. Удалите ноду из custom_nodes
2. Установите через ComfyUI Manager
3. Проверьте работу обеих нод
4. Убедитесь, что модели загружаются автоматически

## Поддержка

- GitHub Issues: https://github.com/blacksnowskill/wd14_batch_tagger/issues
- ComfyUI Community: Упоминайте @blacksnowskill

---

**Готово к публикации!** 🚀

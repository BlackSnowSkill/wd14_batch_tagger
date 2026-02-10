# Публикация v2.0.0 в ComfyUI Registry

## Проверка перед релизом

- `__init__.py` → `__version__ = "2.0.0"`
- `pyproject.toml` → `version = "2.0.0"`
- `package.json` → `version = "2.0.0"`

## Публикация

1. Закоммитьте изменения.
2. Создайте тег:
   ```bash
   git tag v2.0.0
   git push origin main --tags
   ```
3. Опубликуйте ноду:
   ```bash
   comfy node publish
   ```

## Через GitHub Actions

```yaml
name: Publish to Comfy registry
on:
  workflow_dispatch:
  push:
    tags:
      - 'v*'

jobs:
  publish-node:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Comfy-Org/publish-node-action@main
        with:
          personal_access_token: ${{ secrets.REGISTRY_ACCESS_TOKEN }}
```

## Важно

- Не храните API ключи в репозитории.
- Используйте только GitHub Secrets / локальные переменные окружения.

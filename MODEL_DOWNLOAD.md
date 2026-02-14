# Информация о модели RoBERTa

## Проблема с размером

Файл модели `roberta_reaction_classifier/best_model/model.safetensors` весит **476MB**, что превышает лимит GitHub (100MB на файл) и вызывает таймауты при push.

## Решение

Модель была исключена из репозитория. Есть несколько вариантов:

### Вариант 1: Использовать Git LFS (Large File Storage)

Если нужно хранить модель в репозитории:

```bash
# Установите Git LFS
brew install git-lfs  # macOS
# или скачайте с https://git-lfs.github.com/

# Инициализируйте Git LFS
git lfs install

# Отслеживайте большие файлы
git lfs track "*.safetensors"
git lfs track "roberta_reaction_classifier/best_model/*.safetensors"

# Добавьте файл обратно
git add .gitattributes
git add roberta_reaction_classifier/best_model/model.safetensors
git commit -m "Add model using Git LFS"
git push
```

**Примечание:** Git LFS требует подписку GitHub (бесплатно до 1GB хранилища).

### Вариант 2: Загрузить модель отдельно

1. Загрузите модель на Google Drive / Dropbox / другой файлообменник
2. Добавьте ссылку в README.md
3. Пользователи скачают модель отдельно

### Вариант 3: Обучить модель заново

Модель можно обучить заново используя скрипт `finetune_roberta_context.py`:

```bash
python finetune_roberta_context.py
```

### Вариант 4: Использовать предобученную модель

Вместо fine-tuned модели можно использовать предобученную модель напрямую в коде.

## Текущее состояние

В репозитории сохранены:
- ✅ Конфигурация модели (`config.json`)
- ✅ Токенизатор (`tokenizer.json`, `vocab.json`)
- ✅ Метаданные модели

Отсутствует:
- ❌ Веса модели (`model.safetensors` - 476MB)

Для использования модели нужно либо:
1. Обучить её заново
2. Скачать из отдельного источника
3. Использовать Git LFS

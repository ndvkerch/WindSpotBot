# Система контроля версий WindSpotBot

## Обзор

WindSpotBot использует автоматизированную систему контроля версий, которая обеспечивает:
- Автоматическое обновление документации при каждом коммите
- Создание коммитов на русском языке
- Организованную работу с веткой `dev`
- Автоматическую синхронизацию с GitHub

## Архитектура системы

### Компоненты

1. **Pre-commit hooks** (`.pre-commit-config.yaml`)
   - Автоматическое обновление документации
   - Форматирование кода
   - Проверка стиля и типов
   - Запуск тестов

2. **Скрипты автоматизации** (`scripts/`)
   - `update_docs.py` - обновление документации
   - `update_changelog.py` - обновление CHANGELOG
   - `commit_helper.py` - помощник создания коммитов
   - `github_helper.py` - работа с GitHub
   - `auto_commit.py` - автоматические коммиты
   - `dev_workflow.py` - workflow для ветки dev
   - `dev_auto_commit.py` - автоматические коммиты для dev
   - `version_manager.py` - управление версиями

3. **Makefile команды**
   - Команды для разработки
   - Специальные команды для ветки dev
   - Команды для работы с версиями

## Настройка

### 1. Установка pre-commit hooks

```bash
# Установка pre-commit
pip install pre-commit

# Установка hooks
make pre-commit
```

### 2. Настройка GitHub CLI

```bash
# Установка GitHub CLI
# Windows: winget install GitHub.cli
# Linux: sudo apt install gh
# macOS: brew install gh

# Авторизация
gh auth login
```

### 3. Настройка Git

```bash
# Настройка пользователя
git config --global user.name "Ваше Имя"
git config --global user.email "your.email@example.com"

# Настройка автоперевода строк
git config --global core.autocrlf true
```

## Работа с веткой dev

### Основные команды

```bash
# Полный workflow для dev
make dev-workflow

# Синхронизация с main
make dev-sync

# Отправка на GitHub
make dev-push

# Создание Pull Request
make dev-pr

# Автоматические коммиты
make dev-auto

# Один цикл обработки
make dev-once

# Создание коммита с помощью
make dev-commit

# Автоматический коммит
make dev-auto-commit
```

### Workflow для разработки

1. **Начало работы**
   ```bash
   # Переключение на dev
   git checkout dev
   
   # Синхронизация с main
   make dev-sync
   ```

2. **Разработка**
   ```bash
   # Автоматические коммиты
   make dev-auto
   
   # Или один цикл
   make dev-once
   ```

3. **Завершение работы**
   ```bash
   # Создание PR
   make dev-pr
   
   # Или отправка на GitHub
   make dev-push
   ```

## Автоматические коммиты

### Настройка

```bash
# Запуск мониторинга изменений
python scripts/dev_auto_commit.py --auto-push

# Один цикл обработки
python scripts/dev_auto_commit.py --once --auto-push

# Без автоматической отправки
python scripts/dev_auto_commit.py --no-commit
```

### Параметры

- `--interval N` - интервал проверки в секундах (по умолчанию: 30)
- `--no-commit` - не создавать коммиты автоматически
- `--auto-push` - автоматически отправлять на GitHub
- `--once` - выполнить один раз и выйти

## Управление версиями

### Создание релизов

```bash
# Patch релиз (0.0.1)
python scripts/version_manager.py --patch

# Minor релиз (0.1.0)
python scripts/version_manager.py --minor

# Major релиз (1.0.0)
python scripts/version_manager.py --major

# Список версий
python scripts/version_manager.py --list
```

### Процесс релиза

1. **Подготовка**
   ```bash
   # Переключение на main
   git checkout main
   
   # Синхронизация
   git pull origin main
   ```

2. **Создание релиза**
   ```bash
   # Patch релиз
   python scripts/version_manager.py --patch
   
   # Или через Makefile
   make release-patch
   ```

3. **Проверка**
   ```bash
   # Проверка тегов
   git tag --list
   
   # Проверка на GitHub
   gh release list
   ```

## Типы коммитов

### Автоматические типы

- **feat** - новые функции
- **fix** - исправления ошибок
- **docs** - документация
- **test** - тесты
- **chore** - конфигурация
- **refactor** - рефакторинг

### Примеры сообщений

```
feat: Добавлена новая функция прогноза погоды
fix: Исправлена ошибка в обработке геолокации
docs: Обновлена документация API
test: Добавлены тесты для сервиса погоды
chore: Обновлена конфигурация pre-commit
refactor: Улучшена структура обработчиков
```

## Конфигурация

### Pre-commit hooks

Файл `.pre-commit-config.yaml` содержит:
- Обновление документации
- Форматирование кода (Black)
- Проверка стиля (flake8)
- Проверка типов (mypy)
- Запуск тестов

### Makefile

Основные команды:
- `make help` - справка по командам
- `make install` - установка зависимостей
- `make test` - запуск тестов
- `make format` - форматирование кода
- `make lint` - проверка стиля
- `make docs` - обновление документации
- `make check` - полная проверка

## Troubleshooting

### Проблемы с pre-commit

```bash
# Переустановка hooks
pre-commit uninstall
pre-commit install

# Обновление hooks
pre-commit autoupdate
```

### Проблемы с GitHub CLI

```bash
# Проверка авторизации
gh auth status

# Повторная авторизация
gh auth login
```

### Проблемы с Git

```bash
# Проверка конфигурации
git config --list

# Сброс к последнему коммиту
git reset --hard HEAD
```

## Лучшие практики

### Для разработчиков

1. **Всегда работайте в ветке dev**
   ```bash
   git checkout dev
   ```

2. **Используйте автоматические коммиты**
   ```bash
   make dev-auto
   ```

3. **Синхронизируйтесь с main**
   ```bash
   make dev-sync
   ```

4. **Создавайте PR для изменений**
   ```bash
   make dev-pr
   ```

### Для релизов

1. **Тестируйте перед релизом**
   ```bash
   make check
   ```

2. **Используйте семантическое версионирование**
   - Patch: исправления ошибок
   - Minor: новые функции
   - Major: breaking changes

3. **Проверяйте релизы на GitHub**
   ```bash
   gh release list
   ```

## Дополнительные ресурсы

- [Git Documentation](https://git-scm.com/doc)
- [GitHub CLI Documentation](https://cli.github.com/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## Поддержка

Если у вас возникли проблемы с системой контроля версий:

1. Проверьте логи: `make status`
2. Запустите проверку: `make check`
3. Обратитесь к документации: `make help`
4. Создайте issue в репозитории

---

*Документация обновлена: 2025-01-17*




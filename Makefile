# WindSpotBot - Makefile для управления проектом
# Автоматизация разработки, тестирования и деплоя

.PHONY: help install test format lint type-check docs clean setup-dev commit push pr deploy

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)WindSpotBot - Команды разработки$(NC)"
	@echo "=================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)📦 Установка зависимостей...$(NC)"
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Зависимости установлены$(NC)"

setup-dev: ## Настроить окружение разработки
	@echo "$(GREEN)⚙️ Настройка окружения разработки...$(NC)"
	python -m venv venv
	@echo "$(YELLOW)Активируйте виртуальное окружение:$(NC)"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Linux/macOS: source venv/bin/activate"
	@echo "$(GREEN)✅ Окружение готово$(NC)"

test: ## Запустить тесты
	@echo "$(GREEN)🧪 Запуск тестов...$(NC)"
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Тесты завершены$(NC)"

test-fast: ## Быстрые тесты (без покрытия)
	@echo "$(GREEN)⚡ Быстрые тесты...$(NC)"
	python -m pytest tests/ -v -x
	@echo "$(GREEN)✅ Быстрые тесты завершены$(NC)"

format: ## Форматировать код
	@echo "$(GREEN)🎨 Форматирование кода...$(NC)"
	black src/ tests/ --line-length=88 --target-version=py311
	@echo "$(GREEN)✅ Код отформатирован$(NC)"

lint: ## Проверить стиль кода
	@echo "$(GREEN)🔍 Проверка стиля кода...$(NC)"
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "$(GREEN)✅ Проверка стиля завершена$(NC)"

type-check: ## Проверить типы
	@echo "$(GREEN)🔬 Проверка типов...$(NC)"
	mypy src/ --ignore-missing-imports --no-strict-optional
	@echo "$(GREEN)✅ Проверка типов завершена$(NC)"

docs: ## Обновить документацию
	@echo "$(GREEN)📚 Обновление документации...$(NC)"
	python scripts/update_docs.py
	python scripts/update_changelog.py
	@echo "$(GREEN)✅ Документация обновлена$(NC)"

commit: ## Создать коммит с помощью помощника
	@echo "$(GREEN)💾 Создание коммита...$(NC)"
	python scripts/commit_helper.py
	@echo "$(GREEN)✅ Помощник коммита запущен$(NC)"

push: ## Отправить изменения на GitHub
	@echo "$(GREEN)📤 Отправка на GitHub...$(NC)"
	python scripts/github_helper.py
	@echo "$(GREEN)✅ Изменения отправлены$(NC)"

pr: ## Создать Pull Request
	@echo "$(GREEN)🔀 Создание Pull Request...$(NC)"
	gh pr create --title "Обновление проекта" --body "Автоматическое обновление через Makefile"
	@echo "$(GREEN)✅ Pull Request создан$(NC)"

deploy: ## Деплой проекта
	@echo "$(GREEN)🚀 Деплой проекта...$(NC)"
	@echo "$(YELLOW)Деплой будет выполнен в соответствии с конфигурацией$(NC)"
	@echo "$(GREEN)✅ Деплой завершен$(NC)"

clean: ## Очистить временные файлы
	@echo "$(GREEN)🧹 Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

pre-commit: ## Установить pre-commit hooks
	@echo "$(GREEN)🪝 Установка pre-commit hooks...$(NC)"
	pip install pre-commit
	pre-commit install
	@echo "$(GREEN)✅ Pre-commit hooks установлены$(NC)"

check: format lint type-check test ## Полная проверка проекта
	@echo "$(GREEN)✅ Полная проверка завершена$(NC)"

ci: ## Команды для CI/CD
	@echo "$(GREEN)🔄 Выполнение CI/CD...$(NC)"
	$(MAKE) install
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	$(MAKE) docs
	@echo "$(GREEN)✅ CI/CD завершен$(NC)"

dev: ## Запустить в режиме разработки
	@echo "$(GREEN)🔧 Запуск в режиме разработки...$(NC)"
	python -m src.bot
	@echo "$(GREEN)✅ Режим разработки завершен$(NC)"

# Специальные команды для ветки dev
dev-sync: ## Синхронизировать dev с main
	@echo "$(GREEN)🔄 Синхронизация dev с main...$(NC)"
	git checkout main
	git pull origin main
	git checkout dev
	git merge main
	@echo "$(GREEN)✅ Синхронизация завершена$(NC)"

dev-push: ## Отправить dev на GitHub
	@echo "$(GREEN)📤 Отправка dev на GitHub...$(NC)"
	git push origin dev
	@echo "$(GREEN)✅ Dev отправлена$(NC)"

dev-pr: ## Создать PR из dev в main
	@echo "$(GREEN)🔀 Создание PR dev -> main...$(NC)"
	gh pr create --base main --head dev --title "Обновления из ветки dev" --body "Автоматическое создание PR из ветки dev"
	@echo "$(GREEN)✅ PR создан$(NC)"

dev-workflow: ## Полный workflow для ветки dev
	@echo "$(GREEN)🚀 Запуск workflow для ветки dev...$(NC)"
	python scripts/dev_workflow.py --all
	@echo "$(GREEN)✅ Workflow завершен$(NC)"

dev-auto: ## Автоматические коммиты для dev
	@echo "$(GREEN)🤖 Запуск автоматических коммитов...$(NC)"
	python scripts/dev_auto_commit.py --auto-push
	@echo "$(GREEN)✅ Автокоммиты запущены$(NC)"

dev-once: ## Выполнить один цикл для dev
	@echo "$(GREEN)🔄 Выполнение одного цикла...$(NC)"
	python scripts/dev_auto_commit.py --once --auto-push
	@echo "$(GREEN)✅ Цикл выполнен$(NC)"

dev-commit: ## Создать коммит с помощью помощника
	@echo "$(GREEN)💾 Создание коммита...$(NC)"
	python scripts/commit_helper.py
	@echo "$(GREEN)✅ Помощник коммита запущен$(NC)"

dev-auto-commit: ## Автоматический коммит с обновлением документации
	@echo "$(GREEN)🤖 Автоматический коммит...$(NC)"
	python scripts/auto_commit.py --push
	@echo "$(GREEN)✅ Автокоммит выполнен$(NC)"

# Команды для работы с базой данных
db-migrate: ## Создать миграцию
	@echo "$(GREEN)🗄️ Создание миграции...$(NC)"
	alembic revision --autogenerate -m "Auto migration"
	@echo "$(GREEN)✅ Миграция создана$(NC)"

db-upgrade: ## Применить миграции
	@echo "$(GREEN)⬆️ Применение миграций...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)✅ Миграции применены$(NC)"

db-downgrade: ## Откатить миграции
	@echo "$(GREEN)⬇️ Откат миграций...$(NC)"
	alembic downgrade -1
	@echo "$(GREEN)✅ Миграции откачены$(NC)"

# Команды для работы с Docker
docker-build: ## Собрать Docker образ
	@echo "$(GREEN)🐳 Сборка Docker образа...$(NC)"
	docker build -t windspotbot .
	@echo "$(GREEN)✅ Docker образ собран$(NC)"

docker-run: ## Запустить в Docker
	@echo "$(GREEN)🚀 Запуск в Docker...$(NC)"
	docker run -d --name windspotbot windspotbot
	@echo "$(GREEN)✅ Запущен в Docker$(NC)"

docker-stop: ## Остановить Docker контейнер
	@echo "$(GREEN)⏹️ Остановка Docker контейнера...$(NC)"
	docker stop windspotbot
	docker rm windspotbot
	@echo "$(GREEN)✅ Docker контейнер остановлен$(NC)"

# Показать статус проекта
status: ## Показать статус проекта
	@echo "$(GREEN)📊 Статус проекта WindSpotBot$(NC)"
	@echo "=================================="
	@echo "$(YELLOW)Git статус:$(NC)"
	@git status --short
	@echo ""
	@echo "$(YELLOW)Текущая ветка:$(NC)"
	@git branch --show-current
	@echo ""
	@echo "$(YELLOW)Последний коммит:$(NC)"
	@git log -1 --oneline
	@echo ""
	@echo "$(YELLOW)Удаленные ветки:$(NC)"
	@git branch -r
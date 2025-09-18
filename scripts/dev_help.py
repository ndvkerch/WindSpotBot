#!/usr/bin/env python3
"""
Справка по системе контроля версий для ветки dev.
Показывает доступные команды и их описание.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Добавляем корневую папку проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_help():
    """Выводит справку по системе контроля версий."""
    print("🚀 Справка по системе контроля версий WindSpotBot")
    print("=" * 55)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {project_root}")
    print()
    
    print("📋 Основные команды Makefile:")
    print("=" * 30)
    print("make help                 # Показать эту справку")
    print("make install              # Установить зависимости")
    print("make test                 # Запустить тесты")
    print("make format               # Форматировать код")
    print("make lint                 # Проверить стиль кода")
    print("make docs                 # Обновить документацию")
    print("make check                # Полная проверка проекта")
    print("make clean                # Очистить временные файлы")
    print()
    
    print("🌿 Команды для ветки dev:")
    print("=" * 25)
    print("make dev-workflow         # Полный workflow для dev")
    print("make dev-sync             # Синхронизировать с main")
    print("make dev-push             # Отправить dev на GitHub")
    print("make dev-pr               # Создать Pull Request")
    print("make dev-auto             # Автоматические коммиты")
    print("make dev-once             # Выполнить один цикл")
    print("make dev-commit           # Помощник коммита")
    print("make dev-auto-commit      # Автоматический коммит")
    print()
    
    print("📜 Скрипты Python:")
    print("=" * 20)
    print("python scripts/dev_setup.py           # Полная настройка dev")
    print("python scripts/dev_workflow.py        # Workflow для dev")
    print("python scripts/dev_auto_commit.py     # Автоматические коммиты")
    print("python scripts/dev_monitor.py         # Мониторинг изменений")
    print("python scripts/dev_status.py          # Статус системы")
    print("python scripts/commit_helper.py       # Помощник коммита")
    print("python scripts/github_helper.py       # Работа с GitHub")
    print("python scripts/version_manager.py     # Управление версиями")
    print("python scripts/auto_commit.py         # Автоматический коммит")
    print("python scripts/update_docs.py         # Обновление документации")
    print("python scripts/update_changelog.py    # Обновление CHANGELOG")
    print()
    
    print("🔧 Настройка системы:")
    print("=" * 25)
    print("1. Установка зависимостей:")
    print("   make install")
    print()
    print("2. Настройка ветки dev:")
    print("   python scripts/dev_setup.py")
    print()
    print("3. Установка pre-commit hooks:")
    print("   make pre-commit")
    print()
    print("4. Настройка GitHub CLI:")
    print("   gh auth login")
    print()
    
    print("🚀 Работа с веткой dev:")
    print("=" * 25)
    print("1. Переключение на dev:")
    print("   git checkout dev")
    print()
    print("2. Синхронизация с main:")
    print("   make dev-sync")
    print()
    print("3. Автоматические коммиты:")
    print("   make dev-auto")
    print()
    print("4. Создание Pull Request:")
    print("   make dev-pr")
    print()
    
    print("📊 Мониторинг и статус:")
    print("=" * 25)
    print("make status               # Статус проекта")
    print("python scripts/dev_status.py  # Детальный статус")
    print("python scripts/dev_monitor.py # Мониторинг изменений")
    print()
    
    print("🔄 Автоматические коммиты:")
    print("=" * 25)
    print("make dev-auto             # Запуск мониторинга")
    print("make dev-once             # Один цикл")
    print("make dev-auto-commit      # Автокоммит с отправкой")
    print()
    print("Параметры мониторинга:")
    print("--interval N              # Интервал проверки (сек)")
    print("--no-commit               # Не создавать коммиты")
    print("--auto-push               # Автоматически отправлять")
    print("--max-commits N           # Максимум коммитов")
    print("--once                    # Выполнить один раз")
    print()
    
    print("📝 Типы коммитов:")
    print("=" * 20)
    print("feat: Новая функция")
    print("fix: Исправление ошибки")
    print("docs: Документация")
    print("test: Тесты")
    print("chore: Конфигурация")
    print("refactor: Рефакторинг")
    print()
    
    print("🌐 Работа с GitHub:")
    print("=" * 20)
    print("make dev-push             # Отправить на GitHub")
    print("make dev-pr               # Создать Pull Request")
    print("python scripts/github_helper.py  # Помощник GitHub")
    print()
    
    print("🏷️ Управление версиями:")
    print("=" * 25)
    print("python scripts/version_manager.py --patch   # Patch релиз")
    print("python scripts/version_manager.py --minor   # Minor релиз")
    print("python scripts/version_manager.py --major   # Major релиз")
    print("python scripts/version_manager.py --list    # Список версий")
    print()
    
    print("📚 Документация:")
    print("=" * 15)
    print("docs/version_control.md   # Система контроля версий")
    print("README_DEVELOPMENT.md     # Руководство разработчика")
    print("docs/api.md               # API документация")
    print("docs/architecture.md      # Архитектура проекта")
    print("docs/testing.md           # Тестирование")
    print("docs/ux.md                # UX/UI принципы")
    print()
    
    print("⚠️ Важные замечания:")
    print("=" * 20)
    print("• Все команды работают только в ветке dev")
    print("• Автоматические коммиты обновляют документацию")
    print("• Pre-commit hooks проверяют код перед коммитом")
    print("• Тесты запускаются автоматически")
    print("• Документация обновляется при каждом коммите")
    print()
    
    print("🔍 Troubleshooting:")
    print("=" * 20)
    print("• Проблемы с pre-commit: make pre-commit")
    print("• Проблемы с GitHub: gh auth status")
    print("• Проблемы с Git: git status")
    print("• Статус системы: python scripts/dev_status.py")
    print()
    
    print("📞 Поддержка:")
    print("=" * 10)
    print("• Документация: docs/version_control.md")
    print("• Статус: python scripts/dev_status.py")
    print("• Логи: make status")
    print("• Issues: GitHub Issues")
    print()
    
    print("🎯 Быстрый старт:")
    print("=" * 15)
    print("1. git checkout dev")
    print("2. make dev-sync")
    print("3. make dev-auto")
    print("4. make dev-pr")
    print()
    
    print("✅ Система готова к работе!")

def main():
    """Основная функция справки."""
    print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())




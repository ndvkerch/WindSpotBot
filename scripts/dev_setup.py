#!/usr/bin/env python3
"""
Полная настройка ветки dev для автоматических коммитов.
Объединяет все настройки в одном скрипте.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Добавляем корневую папку проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(command: str, cwd: Path = None) -> tuple[bool, str]:
    """Выполняет команду и возвращает результат."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or project_root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'  # Заменяем проблемные символы
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_requirements() -> bool:
    """Проверяет необходимые зависимости."""
    print("🔍 Проверка зависимостей...")
    
    # Проверяем Python
    if sys.version_info < (3, 11):
        print("❌ Требуется Python 3.11 или выше")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Проверяем Git
    success, output = run_command("git --version")
    if not success:
        print("❌ Git не установлен")
        return False
    
    print(f"✅ {output.strip()}")
    
    # Проверяем pip
    success, output = run_command("python -m pip --version")
    if not success:
        print("❌ pip не установлен")
        return False
    
    print(f"✅ {output.strip()}")
    
    return True

def install_dependencies() -> bool:
    """Устанавливает зависимости."""
    print("📦 Установка зависимостей...")
    
    # Устанавливаем основные зависимости
    success, output = run_command("pip install -r requirements.txt")
    if not success:
        print(f"❌ Ошибка установки зависимостей: {output}")
        return False
    
    # Устанавливаем pre-commit
    success, output = run_command("pip install pre-commit")
    if not success:
        print(f"❌ Ошибка установки pre-commit: {output}")
        return False
    
    print("✅ Зависимости установлены")
    return True

def setup_git() -> bool:
    """Настраивает Git."""
    print("🔧 Настройка Git...")
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        print("Инициализируйте репозиторий: git init")
        return False
    
    # Проверяем конфигурацию пользователя
    success, output = run_command("git config user.name")
    if not success or not output.strip():
        print("⚠️ Не настроено имя пользователя Git")
        print("Выполните: git config --global user.name 'Ваше Имя'")
    
    success, output = run_command("git config user.email")
    if not success or not output.strip():
        print("⚠️ Не настроен email пользователя Git")
        print("Выполните: git config --global user.email 'your.email@example.com'")
    
    print("✅ Git настроен")
    return True

def create_dev_branch() -> bool:
    """Создает ветку dev."""
    print("🌿 Настройка ветки dev...")
    
    # Проверяем текущую ветку
    success, output = run_command("git branch --show-current")
    if not success:
        print("❌ Ошибка получения текущей ветки")
        return False
    
    current_branch = output.strip()
    print(f"📁 Текущая ветка: {current_branch}")
    
    # Если не в ветке dev, переключаемся
    if current_branch != "dev":
        # Проверяем, существует ли ветка dev
        success, output = run_command("git branch --list dev")
        if success and output.strip():
            # Переключаемся на dev
            success, output = run_command("git checkout dev")
            if not success:
                print(f"❌ Ошибка переключения на dev: {output}")
                return False
        else:
            # Создаем ветку dev
            success, output = run_command("git checkout -b dev")
            if not success:
                print(f"❌ Ошибка создания ветки dev: {output}")
                return False
    
    print("✅ Ветка dev настроена")
    return True

def setup_pre_commit() -> bool:
    """Настраивает pre-commit hooks."""
    print("🪝 Настройка pre-commit hooks...")
    
    # Устанавливаем pre-commit hooks
    success, output = run_command("pre-commit install")
    if not success:
        print(f"❌ Ошибка установки pre-commit hooks: {output}")
        return False
    
    print("✅ Pre-commit hooks настроены")
    return True

def setup_git_hooks() -> bool:
    """Настраивает Git hooks."""
    print("🪝 Настройка Git hooks...")
    
    # Запускаем скрипт установки hooks
    success, output = run_command("python scripts/install_hooks.py")
    if not success:
        print(f"❌ Ошибка установки Git hooks: {output}")
        return False
    
    print("✅ Git hooks настроены")
    return True

def setup_github() -> bool:
    """Настраивает GitHub."""
    print("🔗 Настройка GitHub...")
    
    # Проверяем GitHub CLI
    success, output = run_command("gh --version")
    if not success:
        print("⚠️ GitHub CLI не установлен")
        print("Установите: https://cli.github.com/")
        return True  # Не критично
    
    # Проверяем авторизацию
    success, output = run_command("gh auth status")
    if not success:
        print("⚠️ GitHub CLI не авторизован")
        print("Выполните: gh auth login")
        return True  # Не критично
    
    print("✅ GitHub настроен")
    return True

def create_initial_commit() -> bool:
    """Создает начальный коммит."""
    print("💾 Создание начального коммита...")
    
    # Проверяем, есть ли коммиты
    success, output = run_command("git log --oneline -1")
    if success and output.strip():
        print("✅ Коммиты уже существуют")
        return True
    
    # Добавляем все файлы
    success, output = run_command("git add .")
    if not success:
        print(f"❌ Ошибка добавления файлов: {output}")
        return False
    
    # Создаем коммит
    commit_message = "Начальная настройка проекта WindSpotBot с автоматическими коммитами"
    success, output = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Ошибка создания коммита: {output}")
        return False
    
    print("✅ Начальный коммит создан")
    return True

def test_setup() -> bool:
    """Тестирует настройку."""
    print("🧪 Тестирование настройки...")
    
    # Проверяем, что мы в ветке dev
    success, output = run_command("git branch --show-current")
    if not success or output.strip() != "dev":
        print("❌ Не в ветке dev")
        return False
    
    # Проверяем pre-commit
    success, output = run_command("pre-commit --version")
    if not success:
        print("❌ Pre-commit не работает")
        return False
    
    # Проверяем скрипты
    scripts = [
        "scripts/update_docs.py",
        "scripts/update_changelog.py",
        "scripts/commit_helper.py",
        "scripts/github_helper.py",
        "scripts/auto_commit.py",
        "scripts/dev_workflow.py",
        "scripts/dev_auto_commit.py",
        "scripts/version_manager.py"
    ]
    
    for script in scripts:
        if not (project_root / script).exists():
            print(f"❌ Скрипт {script} не найден")
            return False
    
    print("✅ Настройка протестирована")
    return True

def main():
    """Основная функция настройки."""
    print("🚀 Полная настройка ветки dev для WindSpotBot")
    print("=" * 50)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {project_root}")
    print()
    
    # Проверяем зависимости
    if not check_requirements():
        return 1
    
    # Устанавливаем зависимости
    if not install_dependencies():
        return 1
    
    # Настраиваем Git
    if not setup_git():
        return 1
    
    # Создаем ветку dev
    if not create_dev_branch():
        return 1
    
    # Настраиваем pre-commit
    if not setup_pre_commit():
        return 1
    
    # Настраиваем Git hooks
    if not setup_git_hooks():
        return 1
    
    # Настраиваем GitHub
    if not setup_github():
        return 1
    
    # Создаем начальный коммит
    if not create_initial_commit():
        return 1
    
    # Тестируем настройку
    if not test_setup():
        return 1
    
    print("\n🎉 Настройка завершена успешно!")
    print("\n📋 Что было настроено:")
    print("✅ Зависимости установлены")
    print("✅ Ветка dev создана")
    print("✅ Pre-commit hooks настроены")
    print("✅ Git hooks установлены")
    print("✅ GitHub настроен")
    print("✅ Начальный коммит создан")
    
    print("\n🔧 Доступные команды:")
    print("- make dev-workflow    # Полный workflow")
    print("- make dev-auto        # Автоматические коммиты")
    print("- make dev-once        # Один цикл")
    print("- make dev-commit      # Помощник коммита")
    print("- make dev-sync        # Синхронизация с main")
    print("- make dev-push        # Отправка на GitHub")
    print("- make dev-pr          # Создание PR")
    
    print("\n📚 Документация:")
    print("- docs/version_control.md - Система контроля версий")
    print("- README_DEVELOPMENT.md - Руководство разработчика")
    
    print("\n⚠️ Важно:")
    print("1. Настройте удаленный репозиторий: git remote add origin <URL>")
    print("2. Отправьте ветку dev: git push -u origin dev")
    print("3. Запустите автоматические коммиты: make dev-auto")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

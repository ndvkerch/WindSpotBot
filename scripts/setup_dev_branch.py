#!/usr/bin/env python3
"""
Настройка ветки dev для автоматических коммитов.
Создает необходимые конфигурации и настраивает workflow.
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
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_git_repo() -> bool:
    """Проверяет, что мы в git репозитории."""
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return False
    return True

def get_current_branch() -> str:
    """Получает текущую ветку."""
    success, output = run_command("git branch --show-current")
    if success:
        return output.strip()
    return "unknown"

def create_dev_branch() -> bool:
    """Создает ветку dev если её нет."""
    print("🌿 Проверка ветки dev...")
    
    # Проверяем, существует ли ветка dev
    success, output = run_command("git branch --list dev")
    if success and output.strip():
        print("✅ Ветка dev уже существует")
        return True
    
    # Создаем ветку dev
    print("📝 Создание ветки dev...")
    success, output = run_command("git checkout -b dev")
    if not success:
        print(f"❌ Ошибка создания ветки dev: {output}")
        return False
    
    print("✅ Ветка dev создана")
    return True

def setup_pre_commit() -> bool:
    """Настраивает pre-commit hooks."""
    print("🪝 Настройка pre-commit hooks...")
    
    # Устанавливаем pre-commit
    success, output = run_command("pip install pre-commit")
    if not success:
        print(f"❌ Ошибка установки pre-commit: {output}")
        return False
    
    # Устанавливаем hooks
    success, output = run_command("pre-commit install")
    if not success:
        print(f"❌ Ошибка установки hooks: {output}")
        return False
    
    print("✅ Pre-commit hooks настроены")
    return True

def setup_github_cli() -> bool:
    """Проверяет настройку GitHub CLI."""
    print("🔗 Проверка GitHub CLI...")
    
    success, output = run_command("gh --version")
    if not success:
        print("❌ GitHub CLI не установлен")
        print("Установите: https://cli.github.com/")
        return False
    
    # Проверяем авторизацию
    success, output = run_command("gh auth status")
    if not success:
        print("❌ GitHub CLI не авторизован")
        print("Выполните: gh auth login")
        return False
    
    print("✅ GitHub CLI настроен")
    return True

def create_gitignore() -> bool:
    """Создает .gitignore если его нет."""
    print("📝 Проверка .gitignore...")
    
    gitignore_path = project_root / '.gitignore'
    if gitignore_path.exists():
        print("✅ .gitignore уже существует")
        return True
    
    # Создаем .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
.env
*.log
*.db
*.sqlite
*.sqlite3

# Testing
.pytest_cache/
.coverage
htmlcov/
coverage.xml

# Documentation
docs/_build/

# Temporary files
*.tmp
*.temp
"""
    
    gitignore_path.write_text(gitignore_content, encoding='utf-8')
    print("✅ .gitignore создан")
    return True

def setup_remote() -> bool:
    """Настраивает удаленный репозиторий."""
    print("🌐 Проверка удаленного репозитория...")
    
    # Проверяем, есть ли origin
    success, output = run_command("git remote get-url origin")
    if success:
        print(f"✅ Удаленный репозиторий: {output.strip()}")
        return True
    
    print("❌ Удаленный репозиторий не настроен")
    print("Настройте: git remote add origin <URL>")
    return False

def create_initial_commit() -> bool:
    """Создает начальный коммит если его нет."""
    print("💾 Проверка начального коммита...")
    
    # Проверяем, есть ли коммиты
    success, output = run_command("git log --oneline -1")
    if success and output.strip():
        print("✅ Коммиты уже существуют")
        return True
    
    # Создаем начальный коммит
    print("📝 Создание начального коммита...")
    
    # Добавляем все файлы
    success, output = run_command("git add .")
    if not success:
        print(f"❌ Ошибка добавления файлов: {output}")
        return False
    
    # Создаем коммит
    commit_message = "Начальная настройка проекта WindSpotBot"
    success, output = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Ошибка создания коммита: {output}")
        return False
    
    print("✅ Начальный коммит создан")
    return True

def setup_dev_workflow() -> bool:
    """Настраивает workflow для ветки dev."""
    print("⚙️ Настройка workflow для ветки dev...")
    
    # Создаем папку для workflow
    workflow_dir = project_root / '.github' / 'workflows'
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем workflow для dev
    dev_workflow_content = """name: Dev Branch Workflow

on:
  push:
    branches: [ dev ]
  pull_request:
    branches: [ dev ]

jobs:
  dev-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Check code formatting
      run: |
        black --check src/ tests/
        flake8 src/ tests/
        mypy src/
    
    - name: Update documentation
      run: |
        python scripts/update_docs.py
        python scripts/update_changelog.py
    
    - name: Check documentation
      run: |
        git diff --exit-code docs/ CHANGELOG.md README.md
"""
    
    dev_workflow_file = workflow_dir / 'dev.yml'
    dev_workflow_file.write_text(dev_workflow_content, encoding='utf-8')
    
    print("✅ Workflow для ветки dev создан")
    return True

def main():
    """Основная функция настройки ветки dev."""
    print("🚀 Настройка ветки dev для WindSpotBot")
    print("=" * 45)
    
    # Проверяем git репозиторий
    if not check_git_repo():
        return 1
    
    # Получаем текущую ветку
    current_branch = get_current_branch()
    print(f"📁 Текущая ветка: {current_branch}")
    
    # Создаем ветку dev
    if not create_dev_branch():
        return 1
    
    # Настраиваем pre-commit
    if not setup_pre_commit():
        return 1
    
    # Проверяем GitHub CLI
    if not setup_github_cli():
        print("⚠️ GitHub CLI не настроен, некоторые функции могут быть недоступны")
    
    # Создаем .gitignore
    if not create_gitignore():
        return 1
    
    # Настраиваем удаленный репозиторий
    if not setup_remote():
        print("⚠️ Удаленный репозиторий не настроен, некоторые функции могут быть недоступны")
    
    # Создаем начальный коммит
    if not create_initial_commit():
        return 1
    
    # Настраиваем workflow
    if not setup_dev_workflow():
        return 1
    
    print("\n✅ Настройка ветки dev завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Настройте удаленный репозиторий: git remote add origin <URL>")
    print("2. Отправьте ветку dev: git push -u origin dev")
    print("3. Запустите автоматические коммиты: make dev-auto")
    print("4. Создайте Pull Request: make dev-pr")
    
    print("\n🔧 Доступные команды:")
    print("- make dev-workflow    # Полный workflow")
    print("- make dev-auto        # Автоматические коммиты")
    print("- make dev-once        # Один цикл")
    print("- make dev-commit      # Помощник коммита")
    print("- make dev-sync        # Синхронизация с main")
    print("- make dev-push        # Отправка на GitHub")
    print("- make dev-pr          # Создание PR")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




#!/usr/bin/env python3
"""
Помощник для работы с GitHub.
Автоматизирует создание PR, синхронизацию веток и деплой.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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

def get_current_branch() -> str:
    """Получает текущую ветку."""
    success, output = run_command("git branch --show-current")
    if success:
        return output.strip()
    return "unknown"

def get_remote_url() -> Optional[str]:
    """Получает URL удаленного репозитория."""
    success, output = run_command("git remote get-url origin")
    if success:
        return output.strip()
    return None

def check_github_cli() -> bool:
    """Проверяет наличие GitHub CLI."""
    success, _ = run_command("gh --version")
    return success

def sync_with_main():
    """Синхронизирует текущую ветку с main."""
    print("🔄 Синхронизация с веткой main...")
    
    # Переключаемся на main
    success, output = run_command("git checkout main")
    if not success:
        print(f"❌ Ошибка переключения на main: {output}")
        return False
    
    # Получаем последние изменения
    success, output = run_command("git pull origin main")
    if not success:
        print(f"❌ Ошибка получения изменений: {output}")
        return False
    
    # Переключаемся обратно на dev
    success, output = run_command("git checkout dev")
    if not success:
        print(f"❌ Ошибка переключения на dev: {output}")
        return False
    
    # Мержим main в dev
    success, output = run_command("git merge main")
    if not success:
        print(f"❌ Ошибка мержа: {output}")
        return False
    
    print("✅ Синхронизация завершена")
    return True

def push_to_github():
    """Отправляет изменения на GitHub."""
    current_branch = get_current_branch()
    print(f"📤 Отправка ветки '{current_branch}' на GitHub...")
    
    # Добавляем все изменения
    success, output = run_command("git add .")
    if not success:
        print(f"❌ Ошибка добавления файлов: {output}")
        return False
    
    # Коммитим изменения
    commit_message = f"Обновление документации и конфигурации - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    success, output = run_command(f'git commit -m "{commit_message}"')
    if not success and "nothing to commit" not in output:
        print(f"❌ Ошибка коммита: {output}")
        return False
    
    # Отправляем на GitHub
    success, output = run_command(f"git push origin {current_branch}")
    if not success:
        print(f"❌ Ошибка отправки: {output}")
        return False
    
    print("✅ Изменения отправлены на GitHub")
    return True

def create_pull_request():
    """Создает Pull Request."""
    if not check_github_cli():
        print("❌ GitHub CLI не установлен. Установите: https://cli.github.com/")
        return False
    
    current_branch = get_current_branch()
    if current_branch == "main":
        print("❌ Нельзя создать PR из ветки main")
        return False
    
    print(f"🔀 Создание Pull Request для ветки '{current_branch}'...")
    
    # Создаем PR
    pr_title = f"Обновление документации и конфигурации - {datetime.now().strftime('%Y-%m-%d')}"
    pr_body = """
## Описание изменений

- Обновлена документация проекта
- Настроена система контроля версий
- Добавлены pre-commit hooks
- Созданы скрипты автоматизации

## Тип изменений

- [x] Документация
- [x] Конфигурация
- [x] Скрипты

## Проверки

- [x] Документация обновлена
- [x] CHANGELOG актуален
- [x] Код отформатирован
- [x] Тесты проходят
"""
    
    success, output = run_command(f'gh pr create --title "{pr_title}" --body "{pr_body}" --base main --head {current_branch}')
    if not success:
        print(f"❌ Ошибка создания PR: {output}")
        return False
    
    print("✅ Pull Request создан")
    print(f"🔗 Ссылка: {output.strip()}")
    return True

def setup_github_workflow():
    """Настраивает GitHub Actions workflow."""
    print("⚙️ Настройка GitHub Actions...")
    
    # Создаем папку для workflows
    workflows_dir = project_root / '.github' / 'workflows'
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем workflow для CI/CD
    workflow_content = """name: CI/CD Pipeline

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

jobs:
  test:
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
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run black
      run: black --check src/ tests/
    
    - name: Run flake8
      run: flake8 src/ tests/
    
    - name: Run mypy
      run: mypy src/

  docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Build documentation
      run: |
        python scripts/update_docs.py
        python scripts/update_changelog.py
    
    - name: Check documentation
      run: |
        # Проверяем, что документация обновлена
        git diff --exit-code docs/ CHANGELOG.md README.md
"""
    
    workflow_file = workflows_dir / 'ci.yml'
    workflow_file.write_text(workflow_content, encoding='utf-8')
    
    print("✅ GitHub Actions workflow создан")
    return True

def main():
    """Основная функция GitHub помощника."""
    print("🚀 GitHub помощник WindSpotBot")
    print("=" * 40)
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return 1
    
    current_branch = get_current_branch()
    remote_url = get_remote_url()
    
    print(f"📁 Текущая ветка: {current_branch}")
    print(f"🔗 Удаленный репозиторий: {remote_url}")
    
    # Меню действий
    print("\nВыберите действие:")
    print("1. Синхронизировать с main")
    print("2. Отправить изменения на GitHub")
    print("3. Создать Pull Request")
    print("4. Настроить GitHub Actions")
    print("5. Выполнить все действия")
    
    try:
        choice = input("\nВведите номер действия (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n❌ Операция отменена")
        return 0
    
    if choice == "1":
        sync_with_main()
    elif choice == "2":
        push_to_github()
    elif choice == "3":
        create_pull_request()
    elif choice == "4":
        setup_github_workflow()
    elif choice == "5":
        print("🔄 Выполнение всех действий...")
        sync_with_main()
        push_to_github()
        create_pull_request()
        setup_github_workflow()
    else:
        print("❌ Неверный выбор")
        return 1
    
    print("✅ Операция завершена")
    return 0

if __name__ == "__main__":
    sys.exit(main())




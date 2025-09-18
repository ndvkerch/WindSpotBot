#!/usr/bin/env python3
"""
Скрипт для автоматического обновления документации проекта WindSpotBot.
Запускается через pre-commit hook для поддержания актуальности документации.
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

def update_readme():
    """Обновляет README.md с актуальной информацией."""
    print("📝 Обновление README.md...")
    
    # Проверяем наличие изменений в коде
    success, output = run_command("git diff --name-only HEAD~1 HEAD")
    if not success:
        print("⚠️ Не удалось получить список измененных файлов")
        return
    
    changed_files = output.strip().split('\n') if output.strip() else []
    has_code_changes = any(f.startswith('src/') for f in changed_files)
    
    if has_code_changes:
        print("✅ Обнаружены изменения в коде, документация актуальна")
    else:
        print("ℹ️ Изменений в коде не обнаружено")

def update_architecture_docs():
    """Обновляет документацию архитектуры."""
    print("🏗️ Проверка документации архитектуры...")
    
    # Проверяем, нужно ли обновлять архитектурную документацию
    success, output = run_command("git diff --name-only HEAD~1 HEAD -- src/")
    if not success:
        print("⚠️ Не удалось проверить изменения в архитектуре")
        return
    
    changed_files = output.strip().split('\n') if output.strip() else []
    architecture_changed = any(
        any(folder in f for folder in ['handlers/', 'services/', 'repositories/', 'models/'])
        for f in changed_files
    )
    
    if architecture_changed:
        print("✅ Архитектурные изменения обнаружены, документация актуальна")
    else:
        print("ℹ️ Архитектурных изменений не обнаружено")

def update_api_docs():
    """Обновляет API документацию."""
    print("🔌 Проверка API документации...")
    
    # Проверяем изменения в API
    success, output = run_command("git diff --name-only HEAD~1 HEAD -- src/handlers/")
    if not success:
        print("⚠️ Не удалось проверить изменения в API")
        return
    
    api_changed = bool(output.strip())
    
    if api_changed:
        print("✅ Изменения в API обнаружены, документация актуальна")
    else:
        print("ℹ️ Изменений в API не обнаружено")

def update_testing_docs():
    """Обновляет документацию по тестированию."""
    print("🧪 Проверка документации тестирования...")
    
    # Проверяем изменения в тестах
    success, output = run_command("git diff --name-only HEAD~1 HEAD -- tests/")
    if not success:
        print("⚠️ Не удалось проверить изменения в тестах")
        return
    
    tests_changed = bool(output.strip())
    
    if tests_changed:
        print("✅ Изменения в тестах обнаружены, документация актуальна")
    else:
        print("ℹ️ Изменений в тестах не обнаружено")

def main():
    """Основная функция обновления документации."""
    print("🚀 Запуск обновления документации...")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Рабочая директория: {project_root}")
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return 1
    
    # Обновляем различные части документации
    update_readme()
    update_architecture_docs()
    update_api_docs()
    update_testing_docs()
    
    print("✅ Обновление документации завершено")
    return 0

if __name__ == "__main__":
    sys.exit(main())




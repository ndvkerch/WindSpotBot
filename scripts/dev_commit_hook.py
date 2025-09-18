#!/usr/bin/env python3
"""
Git hook для автоматических коммитов в ветке dev.
Запускается при каждом коммите и обновляет документацию.
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

def get_current_branch() -> str:
    """Получает текущую ветку."""
    success, output = run_command("git branch --show-current")
    if success:
        return output.strip()
    return "unknown"

def is_dev_branch() -> bool:
    """Проверяет, что мы в ветке dev."""
    current_branch = get_current_branch()
    return current_branch == "dev"

def update_documentation():
    """Обновляет документацию."""
    print("📚 Обновление документации...")
    
    # Обновляем документацию
    success, output = run_command("python scripts/update_docs.py")
    if not success:
        print(f"⚠️ Ошибка обновления документации: {output}")
        return False
    
    # Обновляем CHANGELOG
    success, output = run_command("python scripts/update_changelog.py")
    if not success:
        print(f"⚠️ Ошибка обновления CHANGELOG: {output}")
        return False
    
    print("✅ Документация обновлена")
    return True

def format_code():
    """Форматирует код."""
    print("🎨 Форматирование кода...")
    
    success, output = run_command("black src/ tests/ --line-length=88 --target-version=py311")
    if not success:
        print(f"⚠️ Ошибка форматирования: {output}")
        return False
    
    print("✅ Код отформатирован")
    return True

def run_tests() -> bool:
    """Запускает тесты."""
    print("🧪 Запуск тестов...")
    
    success, output = run_command("python -m pytest tests/ -v --maxfail=1")
    if not success:
        print(f"⚠️ Тесты не прошли: {output}")
        return False
    
    print("✅ Тесты прошли успешно")
    return True

def check_changes() -> bool:
    """Проверяет, есть ли изменения для коммита."""
    success, output = run_command("git diff --cached --quiet")
    return not success  # Если есть изменения, команда вернет False

def add_changes():
    """Добавляет изменения в индекс."""
    print("📝 Добавление изменений в индекс...")
    
    success, output = run_command("git add .")
    if not success:
        print(f"❌ Ошибка добавления файлов: {output}")
        return False
    
    print("✅ Изменения добавлены в индекс")
    return True

def main():
    """Основная функция hook."""
    print("🪝 Git hook для ветки dev")
    print("=" * 30)
    
    # Проверяем, что мы в ветке dev
    if not is_dev_branch():
        print("ℹ️ Не в ветке dev, hook пропущен")
        return 0
    
    print(f"📁 Ветка: {get_current_branch()}")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверяем, есть ли изменения
    if not check_changes():
        print("ℹ️ Нет изменений для коммита")
        return 0
    
    # Обновляем документацию
    if not update_documentation():
        print("⚠️ Ошибка обновления документации")
    
    # Форматируем код
    if not format_code():
        print("⚠️ Ошибка форматирования кода")
    
    # Запускаем тесты
    if not run_tests():
        print("❌ Тесты не прошли, коммит отменен")
        return 1
    
    # Добавляем изменения
    if not add_changes():
        return 1
    
    print("✅ Hook выполнен успешно")
    return 0

if __name__ == "__main__":
    sys.exit(main())




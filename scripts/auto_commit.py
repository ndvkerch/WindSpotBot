#!/usr/bin/env python3
"""
Автоматический коммит с обновлением документации.
Используется для автоматизации процесса коммитов.
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional

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

def get_changed_files() -> List[str]:
    """Получает список измененных файлов."""
    success, output = run_command("git status --porcelain")
    if not success:
        return []
    
    files = []
    for line in output.strip().split('\n'):
        if line.strip():
            # Убираем статус файла (M, A, D, etc.)
            file_path = line[3:].strip()
            files.append(file_path)
    
    return files

def analyze_changes(files: List[str]) -> dict:
    """Анализирует изменения и определяет тип коммита."""
    changes = {
        'has_code': False,
        'has_docs': False,
        'has_tests': False,
        'has_config': False,
        'has_scripts': False
    }
    
    for file_path in files:
        if file_path.startswith('src/'):
            changes['has_code'] = True
        elif file_path.startswith('docs/') or file_path in ['README.md', 'CHANGELOG.md']:
            changes['has_docs'] = True
        elif file_path.startswith('tests/'):
            changes['has_tests'] = True
        elif file_path.startswith('.') or file_path in ['requirements.txt', 'pyproject.toml', 'Makefile']:
            changes['has_config'] = True
        elif file_path.startswith('scripts/'):
            changes['has_scripts'] = True
    
    return changes

def generate_commit_message(changes: dict, custom_message: Optional[str] = None) -> str:
    """Генерирует сообщение коммита."""
    if custom_message:
        return custom_message
    
    # Определяем тип коммита
    if changes['has_code'] and changes['has_docs']:
        return "Обновление кода и документации"
    elif changes['has_code']:
        return "Обновление кода"
    elif changes['has_docs']:
        return "Обновление документации"
    elif changes['has_tests']:
        return "Обновление тестов"
    elif changes['has_config']:
        return "Обновление конфигурации"
    elif changes['has_scripts']:
        return "Обновление скриптов"
    else:
        return f"Обновление проекта - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

def update_documentation():
    """Обновляет документацию."""
    print("📚 Обновление документации...")
    
    # Обновляем документацию
    success, output = run_command("python scripts/update_docs.py")
    if not success:
        print(f"⚠️ Ошибка обновления документации: {output}")
    
    # Обновляем CHANGELOG
    success, output = run_command("python scripts/update_changelog.py")
    if not success:
        print(f"⚠️ Ошибка обновления CHANGELOG: {output}")

def format_code():
    """Форматирует код."""
    print("🎨 Форматирование кода...")
    
    success, output = run_command("black src/ tests/ --line-length=88 --target-version=py311")
    if not success:
        print(f"⚠️ Ошибка форматирования: {output}")

def run_tests():
    """Запускает тесты."""
    print("🧪 Запуск тестов...")
    
    success, output = run_command("python -m pytest tests/ -v --maxfail=1")
    if not success:
        print(f"⚠️ Тесты не прошли: {output}")
        return False
    
    return True

def create_commit(message: str, skip_tests: bool = False):
    """Создает коммит."""
    print(f"💾 Создание коммита: {message}")
    
    # Добавляем все изменения
    success, output = run_command("git add .")
    if not success:
        print(f"❌ Ошибка добавления файлов: {output}")
        return False
    
    # Проверяем, есть ли что коммитить
    success, output = run_command("git diff --cached --quiet")
    if success:
        print("ℹ️ Нет изменений для коммита")
        return True
    
    # Создаем коммит
    success, output = run_command(f'git commit -m "{message}"')
    if not success:
        print(f"❌ Ошибка создания коммита: {output}")
        return False
    
    print("✅ Коммит создан")
    return True

def push_changes():
    """Отправляет изменения на GitHub."""
    print("📤 Отправка изменений на GitHub...")
    
    current_branch = run_command("git branch --show-current")[1].strip()
    success, output = run_command(f"git push origin {current_branch}")
    if not success:
        print(f"❌ Ошибка отправки: {output}")
        return False
    
    print("✅ Изменения отправлены")
    return True

def main():
    """Основная функция автоматического коммита."""
    parser = argparse.ArgumentParser(description="Автоматический коммит с обновлением документации")
    parser.add_argument("-m", "--message", help="Сообщение коммита")
    parser.add_argument("--skip-tests", action="store_true", help="Пропустить тесты")
    parser.add_argument("--skip-docs", action="store_true", help="Пропустить обновление документации")
    parser.add_argument("--skip-format", action="store_true", help="Пропустить форматирование")
    parser.add_argument("--push", action="store_true", help="Отправить изменения на GitHub")
    parser.add_argument("--dry-run", action="store_true", help="Показать что будет сделано без выполнения")
    
    args = parser.parse_args()
    
    print("🚀 Автоматический коммит WindSpotBot")
    print("=" * 40)
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return 1
    
    # Получаем измененные файлы
    changed_files = get_changed_files()
    if not changed_files:
        print("ℹ️ Нет изменений для коммита")
        return 0
    
    print(f"📁 Измененные файлы ({len(changed_files)}):")
    for file_path in changed_files:
        print(f"  - {file_path}")
    
    # Анализируем изменения
    changes = analyze_changes(changed_files)
    
    # Генерируем сообщение коммита
    commit_message = generate_commit_message(changes, args.message)
    print(f"💬 Сообщение коммита: {commit_message}")
    
    if args.dry_run:
        print("🔍 Режим предварительного просмотра:")
        print("  - Обновление документации: " + ("Да" if not args.skip_docs else "Нет"))
        print("  - Форматирование кода: " + ("Да" if not args.skip_format else "Нет"))
        print("  - Запуск тестов: " + ("Нет" if args.skip_tests else "Да"))
        print("  - Создание коммита: Да")
        print("  - Отправка на GitHub: " + ("Да" if args.push else "Нет"))
        return 0
    
    # Обновляем документацию
    if not args.skip_docs:
        update_documentation()
    
    # Форматируем код
    if not args.skip_format:
        format_code()
    
    # Запускаем тесты
    if not args.skip_tests:
        if not run_tests():
            print("❌ Тесты не прошли, коммит отменен")
            return 1
    
    # Создаем коммит
    if not create_commit(commit_message, args.skip_tests):
        return 1
    
    # Отправляем изменения
    if args.push:
        if not push_changes():
            return 1
    
    print("✅ Автоматический коммит завершен")
    return 0

if __name__ == "__main__":
    sys.exit(main())




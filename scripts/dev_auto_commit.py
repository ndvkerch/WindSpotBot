#!/usr/bin/env python3
"""
Автоматические коммиты для ветки dev.
Мониторит изменения и автоматически создает коммиты с обновлением документации.
"""

import os
import sys
import subprocess
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Set

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

def get_changed_files() -> List[str]:
    """Получает список измененных файлов."""
    success, output = run_command("git status --porcelain")
    if not success:
        return []
    
    files = []
    for line in output.strip().split('\n'):
        if line.strip():
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
        'has_scripts': False,
        'code_files': [],
        'doc_files': [],
        'test_files': [],
        'config_files': [],
        'script_files': []
    }
    
    for file_path in files:
        if file_path.startswith('src/'):
            changes['has_code'] = True
            changes['code_files'].append(file_path)
        elif file_path.startswith('docs/') or file_path in ['README.md', 'CHANGELOG.md']:
            changes['has_docs'] = True
            changes['doc_files'].append(file_path)
        elif file_path.startswith('tests/'):
            changes['has_tests'] = True
            changes['test_files'].append(file_path)
        elif file_path.startswith('.') or file_path in ['requirements.txt', 'pyproject.toml', 'Makefile']:
            changes['has_config'] = True
            changes['config_files'].append(file_path)
        elif file_path.startswith('scripts/'):
            changes['has_scripts'] = True
            changes['script_files'].append(file_path)
    
    return changes

def generate_commit_message(changes: dict) -> str:
    """Генерирует сообщение коммита на основе изменений."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Определяем основной тип изменений
    if changes['has_code'] and changes['has_docs']:
        return f"Обновление кода и документации - {timestamp}"
    elif changes['has_code']:
        return f"Обновление кода - {timestamp}"
    elif changes['has_docs']:
        return f"Обновление документации - {timestamp}"
    elif changes['has_tests']:
        return f"Обновление тестов - {timestamp}"
    elif changes['has_config']:
        return f"Обновление конфигурации - {timestamp}"
    elif changes['has_scripts']:
        return f"Обновление скриптов - {timestamp}"
    else:
        return f"Обновление проекта - {timestamp}"

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

def create_commit(message: str) -> bool:
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

def push_changes() -> bool:
    """Отправляет изменения на GitHub."""
    current_branch = get_current_branch()
    print(f"📤 Отправка ветки '{current_branch}' на GitHub...")
    
    success, output = run_command(f"git push origin {current_branch}")
    if not success:
        print(f"❌ Ошибка отправки: {output}")
        return False
    
    print("✅ Изменения отправлены на GitHub")
    return True

def monitor_changes(interval: int = 30, auto_commit: bool = True, auto_push: bool = False):
    """Мониторит изменения и автоматически создает коммиты."""
    print("👀 Мониторинг изменений в ветке dev")
    print("=" * 40)
    print(f"⏱️ Интервал проверки: {interval} секунд")
    print(f"💾 Автокоммит: {'Включен' if auto_commit else 'Отключен'}")
    print(f"📤 Автоотправка: {'Включена' if auto_push else 'Отключена'}")
    print("Нажмите Ctrl+C для остановки")
    print()
    
    last_commit_time = datetime.now()
    processed_files: Set[str] = set()
    
    try:
        while True:
            # Получаем измененные файлы
            changed_files = get_changed_files()
            
            if changed_files:
                # Фильтруем уже обработанные файлы
                new_files = [f for f in changed_files if f not in processed_files]
                
                if new_files:
                    print(f"📁 Обнаружены изменения ({len(new_files)} файлов):")
                    for file_path in new_files:
                        print(f"  - {file_path}")
                    
                    # Анализируем изменения
                    changes = analyze_changes(new_files)
                    
                    # Обновляем документацию
                    if changes['has_code'] or changes['has_docs']:
                        update_documentation()
                    
                    # Форматируем код
                    if changes['has_code']:
                        format_code()
                    
                    # Запускаем тесты
                    if changes['has_code'] or changes['has_tests']:
                        if not run_tests():
                            print("❌ Тесты не прошли, коммит отменен")
                            time.sleep(interval)
                            continue
                    
                    # Создаем коммит
                    if auto_commit:
                        message = generate_commit_message(changes)
                        if create_commit(message):
                            # Отправляем на GitHub
                            if auto_push:
                                push_changes()
                            
                            # Обновляем время последнего коммита
                            last_commit_time = datetime.now()
                            
                            # Добавляем файлы в обработанные
                            processed_files.update(new_files)
                            
                            print(f"✅ Изменения обработаны: {message}")
                        else:
                            print("❌ Ошибка создания коммита")
                    else:
                        print("ℹ️ Автокоммит отключен, изменения не закоммичены")
                
                # Очищаем старые файлы из обработанных (старше 1 часа)
                current_time = datetime.now()
                if (current_time - last_commit_time).seconds > 3600:
                    processed_files.clear()
                    last_commit_time = current_time
            else:
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Изменений не обнаружено")
            
            # Ждем следующий интервал
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n🛑 Мониторинг остановлен")
        return True

def main():
    """Основная функция автоматических коммитов."""
    parser = argparse.ArgumentParser(description="Автоматические коммиты для ветки dev")
    parser.add_argument("--interval", type=int, default=30, help="Интервал проверки в секундах (по умолчанию: 30)")
    parser.add_argument("--no-commit", action="store_true", help="Не создавать коммиты автоматически")
    parser.add_argument("--auto-push", action="store_true", help="Автоматически отправлять на GitHub")
    parser.add_argument("--once", action="store_true", help="Выполнить один раз и выйти")
    
    args = parser.parse_args()
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return 1
    
    # Проверяем, что мы в ветке dev
    current_branch = get_current_branch()
    if current_branch != "dev":
        print(f"⚠️ Текущая ветка: {current_branch}")
        print("ℹ️ Рекомендуется использовать в ветке dev")
    
    # Выполняем один раз
    if args.once:
        print("🔄 Выполнение одного цикла...")
        
        changed_files = get_changed_files()
        if not changed_files:
            print("ℹ️ Нет изменений для обработки")
            return 0
        
        changes = analyze_changes(changed_files)
        
        # Обновляем документацию
        if changes['has_code'] or changes['has_docs']:
            update_documentation()
        
        # Форматируем код
        if changes['has_code']:
            format_code()
        
        # Запускаем тесты
        if changes['has_code'] or changes['has_tests']:
            if not run_tests():
                print("❌ Тесты не прошли")
                return 1
        
        # Создаем коммит
        if not args.no_commit:
            message = generate_commit_message(changes)
            if create_commit(message):
                if args.auto_push:
                    push_changes()
                print("✅ Цикл выполнен успешно")
            else:
                print("❌ Ошибка создания коммита")
                return 1
        else:
            print("ℹ️ Коммит пропущен (--no-commit)")
        
        return 0
    
    # Запускаем мониторинг
    return 0 if monitor_changes(
        interval=args.interval,
        auto_commit=not args.no_commit,
        auto_push=args.auto_push
    ) else 1

if __name__ == "__main__":
    sys.exit(main())




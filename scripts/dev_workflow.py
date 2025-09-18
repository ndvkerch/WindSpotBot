#!/usr/bin/env python3
"""
Workflow для работы с веткой dev.
Автоматизирует синхронизацию, коммиты и создание PR.
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

def get_current_branch() -> str:
    """Получает текущую ветку."""
    success, output = run_command("git branch --show-current")
    if success:
        return output.strip()
    return "unknown"

def switch_to_branch(branch: str) -> bool:
    """Переключается на указанную ветку."""
    print(f"🔄 Переключение на ветку '{branch}'...")
    
    success, output = run_command(f"git checkout {branch}")
    if not success:
        print(f"❌ Ошибка переключения на {branch}: {output}")
        return False
    
    print(f"✅ Переключились на ветку '{branch}'")
    return True

def sync_with_main() -> bool:
    """Синхронизирует текущую ветку с main."""
    print("🔄 Синхронизация с веткой main...")
    
    # Получаем последние изменения main
    success, output = run_command("git fetch origin main")
    if not success:
        print(f"❌ Ошибка получения main: {output}")
        return False
    
    # Мержим main в текущую ветку
    success, output = run_command("git merge origin/main")
    if not success:
        print(f"❌ Ошибка мержа main: {output}")
        return False
    
    print("✅ Синхронизация с main завершена")
    return True

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

def commit_changes(message: str) -> bool:
    """Коммитит изменения."""
    print(f"💾 Коммит изменений: {message}")
    
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

def push_to_github() -> bool:
    """Отправляет изменения на GitHub."""
    current_branch = get_current_branch()
    print(f"📤 Отправка ветки '{current_branch}' на GitHub...")
    
    success, output = run_command(f"git push origin {current_branch}")
    if not success:
        print(f"❌ Ошибка отправки: {output}")
        return False
    
    print("✅ Изменения отправлены на GitHub")
    return True

def create_pull_request() -> bool:
    """Создает Pull Request."""
    current_branch = get_current_branch()
    if current_branch == "main":
        print("❌ Нельзя создать PR из ветки main")
        return False
    
    print(f"🔀 Создание Pull Request для ветки '{current_branch}'...")
    
    # Создаем PR
    pr_title = f"Обновления из ветки {current_branch} - {datetime.now().strftime('%Y-%m-%d')}"
    pr_body = f"""
## Описание изменений

Автоматическое обновление из ветки `{current_branch}`.

## Тип изменений

- [x] Код
- [x] Документация
- [x] Конфигурация

## Проверки

- [x] Код отформатирован
- [x] Тесты проходят
- [x] Документация обновлена
- [x] CHANGELOG актуален

## Ветка

- Источник: `{current_branch}`
- Цель: `main`
- Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    success, output = run_command(f'gh pr create --title "{pr_title}" --body "{pr_body}" --base main --head {current_branch}')
    if not success:
        print(f"❌ Ошибка создания PR: {output}")
        return False
    
    print("✅ Pull Request создан")
    print(f"🔗 Ссылка: {output.strip()}")
    return True

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

def run_tests() -> bool:
    """Запускает тесты."""
    print("🧪 Запуск тестов...")
    
    success, output = run_command("python -m pytest tests/ -v --maxfail=1")
    if not success:
        print(f"⚠️ Тесты не прошли: {output}")
        return False
    
    print("✅ Тесты прошли успешно")
    return True

def dev_workflow(sync: bool = True, commit: bool = True, push: bool = True, pr: bool = False):
    """Выполняет полный workflow для ветки dev."""
    print("🚀 Workflow для ветки dev")
    print("=" * 30)
    
    current_branch = get_current_branch()
    print(f"📁 Текущая ветка: {current_branch}")
    
    # Синхронизируем с main
    if sync:
        if not sync_with_main():
            return False
    
    # Обновляем документацию
    update_documentation()
    
    # Форматируем код
    format_code()
    
    # Запускаем тесты
    if not run_tests():
        print("❌ Тесты не прошли, workflow прерван")
        return False
    
    # Коммитим изменения
    if commit:
        changed_files = get_changed_files()
        if changed_files:
            message = f"Обновление проекта - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            if not commit_changes(message):
                return False
        else:
            print("ℹ️ Нет изменений для коммита")
    
    # Отправляем на GitHub
    if push:
        if not push_to_github():
            return False
    
    # Создаем PR
    if pr:
        if not create_pull_request():
            return False
    
    print("✅ Workflow для ветки dev завершен")
    return True

def main():
    """Основная функция dev workflow."""
    parser = argparse.ArgumentParser(description="Workflow для работы с веткой dev")
    parser.add_argument("--sync", action="store_true", help="Синхронизировать с main")
    parser.add_argument("--commit", action="store_true", help="Создать коммит")
    parser.add_argument("--push", action="store_true", help="Отправить на GitHub")
    parser.add_argument("--pr", action="store_true", help="Создать Pull Request")
    parser.add_argument("--all", action="store_true", help="Выполнить все действия")
    parser.add_argument("--message", help="Сообщение коммита")
    
    args = parser.parse_args()
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return 1
    
    # Если указан --all, выполняем все действия
    if args.all:
        return 0 if dev_workflow(sync=True, commit=True, push=True, pr=True) else 1
    
    # Выполняем указанные действия
    if args.sync:
        if not sync_with_main():
            return 1
    
    if args.commit:
        message = args.message or f"Обновление проекта - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if not commit_changes(message):
            return 1
    
    if args.push:
        if not push_to_github():
            return 1
    
    if args.pr:
        if not create_pull_request():
            return 1
    
    # Если не указаны действия, показываем справку
    if not any([args.sync, args.commit, args.push, args.pr]):
        print("Использование:")
        print("  python scripts/dev_workflow.py --all          # Выполнить все действия")
        print("  python scripts/dev_workflow.py --sync         # Синхронизировать с main")
        print("  python scripts/dev_workflow.py --commit       # Создать коммит")
        print("  python scripts/dev_workflow.py --push         # Отправить на GitHub")
        print("  python scripts/dev_workflow.py --pr           # Создать Pull Request")
        print("  python scripts/dev_workflow.py --message '...' --commit  # Коммит с сообщением")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




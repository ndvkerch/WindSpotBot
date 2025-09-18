#!/usr/bin/env python3
"""
Скрипт для автоматического обновления CHANGELOG.md.
Анализирует коммиты и обновляет файл изменений.
"""

import os
import sys
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

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

def get_commit_messages() -> List[Dict[str, str]]:
    """Получает сообщения коммитов с последнего тега."""
    # Получаем последний тег
    success, output = run_command("git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'")
    if not success:
        last_tag = "v0.0.0"
    else:
        last_tag = output.strip()
    
    # Получаем коммиты после последнего тега
    success, output = run_command(f"git log {last_tag}..HEAD --oneline --no-merges")
    if not success:
        return []
    
    commits = []
    for line in output.strip().split('\n'):
        if line.strip():
            # Парсим коммит: hash message
            parts = line.split(' ', 1)
            if len(parts) == 2:
                commits.append({
                    'hash': parts[0],
                    'message': parts[1]
                })
    
    return commits

def categorize_commit(message: str) -> str:
    """Категоризирует коммит по типу изменений."""
    message_lower = message.lower()
    
    # Новые функции
    if any(keyword in message_lower for keyword in ['добавлен', 'новая функция', 'новый', 'feat', 'feature']):
        return 'Добавлено'
    
    # Исправления
    if any(keyword in message_lower for keyword in ['исправлен', 'исправление', 'баг', 'fix', 'bug']):
        return 'Исправлено'
    
    # Изменения
    if any(keyword in message_lower for keyword in ['изменен', 'обновлен', 'улучшен', 'refactor', 'update']):
        return 'Изменено'
    
    # Документация
    if any(keyword in message_lower for keyword in ['документация', 'docs', 'readme', 'changelog']):
        return 'Документация'
    
    # Тесты
    if any(keyword in message_lower for keyword in ['тест', 'test', 'покрытие']):
        return 'Тесты'
    
    # Конфигурация
    if any(keyword in message_lower for keyword in ['конфиг', 'config', 'настройка', 'setup']):
        return 'Конфигурация'
    
    # По умолчанию
    return 'Прочее'

def format_commit_message(message: str) -> str:
    """Форматирует сообщение коммита для CHANGELOG."""
    # Убираем префиксы типа "feat:", "fix:" и т.д.
    message = re.sub(r'^(feat|fix|docs|style|refactor|test|chore):\s*', '', message, flags=re.IGNORECASE)
    
    # Делаем первую букву заглавной
    if message:
        message = message[0].upper() + message[1:]
    
    return message

def update_changelog():
    """Обновляет CHANGELOG.md."""
    print("📝 Обновление CHANGELOG.md...")
    
    commits = get_commit_messages()
    if not commits:
        print("ℹ️ Новых коммитов не найдено")
        return
    
    # Группируем коммиты по категориям
    categorized = {}
    for commit in commits:
        category = categorize_commit(commit['message'])
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(commit)
    
    # Читаем существующий CHANGELOG
    changelog_path = project_root / 'CHANGELOG.md'
    existing_content = ""
    if changelog_path.exists():
        existing_content = changelog_path.read_text(encoding='utf-8')
    
    # Создаем новую запись
    today = datetime.now().strftime('%Y-%m-%d')
    new_entry = f"## [Unreleased] - {today}\n\n"
    
    # Добавляем изменения по категориям
    for category in ['Добавлено', 'Исправлено', 'Изменено', 'Документация', 'Тесты', 'Конфигурация', 'Прочее']:
        if category in categorized:
            new_entry += f"### {category}\n\n"
            for commit in categorized[category]:
                formatted_message = format_commit_message(commit['message'])
                new_entry += f"- {formatted_message}\n"
            new_entry += "\n"
    
    # Вставляем новую запись в начало файла
    if "## [Unreleased]" in existing_content:
        # Заменяем существующую секцию Unreleased
        pattern = r'## \[Unreleased\].*?(?=## \[|\Z)'
        new_content = re.sub(pattern, new_entry.strip() + '\n\n', existing_content, flags=re.DOTALL)
    else:
        # Добавляем в начало файла
        if existing_content.strip():
            new_content = new_entry + "\n" + existing_content
        else:
            new_content = new_entry + "\n"
    
    # Записываем обновленный файл
    changelog_path.write_text(new_content, encoding='utf-8')
    
    print(f"✅ CHANGELOG.md обновлен с {len(commits)} коммитами")
    for category, items in categorized.items():
        if items:
            print(f"  - {category}: {len(items)} изменений")

def main():
    """Основная функция обновления CHANGELOG."""
    print("🚀 Запуск обновления CHANGELOG...")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Рабочая директория: {project_root}")
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return 1
    
    update_changelog()
    
    print("✅ Обновление CHANGELOG завершено")
    return 0

if __name__ == "__main__":
    sys.exit(main())




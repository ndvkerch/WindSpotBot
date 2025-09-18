#!/usr/bin/env python3
"""
Помощник для создания коммитов на русском языке.
Предлагает типы коммитов и помогает сформулировать сообщение.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict

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

def analyze_changes(files: List[str]) -> Dict[str, List[str]]:
    """Анализирует изменения и группирует файлы по типам."""
    changes = {
        'features': [],
        'fixes': [],
        'docs': [],
        'tests': [],
        'config': [],
        'other': []
    }
    
    for file_path in files:
        if file_path.startswith('src/handlers/') or file_path.startswith('src/services/'):
            changes['features'].append(file_path)
        elif file_path.startswith('tests/'):
            changes['tests'].append(file_path)
        elif file_path.startswith('docs/') or file_path in ['README.md', 'CHANGELOG.md']:
            changes['docs'].append(file_path)
        elif file_path.startswith('.') or file_path in ['requirements.txt', 'pyproject.toml']:
            changes['config'].append(file_path)
        else:
            changes['other'].append(file_path)
    
    return changes

def suggest_commit_type(changes: Dict[str, List[str]]) -> str:
    """Предлагает тип коммита на основе изменений."""
    if changes['features']:
        return "feat"
    elif changes['fixes']:
        return "fix"
    elif changes['docs']:
        return "docs"
    elif changes['tests']:
        return "test"
    elif changes['config']:
        return "chore"
    else:
        return "refactor"

def get_commit_templates() -> Dict[str, List[str]]:
    """Возвращает шаблоны сообщений коммитов."""
    return {
        "feat": [
            "Добавлена новая функция: {description}",
            "Реализован {feature}: {description}",
            "Добавлена поддержка {feature}",
            "Новая возможность: {description}"
        ],
        "fix": [
            "Исправлена ошибка: {description}",
            "Исправлен баг в {component}: {description}",
            "Устранена проблема с {feature}",
            "Исправление: {description}"
        ],
        "docs": [
            "Обновлена документация: {description}",
            "Добавлена документация для {component}",
            "Улучшена документация: {description}",
            "Обновлен {doc_type}: {description}"
        ],
        "test": [
            "Добавлены тесты для {component}",
            "Улучшено покрытие тестами: {description}",
            "Исправлены тесты: {description}",
            "Добавлен тест: {description}"
        ],
        "chore": [
            "Обновлена конфигурация: {description}",
            "Настройка {tool}: {description}",
            "Обновлены зависимости: {description}",
            "Рефакторинг конфигурации: {description}"
        ],
        "refactor": [
            "Рефакторинг {component}: {description}",
            "Улучшена структура {component}",
            "Оптимизация {feature}: {description}",
            "Переработка {component}: {description}"
        ]
    }

def create_commit_message(commit_type: str, description: str) -> str:
    """Создает сообщение коммита."""
    templates = get_commit_templates()
    if commit_type in templates:
        template = templates[commit_type][0]  # Используем первый шаблон
        return template.format(description=description)
    else:
        return description

def main():
    """Основная функция помощника коммитов."""
    print("🚀 Помощник создания коммитов WindSpotBot")
    print("=" * 50)
    
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
    suggested_type = suggest_commit_type(changes)
    
    print(f"\n🎯 Предлагаемый тип коммита: {suggested_type}")
    
    # Показываем шаблоны
    templates = get_commit_templates()
    if suggested_type in templates:
        print(f"\n📝 Шаблоны для типа '{suggested_type}':")
        for i, template in enumerate(templates[suggested_type], 1):
            print(f"  {i}. {template}")
    
    print(f"\n💡 Пример использования:")
    print(f"git commit -m \"{create_commit_message(suggested_type, 'описание изменений')}\"")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




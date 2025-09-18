#!/usr/bin/env python3
"""
Установка Git hooks для автоматических коммитов.
Настраивает hooks для ветки dev.
"""

import os
import sys
import subprocess
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

def install_pre_commit_hook():
    """Устанавливает pre-commit hook."""
    print("🪝 Установка pre-commit hook...")
    
    # Создаем папку для hooks
    hooks_dir = project_root / '.git' / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    # Создаем pre-commit hook
    pre_commit_hook = hooks_dir / 'pre-commit'
    pre_commit_content = """#!/bin/bash
# Pre-commit hook для WindSpotBot

echo "🪝 Pre-commit hook запущен"

# Проверяем, что мы в ветке dev
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "dev" ]; then
    echo "📁 Ветка: dev"
    
    # Запускаем скрипт обновления документации
    python scripts/dev_commit_hook.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Pre-commit hook завершился с ошибкой"
        exit 1
    fi
    
    echo "✅ Pre-commit hook выполнен успешно"
else
    echo "ℹ️ Не в ветке dev, hook пропущен"
fi
"""
    
    pre_commit_hook.write_text(pre_commit_content, encoding='utf-8')
    
    # Делаем файл исполняемым
    if os.name != 'nt':  # Не Windows
        os.chmod(pre_commit_hook, 0o755)
    
    print("✅ Pre-commit hook установлен")
    return True

def install_commit_msg_hook():
    """Устанавливает commit-msg hook."""
    print("💬 Установка commit-msg hook...")
    
    # Создаем папку для hooks
    hooks_dir = project_root / '.git' / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    # Создаем commit-msg hook
    commit_msg_hook = hooks_dir / 'commit-msg'
    commit_msg_content = """#!/bin/bash
# Commit-msg hook для WindSpotBot

echo "💬 Commit-msg hook запущен"

# Проверяем, что мы в ветке dev
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "dev" ]; then
    echo "📁 Ветка: dev"
    
    # Проверяем сообщение коммита
    COMMIT_MSG=$(cat "$1")
    
    # Проверяем, что сообщение на русском языке
    if [[ "$COMMIT_MSG" =~ [а-яё] ]]; then
        echo "✅ Сообщение коммита на русском языке"
    else
        echo "⚠️ Сообщение коммита не на русском языке"
        echo "Рекомендуется использовать русский язык для коммитов в ветке dev"
    fi
    
    echo "✅ Commit-msg hook выполнен"
else
    echo "ℹ️ Не в ветке dev, hook пропущен"
fi
"""
    
    commit_msg_hook.write_text(commit_msg_content, encoding='utf-8')
    
    # Делаем файл исполняемым
    if os.name != 'nt':  # Не Windows
        os.chmod(commit_msg_hook, 0o755)
    
    print("✅ Commit-msg hook установлен")
    return True

def install_post_commit_hook():
    """Устанавливает post-commit hook."""
    print("📤 Установка post-commit hook...")
    
    # Создаем папку для hooks
    hooks_dir = project_root / '.git' / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    # Создаем post-commit hook
    post_commit_hook = hooks_dir / 'post-commit'
    post_commit_content = """#!/bin/bash
# Post-commit hook для WindSpotBot

echo "📤 Post-commit hook запущен"

# Проверяем, что мы в ветке dev
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "dev" ]; then
    echo "📁 Ветка: dev"
    
    # Показываем информацию о коммите
    echo "📝 Последний коммит:"
    git log -1 --oneline
    
    # Показываем статус
    echo "📊 Статус репозитория:"
    git status --short
    
    echo "✅ Post-commit hook выполнен"
else
    echo "ℹ️ Не в ветке dev, hook пропущен"
fi
"""
    
    post_commit_hook.write_text(post_commit_content, encoding='utf-8')
    
    # Делаем файл исполняемым
    if os.name != 'nt':  # Не Windows
        os.chmod(post_commit_hook, 0o755)
    
    print("✅ Post-commit hook установлен")
    return True

def install_pre_push_hook():
    """Устанавливает pre-push hook."""
    print("🚀 Установка pre-push hook...")
    
    # Создаем папку для hooks
    hooks_dir = project_root / '.git' / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    # Создаем pre-push hook
    pre_push_hook = hooks_dir / 'pre-push'
    pre_push_content = """#!/bin/bash
# Pre-push hook для WindSpotBot

echo "🚀 Pre-push hook запущен"

# Проверяем, что мы в ветке dev
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "dev" ]; then
    echo "📁 Ветка: dev"
    
    # Запускаем тесты
    echo "🧪 Запуск тестов..."
    python -m pytest tests/ -v --maxfail=1
    
    if [ $? -ne 0 ]; then
        echo "❌ Тесты не прошли, push отменен"
        exit 1
    fi
    
    echo "✅ Тесты прошли успешно"
    echo "✅ Pre-push hook выполнен"
else
    echo "ℹ️ Не в ветке dev, hook пропущен"
fi
"""
    
    pre_push_hook.write_text(pre_push_content, encoding='utf-8')
    
    # Делаем файл исполняемым
    if os.name != 'nt':  # Не Windows
        os.chmod(pre_push_hook, 0o755)
    
    print("✅ Pre-push hook установлен")
    return True

def main():
    """Основная функция установки hooks."""
    print("🚀 Установка Git hooks для WindSpotBot")
    print("=" * 40)
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return 1
    
    # Устанавливаем hooks
    if not install_pre_commit_hook():
        return 1
    
    if not install_commit_msg_hook():
        return 1
    
    if not install_post_commit_hook():
        return 1
    
    if not install_pre_push_hook():
        return 1
    
    print("\n✅ Все Git hooks установлены!")
    print("\n📋 Установленные hooks:")
    print("- pre-commit: Обновление документации и форматирование")
    print("- commit-msg: Проверка сообщений коммитов")
    print("- post-commit: Информация о коммите")
    print("- pre-push: Запуск тестов перед отправкой")
    
    print("\n🔧 Hooks будут автоматически запускаться при:")
    print("- git commit (pre-commit, commit-msg, post-commit)")
    print("- git push (pre-push)")
    
    print("\n⚠️ Примечание:")
    print("Hooks работают только в ветке dev")
    print("В других ветках hooks пропускаются")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




#!/usr/bin/env python3
"""
Менеджер версий для WindSpotBot.
Автоматизирует создание тегов, обновление версий и релизы.
"""

import os
import sys
import subprocess
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

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

def get_current_version() -> str:
    """Получает текущую версию из git тегов."""
    success, output = run_command("git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'")
    if success:
        return output.strip()
    return "v0.0.0"

def get_next_version(current_version: str, version_type: str) -> str:
    """Вычисляет следующую версию."""
    # Убираем префикс 'v' если есть
    version = current_version.lstrip('v')
    
    # Парсим версию
    try:
        major, minor, patch = map(int, version.split('.'))
    except ValueError:
        major, minor, patch = 0, 0, 0
    
    # Увеличиваем соответствующую часть
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Неизвестный тип версии: {version_type}")
    
    return f"v{major}.{minor}.{patch}"

def update_version_files(version: str):
    """Обновляет файлы с версией."""
    print(f"📝 Обновление файлов с версией {version}...")
    
    # Обновляем pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding='utf-8')
        content = re.sub(r'version = "[^"]*"', f'version = "{version.lstrip("v")}"', content)
        pyproject_path.write_text(content, encoding='utf-8')
        print(f"  ✅ Обновлен pyproject.toml")
    
    # Обновляем README.md
    readme_path = project_root / "README.md"
    if readme_path.exists():
        content = readme_path.read_text(encoding='utf-8')
        content = re.sub(r'Версия: v[\d.]+', f'Версия: {version}', content)
        readme_path.write_text(content, encoding='utf-8')
        print(f"  ✅ Обновлен README.md")
    
    # Обновляем CHANGELOG.md
    changelog_path = project_root / "CHANGELOG.md"
    if changelog_path.exists():
        content = changelog_path.read_text(encoding='utf-8')
        
        # Заменяем [Unreleased] на новую версию
        today = datetime.now().strftime('%Y-%m-%d')
        content = content.replace('[Unreleased]', f'[{version}] - {today}')
        
        changelog_path.write_text(content, encoding='utf-8')
        print(f"  ✅ Обновлен CHANGELOG.md")

def create_version_commit(version: str) -> bool:
    """Создает коммит с новой версией."""
    print(f"💾 Создание коммита версии {version}...")
    
    # Добавляем файлы
    success, output = run_command("git add pyproject.toml README.md CHANGELOG.md")
    if not success:
        print(f"❌ Ошибка добавления файлов: {output}")
        return False
    
    # Создаем коммит
    commit_message = f"Релиз версии {version}"
    success, output = run_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Ошибка создания коммита: {output}")
        return False
    
    print("✅ Коммит версии создан")
    return True

def create_version_tag(version: str) -> bool:
    """Создает тег версии."""
    print(f"🏷️ Создание тега {version}...")
    
    # Создаем аннотированный тег
    tag_message = f"Релиз версии {version}\n\nОсновные изменения:\n- Обновления и улучшения\n- Исправления ошибок\n- Обновленная документация"
    success, output = run_command(f'git tag -a {version} -m "{tag_message}"')
    if not success:
        print(f"❌ Ошибка создания тега: {output}")
        return False
    
    print("✅ Тег версии создан")
    return True

def push_version(version: str) -> bool:
    """Отправляет версию на GitHub."""
    print(f"📤 Отправка версии {version} на GitHub...")
    
    # Отправляем коммиты
    success, output = run_command("git push origin HEAD")
    if not success:
        print(f"❌ Ошибка отправки коммитов: {output}")
        return False
    
    # Отправляем тег
    success, output = run_command(f"git push origin {version}")
    if not success:
        print(f"❌ Ошибка отправки тега: {output}")
        return False
    
    print("✅ Версия отправлена на GitHub")
    return True

def create_release_notes(version: str) -> str:
    """Создает заметки о релизе."""
    # Получаем коммиты с последнего тега
    success, output = run_command("git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo 'v0.0.0'")
    if not success:
        last_tag = "v0.0.0"
    else:
        last_tag = output.strip()
    
    # Получаем коммиты
    success, output = run_command(f"git log {last_tag}..HEAD --oneline --no-merges")
    if not success:
        commits = []
    else:
        commits = [line.strip() for line in output.strip().split('\n') if line.strip()]
    
    # Создаем заметки
    notes = f"# Релиз {version}\n\n"
    notes += f"Дата: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    if commits:
        notes += "## Изменения\n\n"
        for commit in commits[:10]:  # Ограничиваем количество коммитов
            notes += f"- {commit}\n"
        
        if len(commits) > 10:
            notes += f"- ... и еще {len(commits) - 10} изменений\n"
    else:
        notes += "## Изменения\n\n- Обновления и улучшения\n- Исправления ошибок\n"
    
    notes += "\n## Установка\n\n"
    notes += "```bash\n"
    notes += "pip install windspotbot\n"
    notes += "```\n"
    
    return notes

def create_github_release(version: str) -> bool:
    """Создает релиз на GitHub."""
    print(f"🚀 Создание релиза {version} на GitHub...")
    
    # Создаем заметки о релизе
    release_notes = create_release_notes(version)
    
    # Создаем релиз
    success, output = run_command(f'gh release create {version} --title "Релиз {version}" --notes "{release_notes}"')
    if not success:
        print(f"❌ Ошибка создания релиза: {output}")
        return False
    
    print("✅ Релиз создан на GitHub")
    print(f"🔗 Ссылка: {output.strip()}")
    return True

def release_version(version_type: str, push: bool = True, github: bool = True) -> bool:
    """Создает релиз новой версии."""
    print("🚀 Создание релиза WindSpotBot")
    print("=" * 35)
    
    # Получаем текущую версию
    current_version = get_current_version()
    print(f"📋 Текущая версия: {current_version}")
    
    # Вычисляем следующую версию
    try:
        next_version = get_next_version(current_version, version_type)
        print(f"📋 Следующая версия: {next_version}")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    # Подтверждаем создание релиза
    print(f"\n⚠️ Будет создан релиз {next_version}")
    if not push:
        print("ℹ️ Режим предварительного просмотра (без отправки)")
    
    # Обновляем файлы с версией
    update_version_files(next_version)
    
    # Создаем коммит версии
    if not create_version_commit(next_version):
        return False
    
    # Создаем тег версии
    if not create_version_tag(next_version):
        return False
    
    # Отправляем на GitHub
    if push:
        if not push_version(next_version):
            return False
        
        # Создаем релиз на GitHub
        if github:
            if not create_github_release(next_version):
                return False
    
    print(f"✅ Релиз {next_version} создан успешно")
    return True

def list_versions():
    """Показывает список версий."""
    print("📋 Список версий WindSpotBot")
    print("=" * 30)
    
    # Получаем все теги
    success, output = run_command("git tag --sort=-version:refname")
    if not success:
        print("❌ Ошибка получения тегов")
        return
    
    tags = [tag.strip() for tag in output.strip().split('\n') if tag.strip()]
    
    if not tags:
        print("ℹ️ Тегов не найдено")
        return
    
    print(f"Найдено {len(tags)} версий:")
    for tag in tags[:10]:  # Показываем последние 10
        print(f"  - {tag}")
    
    if len(tags) > 10:
        print(f"  ... и еще {len(tags) - 10} версий")

def main():
    """Основная функция менеджера версий."""
    parser = argparse.ArgumentParser(description="Менеджер версий WindSpotBot")
    parser.add_argument("--patch", action="store_true", help="Создать patch релиз (0.0.1)")
    parser.add_argument("--minor", action="store_true", help="Создать minor релиз (0.1.0)")
    parser.add_argument("--major", action="store_true", help="Создать major релиз (1.0.0)")
    parser.add_argument("--list", action="store_true", help="Показать список версий")
    parser.add_argument("--no-push", action="store_true", help="Не отправлять на GitHub")
    parser.add_argument("--no-github", action="store_true", help="Не создавать релиз на GitHub")
    
    args = parser.parse_args()
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        print("❌ Не обнаружен git репозиторий")
        return 1
    
    # Показываем список версий
    if args.list:
        list_versions()
        return 0
    
    # Определяем тип версии
    version_type = None
    if args.patch:
        version_type = "patch"
    elif args.minor:
        version_type = "minor"
    elif args.major:
        version_type = "major"
    
    if not version_type:
        print("Использование:")
        print("  python scripts/version_manager.py --patch    # Patch релиз (0.0.1)")
        print("  python scripts/version_manager.py --minor    # Minor релиз (0.1.0)")
        print("  python scripts/version_manager.py --major    # Major релиз (1.0.0)")
        print("  python scripts/version_manager.py --list     # Список версий")
        return 0
    
    # Создаем релиз
    success = release_version(
        version_type=version_type,
        push=not args.no_push,
        github=not args.no_github
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())




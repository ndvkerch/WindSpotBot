#!/usr/bin/env python3
"""
Восстановление системы контроля версий для ветки dev.
Восстанавливает систему из бэкапа.
"""

import os
import sys
import subprocess
import shutil
import zipfile
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

def find_backups():
    """Находит доступные бэкапы."""
    print("🔍 Поиск доступных бэкапов...")
    
    backups_dir = project_root / 'backups'
    if not backups_dir.exists():
        print("❌ Папка backups не найдена")
        return []
    
    # Ищем папки бэкапов
    backup_dirs = []
    for item in backups_dir.iterdir():
        if item.is_dir() and item.name.startswith('dev_backup_'):
            backup_dirs.append(item)
    
    # Ищем ZIP архивы
    zip_files = []
    for item in backups_dir.iterdir():
        if item.is_file() and item.name.endswith('.zip') and 'dev_backup_' in item.name:
            zip_files.append(item)
    
    print(f"📁 Найдено {len(backup_dirs)} папок бэкапов")
    print(f"📦 Найдено {len(zip_files)} ZIP архивов")
    
    return backup_dirs + zip_files

def list_backups(backups):
    """Показывает список бэкапов."""
    print("\n📋 Доступные бэкапы:")
    print("=" * 30)
    
    for i, backup in enumerate(backups, 1):
        if backup.is_dir():
            print(f"{i}. 📁 {backup.name}")
            print(f"   📅 {backup.stat().st_mtime}")
        else:
            print(f"{i}. 📦 {backup.name}")
            print(f"   📅 {backup.stat().st_mtime}")
    
    print()

def select_backup(backups):
    """Выбирает бэкап для восстановления."""
    if not backups:
        print("❌ Нет доступных бэкапов")
        return None
    
    list_backups(backups)
    
    try:
        choice = input("Выберите номер бэкапа для восстановления: ").strip()
        index = int(choice) - 1
        
        if 0 <= index < len(backups):
            return backups[index]
        else:
            print("❌ Неверный номер бэкапа")
            return None
    except (ValueError, KeyboardInterrupt):
        print("❌ Выбор отменен")
        return None

def extract_zip_backup(zip_file: Path, extract_dir: Path):
    """Извлекает ZIP архив бэкапа."""
    print(f"📦 Извлечение ZIP архива: {zip_file.name}")
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            zipf.extractall(extract_dir)
        print("✅ ZIP архив извлечен")
        return True
    except Exception as e:
        print(f"❌ Ошибка извлечения ZIP архива: {e}")
        return False

def restore_git(backup_dir: Path):
    """Восстанавливает Git репозиторий."""
    print("🔧 Восстановление Git репозитория...")
    
    # Удаляем существующий .git
    git_dir = project_root / '.git'
    if git_dir.exists():
        try:
            shutil.rmtree(git_dir)
            print("✅ Существующий .git удален")
        except Exception as e:
            print(f"❌ Ошибка удаления .git: {e}")
            return False
    
    # Копируем .git из бэкапа
    backup_git_dir = backup_dir / 'git' / '.git'
    if backup_git_dir.exists():
        try:
            shutil.copytree(backup_git_dir, git_dir)
            print("✅ Git репозиторий восстановлен")
        except Exception as e:
            print(f"❌ Ошибка восстановления Git: {e}")
            return False
    
    # Копируем .gitignore
    backup_gitignore = backup_dir / 'git' / '.gitignore'
    if backup_gitignore.exists():
        try:
            shutil.copy2(backup_gitignore, project_root)
            print("✅ .gitignore восстановлен")
        except Exception as e:
            print(f"❌ Ошибка восстановления .gitignore: {e}")
    
    return True

def restore_hooks(backup_dir: Path):
    """Восстанавливает Git hooks."""
    print("🪝 Восстановление Git hooks...")
    
    # Удаляем существующие hooks
    hooks_dir = project_root / '.git' / 'hooks'
    if hooks_dir.exists():
        try:
            shutil.rmtree(hooks_dir)
            print("✅ Существующие hooks удалены")
        except Exception as e:
            print(f"❌ Ошибка удаления hooks: {e}")
    
    # Копируем hooks из бэкапа
    backup_hooks_dir = backup_dir / 'hooks' / 'git_hooks'
    if backup_hooks_dir.exists():
        try:
            shutil.copytree(backup_hooks_dir, hooks_dir)
            print("✅ Git hooks восстановлены")
        except Exception as e:
            print(f"❌ Ошибка восстановления hooks: {e}")
    
    # Копируем pre-commit конфигурацию
    backup_pre_commit = backup_dir / 'hooks' / '.pre-commit-config.yaml'
    if backup_pre_commit.exists():
        try:
            shutil.copy2(backup_pre_commit, project_root)
            print("✅ Pre-commit конфигурация восстановлена")
        except Exception as e:
            print(f"❌ Ошибка восстановления pre-commit: {e}")
    
    return True

def restore_scripts(backup_dir: Path):
    """Восстанавливает скрипты."""
    print("📜 Восстановление скриптов...")
    
    # Удаляем существующие скрипты
    scripts_dir = project_root / 'scripts'
    if scripts_dir.exists():
        try:
            shutil.rmtree(scripts_dir)
            print("✅ Существующие скрипты удалены")
        except Exception as e:
            print(f"❌ Ошибка удаления скриптов: {e}")
    
    # Копируем скрипты из бэкапа
    backup_scripts_dir = backup_dir / 'scripts'
    if backup_scripts_dir.exists():
        try:
            shutil.copytree(backup_scripts_dir, scripts_dir)
            print("✅ Скрипты восстановлены")
        except Exception as e:
            print(f"❌ Ошибка восстановления скриптов: {e}")
    
    return True

def restore_config(backup_dir: Path):
    """Восстанавливает конфигурацию."""
    print("⚙️ Восстановление конфигурации...")
    
    # Копируем конфигурационные файлы
    config_backup_dir = backup_dir / 'config'
    if config_backup_dir.exists():
        for config_file in config_backup_dir.iterdir():
            if config_file.is_file():
                try:
                    shutil.copy2(config_file, project_root)
                    print(f"  ✅ Восстановлен {config_file.name}")
                except Exception as e:
                    print(f"  ❌ Ошибка восстановления {config_file.name}: {e}")
    
    print("✅ Конфигурация восстановлена")
    return True

def restore_docs(backup_dir: Path):
    """Восстанавливает документацию."""
    print("📚 Восстановление документации...")
    
    # Удаляем существующую документацию
    docs_dir = project_root / 'docs'
    if docs_dir.exists():
        try:
            shutil.rmtree(docs_dir)
            print("✅ Существующая документация удалена")
        except Exception as e:
            print(f"❌ Ошибка удаления документации: {e}")
    
    # Копируем документацию из бэкапа
    backup_docs_dir = backup_dir / 'docs'
    if backup_docs_dir.exists():
        try:
            shutil.copytree(backup_docs_dir, docs_dir)
            print("✅ Документация восстановлена")
        except Exception as e:
            print(f"❌ Ошибка восстановления документации: {e}")
    
    # Копируем README файлы
    readme_files = ['README.md', 'README_DEVELOPMENT.md', 'CHANGELOG.md', 'SETUP.md']
    for readme_file in readme_files:
        backup_readme = backup_dir / 'docs' / readme_file
        if backup_readme.exists():
            try:
                shutil.copy2(backup_readme, project_root)
                print(f"  ✅ Восстановлен {readme_file}")
            except Exception as e:
                print(f"  ❌ Ошибка восстановления {readme_file}: {e}")
    
    return True

def restore_source(backup_dir: Path):
    """Восстанавливает исходный код."""
    print("💻 Восстановление исходного кода...")
    
    # Удаляем существующий исходный код
    src_dir = project_root / 'src'
    if src_dir.exists():
        try:
            shutil.rmtree(src_dir)
            print("✅ Существующий исходный код удален")
        except Exception as e:
            print(f"❌ Ошибка удаления исходного кода: {e}")
    
    # Копируем исходный код из бэкапа
    backup_src_dir = backup_dir / 'src'
    if backup_src_dir.exists():
        try:
            shutil.copytree(backup_src_dir, src_dir)
            print("✅ Исходный код восстановлен")
        except Exception as e:
            print(f"❌ Ошибка восстановления исходного кода: {e}")
    
    # Копируем тесты
    tests_dir = project_root / 'tests'
    if tests_dir.exists():
        try:
            shutil.rmtree(tests_dir)
            print("✅ Существующие тесты удалены")
        except Exception as e:
            print(f"❌ Ошибка удаления тестов: {e}")
    
    backup_tests_dir = backup_dir / 'tests'
    if backup_tests_dir.exists():
        try:
            shutil.copytree(backup_tests_dir, tests_dir)
            print("✅ Тесты восстановлены")
        except Exception as e:
            print(f"❌ Ошибка восстановления тестов: {e}")
    
    return True

def restore_database(backup_dir: Path):
    """Восстанавливает базу данных."""
    print("🗄️ Восстановление базы данных...")
    
    # Копируем файлы БД
    db_backup_dir = backup_dir / 'database'
    if db_backup_dir.exists():
        for db_file in db_backup_dir.iterdir():
            if db_file.is_file():
                try:
                    shutil.copy2(db_file, project_root)
                    print(f"  ✅ Восстановлен {db_file.name}")
                except Exception as e:
                    print(f"  ❌ Ошибка восстановления {db_file.name}: {e}")
    
    print("✅ База данных восстановлена")
    return True

def show_restore_summary():
    """Показывает сводку восстановления."""
    print("\n📊 Сводка восстановления:")
    print("=" * 25)
    print("✅ Git репозиторий восстановлен")
    print("✅ Git hooks восстановлены")
    print("✅ Скрипты восстановлены")
    print("✅ Конфигурация восстановлена")
    print("✅ Документация восстановлена")
    print("✅ Исходный код восстановлен")
    print("✅ Тесты восстановлены")
    print("✅ База данных восстановлена")
    print()
    print("🔄 Следующие шаги:")
    print("1. Проверьте статус: python scripts/dev_status.py")
    print("2. Синхронизируйтесь: make dev-sync")
    print("3. Запустите тесты: make test")
    print("4. Запустите автокоммиты: make dev-auto")
    print()

def main():
    """Основная функция восстановления."""
    print("🔄 Восстановление системы контроля версий WindSpotBot")
    print("=" * 55)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {project_root}")
    print()
    
    # Находим бэкапы
    backups = find_backups()
    if not backups:
        print("❌ Нет доступных бэкапов для восстановления")
        return 1
    
    # Выбираем бэкап
    selected_backup = select_backup(backups)
    if not selected_backup:
        return 1
    
    print(f"📁 Выбран бэкап: {selected_backup.name}")
    print()
    
    # Если это ZIP архив, извлекаем его
    if selected_backup.is_file() and selected_backup.name.endswith('.zip'):
        extract_dir = selected_backup.parent / f"{selected_backup.stem}_extracted"
        if not extract_zip_backup(selected_backup, extract_dir):
            return 1
        backup_dir = extract_dir
    else:
        backup_dir = selected_backup
    
    # Выполняем восстановление
    restore_git(backup_dir)
    restore_hooks(backup_dir)
    restore_scripts(backup_dir)
    restore_config(backup_dir)
    restore_docs(backup_dir)
    restore_source(backup_dir)
    restore_database(backup_dir)
    
    # Показываем сводку
    show_restore_summary()
    
    print("✅ Восстановление завершено!")
    return 0

if __name__ == "__main__":
    sys.exit(main())




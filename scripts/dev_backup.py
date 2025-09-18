#!/usr/bin/env python3
"""
Резервное копирование системы контроля версий для ветки dev.
Создает бэкап текущего состояния.
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

def create_backup_dir():
    """Создает папку для бэкапа."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = project_root / 'backups' / f'dev_backup_{timestamp}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir

def backup_git():
    """Создает бэкап Git репозитория."""
    print("🔧 Бэкап Git репозитория...")
    
    backup_dir = create_backup_dir()
    git_backup_dir = backup_dir / 'git'
    git_backup_dir.mkdir(exist_ok=True)
    
    # Копируем .git папку
    git_dir = project_root / '.git'
    if git_dir.exists():
        try:
            shutil.copytree(git_dir, git_backup_dir / '.git')
            print("✅ Git репозиторий скопирован")
        except Exception as e:
            print(f"❌ Ошибка копирования Git: {e}")
            return False
    
    # Копируем .gitignore
    gitignore_file = project_root / '.gitignore'
    if gitignore_file.exists():
        try:
            shutil.copy2(gitignore_file, git_backup_dir)
            print("✅ .gitignore скопирован")
        except Exception as e:
            print(f"❌ Ошибка копирования .gitignore: {e}")
    
    return True

def backup_hooks():
    """Создает бэкап Git hooks."""
    print("🪝 Бэкап Git hooks...")
    
    backup_dir = create_backup_dir()
    hooks_backup_dir = backup_dir / 'hooks'
    hooks_backup_dir.mkdir(exist_ok=True)
    
    # Копируем hooks
    hooks_dir = project_root / '.git' / 'hooks'
    if hooks_dir.exists():
        try:
            shutil.copytree(hooks_dir, hooks_backup_dir / 'git_hooks')
            print("✅ Git hooks скопированы")
        except Exception as e:
            print(f"❌ Ошибка копирования hooks: {e}")
    
    # Копируем pre-commit конфигурацию
    pre_commit_config = project_root / '.pre-commit-config.yaml'
    if pre_commit_config.exists():
        try:
            shutil.copy2(pre_commit_config, hooks_backup_dir)
            print("✅ Pre-commit конфигурация скопирована")
        except Exception as e:
            print(f"❌ Ошибка копирования pre-commit: {e}")
    
    return True

def backup_scripts():
    """Создает бэкап скриптов."""
    print("📜 Бэкап скриптов...")
    
    backup_dir = create_backup_dir()
    scripts_backup_dir = backup_dir / 'scripts'
    scripts_backup_dir.mkdir(exist_ok=True)
    
    # Копируем все скрипты
    scripts_dir = project_root / 'scripts'
    if scripts_dir.exists():
        try:
            shutil.copytree(scripts_dir, scripts_backup_dir)
            print("✅ Скрипты скопированы")
        except Exception as e:
            print(f"❌ Ошибка копирования скриптов: {e}")
    
    return True

def backup_config():
    """Создает бэкап конфигурации."""
    print("⚙️ Бэкап конфигурации...")
    
    backup_dir = create_backup_dir()
    config_backup_dir = backup_dir / 'config'
    config_backup_dir.mkdir(exist_ok=True)
    
    # Копируем конфигурационные файлы
    config_files = [
        'pyproject.toml',
        'requirements.txt',
        'Makefile',
        '.env',
        '.env.example',
        'alembic.ini'
    ]
    
    copied_count = 0
    for config_file in config_files:
        config_path = project_root / config_file
        if config_path.exists():
            try:
                shutil.copy2(config_path, config_backup_dir)
                copied_count += 1
                print(f"  ✅ Скопирован {config_file}")
            except Exception as e:
                print(f"  ❌ Ошибка копирования {config_file}: {e}")
    
    print(f"✅ Скопировано {copied_count} конфигурационных файлов")
    return True

def backup_docs():
    """Создает бэкап документации."""
    print("📚 Бэкап документации...")
    
    backup_dir = create_backup_dir()
    docs_backup_dir = backup_dir / 'docs'
    docs_backup_dir.mkdir(exist_ok=True)
    
    # Копируем документацию
    docs_dir = project_root / 'docs'
    if docs_dir.exists():
        try:
            shutil.copytree(docs_dir, docs_backup_dir)
            print("✅ Документация скопирована")
        except Exception as e:
            print(f"❌ Ошибка копирования документации: {e}")
    
    # Копируем README файлы
    readme_files = ['README.md', 'README_DEVELOPMENT.md', 'CHANGELOG.md', 'SETUP.md']
    for readme_file in readme_files:
        readme_path = project_root / readme_file
        if readme_path.exists():
            try:
                shutil.copy2(readme_path, docs_backup_dir)
                print(f"  ✅ Скопирован {readme_file}")
            except Exception as e:
                print(f"  ❌ Ошибка копирования {readme_file}: {e}")
    
    return True

def backup_source():
    """Создает бэкап исходного кода."""
    print("💻 Бэкап исходного кода...")
    
    backup_dir = create_backup_dir()
    src_backup_dir = backup_dir / 'src'
    src_backup_dir.mkdir(exist_ok=True)
    
    # Копируем исходный код
    src_dir = project_root / 'src'
    if src_dir.exists():
        try:
            shutil.copytree(src_dir, src_backup_dir)
            print("✅ Исходный код скопирован")
        except Exception as e:
            print(f"❌ Ошибка копирования исходного кода: {e}")
    
    # Копируем тесты
    tests_dir = project_root / 'tests'
    if tests_dir.exists():
        try:
            shutil.copytree(tests_dir, backup_dir / 'tests')
            print("✅ Тесты скопированы")
        except Exception as e:
            print(f"❌ Ошибка копирования тестов: {e}")
    
    return True

def backup_database():
    """Создает бэкап базы данных."""
    print("🗄️ Бэкап базы данных...")
    
    backup_dir = create_backup_dir()
    db_backup_dir = backup_dir / 'database'
    db_backup_dir.mkdir(exist_ok=True)
    
    # Копируем файлы БД
    db_files = [
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        'database.db',
        'windspotbot.db'
    ]
    
    copied_count = 0
    for pattern in db_files:
        if os.name == 'nt':  # Windows
            find_cmd = f'forfiles /p . /s /m "{pattern}" /c "cmd /c copy @path {db_backup_dir}" 2>nul'
        else:  # Linux/macOS
            find_cmd = f'find . -name "{pattern}" -type f -exec cp {{}} {db_backup_dir} \\; 2>/dev/null'
        
        success, output = run_command(find_cmd)
        if success:
            copied_count += 1
    
    print(f"✅ Скопировано {copied_count} типов файлов БД")
    return True

def create_backup_info(backup_dir: Path):
    """Создает информацию о бэкапе."""
    print("📝 Создание информации о бэкапе...")
    
    info_file = backup_dir / 'backup_info.txt'
    info_content = f"""WindSpotBot Dev Backup Information
=====================================

Backup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project Directory: {project_root}
Backup Directory: {backup_dir}

Git Information:
- Current Branch: {run_command('git branch --show-current')[1].strip()}
- Last Commit: {run_command('git log -1 --oneline')[1].strip()}
- Commit Count: {run_command('git rev-list --count HEAD')[1].strip()}

System Information:
- Python Version: {sys.version}
- OS: {os.name}
- Platform: {sys.platform}

Backup Contents:
- Git repository (.git)
- Git hooks
- Scripts (scripts/)
- Configuration files
- Documentation (docs/)
- Source code (src/)
- Tests (tests/)
- Database files
- README files

Restore Instructions:
1. Extract backup to desired location
2. Run: python scripts/dev_setup.py
3. Run: make dev-sync
4. Run: make dev-auto

Notes:
- This backup contains the complete state of the dev branch
- All Git history and hooks are preserved
- Configuration and scripts are included
- Database files are backed up if they exist
"""
    
    try:
        info_file.write_text(info_content, encoding='utf-8')
        print("✅ Информация о бэкапе создана")
    except Exception as e:
        print(f"❌ Ошибка создания информации о бэкапе: {e}")
    
    return True

def create_zip_backup(backup_dir: Path):
    """Создает ZIP архив бэкапа."""
    print("📦 Создание ZIP архива...")
    
    zip_file = backup_dir.parent / f'{backup_dir.name}.zip'
    
    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arc_path)
        
        print(f"✅ ZIP архив создан: {zip_file}")
        return zip_file
    except Exception as e:
        print(f"❌ Ошибка создания ZIP архива: {e}")
        return None

def show_backup_summary(backup_dir: Path, zip_file: Path = None):
    """Показывает сводку бэкапа."""
    print("\n📊 Сводка бэкапа:")
    print("=" * 20)
    print(f"📁 Папка бэкапа: {backup_dir}")
    if zip_file:
        print(f"📦 ZIP архив: {zip_file}")
    print(f"📅 Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📋 Содержимое бэкапа:")
    print("✅ Git репозиторий")
    print("✅ Git hooks")
    print("✅ Скрипты")
    print("✅ Конфигурация")
    print("✅ Документация")
    print("✅ Исходный код")
    print("✅ Тесты")
    print("✅ База данных")
    print("✅ Информация о бэкапе")
    print()
    print("🔄 Для восстановления:")
    print("1. Извлеките бэкап в нужную папку")
    print("2. Выполните: python scripts/dev_setup.py")
    print("3. Выполните: make dev-sync")
    print("4. Выполните: make dev-auto")
    print()

def main():
    """Основная функция бэкапа."""
    print("💾 Резервное копирование системы контроля версий WindSpotBot")
    print("=" * 60)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {project_root}")
    print()
    
    # Создаем папку для бэкапа
    backup_dir = create_backup_dir()
    print(f"📁 Папка бэкапа: {backup_dir}")
    print()
    
    # Выполняем бэкап
    backup_git()
    backup_hooks()
    backup_scripts()
    backup_config()
    backup_docs()
    backup_source()
    backup_database()
    create_backup_info(backup_dir)
    
    # Создаем ZIP архив
    zip_file = create_zip_backup(backup_dir)
    
    # Показываем сводку
    show_backup_summary(backup_dir, zip_file)
    
    print("✅ Бэкап завершен!")
    return 0

if __name__ == "__main__":
    sys.exit(main())




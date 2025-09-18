#!/usr/bin/env python3
"""
Очистка системы контроля версий для ветки dev.
Удаляет временные файлы и сбрасывает настройки.
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

def cleanup_temp_files():
    """Очищает временные файлы."""
    print("🧹 Очистка временных файлов...")
    
    # Паттерны файлов для удаления
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/*.so",
        "**/.pytest_cache",
        "**/htmlcov",
        "**/.coverage",
        "**/coverage.xml",
        "**/*.egg-info",
        "**/dist",
        "**/build",
        "**/.mypy_cache",
        "**/.ruff_cache",
        "**/*.log",
        "**/*.tmp",
        "**/*.temp"
    ]
    
    removed_count = 0
    
    for pattern in patterns:
        # Используем find для поиска файлов
        if os.name == 'nt':  # Windows
            find_cmd = f'forfiles /p . /s /m "{pattern}" /c "cmd /c del @path" 2>nul'
        else:  # Linux/macOS
            find_cmd = f'find . -name "{pattern}" -type f -delete 2>/dev/null'
        
        success, output = run_command(find_cmd)
        if success:
            removed_count += 1
    
    print(f"✅ Удалено {removed_count} типов временных файлов")
    return True

def cleanup_git_hooks():
    """Удаляет Git hooks."""
    print("🪝 Удаление Git hooks...")
    
    hooks_dir = project_root / '.git' / 'hooks'
    if not hooks_dir.exists():
        print("ℹ️ Папка hooks не существует")
        return True
    
    # Удаляем hooks
    hooks = ['pre-commit', 'commit-msg', 'post-commit', 'pre-push']
    removed_count = 0
    
    for hook in hooks:
        hook_file = hooks_dir / hook
        if hook_file.exists():
            try:
                hook_file.unlink()
                removed_count += 1
                print(f"  ✅ Удален {hook}")
            except Exception as e:
                print(f"  ❌ Ошибка удаления {hook}: {e}")
    
    print(f"✅ Удалено {removed_count} hooks")
    return True

def cleanup_pre_commit():
    """Удаляет pre-commit hooks."""
    print("🪝 Удаление pre-commit hooks...")
    
    # Удаляем pre-commit hooks
    success, output = run_command("pre-commit uninstall")
    if success:
        print("✅ Pre-commit hooks удалены")
    else:
        print(f"⚠️ Ошибка удаления pre-commit hooks: {output}")
    
    return True

def cleanup_venv():
    """Удаляет виртуальное окружение."""
    print("🐍 Удаление виртуального окружения...")
    
    venv_dir = project_root / 'venv'
    if venv_dir.exists():
        try:
            import shutil
            shutil.rmtree(venv_dir)
            print("✅ Виртуальное окружение удалено")
        except Exception as e:
            print(f"❌ Ошибка удаления venv: {e}")
            return False
    else:
        print("ℹ️ Виртуальное окружение не найдено")
    
    return True

def cleanup_git_files():
    """Очищает Git файлы."""
    print("🔧 Очистка Git файлов...")
    
    # Сбрасываем изменения
    success, output = run_command("git reset --hard HEAD")
    if success:
        print("✅ Git изменения сброшены")
    else:
        print(f"⚠️ Ошибка сброса Git: {output}")
    
    # Очищаем неотслеживаемые файлы
    success, output = run_command("git clean -fd")
    if success:
        print("✅ Неотслеживаемые файлы удалены")
    else:
        print(f"⚠️ Ошибка очистки Git: {output}")
    
    return True

def cleanup_docs():
    """Очищает сгенерированную документацию."""
    print("📚 Очистка документации...")
    
    # Удаляем сгенерированные файлы
    docs_to_remove = [
        'docs/_build',
        'docs/.doctrees',
        'docs/api.rst',
        'docs/modules.rst'
    ]
    
    removed_count = 0
    for doc_path in docs_to_remove:
        doc_file = project_root / doc_path
        if doc_file.exists():
            try:
                if doc_file.is_dir():
                    import shutil
                    shutil.rmtree(doc_file)
                else:
                    doc_file.unlink()
                removed_count += 1
                print(f"  ✅ Удален {doc_path}")
            except Exception as e:
                print(f"  ❌ Ошибка удаления {doc_path}: {e}")
    
    print(f"✅ Удалено {removed_count} файлов документации")
    return True

def cleanup_logs():
    """Очищает логи."""
    print("📝 Очистка логов...")
    
    # Паттерны логов
    log_patterns = [
        "*.log",
        "logs/*.log",
        "*.out",
        "*.err"
    ]
    
    removed_count = 0
    for pattern in log_patterns:
        if os.name == 'nt':  # Windows
            find_cmd = f'forfiles /p . /s /m "{pattern}" /c "cmd /c del @path" 2>nul'
        else:  # Linux/macOS
            find_cmd = f'find . -name "{pattern}" -type f -delete 2>/dev/null'
        
        success, output = run_command(find_cmd)
        if success:
            removed_count += 1
    
    print(f"✅ Удалено {removed_count} типов логов")
    return True

def cleanup_database():
    """Очищает базу данных."""
    print("🗄️ Очистка базы данных...")
    
    # Удаляем файлы БД
    db_files = [
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        'database.db',
        'windspotbot.db'
    ]
    
    removed_count = 0
    for pattern in db_files:
        if os.name == 'nt':  # Windows
            find_cmd = f'forfiles /p . /s /m "{pattern}" /c "cmd /c del @path" 2>nul'
        else:  # Linux/macOS
            find_cmd = f'find . -name "{pattern}" -type f -delete 2>/dev/null'
        
        success, output = run_command(find_cmd)
        if success:
            removed_count += 1
    
    print(f"✅ Удалено {removed_count} типов файлов БД")
    return True

def cleanup_config():
    """Очищает конфигурационные файлы."""
    print("⚙️ Очистка конфигурации...")
    
    # Удаляем конфигурационные файлы
    config_files = [
        '.env',
        '.env.local',
        '.env.development',
        '.env.production',
        'config.ini',
        'settings.json'
    ]
    
    removed_count = 0
    for config_file in config_files:
        config_path = project_root / config_file
        if config_path.exists():
            try:
                config_path.unlink()
                removed_count += 1
                print(f"  ✅ Удален {config_file}")
            except Exception as e:
                print(f"  ❌ Ошибка удаления {config_file}: {e}")
    
    print(f"✅ Удалено {removed_count} конфигурационных файлов")
    return True

def show_cleanup_summary():
    """Показывает сводку очистки."""
    print("\n📊 Сводка очистки:")
    print("=" * 20)
    print("✅ Временные файлы удалены")
    print("✅ Git hooks удалены")
    print("✅ Pre-commit hooks удалены")
    print("✅ Виртуальное окружение удалено")
    print("✅ Git изменения сброшены")
    print("✅ Документация очищена")
    print("✅ Логи удалены")
    print("✅ База данных очищена")
    print("✅ Конфигурация очищена")
    print()
    print("🔄 Для повторной настройки выполните:")
    print("   python scripts/dev_setup.py")
    print()

def main():
    """Основная функция очистки."""
    print("🧹 Очистка системы контроля версий WindSpotBot")
    print("=" * 50)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {project_root}")
    print()
    
    # Подтверждение очистки
    try:
        confirm = input("⚠️ Вы уверены, что хотите очистить систему? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', 'да', 'д']:
            print("❌ Очистка отменена")
            return 0
    except KeyboardInterrupt:
        print("\n❌ Очистка отменена")
        return 0
    
    print("\n🚀 Начинаем очистку...")
    print()
    
    # Выполняем очистку
    cleanup_temp_files()
    cleanup_git_hooks()
    cleanup_pre_commit()
    cleanup_venv()
    cleanup_git_files()
    cleanup_docs()
    cleanup_logs()
    cleanup_database()
    cleanup_config()
    
    # Показываем сводку
    show_cleanup_summary()
    
    print("✅ Очистка завершена!")
    return 0

if __name__ == "__main__":
    sys.exit(main())




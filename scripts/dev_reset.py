#!/usr/bin/env python3
"""
Сброс системы контроля версий для ветки dev.
Возвращает систему к исходному состоянию.
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

def reset_git():
    """Сбрасывает Git к исходному состоянию."""
    print("🔧 Сброс Git...")
    
    # Сбрасываем все изменения
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
    
    # Сбрасываем индекс
    success, output = run_command("git reset --mixed HEAD")
    if success:
        print("✅ Git индекс сброшен")
    else:
        print(f"⚠️ Ошибка сброса индекса: {output}")
    
    return True

def reset_branches():
    """Сбрасывает ветки к исходному состоянию."""
    print("🌿 Сброс веток...")
    
    # Получаем текущую ветку
    success, output = run_command("git branch --show-current")
    if not success:
        print("❌ Ошибка получения текущей ветки")
        return False
    
    current_branch = output.strip()
    print(f"📁 Текущая ветка: {current_branch}")
    
    # Если в ветке dev, переключаемся на main
    if current_branch == "dev":
        print("🔄 Переключение на main...")
        success, output = run_command("git checkout main")
        if not success:
            print(f"❌ Ошибка переключения на main: {output}")
            return False
        
        print("✅ Переключились на main")
    
    # Удаляем ветку dev
    print("🗑️ Удаление ветки dev...")
    success, output = run_command("git branch -D dev")
    if success:
        print("✅ Ветка dev удалена")
    else:
        print(f"⚠️ Ошибка удаления ветки dev: {output}")
    
    # Создаем новую ветку dev
    print("🌿 Создание новой ветки dev...")
    success, output = run_command("git checkout -b dev")
    if not success:
        print(f"❌ Ошибка создания ветки dev: {output}")
        return False
    
    print("✅ Новая ветка dev создана")
    return True

def reset_hooks():
    """Сбрасывает Git hooks."""
    print("🪝 Сброс Git hooks...")
    
    # Удаляем существующие hooks
    hooks_dir = project_root / '.git' / 'hooks'
    if hooks_dir.exists():
        hooks = ['pre-commit', 'commit-msg', 'post-commit', 'pre-push']
        for hook in hooks:
            hook_file = hooks_dir / hook
            if hook_file.exists():
                try:
                    hook_file.unlink()
                    print(f"  ✅ Удален {hook}")
                except Exception as e:
                    print(f"  ❌ Ошибка удаления {hook}: {e}")
    
    # Удаляем pre-commit hooks
    success, output = run_command("pre-commit uninstall")
    if success:
        print("✅ Pre-commit hooks удалены")
    else:
        print(f"⚠️ Ошибка удаления pre-commit hooks: {output}")
    
    return True

def reset_dependencies():
    """Сбрасывает зависимости."""
    print("📦 Сброс зависимостей...")
    
    # Удаляем виртуальное окружение
    venv_dir = project_root / 'venv'
    if venv_dir.exists():
        try:
            import shutil
            shutil.rmtree(venv_dir)
            print("✅ Виртуальное окружение удалено")
        except Exception as e:
            print(f"❌ Ошибка удаления venv: {e}")
    
    # Удаляем кэш pip
    success, output = run_command("pip cache purge")
    if success:
        print("✅ Кэш pip очищен")
    else:
        print(f"⚠️ Ошибка очистки кэша pip: {output}")
    
    return True

def reset_docs():
    """Сбрасывает документацию."""
    print("📚 Сброс документации...")
    
    # Удаляем сгенерированные файлы
    docs_to_remove = [
        'docs/_build',
        'docs/.doctrees',
        'docs/api.rst',
        'docs/modules.rst',
        'CHANGELOG.md'
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

def reset_config():
    """Сбрасывает конфигурацию."""
    print("⚙️ Сброс конфигурации...")
    
    # Удаляем конфигурационные файлы
    config_files = [
        '.env',
        '.env.local',
        '.env.development',
        '.env.production',
        'config.ini',
        'settings.json',
        '.pre-commit-config.yaml'
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

def reset_database():
    """Сбрасывает базу данных."""
    print("🗄️ Сброс базы данных...")
    
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

def reset_logs():
    """Сбрасывает логи."""
    print("📝 Сброс логов...")
    
    # Удаляем логи
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

def reset_temp_files():
    """Сбрасывает временные файлы."""
    print("🧹 Сброс временных файлов...")
    
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

def show_reset_summary():
    """Показывает сводку сброса."""
    print("\n📊 Сводка сброса:")
    print("=" * 20)
    print("✅ Git сброшен")
    print("✅ Ветки сброшены")
    print("✅ Hooks сброшены")
    print("✅ Зависимости сброшены")
    print("✅ Документация сброшена")
    print("✅ Конфигурация сброшена")
    print("✅ База данных сброшена")
    print("✅ Логи сброшены")
    print("✅ Временные файлы сброшены")
    print()
    print("🔄 Для повторной настройки выполните:")
    print("   python scripts/dev_setup.py")
    print()

def main():
    """Основная функция сброса."""
    print("🔄 Сброс системы контроля версий WindSpotBot")
    print("=" * 50)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {project_root}")
    print()
    
    # Подтверждение сброса
    try:
        confirm = input("⚠️ Вы уверены, что хотите сбросить систему? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', 'да', 'д']:
            print("❌ Сброс отменен")
            return 0
    except KeyboardInterrupt:
        print("\n❌ Сброс отменен")
        return 0
    
    print("\n🚀 Начинаем сброс...")
    print()
    
    # Выполняем сброс
    reset_git()
    reset_branches()
    reset_hooks()
    reset_dependencies()
    reset_docs()
    reset_config()
    reset_database()
    reset_logs()
    reset_temp_files()
    
    # Показываем сводку
    show_reset_summary()
    
    print("✅ Сброс завершен!")
    return 0

if __name__ == "__main__":
    sys.exit(main())




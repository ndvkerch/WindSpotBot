#!/usr/bin/env python3
"""
Валидация системы контроля версий для ветки dev.
Проверяет корректность настройки и работы системы.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

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

def validate_git() -> Tuple[bool, List[str]]:
    """Валидирует Git репозиторий."""
    print("🔧 Валидация Git...")
    
    issues = []
    
    # Проверяем, что мы в git репозитории
    if not (project_root / '.git').exists():
        issues.append("❌ Не обнаружен git репозиторий")
        return False, issues
    
    # Проверяем текущую ветку
    success, output = run_command("git branch --show-current")
    if not success:
        issues.append("❌ Ошибка получения текущей ветки")
        return False, issues
    
    current_branch = output.strip()
    if current_branch != "dev":
        issues.append(f"⚠️ Текущая ветка: {current_branch} (рекомендуется dev)")
    
    # Проверяем статус
    success, output = run_command("git status --porcelain")
    if success:
        if output.strip():
            issues.append("ℹ️ Есть несохраненные изменения")
        else:
            print("✅ Git репозиторий в чистом состоянии")
    
    # Проверяем удаленный репозиторий
    success, output = run_command("git remote get-url origin")
    if not success:
        issues.append("⚠️ Удаленный репозиторий не настроен")
    else:
        print(f"✅ Удаленный репозиторий: {output.strip()}")
    
    return len(issues) == 0, issues

def validate_hooks() -> Tuple[bool, List[str]]:
    """Валидирует Git hooks."""
    print("🪝 Валидация Git hooks...")
    
    issues = []
    
    hooks_dir = project_root / '.git' / 'hooks'
    if not hooks_dir.exists():
        issues.append("❌ Папка hooks не существует")
        return False, issues
    
    # Проверяем наличие hooks
    required_hooks = ['pre-commit', 'commit-msg', 'post-commit', 'pre-push']
    for hook in required_hooks:
        hook_file = hooks_dir / hook
        if hook_file.exists():
            print(f"✅ {hook} найден")
        else:
            issues.append(f"❌ {hook} не найден")
    
    return len(issues) == 0, issues

def validate_pre_commit() -> Tuple[bool, List[str]]:
    """Валидирует pre-commit."""
    print("🪝 Валидация pre-commit...")
    
    issues = []
    
    # Проверяем установку
    success, output = run_command("pre-commit --version")
    if not success:
        issues.append("❌ Pre-commit не установлен")
        return False, issues
    
    print(f"✅ Pre-commit установлен: {output.strip()}")
    
    # Проверяем установленные hooks
    success, output = run_command("pre-commit installed")
    if not success:
        issues.append("❌ Pre-commit hooks не установлены")
    else:
        print("✅ Pre-commit hooks установлены")
    
    return len(issues) == 0, issues

def validate_scripts() -> Tuple[bool, List[str]]:
    """Валидирует скрипты."""
    print("📜 Валидация скриптов...")
    
    issues = []
    
    scripts_dir = project_root / 'scripts'
    if not scripts_dir.exists():
        issues.append("❌ Папка scripts не существует")
        return False, issues
    
    # Проверяем наличие основных скриптов
    required_scripts = [
        'update_docs.py',
        'update_changelog.py',
        'commit_helper.py',
        'github_helper.py',
        'auto_commit.py',
        'dev_workflow.py',
        'dev_auto_commit.py',
        'version_manager.py',
        'dev_status.py',
        'dev_help.py'
    ]
    
    for script in required_scripts:
        script_file = scripts_dir / script
        if script_file.exists():
            print(f"✅ {script} найден")
        else:
            issues.append(f"❌ {script} не найден")
    
    return len(issues) == 0, issues

def validate_config() -> Tuple[bool, List[str]]:
    """Валидирует конфигурацию."""
    print("⚙️ Валидация конфигурации...")
    
    issues = []
    
    # Проверяем основные конфигурационные файлы
    config_files = [
        'pyproject.toml',
        'requirements.txt',
        'Makefile',
        '.pre-commit-config.yaml'
    ]
    
    for config_file in config_files:
        config_path = project_root / config_file
        if config_path.exists():
            print(f"✅ {config_file} найден")
        else:
            issues.append(f"❌ {config_file} не найден")
    
    return len(issues) == 0, issues

def validate_docs() -> Tuple[bool, List[str]]:
    """Валидирует документацию."""
    print("📚 Валидация документации...")
    
    issues = []
    
    # Проверяем основные документы
    doc_files = [
        'README.md',
        'README_DEVELOPMENT.md',
        'CHANGELOG.md',
        'SETUP.md'
    ]
    
    for doc_file in doc_files:
        doc_path = project_root / doc_file
        if doc_path.exists():
            print(f"✅ {doc_file} найден")
        else:
            issues.append(f"❌ {doc_file} не найден")
    
    return len(issues) == 0, issues

def validate_source() -> Tuple[bool, List[str]]:
    """Валидирует исходный код."""
    print("💻 Валидация исходного кода...")
    
    issues = []
    
    # Проверяем папку src
    src_dir = project_root / 'src'
    if not src_dir.exists():
        issues.append("❌ Папка src не найдена")
        return False, issues
    
    print("✅ Папка src найдена")
    
    # Проверяем основные модули
    src_modules = [
        'bot.py',
        'config',
        'handlers',
        'services',
        'repositories',
        'models',
        'keyboards'
    ]
    
    for module in src_modules:
        module_path = src_dir / module
        if module_path.exists():
            print(f"✅ {module} найден")
        else:
            issues.append(f"❌ {module} не найден")
    
    return len(issues) == 0, issues

def validate_dependencies() -> Tuple[bool, List[str]]:
    """Валидирует зависимости."""
    print("📦 Валидация зависимостей...")
    
    issues = []
    
    # Проверяем Python версию
    if sys.version_info < (3, 11):
        issues.append(f"❌ Требуется Python 3.11+, текущая: {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print(f"✅ Python версия: {sys.version_info.major}.{sys.version_info.minor}")
    
    # Проверяем основные зависимости
    required_packages = [
        'aiogram',
        'pydantic',
        'sqlalchemy',
        'alembic',
        'pytest',
        'black',
        'flake8',
        'mypy',
        'pre-commit'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} установлен")
        except ImportError:
            issues.append(f"❌ {package} не установлен")
    
    return len(issues) == 0, issues

def validate_github() -> Tuple[bool, List[str]]:
    """Валидирует GitHub CLI."""
    print("🔗 Валидация GitHub CLI...")
    
    issues = []
    
    # Проверяем установку
    success, output = run_command("gh --version")
    if not success:
        issues.append("❌ GitHub CLI не установлен")
        return False, issues
    
    print(f"✅ GitHub CLI установлен: {output.strip()}")
    
    # Проверяем авторизацию
    success, output = run_command("gh auth status")
    if not success:
        issues.append("❌ GitHub CLI не авторизован")
    else:
        print("✅ GitHub CLI авторизован")
    
    return len(issues) == 0, issues

def validate_tests() -> Tuple[bool, List[str]]:
    """Валидирует тесты."""
    print("🧪 Валидация тестов...")
    
    issues = []
    
    # Проверяем наличие тестов
    tests_dir = project_root / 'tests'
    if not tests_dir.exists():
        issues.append("❌ Папка tests не найдена")
        return False, issues
    
    # Запускаем тесты
    success, output = run_command("python -m pytest tests/ -v --maxfail=1")
    if not success:
        issues.append("❌ Тесты не прошли")
        print(f"Ошибка тестов: {output}")
    else:
        print("✅ Тесты прошли успешно")
    
    return len(issues) == 0, issues

def validate_formatting() -> Tuple[bool, List[str]]:
    """Валидирует форматирование кода."""
    print("🎨 Валидация форматирования...")
    
    issues = []
    
    # Проверяем Black
    success, output = run_command("black --check src/ tests/")
    if not success:
        issues.append("❌ Код не отформатирован (Black)")
    else:
        print("✅ Код отформатирован (Black)")
    
    # Проверяем flake8
    success, output = run_command("flake8 src/ tests/")
    if not success:
        issues.append("❌ Ошибки стиля кода (flake8)")
    else:
        print("✅ Стиль кода корректен (flake8)")
    
    # Проверяем mypy
    success, output = run_command("mypy src/")
    if not success:
        issues.append("⚠️ Ошибки типов (mypy)")
    else:
        print("✅ Типы корректны (mypy)")
    
    return len(issues) == 0, issues

def show_validation_summary(results: Dict[str, Tuple[bool, List[str]]]):
    """Показывает сводку валидации."""
    print("\n📊 Сводка валидации:")
    print("=" * 25)
    
    total_checks = len(results)
    passed_checks = sum(1 for success, _ in results.values() if success)
    
    print(f"✅ Пройдено: {passed_checks}/{total_checks}")
    print(f"❌ Не пройдено: {total_checks - passed_checks}/{total_checks}")
    print()
    
    for check_name, (success, issues) in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {check_name}")
        
        if issues:
            for issue in issues:
                print(f"  {issue}")
        print()
    
    if passed_checks == total_checks:
        print("🎉 Все проверки пройдены! Система готова к работе.")
    else:
        print("⚠️ Некоторые проверки не пройдены. Исправьте ошибки и повторите валидацию.")
    
    print()

def main():
    """Основная функция валидации."""
    print("🔍 Валидация системы контроля версий WindSpotBot")
    print("=" * 55)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {project_root}")
    print()
    
    # Выполняем все проверки
    results = {
        "Git репозиторий": validate_git(),
        "Git hooks": validate_hooks(),
        "Pre-commit": validate_pre_commit(),
        "Скрипты": validate_scripts(),
        "Конфигурация": validate_config(),
        "Документация": validate_docs(),
        "Исходный код": validate_source(),
        "Зависимости": validate_dependencies(),
        "GitHub CLI": validate_github(),
        "Тесты": validate_tests(),
        "Форматирование": validate_formatting()
    }
    
    # Показываем сводку
    show_validation_summary(results)
    
    # Возвращаем код выхода
    total_checks = len(results)
    passed_checks = sum(1 for success, _ in results.values() if success)
    
    return 0 if passed_checks == total_checks else 1

if __name__ == "__main__":
    sys.exit(main())
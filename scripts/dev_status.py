#!/usr/bin/env python3
"""
Статус системы контроля версий для ветки dev.
Показывает текущее состояние и статистику.
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

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

def get_git_status() -> Dict[str, any]:
    """Получает статус Git."""
    status = {
        'current_branch': 'unknown',
        'is_dev_branch': False,
        'has_changes': False,
        'staged_files': [],
        'unstaged_files': [],
        'untracked_files': [],
        'last_commit': '',
        'commit_count': 0,
        'remote_url': '',
        'is_clean': False
    }
    
    # Текущая ветка
    success, output = run_command("git branch --show-current")
    if success:
        status['current_branch'] = output.strip()
        status['is_dev_branch'] = output.strip() == "dev"
    
    # Статус файлов
    success, output = run_command("git status --porcelain")
    if success:
        files = [line.strip() for line in output.strip().split('\n') if line.strip()]
        status['has_changes'] = len(files) > 0
        
        for line in files:
            if line.startswith('M '):
                status['staged_files'].append(line[2:])
            elif line.startswith(' M'):
                status['unstaged_files'].append(line[3:])
            elif line.startswith('??'):
                status['untracked_files'].append(line[3:])
    
    # Последний коммит
    success, output = run_command("git log -1 --oneline")
    if success:
        status['last_commit'] = output.strip()
    
    # Количество коммитов
    success, output = run_command("git rev-list --count HEAD")
    if success:
        status['commit_count'] = int(output.strip())
    
    # Удаленный репозиторий
    success, output = run_command("git remote get-url origin")
    if success:
        status['remote_url'] = output.strip()
    
    # Чистое состояние
    success, output = run_command("git diff --quiet")
    status['is_clean'] = success
    
    return status

def get_branch_info() -> Dict[str, any]:
    """Получает информацию о ветках."""
    info = {
        'local_branches': [],
        'remote_branches': [],
        'current_branch': 'unknown',
        'dev_exists': False,
        'main_exists': False
    }
    
    # Локальные ветки
    success, output = run_command("git branch --list")
    if success:
        info['local_branches'] = [line.strip().lstrip('* ') for line in output.strip().split('\n') if line.strip()]
    
    # Удаленные ветки
    success, output = run_command("git branch -r")
    if success:
        info['remote_branches'] = [line.strip() for line in output.strip().split('\n') if line.strip()]
    
    # Текущая ветка
    success, output = run_command("git branch --show-current")
    if success:
        info['current_branch'] = output.strip()
    
    # Проверяем наличие веток
    info['dev_exists'] = 'dev' in info['local_branches']
    info['main_exists'] = 'main' in info['local_branches']
    
    return info

def get_commit_history() -> List[Dict[str, str]]:
    """Получает историю коммитов."""
    success, output = run_command("git log --oneline -10")
    if not success:
        return []
    
    commits = []
    for line in output.strip().split('\n'):
        if line.strip():
            parts = line.split(' ', 1)
            if len(parts) == 2:
                commits.append({
                    'hash': parts[0],
                    'message': parts[1]
                })
    
    return commits

def get_hooks_status() -> Dict[str, bool]:
    """Проверяет статус Git hooks."""
    hooks_dir = project_root / '.git' / 'hooks'
    hooks = {
        'pre_commit': False,
        'commit_msg': False,
        'post_commit': False,
        'pre_push': False
    }
    
    if hooks_dir.exists():
        hooks['pre_commit'] = (hooks_dir / 'pre-commit').exists()
        hooks['commit_msg'] = (hooks_dir / 'commit-msg').exists()
        hooks['post_commit'] = (hooks_dir / 'post-commit').exists()
        hooks['pre_push'] = (hooks_dir / 'pre-push').exists()
    
    return hooks

def get_pre_commit_status() -> Dict[str, any]:
    """Проверяет статус pre-commit."""
    status = {
        'installed': False,
        'version': '',
        'hooks_installed': False
    }
    
    # Проверяем установку
    success, output = run_command("pre-commit --version")
    if success:
        status['installed'] = True
        status['version'] = output.strip()
    
    # Проверяем установленные hooks
    success, output = run_command("pre-commit installed")
    if success:
        status['hooks_installed'] = True
    
    return status

def get_github_status() -> Dict[str, any]:
    """Проверяет статус GitHub."""
    status = {
        'cli_installed': False,
        'authenticated': False,
        'version': '',
        'username': ''
    }
    
    # Проверяем установку
    success, output = run_command("gh --version")
    if success:
        status['cli_installed'] = True
        status['version'] = output.strip()
    
    # Проверяем авторизацию
    success, output = run_command("gh auth status")
    if success:
        status['authenticated'] = True
        # Извлекаем имя пользователя
        for line in output.split('\n'):
            if 'Logged in as' in line:
                status['username'] = line.split('Logged in as ')[1].split(' ')[0]
                break
    
    return status

def get_scripts_status() -> Dict[str, bool]:
    """Проверяет статус скриптов."""
    scripts_dir = project_root / 'scripts'
    scripts = {
        'update_docs': False,
        'update_changelog': False,
        'commit_helper': False,
        'github_helper': False,
        'auto_commit': False,
        'dev_workflow': False,
        'dev_auto_commit': False,
        'version_manager': False,
        'dev_monitor': False,
        'dev_status': False
    }
    
    if scripts_dir.exists():
        for script in scripts:
            script_file = scripts_dir / f"{script}.py"
            scripts[script] = script_file.exists()
    
    return scripts

def print_status():
    """Выводит статус системы."""
    print("📊 Статус системы контроля версий WindSpotBot")
    print("=" * 50)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Директория: {project_root}")
    print()
    
    # Git статус
    git_status = get_git_status()
    print("🔧 Git статус:")
    print(f"  📁 Текущая ветка: {git_status['current_branch']}")
    print(f"  🌿 Ветка dev: {'✅' if git_status['is_dev_branch'] else '❌'}")
    print(f"  📝 Изменения: {'✅' if git_status['has_changes'] else '❌'}")
    print(f"  🧹 Чистое состояние: {'✅' if git_status['is_clean'] else '❌'}")
    print(f"  📊 Коммитов: {git_status['commit_count']}")
    print(f"  🔗 Удаленный репозиторий: {git_status['remote_url'] or 'Не настроен'}")
    
    if git_status['has_changes']:
        print(f"  📁 Статус файлов:")
        if git_status['staged_files']:
            print(f"    - В индексе: {len(git_status['staged_files'])} файлов")
        if git_status['unstaged_files']:
            print(f"    - Изменены: {len(git_status['unstaged_files'])} файлов")
        if git_status['untracked_files']:
            print(f"    - Не отслеживаются: {len(git_status['untracked_files'])} файлов")
    
    print()
    
    # Информация о ветках
    branch_info = get_branch_info()
    print("🌿 Ветки:")
    print(f"  📁 Локальные: {', '.join(branch_info['local_branches'])}")
    print(f"  🌐 Удаленные: {len(branch_info['remote_branches'])} веток")
    print(f"  🌿 Dev существует: {'✅' if branch_info['dev_exists'] else '❌'}")
    print(f"  🌿 Main существует: {'✅' if branch_info['main_exists'] else '❌'}")
    print()
    
    # История коммитов
    commits = get_commit_history()
    if commits:
        print("📝 Последние коммиты:")
        for i, commit in enumerate(commits[:5], 1):
            print(f"  {i}. {commit['hash'][:8]} - {commit['message']}")
        print()
    
    # Git hooks
    hooks_status = get_hooks_status()
    print("🪝 Git hooks:")
    print(f"  pre-commit: {'✅' if hooks_status['pre_commit'] else '❌'}")
    print(f"  commit-msg: {'✅' if hooks_status['commit_msg'] else '❌'}")
    print(f"  post-commit: {'✅' if hooks_status['post_commit'] else '❌'}")
    print(f"  pre-push: {'✅' if hooks_status['pre_push'] else '❌'}")
    print()
    
    # Pre-commit
    pre_commit_status = get_pre_commit_status()
    print("🪝 Pre-commit:")
    print(f"  Установлен: {'✅' if pre_commit_status['installed'] else '❌'}")
    print(f"  Версия: {pre_commit_status['version'] or 'Не установлен'}")
    print(f"  Hooks установлены: {'✅' if pre_commit_status['hooks_installed'] else '❌'}")
    print()
    
    # GitHub
    github_status = get_github_status()
    print("🔗 GitHub:")
    print(f"  CLI установлен: {'✅' if github_status['cli_installed'] else '❌'}")
    print(f"  Авторизован: {'✅' if github_status['authenticated'] else '❌'}")
    print(f"  Пользователь: {github_status['username'] or 'Не авторизован'}")
    print(f"  Версия: {github_status['version'] or 'Не установлен'}")
    print()
    
    # Скрипты
    scripts_status = get_scripts_status()
    print("📜 Скрипты:")
    for script, exists in scripts_status.items():
        print(f"  {script}: {'✅' if exists else '❌'}")
    print()
    
    # Рекомендации
    print("💡 Рекомендации:")
    
    if not git_status['is_dev_branch']:
        print("  ⚠️ Переключитесь на ветку dev: git checkout dev")
    
    if not git_status['remote_url']:
        print("  ⚠️ Настройте удаленный репозиторий: git remote add origin <URL>")
    
    if not pre_commit_status['installed']:
        print("  ⚠️ Установите pre-commit: pip install pre-commit")
    
    if not github_status['authenticated']:
        print("  ⚠️ Авторизуйтесь в GitHub: gh auth login")
    
    if git_status['has_changes']:
        print("  ℹ️ Есть несохраненные изменения, используйте: make dev-auto-commit")
    
    print()

def main():
    """Основная функция статуса."""
    print_status()
    return 0

if __name__ == "__main__":
    sys.exit(main())




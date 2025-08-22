#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Hooks 管理脚本

用于启用、禁用和管理Git钩子
"""

import os
import sys
import shutil
from pathlib import Path


class GitHooksManager:
    """Git钩子管理器"""
    
    def __init__(self):
        self.projectRoot = Path(__file__).parent.parent
        self.hooksDir = self.projectRoot / '.git' / 'hooks'
        self.backupDir = self.projectRoot / '.git' / 'hooks_backup'
        
    def enableHooks(self):
        """启用Git钩子"""
        if not self.hooksDir.exists():
            print("❌ Git hooks目录不存在")
            return False
            
        hooks = ['pre-commit', 'pre-push']
        enabled = []
        
        for hook in hooks:
            hookPath = self.hooksDir / hook
            if hookPath.exists() and os.access(hookPath, os.X_OK):
                enabled.append(hook)
                
        if enabled:
            print(f"✅ 已启用的Git钩子: {', '.join(enabled)}")
            return True
        else:
            print("❌ 没有找到可执行的Git钩子")
            return False
            
    def disableHooks(self):
        """禁用Git钩子"""
        if not self.hooksDir.exists():
            print("❌ Git hooks目录不存在")
            return False
            
        # 创建备份目录
        self.backupDir.mkdir(exist_ok=True)
        
        hooks = ['pre-commit', 'pre-push']
        disabled = []
        
        for hook in hooks:
            hookPath = self.hooksDir / hook
            backupPath = self.backupDir / f"{hook}.disabled"
            
            if hookPath.exists():
                shutil.move(str(hookPath), str(backupPath))
                disabled.append(hook)
                
        if disabled:
            print(f"✅ 已禁用的Git钩子: {', '.join(disabled)}")
            print(f"📁 备份位置: {self.backupDir}")
            return True
        else:
            print("ℹ️  没有找到需要禁用的Git钩子")
            return False
            
    def restoreHooks(self):
        """恢复Git钩子"""
        if not self.backupDir.exists():
            print("❌ 没有找到备份的Git钩子")
            return False
            
        hooks = ['pre-commit', 'pre-push']
        restored = []
        
        for hook in hooks:
            backupPath = self.backupDir / f"{hook}.disabled"
            hookPath = self.hooksDir / hook
            
            if backupPath.exists():
                shutil.move(str(backupPath), str(hookPath))
                os.chmod(hookPath, 0o755)  # 确保可执行
                restored.append(hook)
                
        if restored:
            print(f"✅ 已恢复的Git钩子: {', '.join(restored)}")
            return True
        else:
            print("ℹ️  没有找到需要恢复的Git钩子")
            return False
            
    def statusHooks(self):
        """显示Git钩子状态"""
        print("📋 Git钩子状态:")
        print("=" * 40)
        
        hooks = ['pre-commit', 'pre-push']
        
        for hook in hooks:
            hookPath = self.hooksDir / hook
            backupPath = self.backupDir / f"{hook}.disabled"
            
            if hookPath.exists() and os.access(hookPath, os.X_OK):
                status = "✅ 已启用"
            elif backupPath.exists():
                status = "⏸️  已禁用 (有备份)"
            else:
                status = "❌ 不存在"
                
            print(f"  {hook:12} : {status}")
            
    def testHooks(self):
        """测试Git钩子"""
        print("🧪 测试Git钩子...")
        
        # 测试pre-commit钩子
        preCommitPath = self.hooksDir / 'pre-commit'
        if preCommitPath.exists() and os.access(preCommitPath, os.X_OK):
            print("\n🔍 测试pre-commit钩子:")
            result = os.system(f"cd {self.projectRoot} && .git/hooks/pre-commit")
            if result == 0:
                print("✅ pre-commit钩子测试通过")
            else:
                print("❌ pre-commit钩子测试失败")
        else:
            print("⚠️  pre-commit钩子不存在或不可执行")
            
        print("\n💡 注意: pre-push钩子需要在实际推送时才会触发")


def main():
    """主函数"""
    manager = GitHooksManager()
    
    if len(sys.argv) < 2:
        print("Git Hooks 管理脚本")
        print("\n用法:")
        print("  python manage_git_hooks.py enable    # 启用Git钩子")
        print("  python manage_git_hooks.py disable   # 禁用Git钩子")
        print("  python manage_git_hooks.py restore   # 恢复Git钩子")
        print("  python manage_git_hooks.py status    # 查看钩子状态")
        print("  python manage_git_hooks.py test      # 测试钩子")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    
    if command == 'enable':
        manager.enableHooks()
    elif command == 'disable':
        manager.disableHooks()
    elif command == 'restore':
        manager.restoreHooks()
    elif command == 'status':
        manager.statusHooks()
    elif command == 'test':
        manager.testHooks()
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动测试监控脚本

监控源代码文件变化，自动运行相关测试
"""

import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class TestRunner(FileSystemEventHandler):
    """测试运行器，监控文件变化并运行测试"""
    
    def __init__(self):
        self.lastRunTime = 0
        self.debounceDelay = 2  # 防抖延迟（秒）
        self.projectRoot = Path(__file__).parent
        
    def on_modified(self, event):
        """文件修改时触发"""
        if event.is_directory:
            return
            
        # 只监控Python文件
        if not event.src_path.endswith('.py'):
            return
            
        # 忽略测试文件本身的变化
        if '/tests/' in event.src_path or event.src_path.endswith('_test.py'):
            return
            
        # 忽略临时文件和缓存文件
        if any(ignore in event.src_path for ignore in ['.pytest_cache', '__pycache__', '.pyc', '~']):
            return
            
        currentTime = time.time()
        if currentTime - self.lastRunTime < self.debounceDelay:
            return
            
        self.lastRunTime = currentTime
        self.runTests(event.src_path)
        
    def runTests(self, changedFile):
        """运行测试"""
        print(f"\n{'=' * 60}")
        print(f"📝 检测到文件变化: {changedFile}")
        print("🚀 开始运行自动测试...")
        print(f"{'=' * 60}")
        
        # 确定运行哪些测试
        testCommand = self.determineTestCommand(changedFile)
        
        try:
            # 运行测试
            result = subprocess.run(
                testCommand,
                cwd=self.projectRoot,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ 所有测试通过!")
                if result.stdout:
                    # 只显示测试结果摘要
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'passed' in line or 'failed' in line or 'error' in line:
                            print(f"   {line}")
            else:
                print("❌ 测试失败!")
                if result.stdout:
                    print("\n标准输出:")
                    print(result.stdout)
                if result.stderr:
                    print("\n错误输出:")
                    print(result.stderr)
                    
        except subprocess.TimeoutExpired:
            print("⏰ 测试超时 (60秒)")
        except Exception as e:
            print(f"❌ 运行测试时出错: {e}")
            
        print(f"{'=' * 60}\n")
        
    def determineTestCommand(self, changedFile):
        """根据变化的文件确定测试命令"""
        filePath = Path(changedFile)
        
        # 如果是UI层文件，运行UI测试
        if '/ui/' in str(filePath):
            return ['python', 'run_tests.py', '--ui']
            
        # 如果是业务逻辑层文件，运行集成测试
        elif '/business/' in str(filePath):
            return ['python', 'run_tests.py', '--integration']
            
        # 如果是数据层文件，运行单元测试
        elif '/data/' in str(filePath):
            return ['python', 'run_tests.py', '--unit']
            
        # 如果是基础设施层文件，运行快速测试
        elif '/infrastructure/' in str(filePath):
            return ['python', 'run_tests.py', '--fast']
            
        # 默认运行快速测试
        else:
            return ['python', 'run_tests.py', '--fast']


def main():
    """主函数"""
    print("🔍 启动自动测试监控...")
    print("监控目录: src/")
    print("按 Ctrl+C 停止监控\n")
    
    # 检查依赖
    try:
        import watchdog
        del watchdog  # 避免未使用警告
    except ImportError:
        print("❌ 缺少watchdog依赖，请安装:")
        print("pip install watchdog")
        sys.exit(1)
        
    # 检查测试脚本
    if not Path('run_tests.py').exists():
        print("❌ 找不到run_tests.py脚本")
        sys.exit(1)
        
    # 设置监控
    eventHandler = TestRunner()
    observer = Observer()
    
    # 监控src目录
    srcPath = Path('src')
    if srcPath.exists():
        observer.schedule(eventHandler, str(srcPath), recursive=True)
        print(f"✅ 已设置监控: {srcPath.absolute()}")
    else:
        print("⚠️  src目录不存在，监控当前目录")
        observer.schedule(eventHandler, '.', recursive=True)
        
    try:
        observer.start()
        print("🎯 监控已启动，等待文件变化...\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 停止监控")
        observer.stop()
        
    observer.join()
    print("👋 监控已停止")


if __name__ == '__main__':
    main()
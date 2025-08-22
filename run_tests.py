#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本

提供便捷的测试执行命令，支持不同类型的测试运行。

使用方法:
    python run_tests.py --help
    python run_tests.py --all
    python run_tests.py --unit
    python run_tests.py --integration
    python run_tests.py --ui
    python run_tests.py --coverage
"""

import argparse
import subprocess
import sys
from pathlib import Path


def runCommand(command, description):
    """执行命令并处理结果"""
    print(f"\n{'=' * 60}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(command)}")
    print(f"{'=' * 60}")
    
    try:
        subprocess.run(command, check=True, capture_output=False)
        print(f"\n✅ {description} - 成功完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - 执行失败 (退出码: {e.returncode})")
        return False
    except FileNotFoundError:
        print("\n❌ 错误: 找不到pytest命令，请确保已安装pytest")
        print("安装命令: pip install pytest pytest-qt")
        return False


def runAllTests():
    """运行所有测试"""
    command = ["pytest", "-v", "--tb=short"]
    return runCommand(command, "运行所有测试")


def runUnitTests():
    """运行单元测试"""
    command = ["pytest", "-v", "-m", "unit", "tests/unit/"]
    return runCommand(command, "运行单元测试")


def runIntegrationTests():
    """运行集成测试"""
    command = ["pytest", "-v", "-m", "integration", "tests/integration/"]
    return runCommand(command, "运行集成测试")


def runUiTests():
    """运行UI测试"""
    command = ["pytest", "-v", "-m", "ui", "tests/ui/"]
    return runCommand(command, "运行UI测试")


def runFastTests():
    """运行快速测试（跳过慢速测试）"""
    command = ["pytest", "-v", "-m", "not slow", "--tb=short"]
    return runCommand(command, "运行快速测试")


def runCoverageTests():
    """运行测试并生成覆盖率报告"""
    commands = [
        (["pytest", "--cov=src", "--cov-report=term-missing", "--cov-report=html"], 
         "运行测试并生成覆盖率报告")
    ]
    
    success = True
    for command, description in commands:
        if not runCommand(command, description):
            success = False
    
    if success:
        print("\n📊 覆盖率报告已生成:")
        print("  - 终端报告: 已显示在上方")
        print("  - HTML报告: htmlcov/index.html")
        
        # 尝试打开HTML报告
        html_report = Path("htmlcov/index.html")
        if html_report.exists():
            print(f"  - 文件路径: {html_report.absolute()}")
    
    return success


def runLinting():
    """运行代码质量检查"""
    commands = [
        (["black", "--check", "src/", "tests/"], "检查代码格式 (Black)"),
        (["pylint", "src/"], "运行代码质量检查 (Pylint)"),
        (["isort", "--check-only", "src/", "tests/"], "检查导入排序 (isort)")
    ]
    
    success = True
    for command, description in commands:
        if not runCommand(command, description):
            success = False
    
    return success


def runSpecificFile(filepath):
    """运行特定文件的测试"""
    if not Path(filepath).exists():
        print(f"❌ 错误: 文件不存在 - {filepath}")
        return False
    
    command = ["pytest", "-v", filepath]
    return runCommand(command, f"运行测试文件: {filepath}")


def checkEnvironment():
    """检查测试环境"""
    print("🔍 检查测试环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要的包
    required_packages = [
        ("pytest", "pytest"),
        ("pytest-qt", "pytestqt"), 
        ("PyQt6", "PyQt6"),
        ("qfluentwidgets", "qfluentwidgets")
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} - 已安装")
        except ImportError:
            print(f"❌ {package_name} - 未安装")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠️  缺少以下包: {', '.join(missing_packages)}")
        print("安装命令:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # 检查测试目录
    test_dirs = ["tests/unit", "tests/integration", "tests/ui", "tests/fixtures"]
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            print(f"✅ {test_dir} - 目录存在")
        else:
            print(f"❌ {test_dir} - 目录不存在")
    
    print("\n✅ 环境检查完成")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="MyQt6App 测试运行脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_tests.py --all                    # 运行所有测试
  python run_tests.py --unit                   # 只运行单元测试
  python run_tests.py --integration            # 只运行集成测试
  python run_tests.py --ui                     # 只运行UI测试
  python run_tests.py --fast                   # 运行快速测试
  python run_tests.py --coverage               # 运行测试并生成覆盖率报告
  python run_tests.py --lint                   # 运行代码质量检查
  python run_tests.py --file tests/unit/test_user_repository.py  # 运行特定文件
  python run_tests.py --check                  # 检查测试环境
        """
    )
    
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--ui", action="store_true", help="运行UI测试")
    parser.add_argument("--fast", action="store_true", help="运行快速测试（跳过慢速测试）")
    parser.add_argument("--coverage", action="store_true", help="运行测试并生成覆盖率报告")
    parser.add_argument("--lint", action="store_true", help="运行代码质量检查")
    parser.add_argument("--file", type=str, help="运行特定测试文件")
    parser.add_argument("--check", action="store_true", help="检查测试环境")
    
    args = parser.parse_args()
    
    # 如果没有提供参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    success = True
    
    if args.check:
        success = checkEnvironment() and success
    
    if args.all:
        success = runAllTests() and success
    
    if args.unit:
        success = runUnitTests() and success
    
    if args.integration:
        success = runIntegrationTests() and success
    
    if args.ui:
        success = runUiTests() and success
    
    if args.fast:
        success = runFastTests() and success
    
    if args.coverage:
        success = runCoverageTests() and success
    
    if args.lint:
        success = runLinting() and success
    
    if args.file:
        success = runSpecificFile(args.file) and success
    
    # 显示最终结果
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有操作成功完成！")
        sys.exit(0)
    else:
        print("💥 部分操作失败，请检查上面的错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
# MyQt6App Makefile
# 提供便捷的开发和测试命令

.PHONY: help install test test-unit test-integration test-ui test-fast test-coverage lint format clean check-env run watch hooks-enable hooks-disable hooks-status hooks-test

# 默认目标
help:
	@echo "MyQt6App 开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  install        - 安装项目依赖"
	@echo "  test           - 运行所有测试"
	@echo "  test-unit      - 运行单元测试"
	@echo "  test-integration - 运行集成测试"
	@echo "  test-ui        - 运行UI测试"
	@echo "  test-fast      - 运行快速测试（跳过慢速测试）"
	@echo "  test-coverage  - 运行测试并生成覆盖率报告"
	@echo "  lint           - 运行代码质量检查"
	@echo "  format         - 格式化代码"
	@echo "  clean          - 清理临时文件"
	@echo "  check-env      - 检查开发环境"
	@echo "  run            - 运行应用程序"
	@echo "  watch          - 启动文件监控自动测试"
	@echo "  hooks-enable   - 启用Git钩子"
	@echo "  hooks-disable  - 禁用Git钩子"
	@echo "  hooks-status   - 查看Git钩子状态"
	@echo "  hooks-test     - 测试Git钩子"
	@echo ""
	@echo "示例:"
	@echo "  make install   # 安装依赖"
	@echo "  make test      # 运行所有测试"
	@echo "  make watch     # 启动自动测试监控"
	@echo "  make lint      # 检查代码质量"

# 安装依赖
install:
	@echo "📦 安装项目依赖..."
	pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

# 安装开发依赖
install-dev:
	@echo "📦 安装开发依赖..."
	pip install -r requirements.txt
	pip install pytest pytest-qt pytest-cov black pylint isort
	@echo "✅ 开发依赖安装完成"

# 运行所有测试
test:
	@echo "🧪 运行所有测试..."
	python run_tests.py --all

# 运行单元测试
test-unit:
	@echo "🧪 运行单元测试..."
	python run_tests.py --unit

# 运行集成测试
test-integration:
	@echo "🧪 运行集成测试..."
	python run_tests.py --integration

# 运行UI测试
test-ui:
	@echo "🧪 运行UI测试..."
	python run_tests.py --ui

# 运行快速测试
test-fast:
	@echo "🧪 运行快速测试..."
	python run_tests.py --fast

# 运行测试并生成覆盖率报告
test-coverage:
	@echo "📊 运行测试并生成覆盖率报告..."
	python run_tests.py --coverage

# 运行代码质量检查
lint:
	@echo "🔍 运行代码质量检查..."
	python run_tests.py --lint

# 格式化代码
format:
	@echo "🎨 格式化代码..."
	black src/ tests/
	isort src/ tests/
	@echo "✅ 代码格式化完成"

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf dist/ 2>/dev/null || true
	rm -rf build/ 2>/dev/null || true
	@echo "✅ 清理完成"

# 检查开发环境
check-env:
	@echo "🔍 检查开发环境..."
	python run_tests.py --check

# 运行应用程序
run:
	@echo "🚀 启动应用程序..."
	cd src && python main.py

# 运行特定测试文件
test-file:
	@echo "🧪 运行特定测试文件..."
	@echo "使用方法: make test-file FILE=tests/unit/test_user_repository.py"
	@if [ -z "$(FILE)" ]; then \
		echo "❌ 错误: 请指定测试文件"; \
		echo "示例: make test-file FILE=tests/unit/test_user_repository.py"; \
	else \
		python run_tests.py --file $(FILE); \
	fi

# 开发环境设置
setup-dev: install-dev
	@echo "🛠️  设置开发环境..."
	@echo "✅ 开发环境设置完成"
	@echo ""
	@echo "下一步:"
	@echo "  1. 运行 'make check-env' 检查环境"
	@echo "  2. 运行 'make test' 验证测试框架"
	@echo "  3. 运行 'make run' 启动应用程序"

# 持续集成命令
ci: clean
	@echo "🔄 运行持续集成检查..."
	python run_tests.py --check
	python run_tests.py --lint
	python run_tests.py --fast
	@echo "✅ 持续集成检查完成"

# 完整检查（包括慢速测试）
full-check: clean
	@echo "🔍 运行完整检查..."
	python run_tests.py --check
	python run_tests.py --lint
	python run_tests.py --coverage

# 启动文件监控自动测试
watch:
	@echo "🔍 启动文件监控自动测试..."
	@echo "按 Ctrl+C 停止监控"
	python watch_tests.py

# Git钩子管理
hooks-enable:
	@echo "🔧 启用Git钩子..."
	python scripts/manage_git_hooks.py enable

hooks-disable:
	@echo "🔧 禁用Git钩子..."
	python scripts/manage_git_hooks.py disable

hooks-status:
	@echo "📋 查看Git钩子状态..."
	python scripts/manage_git_hooks.py status

hooks-test:
	@echo "🧪 测试Git钩子..."
	python scripts/manage_git_hooks.py test

# 自动化设置
setup-auto-test: install-dev hooks-enable
	@echo "🚀 自动化测试环境设置完成!"
	@echo "💡 现在你可以使用以下命令:"
	@echo "   make watch      # 启动文件监控"
	@echo "   git commit      # 提交时自动运行测试"
	@echo "   git push        # 推送时自动运行完整测试"
	@echo "✅ 完整检查完成"

# 发布前检查
pre-release: clean format lint test-coverage
	@echo "🚀 发布前检查完成"
	@echo "✅ 代码已准备好发布"
# 自动测试使用指南

本文档介绍如何使用项目中的自动化测试系统，包括文件监控、Git钩子和CI/CD流水线。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装基础依赖
make install

# 安装开发依赖（包括测试工具）
make install-dev
```

### 2. 设置自动化测试环境

```bash
# 一键设置自动化测试环境
make setup-auto-test
```

这个命令会：
- 安装所有开发依赖
- 启用Git钩子
- 配置自动测试环境

## 📁 文件监控自动测试

### 启动文件监控

```bash
# 使用Makefile命令
make watch

# 或直接运行脚本
python watch_tests.py
```

### 监控特性

- **智能监控**: 只监控Python源代码文件（`.py`）
- **防抖机制**: 避免频繁触发测试
- **智能测试选择**: 根据修改的文件类型选择相应的测试
  - `src/ui/` → 运行UI测试
  - `src/business/` → 运行集成测试
  - `src/data/` → 运行单元测试
  - `src/infrastructure/` → 运行快速测试
  - 其他文件 → 运行快速测试

### 停止监控

按 `Ctrl+C` 停止文件监控。

## 🔗 Git钩子自动测试

### Git钩子类型

1. **pre-commit钩子**: 在代码提交前运行
   - 运行快速测试（单元测试）
   - 基础代码风格检查
   - 测试失败时阻止提交

2. **pre-push钩子**: 在代码推送前运行
   - 运行完整测试套件
   - 代码质量检查
   - 测试覆盖率检查
   - 测试失败时阻止推送

### 管理Git钩子

```bash
# 查看钩子状态
make hooks-status

# 启用钩子
make hooks-enable

# 禁用钩子
make hooks-disable

# 测试钩子
make hooks-test
```

### 钩子工作流程

```bash
# 正常的Git工作流程
git add .
git commit -m "feat: 添加新功能"  # 触发pre-commit钩子
git push origin main              # 触发pre-push钩子
```

如果测试失败，Git操作会被阻止，你需要修复问题后重新提交。

## 🔄 CI/CD自动化

### GitHub Actions工作流

项目包含两个GitHub Actions工作流：

1. **快速测试** (`.github/workflows/test.yml`)
   - 在所有推送和PR时触发
   - 运行快速测试和基础检查
   - 提供快速反馈

2. **完整CI/CD流水线** (`.github/workflows/ci.yml`)
   - 在主分支推送和PR时触发
   - 包含代码质量检查、多版本测试、构建和部署
   - 支持多平台构建

### 工作流阶段

1. **代码质量检查**
   - Black代码格式检查
   - isort导入排序检查
   - Flake8代码风格检查
   - MyPy类型检查

2. **测试阶段**
   - 单元测试（多Python版本）
   - 集成测试
   - UI测试（仅主分支）
   - 测试覆盖率报告

3. **构建阶段**
   - 多平台构建（Ubuntu、Windows、macOS）
   - PyInstaller打包
   - 构建产物上传

4. **部署阶段**
   - 自动发布（标签推送时）
   - 部署到生产环境

## 🧪 测试命令参考

### 基础测试命令

```bash
# 运行所有测试
make test

# 运行特定类型的测试
make test-unit          # 单元测试
make test-integration   # 集成测试
make test-ui           # UI测试
make test-fast         # 快速测试

# 生成测试覆盖率报告
make test-coverage
```

### 使用测试脚本

```bash
# 直接使用测试脚本
python run_tests.py --help          # 查看帮助
python run_tests.py --fast          # 快速测试
python run_tests.py --all           # 所有测试
python run_tests.py --unit          # 单元测试
python run_tests.py --integration   # 集成测试
python run_tests.py --ui            # UI测试
python run_tests.py --coverage      # 覆盖率测试
python run_tests.py --lint          # 代码检查
```

## 🛠️ 配置文件

### pytest配置 (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test* *Tests
python_functions = test_* test*  # 支持camelCase命名
```

### 测试配置 (`tests/conftest.py`)

包含pytest fixtures和测试配置，支持：
- PyQt6应用程序测试
- 数据库测试fixtures
- 模拟对象配置

## 🔧 故障排除

### 常见问题

1. **文件监控不工作**
   ```bash
   # 检查watchdog是否安装
   pip install watchdog
   
   # 检查文件权限
   ls -la watch_tests.py
   ```

2. **Git钩子不执行**
   ```bash
   # 检查钩子权限
   ls -la .git/hooks/
   
   # 重新设置权限
   chmod +x .git/hooks/pre-commit
   chmod +x .git/hooks/pre-push
   ```

3. **测试失败**
   ```bash
   # 查看详细测试输出
   python run_tests.py --fast -v
   
   # 检查测试环境
   python -m pytest --collect-only
   ```

4. **CI/CD失败**
   - 检查GitHub Actions日志
   - 确保requirements.txt包含所有依赖
   - 检查测试在本地是否通过

### 调试技巧

1. **本地模拟CI环境**
   ```bash
   # 设置环境变量
   export QT_QPA_PLATFORM=offscreen
   
   # 运行测试
   python run_tests.py --all
   ```

2. **查看测试覆盖率**
   ```bash
   # 生成HTML覆盖率报告
   python run_tests.py --coverage
   open htmlcov/index.html
   ```

3. **性能分析**
   ```bash
   # 运行性能分析
   python -m pytest --durations=10 tests/
   ```

## 📚 最佳实践

### 开发工作流

1. **开发前**: 启动文件监控
   ```bash
   make watch
   ```

2. **开发中**: 编写代码，自动运行测试

3. **提交前**: 确保所有测试通过
   ```bash
   make test
   ```

4. **提交**: Git钩子自动运行测试
   ```bash
   git commit -m "feat: 新功能"
   ```

5. **推送**: 完整测试套件自动运行
   ```bash
   git push
   ```

### 测试编写建议

1. **遵循命名约定**: 使用camelCase命名测试方法
2. **添加适当的标记**: 使用`@pytest.mark.unit`等标记
3. **编写清晰的测试**: 测试应该易于理解和维护
4. **保持测试独立**: 测试之间不应该有依赖关系
5. **使用fixtures**: 复用测试数据和设置

### 性能优化

1. **并行测试**: 使用`pytest-xdist`并行运行测试
2. **测试分层**: 快速测试优先，慢速测试分离
3. **缓存依赖**: CI/CD中缓存Python依赖
4. **智能触发**: 只运行相关的测试

## 🎯 总结

自动化测试系统提供了三层保护：

1. **开发时**: 文件监控实时反馈
2. **提交时**: Git钩子质量检查
3. **集成时**: CI/CD完整验证

这确保了代码质量，减少了bug，提高了开发效率。

---

如有问题，请查看项目文档或提交issue。
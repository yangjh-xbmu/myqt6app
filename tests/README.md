# 测试文档

本项目采用分层测试架构，确保代码质量和功能正确性。

## 测试结构

```
tests/
├── __init__.py              # 测试模块初始化
├── conftest.py              # pytest配置和共享夹具
├── README.md                # 测试文档（本文件）
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_camel_case.py   # camelCase命名规范测试
│   └── test_user_repository.py  # 用户仓库单元测试
├── integration/             # 集成测试
│   ├── __init__.py
│   ├── test_qfluentwidgets.py   # qfluentwidgets组件集成测试
│   └── test_user_service.py     # 用户服务集成测试
├── ui/                      # UI测试
│   ├── __init__.py
│   └── test_main_window.py  # 主窗口UI测试
└── fixtures/                # 测试夹具和辅助工具
    ├── __init__.py
    └── test_helpers.py      # 测试辅助函数
```

## 测试类型

### 1. 单元测试 (Unit Tests)
- **目的**: 测试单个函数、方法或类的功能
- **特点**: 快速执行，隔离性强，使用模拟对象
- **标记**: `@pytest.mark.unit`
- **示例**: 测试数据仓库类的CRUD操作

### 2. 集成测试 (Integration Tests)
- **目的**: 测试多个组件之间的交互
- **特点**: 测试真实的组件协作，可能涉及数据库或外部服务
- **标记**: `@pytest.mark.integration`
- **示例**: 测试服务层与数据层的集成

### 3. UI测试 (UI Tests)
- **目的**: 测试用户界面组件和交互
- **特点**: 使用QtBot进行UI交互模拟
- **标记**: `@pytest.mark.ui`
- **示例**: 测试窗口创建、按钮点击、表单输入

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定类型的测试
```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 只运行UI测试
pytest -m ui
```

### 运行特定目录的测试
```bash
# 运行单元测试目录
pytest tests/unit/

# 运行集成测试目录
pytest tests/integration/

# 运行UI测试目录
pytest tests/ui/
```

### 运行特定文件的测试
```bash
pytest tests/unit/test_user_repository.py
```

### 运行特定测试方法
```bash
pytest tests/unit/test_user_repository.py::TestUserRepository::testCreateUser
```

### 详细输出
```bash
# 显示详细信息
pytest -v

# 显示测试覆盖率（需要安装pytest-cov）
pytest --cov=src

# 生成HTML覆盖率报告
pytest --cov=src --cov-report=html
```

## 测试配置

### pytest.ini
项目根目录的`pytest.ini`文件包含了pytest的详细配置，包括：
- 测试发现规则
- 输出格式配置
- 标记定义
- 警告过滤
- 日志配置

### pyproject.toml
`pyproject.toml`文件中的`[tool.pytest.ini_options]`部分包含了基本的pytest配置。

### conftest.py
包含了全局测试夹具和配置：
- `qtApp`: QApplication实例
- `qtBot`: QtBot实例用于UI测试
- `sampleUser`: 示例用户数据
- `mockDatabase`: 模拟数据库连接

## 编写测试的最佳实践

### 1. 命名规范
- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试方法: `test*`
- 使用camelCase命名风格

### 2. 测试结构
```python
class TestClassName:
    def setup_method(self):
        """每个测试方法前执行"""
        pass
    
    def test_method_name(self):
        """测试方法"""
        # Arrange - 准备测试数据
        # Act - 执行被测试的操作
        # Assert - 验证结果
        pass
    
    def teardown_method(self):
        """每个测试方法后执行"""
        pass
```

### 3. 使用标记
```python
@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.integration
def test_integration_workflow():
    pass

@pytest.mark.ui
def test_ui_interaction(qtBot):
    pass

@pytest.mark.slow
def test_time_consuming_operation():
    pass
```

### 4. 模拟和夹具
```python
# 使用模拟对象
from unittest.mock import Mock

def test_with_mock():
    mock_obj = Mock()
    mock_obj.method.return_value = "expected_result"
    # 测试代码

# 使用夹具
def test_with_fixture(sampleUser):
    assert sampleUser["username"] == "testUser"
```

### 5. UI测试
```python
def test_ui_component(qtApp, qtBot):
    widget = MyWidget()
    widget.show()
    
    # 点击按钮
    qtBot.mouseClick(widget.button, Qt.LeftButton)
    
    # 输入文本
    qtBot.keyClicks(widget.lineEdit, "test input")
    
    # 验证结果
    assert widget.label.text() == "expected text"
```

## 持续集成

在CI/CD流水线中，可以使用以下命令：

```bash
# 运行所有测试，跳过标记为skip_ci的测试
pytest -m "not skip_ci"

# 运行快速测试（跳过慢速测试）
pytest -m "not slow"

# 生成JUnit格式的测试报告
pytest --junitxml=test-results.xml
```

## 故障排除

### 常见问题

1. **导入错误**: 确保`src`目录在Python路径中
2. **Qt相关错误**: 确保安装了`pytest-qt`插件
3. **模块未找到**: 检查`conftest.py`中的路径配置
4. **测试超时**: 对于UI测试，可能需要增加超时时间

### 调试测试

```bash
# 在测试失败时进入调试器
pytest --pdb

# 显示本地变量
pytest -l

# 显示完整的回溯信息
pytest --tb=long
```

## 扩展测试

### 添加新的测试类型

1. 在相应目录创建测试文件
2. 使用适当的标记
3. 在`pytest.ini`中添加新的标记定义
4. 更新文档

### 性能测试

可以使用`pytest-benchmark`插件进行性能测试：

```python
def test_performance(benchmark):
    result = benchmark(expensive_function, arg1, arg2)
    assert result == expected_result
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_multiple_inputs(input, expected):
    assert process_input(input) == expected
```

## 测试覆盖率目标

- **单元测试覆盖率**: 目标 > 80%
- **集成测试覆盖率**: 目标 > 60%
- **整体覆盖率**: 目标 > 75%

定期检查测试覆盖率，确保关键功能得到充分测试。
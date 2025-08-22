"""pytest配置文件

包含全局测试配置和共享夹具
"""

import pytest
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def qtApp():
    """创建QApplication实例用于UI测试"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def qtBot(qtApp):
    """创建QtBot用于UI交互测试"""
    from pytestqt.qtbot import QtBot
    return QtBot(qtApp)


@pytest.fixture
def sampleUser():
    """示例用户数据"""
    return {
        "id": 1,
        "username": "testUser",
        "email": "test@example.com",
        "password": "testPassword123",
        "createdAt": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mockDatabase():
    """模拟数据库连接"""
    class MockDatabase:
        def __init__(self):
            self.connected = True
            self.data = {}
        
        def execute(self, query, params=None):
            return {"success": True, "data": []}
        
        def close(self):
            self.connected = False
    
    return MockDatabase()


@pytest.fixture(autouse=True)
def setupTestEnvironment():
    """自动设置测试环境"""
    # 测试前设置
    yield
    # 测试后清理
    pass
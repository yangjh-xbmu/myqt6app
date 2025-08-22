#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试辅助函数

提供测试中常用的辅助函数和工具
"""

import tempfile
from pathlib import Path
from PyQt6.QtCore import QTimer


def createTempFile(content="", suffix=".txt"):
    """创建临时文件
    
    Args:
        content: 文件内容
        suffix: 文件后缀
    
    Returns:
        临时文件路径
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


def createTempDir():
    """创建临时目录
    
    Returns:
        临时目录路径
    """
    return tempfile.mkdtemp()


def cleanupTempPath(path):
    """清理临时路径
    
    Args:
        path: 要清理的路径
    """
    path_obj = Path(path)
    if path_obj.is_file():
        path_obj.unlink()
    elif path_obj.is_dir():
        import shutil
        shutil.rmtree(path)


def waitForSignal(signal, timeout=5000):
    """等待信号触发
    
    Args:
        signal: Qt信号
        timeout: 超时时间（毫秒）
    
    Returns:
        是否在超时前收到信号
    """
    from PyQt6.QtCore import QEventLoop
    
    loop = QEventLoop()
    signal.connect(loop.quit)
    
    timer = QTimer()
    timer.timeout.connect(loop.quit)
    timer.start(timeout)
    
    loop.exec()
    
    return not timer.isActive()


def findWidget(parent, widgetType, objectName=None):
    """查找子控件
    
    Args:
        parent: 父控件
        widgetType: 控件类型
        objectName: 对象名称（可选）
    
    Returns:
        找到的控件或None
    """
    for child in parent.findChildren(widgetType):
        if objectName is None or child.objectName() == objectName:
            return child
    return None


def clickWidget(widget, qtBot):
    """点击控件
    
    Args:
        widget: 要点击的控件
        qtBot: QtBot实例
    """
    qtBot.mouseClick(widget, 1)  # 1 = Qt.LeftButton


def typeText(widget, text, qtBot):
    """在控件中输入文本
    
    Args:
        widget: 目标控件
        text: 要输入的文本
        qtBot: QtBot实例
    """
    widget.clear()
    qtBot.keyClicks(widget, text)


def assertWidgetVisible(widget, visible=True):
    """断言控件可见性
    
    Args:
        widget: 要检查的控件
        visible: 期望的可见性
    """
    assert widget.isVisible() == visible, f"控件可见性不符合预期: {visible}"


def assertWidgetEnabled(widget, enabled=True):
    """断言控件启用状态
    
    Args:
        widget: 要检查的控件
        enabled: 期望的启用状态
    """
    assert widget.isEnabled() == enabled, f"控件启用状态不符合预期: {enabled}"


def assertWidgetText(widget, expectedText):
    """断言控件文本
    
    Args:
        widget: 要检查的控件
        expectedText: 期望的文本
    """
    actualText = widget.text() if hasattr(widget, 'text') else str(widget)
    assert actualText == expectedText, f"控件文本不符合预期: 期望 '{expectedText}', 实际 '{actualText}'"


class MockObject:
    """通用模拟对象"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generateUserData(userId=1, username="testUser"):
        """生成用户测试数据"""
        return {
            "id": userId,
            "username": username,
            "email": f"{username}@example.com",
            "password": "testPassword123",
            "createdAt": "2024-01-01T00:00:00Z",
            "isActive": True
        }
    
    @staticmethod
    def generateUserList(count=5):
        """生成用户列表测试数据"""
        return [
            TestDataGenerator.generateUserData(i, f"user{i}")
            for i in range(1, count + 1)
        ]
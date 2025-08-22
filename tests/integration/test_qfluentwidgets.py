#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qfluentwidgets组件集成测试

测试qfluentwidgets组件的集成和交互
"""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import LineEdit
from qfluentwidgets import MessageBox
from qfluentwidgets import PrimaryPushButton
from qfluentwidgets import PushButton
from qfluentwidgets import Theme
from qfluentwidgets import TitleLabel
from qfluentwidgets import setTheme


class QFluentWidgetsWindowForTest(QMainWindow):
    """qfluentwidgets组件测试窗口"""

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        """初始化用户界面"""
        self.setWindowTitle("QFluentWidgets 组件测试")
        self.setGeometry(100, 100, 800, 600)

        # 设置主题
        setTheme(Theme.LIGHT)

        # 创建中央窗口部件
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # 创建布局
        layout = QVBoxLayout(centralWidget)

        # 添加标题
        titleLabel = TitleLabel("QFluentWidgets 组件测试")
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titleLabel)

        # 添加输入框
        self.lineEdit = LineEdit()
        self.lineEdit.setPlaceholderText("请输入测试文本")
        layout.addWidget(self.lineEdit)

        # 添加主要按钮
        primaryButton = PrimaryPushButton("主要按钮")
        primaryButton.clicked.connect(self.onPrimaryButtonClicked)
        layout.addWidget(primaryButton)

        # 添加普通按钮
        normalButton = PushButton("普通按钮")
        normalButton.clicked.connect(self.onNormalButtonClicked)
        layout.addWidget(normalButton)

        # 添加主题切换按钮
        themeButton = PushButton("切换主题")
        themeButton.clicked.connect(self.toggleTheme)
        layout.addWidget(themeButton)

        self.currentTheme = Theme.LIGHT

    def onPrimaryButtonClicked(self):
        """主要按钮点击事件"""
        text = self.lineEdit.text()
        if text:
            MessageBox("信息", f"您输入的文本是: {text}", self).exec()
        else:
            MessageBox("警告", "请先输入一些文本", self).exec()

    def onNormalButtonClicked(self):
        """普通按钮点击事件"""
        MessageBox("提示", "普通按钮被点击了", self).exec()

    def toggleTheme(self):
        """切换主题"""
        if self.currentTheme == Theme.LIGHT:
            setTheme(Theme.DARK)
            self.currentTheme = Theme.DARK
        else:
            setTheme(Theme.LIGHT)
            self.currentTheme = Theme.LIGHT


class TestQFluentWidgetsIntegration:
    """qfluentwidgets集成测试类"""

    @pytest.mark.integration
    def testWindowCreation(self, qtApp):  # pylint: disable=unused-argument  # pyright: ignore[reportUnusedParameter, reportUnusedParameter]
        """测试窗口创建"""
        window = QFluentWidgetsWindowForTest()
        assert window.windowTitle() == "QFluentWidgets 组件测试"
        assert window.centralWidget() is not None

    @pytest.mark.integration
    def testComponentsExist(self, qtApp):  # pylint: disable=unused-argument  # pyright: ignore[reportUnusedParameter]
        """测试组件存在性"""
        window = QFluentWidgetsWindowForTest()

        # 检查LineEdit存在
        assert hasattr(window, 'lineEdit')
        assert window.lineEdit is not None

        # 检查占位符文本
        assert window.lineEdit.placeholderText() == "请输入测试文本"

    @pytest.mark.integration
    def testThemeToggle(self, qtApp):  # pylint: disable=unused-argument  # pyright: ignore[reportUnusedParameter]
        """测试主题切换"""
        window = QFluentWidgetsWindowForTest()

        # 初始主题应该是LIGHT
        assert window.currentTheme == Theme.LIGHT

        # 切换主题
        window.toggleTheme()
        assert window.currentTheme == Theme.DARK

        # 再次切换
        window.toggleTheme()
        assert window.currentTheme == Theme.LIGHT

    @pytest.mark.integration
    def testButtonInteraction(self, qtApp, qtBot):  # pylint: disable=unused-argument  # pyright: ignore[reportUnusedParameter, reportUnusedParameter]
        """测试按钮交互"""
        window = QFluentWidgetsWindowForTest()
        window.show()

        # 测试输入文本
        window.lineEdit.setText("测试文本")
        assert window.lineEdit.text() == "测试文本"

        # 清空文本
        window.lineEdit.clear()
        assert window.lineEdit.text() == ""

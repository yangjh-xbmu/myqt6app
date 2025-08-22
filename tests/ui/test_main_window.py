#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口UI测试

测试主窗口的基本功能和UI组件
"""

import pytest
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from qfluentwidgets import TitleLabel, PrimaryPushButton


class MainWindowForTest(QMainWindow):
    """测试主窗口类"""

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        """初始化用户界面"""
        self.setWindowTitle("测试主窗口")
        self.setGeometry(100, 100, 800, 600)

        # 创建中央窗口部件
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # 创建布局
        layout = QVBoxLayout(centralWidget)

        # 添加简单标签
        label = QLabel("测试主窗口 - 如果看到这个说明基本UI正常")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)


class MainWindowWithMenuForTest(QMainWindow):
    """测试带菜单的主窗口类"""

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("测试带菜单的主窗口")
        self.setGeometry(100, 100, 800, 600)

        # 设置窗口字体
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        # 创建菜单栏
        self.createMenu()

        # 创建中央窗口部件
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # 创建主布局
        layout = QVBoxLayout(centralWidget)

        # 添加欢迎标题
        welcomeLabel = TitleLabel("测试主窗口")
        welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcomeLabel)

        # 添加测试按钮
        testButton = PrimaryPushButton("测试按钮")
        testButton.clicked.connect(self.testAction)
        layout.addWidget(testButton)

    def createMenu(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        fileMenu = menubar.addMenu('文件')

        # 测试动作
        testAction = fileMenu.addAction('测试')
        testAction.triggered.connect(self.testAction)

    def testAction(self):
        """测试动作"""
        print("测试动作被触发")


class MainWindowStepByStepForTest(QMainWindow):
    """逐步测试主窗口类"""

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        """初始化用户界面"""
        print("开始初始化UI...")

        # 设置窗口属性
        self.setWindowTitle("PyQt6 用户权限管理系统")
        self.setGeometry(100, 100, 1200, 800)
        print("窗口属性设置完成")

        # 设置窗口字体
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        print("字体设置完成")

        # 创建菜单栏
        print("开始创建菜单...")
        self.createMenu()
        print("菜单创建完成")

        # 创建中央窗口部件
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        print("中央窗口部件创建完成")

        # 创建主布局
        layout = QVBoxLayout(centralWidget)
        print("主布局创建完成")

        # 添加标题
        titleLabel = TitleLabel("用户权限管理系统")
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titleLabel)

        # 添加测试按钮
        testButton = PrimaryPushButton("测试功能")
        testButton.clicked.connect(self.testSlot)
        layout.addWidget(testButton)

        print("UI初始化完成")

    def createMenu(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        fileMenu = menubar.addMenu('文件')
        exitAction = fileMenu.addAction('退出')
        exitAction.triggered.connect(self.close)

        # 帮助菜单
        helpMenu = menubar.addMenu('帮助')
        aboutAction = helpMenu.addAction('关于')
        aboutAction.triggered.connect(self.testSlot)

    def testSlot(self):
        """测试槽函数"""
        print("测试槽函数被调用")


# 实际的测试用例
class TestMainWindowComponents:
    """主窗口组件测试类"""

    @pytest.mark.ui
    def testBasicMainWindow(self, qtApp):
        """测试基本主窗口创建"""
        window = MainWindowForTest()
        assert window.windowTitle() == "测试主窗口"
        assert window.centralWidget() is not None

    @pytest.mark.ui
    def testMainWindowWithMenu(self, qtApp):
        """测试带菜单的主窗口"""
        window = MainWindowWithMenuForTest()
        assert window.windowTitle() == "测试带菜单的主窗口"
        assert window.menuBar() is not None
        assert window.centralWidget() is not None

    @pytest.mark.ui
    def testStepByStepWindow(self, qtApp):
        """测试逐步创建的窗口"""
        window = MainWindowStepByStepForTest()
        assert window.windowTitle() == "PyQt6 用户权限管理系统"
        assert window.menuBar() is not None
        assert window.centralWidget() is not None

    @pytest.mark.ui
    def testWindowGeometry(self, qtApp):
        """测试窗口几何属性"""
        window = MainWindowForTest()
        geometry = window.geometry()
        assert geometry.width() == 800
        assert geometry.height() == 600

    @pytest.mark.ui
    def testWindowFont(self, qtApp):
        """测试窗口字体设置"""
        window = MainWindowWithMenuForTest()
        font = window.font()
        assert font.pointSize() == 10

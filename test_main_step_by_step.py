#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐步测试主窗口组件 - 用于定位段错误
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from qfluentwidgets import (
    setTheme, Theme, TitleLabel, PrimaryPushButton, PushButton
)

class TestMainWindowStepByStep(QMainWindow):
    """逐步测试主窗口"""
    
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

        # 添加欢迎标题
        print("开始创建欢迎标题...")
        welcomeLabel = TitleLabel("欢迎使用 PyQt6 用户权限管理系统")
        welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcomeLabel)
        print("欢迎标题创建完成")

        # 添加功能说明
        print("开始创建功能说明...")
        infoLabel = QLabel(
            "请使用上方菜单栏访问各项功能：\n\n"
            "• 用户管理：登录、注册、用户认证\n"
            "• 数据库管理：查看和管理用户数据\n"
            "• 开发工具：API测试、脚本管理\n"
            "• 设置：主题切换、应用配置\n"
            "• 帮助：文档、关于信息"
        )
        infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        infoLabel.setStyleSheet(
            "QLabel { "
            "color: #666; "
            "font-size: 14px; "
            "line-height: 1.6; "
            "padding: 20px; "
            "}"
        )
        layout.addWidget(infoLabel)
        print("功能说明创建完成")

        print("UI初始化完成")
    
    def createMenu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        print("菜单栏获取完成")

        # 用户管理菜单
        userMenu = menubar.addMenu('用户管理(&U)')
        print("用户管理菜单创建完成")

        loginAction = QAction('登录(&L)', self)
        loginAction.setShortcut('Ctrl+L')
        loginAction.setStatusTip('打开登录窗口')
        loginAction.triggered.connect(self.testSlot)
        userMenu.addAction(loginAction)
        print("登录菜单项创建完成")

        registerAction = QAction('注册(&R)', self)
        registerAction.setShortcut('Ctrl+R')
        registerAction.setStatusTip('打开注册窗口')
        registerAction.triggered.connect(self.testSlot)
        userMenu.addAction(registerAction)
        print("注册菜单项创建完成")

        # 设置菜单
        settingsMenu = menubar.addMenu('设置(&S)')
        print("设置菜单创建完成")

        settingsAction = QAction('应用设置(&P)', self)
        settingsAction.setShortcut('Ctrl+,')
        settingsAction.setStatusTip('打开应用程序设置')
        settingsAction.triggered.connect(self.testSlot)
        settingsMenu.addAction(settingsAction)
        print("设置菜单项创建完成")
    
    def testSlot(self):
        """测试槽函数"""
        print("菜单项被点击")
        QMessageBox.information(self, "测试", "菜单项工作正常")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    print("QApplication创建成功")
    
    window = TestMainWindowStepByStep()
    print("测试窗口创建成功")
    
    window.show()
    print("测试窗口已显示")
    
    sys.exit(app.exec())
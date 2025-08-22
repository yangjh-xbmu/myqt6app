#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口 - 集成所有功能的菜单式应用
"""

import sys
import subprocess
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMessageBox, QLabel
)
from PyQt6.QtGui import QAction, QFont
from qfluentwidgets import (
    setTheme, Theme, TitleLabel, PrimaryPushButton, PushButton
)

from ui.components.settings import SettingsWidget


class MainWindow(QMainWindow):
    """主应用程序窗口"""

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("PyQt6 用户权限管理系统")
        self.setGeometry(100, 100, 1200, 800)

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
        welcomeLabel = TitleLabel("欢迎使用 PyQt6 用户权限管理系统")
        welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcomeLabel)

        # 添加功能说明
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

        # 添加快速操作按钮
        buttonLayout = QHBoxLayout()

        loginBtn = PrimaryPushButton("用户登录")
        loginBtn.clicked.connect(self.openLogin)
        buttonLayout.addWidget(loginBtn)

        registerBtn = PushButton("用户注册")
        registerBtn.clicked.connect(self.openRegister)
        buttonLayout.addWidget(registerBtn)

        dbBtn = PushButton("数据库管理")
        dbBtn.clicked.connect(self.openDatabasePanel)
        buttonLayout.addWidget(dbBtn)

        testBtn = PushButton("API测试")
        testBtn.clicked.connect(self.openWorkerTest)
        buttonLayout.addWidget(testBtn)

        layout.addLayout(buttonLayout)
        layout.addStretch()

    def createMenu(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 用户管理菜单
        userMenu = menubar.addMenu('用户管理(&U)')

        loginAction = QAction('登录(&L)', self)
        loginAction.setShortcut('Ctrl+L')
        loginAction.setStatusTip('打开用户登录界面')
        loginAction.triggered.connect(self.openLogin)
        userMenu.addAction(loginAction)

        registerAction = QAction('注册(&R)', self)
        registerAction.setShortcut('Ctrl+R')
        registerAction.setStatusTip('打开用户注册界面')
        registerAction.triggered.connect(self.openRegister)
        userMenu.addAction(registerAction)

        userMenu.addSeparator()

        authAction = QAction('用户认证(&A)', self)
        authAction.setShortcut('Ctrl+A')
        authAction.setStatusTip('打开用户认证应用')
        authAction.triggered.connect(self.openUserAuth)
        userMenu.addAction(authAction)

        # 数据库管理菜单
        dbMenu = menubar.addMenu('数据库管理(&D)')

        viewRemoteAction = QAction('查看远程数据库(&R)', self)
        viewRemoteAction.setShortcut('Ctrl+Shift+R')
        viewRemoteAction.setStatusTip(
            '查看远程数据库中的用户信息'
        )
        viewRemoteAction.triggered.connect(self.viewRemoteDatabase)
        dbMenu.addAction(viewRemoteAction)

        # 开发工具菜单
        devMenu = menubar.addMenu('开发工具(&T)')

        workerTestAction = QAction('Worker API 测试(&W)', self)
        workerTestAction.setShortcut('Ctrl+T')
        workerTestAction.setStatusTip('打开 Worker API 测试工具')
        workerTestAction.triggered.connect(self.openWorkerTest)
        devMenu.addAction(workerTestAction)

        devMenu.addSeparator()

        scriptsAction = QAction('脚本目录(&S)', self)
        scriptsAction.setStatusTip('打开脚本管理目录')
        scriptsAction.triggered.connect(self.openScriptsDirectory)
        devMenu.addAction(scriptsAction)

        # 设置菜单
        settingsMenu = menubar.addMenu('设置(&S)')

        themeMenu = settingsMenu.addMenu('主题(&T)')

        lightThemeAction = QAction('浅色主题(&L)', self)
        lightThemeAction.triggered.connect(
            lambda: self.setTheme(Theme.LIGHT)
        )
        themeMenu.addAction(lightThemeAction)

        darkThemeAction = QAction('深色主题(&D)', self)
        darkThemeAction.triggered.connect(
            lambda: self.setTheme(Theme.DARK)
        )
        themeMenu.addAction(darkThemeAction)

        autoThemeAction = QAction('自动主题(&A)', self)
        autoThemeAction.triggered.connect(lambda: self.setTheme(Theme.AUTO))
        themeMenu.addAction(autoThemeAction)

        settingsMenu.addSeparator()

        settingsAction = QAction('应用设置(&P)', self)
        settingsAction.setShortcut('Ctrl+,')
        settingsAction.setStatusTip('打开应用程序设置')
        settingsAction.triggered.connect(self.openSettings)
        settingsMenu.addAction(settingsAction)

        # 帮助菜单
        helpMenu = menubar.addMenu('帮助(&H)')

        docsAction = QAction('文档(&D)', self)
        docsAction.setShortcut('F1')
        docsAction.setStatusTip('打开项目文档')
        docsAction.triggered.connect(self.openDocsDirectory)
        helpMenu.addAction(docsAction)

        helpMenu.addSeparator()

        aboutAction = QAction('关于(&A)', self)
        aboutAction.setStatusTip('关于本应用程序')
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)

    def openLogin(self):
        """打开登录窗口"""
        try:
            from ui.windows.login_window import LoginWindow
            self.loginWindow = LoginWindow()
            self.loginWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开登录窗口：{str(e)}")

    def openRegister(self):
        """打开注册窗口"""
        try:
            from ui.windows.register_window import RegisterWindow
            self.registerWindow = RegisterWindow()
            self.registerWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开注册窗口：{str(e)}")

    def openUserAuth(self):
        """打开用户认证应用"""
        try:
            from ui.windows.auth_window import AuthWindow as UserAuthApp
            self.userAuthWindow = UserAuthApp()
            self.userAuthWindow.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开用户认证应用：{str(e)}")

    def openDatabasePanel(self):
        """打开数据库管理面板"""
        QMessageBox.information(self, "数据库管理", "数据库管理面板正在开发中...")

    def viewRemoteDatabase(self):
        """查看远程数据库"""
        try:
            result = subprocess.run(
                [sys.executable, "scripts/view_users.py", "remote"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )

            if result.returncode == 0:
                QMessageBox.information(self, "远程数据库信息", result.stdout)
            else:
                QMessageBox.warning(self, "错误", f"查看失败：{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法查看远程数据库：{str(e)}")

    def openWorkerTest(self):
        """打开Worker测试工具"""
        try:
            from ui.windows.worker_test_window import WorkerTestWindow
            self.workerTestWindow = WorkerTestWindow()
            self.workerTestWindow.show()
        except Exception as e:
            QMessageBox.critical(
                self, "错误", f"无法打开Worker测试工具：{str(e)}"
            )

    def openSettings(self):
        """打开设置界面"""
        self.settingsWidget = SettingsWidget()
        self.settingsWidget.show()

    def setTheme(self, theme):
        """设置主题"""
        setTheme(theme)
        themeNames = {
            Theme.LIGHT: "浅色主题",
            Theme.DARK: "深色主题",
            Theme.AUTO: "自动主题"
        }
        QMessageBox.information(
            self, "主题设置",
            f"已切换到{themeNames.get(theme, '未知主题')}"
        )

    def openScriptsDirectory(self):
        """打开脚本目录"""
        try:
            scriptsPath = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "scripts"
            )
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", scriptsPath])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", scriptsPath])
            else:  # Linux
                subprocess.run(["xdg-open", scriptsPath])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开脚本目录：{str(e)}")

    def openDocsDirectory(self):
        """打开文档目录"""
        try:
            docsPath = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "docs"
            )
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", docsPath])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", docsPath])
            else:  # Linux
                subprocess.run(["xdg-open", docsPath])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文档目录：{str(e)}")

    def showAbout(self):
        """显示关于对话框"""
        aboutText = """
        <h2>PyQt6 用户权限管理系统</h2>
        <p><b>版本：</b>1.0.0</p>
        <p><b>开发团队：</b>基于 PyQt6 和 Cloudflare Workers 构建</p>
        
        <h3>主要功能：</h3>
        <ul>
        <li>用户注册和登录管理</li>
        <li>基于 Cloudflare D1 数据库的数据存储</li>
        <li>现代化的 Fluent Design UI</li>
        <li>完整的开发和测试工具</li>
        </ul>
        
        <h3>技术栈：</h3>
        <ul>
        <li>前端：PyQt6 + QFluentWidgets</li>
        <li>后端：Cloudflare Workers (Python)</li>
        <li>数据库：Cloudflare D1</li>
        </ul>
        """

        QMessageBox.about(self, "关于", aboutText)

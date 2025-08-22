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

from .login_window import LoginWindow
from .register_window import RegisterWindow
from .auth_window import AuthWindow as UserAuthApp
from ..components.database_management import DatabaseManagementWidget
from ..components.settings import SettingsWidget


class MainAppWithMenu(QMainWindow):
    """主应用程序窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("PyQt6 用户权限管理系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口字体
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        
        # 添加欢迎标题
        welcome_label = TitleLabel("欢迎使用 PyQt6 用户权限管理系统")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        # 添加功能说明
        info_label = QLabel(
            "请使用上方菜单栏访问各项功能：\n\n"
            "• 用户管理：登录、注册、用户认证\n"
            "• 数据库管理：查看和管理用户数据\n"
            "• 开发工具：API测试、脚本管理\n"
            "• 设置：主题切换、应用配置\n"
            "• 帮助：文档、关于信息"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet(
            "QLabel { "
            "color: #666; "
            "font-size: 14px; "
            "line-height: 1.6; "
            "padding: 20px; "
            "}"
        )
        layout.addWidget(info_label)
        
        # 添加快速操作按钮
        button_layout = QHBoxLayout()
        
        login_btn = PrimaryPushButton("用户登录")
        login_btn.clicked.connect(self.open_login)
        button_layout.addWidget(login_btn)
        
        register_btn = PushButton("用户注册")
        register_btn.clicked.connect(self.open_register)
        button_layout.addWidget(register_btn)
        
        db_btn = PushButton("数据库管理")
        db_btn.clicked.connect(self.open_database_panel)
        button_layout.addWidget(db_btn)
        
        test_btn = PushButton("API测试")
        test_btn.clicked.connect(self.open_worker_test)
        button_layout.addWidget(test_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 用户管理菜单
        user_menu = menubar.addMenu('用户管理(&U)')
        
        login_action = QAction('登录(&L)', self)
        login_action.setShortcut('Ctrl+L')
        login_action.setStatusTip('打开用户登录界面')
        login_action.triggered.connect(self.open_login)
        user_menu.addAction(login_action)
        
        register_action = QAction('注册(&R)', self)
        register_action.setShortcut('Ctrl+R')
        register_action.setStatusTip('打开用户注册界面')
        register_action.triggered.connect(self.open_register)
        user_menu.addAction(register_action)
        
        user_menu.addSeparator()
        
        auth_action = QAction('用户认证(&A)', self)
        auth_action.setShortcut('Ctrl+A')
        auth_action.setStatusTip('打开用户认证应用')
        auth_action.triggered.connect(self.open_user_auth)
        user_menu.addAction(auth_action)
        
        # 数据库管理菜单
        db_menu = menubar.addMenu('数据库管理(&D)')
        
        view_remote_action = QAction('查看远程数据库(&R)', self)
        view_remote_action.setShortcut('Ctrl+Shift+R')
        view_remote_action.setStatusTip(
            '查看远程数据库中的用户信息'
        )
        view_remote_action.triggered.connect(self.view_remote_database)
        db_menu.addAction(view_remote_action)
        
        view_local_action = QAction('查看本地数据库(&L)', self)
        view_local_action.setShortcut('Ctrl+Shift+L')
        view_local_action.setStatusTip(
            '查看本地数据库中的用户信息'
        )
        view_local_action.triggered.connect(self.view_local_database)
        db_menu.addAction(view_local_action)
        
        db_menu.addSeparator()
        
        db_panel_action = QAction('数据库管理面板(&P)', self)
        db_panel_action.setShortcut('Ctrl+D')
        db_panel_action.setStatusTip('打开数据库管理面板')
        db_panel_action.triggered.connect(self.open_database_panel)
        db_menu.addAction(db_panel_action)
        
        # 开发工具菜单
        dev_menu = menubar.addMenu('开发工具(&T)')
        
        worker_test_action = QAction('Worker API 测试(&W)', self)
        worker_test_action.setShortcut('Ctrl+T')
        worker_test_action.setStatusTip('打开 Worker API 测试工具')
        worker_test_action.triggered.connect(self.open_worker_test)
        dev_menu.addAction(worker_test_action)
        
        dev_menu.addSeparator()
        
        scripts_action = QAction('脚本目录(&S)', self)
        scripts_action.setStatusTip('打开脚本管理目录')
        scripts_action.triggered.connect(self.open_scripts_directory)
        dev_menu.addAction(scripts_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu('设置(&S)')
        
        theme_menu = settings_menu.addMenu('主题(&T)')
        
        light_theme_action = QAction('浅色主题(&L)', self)
        light_theme_action.triggered.connect(
            lambda: self.set_theme(Theme.LIGHT)
        )
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('深色主题(&D)', self)
        dark_theme_action.triggered.connect(
            lambda: self.set_theme(Theme.DARK)
        )
        theme_menu.addAction(dark_theme_action)
        
        auto_theme_action = QAction('自动主题(&A)', self)
        auto_theme_action.triggered.connect(lambda: self.set_theme(Theme.AUTO))
        theme_menu.addAction(auto_theme_action)
        
        settings_menu.addSeparator()
        
        settings_action = QAction('应用设置(&P)', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.setStatusTip('打开应用程序设置')
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        docs_action = QAction('文档(&D)', self)
        docs_action.setShortcut('F1')
        docs_action.setStatusTip('打开项目文档')
        docs_action.triggered.connect(self.open_docs_directory)
        help_menu.addAction(docs_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('关于(&A)', self)
        about_action.setStatusTip('关于本应用程序')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def open_login(self):
        """打开登录窗口"""
        try:
            self.login_window = LoginWindow()
            self.login_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开登录窗口：{str(e)}")
    
    def open_register(self):
        """打开注册窗口"""
        try:
            self.register_window = RegisterWindow()
            self.register_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开注册窗口：{str(e)}")
    
    def open_user_auth(self):
        """打开用户认证应用"""
        try:
            self.user_auth_window = UserAuthApp()
            self.user_auth_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开用户认证应用：{str(e)}")
    
    def view_remote_database(self):
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
    
    def view_local_database(self):
        """查看本地数据库"""
        try:
            result = subprocess.run(
                [sys.executable, "scripts/view_users.py", "local"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )
            
            if result.returncode == 0:
                QMessageBox.information(self, "本地数据库信息", result.stdout)
            else:
                QMessageBox.warning(self, "错误", f"查看失败：{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法查看本地数据库：{str(e)}")
    
    def open_database_panel(self):
        """打开数据库管理面板"""
        try:
            self.db_panel = DatabaseManagementWidget()
            self.db_panel.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开数据库管理面板：{str(e)}")
    
    def open_worker_test(self):
        """打开Worker测试工具"""
        try:
            from ui.windows.worker_test_window import WorkerTestWindow
            self.worker_test_window = WorkerTestWindow()
            self.worker_test_window.show()
        except Exception as e:
            QMessageBox.critical(
                self, "错误", f"无法打开Worker测试工具：{str(e)}"
            )
    
    def open_settings(self):
        """打开设置界面"""
        self.settings_widget = SettingsWidget()
        self.settings_widget.show()
    
    def set_theme(self, theme):
        """设置主题"""
        setTheme(theme)
        theme_names = {
            Theme.LIGHT: "浅色主题",
            Theme.DARK: "深色主题",
            Theme.AUTO: "自动主题"
        }
        QMessageBox.information(
            self, "主题设置", 
            f"已切换到{theme_names.get(theme, '未知主题')}"
        )
    
    def open_scripts_directory(self):
        """打开脚本目录"""
        try:
            scripts_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "scripts"
            )
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", scripts_path])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", scripts_path])
            else:  # Linux
                subprocess.run(["xdg-open", scripts_path])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开脚本目录：{str(e)}")
    
    def open_docs_directory(self):
        """打开文档目录"""
        try:
            docs_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "docs"
            )
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", docs_path])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["explorer", docs_path])
            else:  # Linux
                subprocess.run(["xdg-open", docs_path])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文档目录：{str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
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
        
        QMessageBox.about(self, "关于", about_text)
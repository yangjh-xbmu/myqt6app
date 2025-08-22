#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主应用程序 - 集成所有功能的菜单式应用
"""

import sys
import subprocess
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMessageBox, QLabel
)
from PyQt6.QtGui import QAction, QFont

# 导入 fluent-widgets 组件
from qfluentwidgets import (
    setTheme, Theme, TitleLabel, PrimaryPushButton, PushButton,
    TextEdit as FluentTextEdit
)

# 导入现有的功能模块
from src.ui.windows.login_window import LoginWindow
from src.ui.windows.register_window import RegisterWindow
from src.ui.windows.auth_window import UserAuthApp
from src.ui.components.database_management import DatabaseManagementWidget
from src.ui.components.settings import SettingsWidget


class MainAppWithMenu(QMainWindow):
    """主应用程序窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.create_menu()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("PyQt6 用户权限管理系统")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 添加欢迎信息
        welcome_layout = QVBoxLayout()
        
        title_label = QLabel("PyQt6 用户权限管理系统")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        welcome_layout.addWidget(title_label)
        
        subtitle_label = QLabel("请使用菜单栏选择功能")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(
            "color: #666; font-size: 16px; margin-top: 10px;"
        )
        welcome_layout.addWidget(subtitle_label)
        
        layout.addLayout(welcome_layout)
        layout.addStretch()
        
        # 创建各个功能界面（隐藏状态）
        self.login_interface = None
        self.register_interface = None
        self.db_management_widget = None
        self.worker_test_widget = None
        self.settings_widget = None
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 用户管理菜单
        user_menu = menubar.addMenu("用户管理")
        
        login_action = QAction("用户登录", self)
        login_action.triggered.connect(self.open_login)
        user_menu.addAction(login_action)
        
        register_action = QAction("用户注册", self)
        register_action.triggered.connect(self.open_register)
        user_menu.addAction(register_action)
        
        # 数据库管理菜单
        db_menu = menubar.addMenu("数据库管理")
        
        view_remote_action = QAction("查看远程数据库", self)
        view_remote_action.triggered.connect(self.view_remote_database)
        db_menu.addAction(view_remote_action)
        
        view_local_action = QAction("查看本地数据库", self)
        view_local_action.triggered.connect(self.view_local_database)
        db_menu.addAction(view_local_action)
        
        db_menu.addSeparator()
        
        db_manage_action = QAction("数据库管理面板", self)
        db_manage_action.triggered.connect(self.open_database_panel)
        db_menu.addAction(db_manage_action)
        
        # 开发工具菜单
        dev_menu = menubar.addMenu("开发工具")
        
        worker_test_action = QAction("Worker API 测试", self)
        worker_test_action.triggered.connect(self.open_worker_test)
        dev_menu.addAction(worker_test_action)
        
        dev_menu.addSeparator()
        
        scripts_action = QAction("打开脚本目录", self)
        scripts_action.triggered.connect(self.open_scripts_directory)
        dev_menu.addAction(scripts_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        
        app_settings_action = QAction("应用设置", self)
        app_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(app_settings_action)
        
        settings_menu.addSeparator()
        
        light_theme_action = QAction("浅色主题", self)
        light_theme_action.triggered.connect(lambda: setTheme(Theme.LIGHT))
        settings_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("深色主题", self)
        dark_theme_action.triggered.connect(lambda: setTheme(Theme.DARK))
        settings_menu.addAction(dark_theme_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("查看文档", self)
        docs_action.triggered.connect(self.open_docs_directory)
        help_menu.addAction(docs_action)
    
    def open_login(self):
        """打开登录窗口"""
        try:
            self.login_window = LoginWindow()
            self.login_window.show()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开登录窗口: {str(e)}")
    
    def open_register(self):
        """打开注册窗口"""
        try:
            self.register_window = RegisterWindow()
            self.register_window.show()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开注册窗口: {str(e)}")
    
    def view_remote_database(self):
        """查看远程数据库"""
        try:
            subprocess.run(
                ["python", "scripts/view_users.py"], 
                cwd=os.path.dirname(__file__)
            )
        except Exception as e:
            QMessageBox.warning(
                self, "错误", f"无法查看远程数据库: {str(e)}"
            )
    
    def view_local_database(self):
        """查看本地数据库"""
        try:
            subprocess.run(
                ["python", "scripts/view_users.py", "local"], 
                cwd=os.path.dirname(__file__)
            )
        except Exception as e:
            QMessageBox.warning(
                self, "错误", f"无法查看本地数据库: {str(e)}"
            )
    
    def open_database_panel(self):
        """打开数据库管理面板"""
        try:
            self.user_auth_app = UserAuthApp()
            self.user_auth_app.show()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开数据库管理面板: {str(e)}")
    
    def open_worker_test(self):
        """打开 Worker API 测试工具"""
        try:
            subprocess.run(
                ["python", "worker_test_app.py"], 
                cwd=os.path.dirname(__file__)
            )
        except Exception as e:
            QMessageBox.warning(
                self, "错误", f"无法打开测试工具: {str(e)}"
            )
    
    def open_settings(self):
        """打开设置面板"""
        QMessageBox.information(self, "设置", "设置功能正在开发中...")
    
    def set_theme(self, theme):
        """设置主题"""
        setTheme(theme)
        theme_map = {
            Theme.LIGHT: "浅色", 
            Theme.DARK: "深色", 
            Theme.AUTO: "自动"
        }
        theme_name = theme_map.get(theme, "未知")
        QMessageBox.information(
            self, "主题设置", f"已切换到{theme_name}主题"
        )
    
    def open_scripts_directory(self):
        """打开脚本目录"""
        scripts_path = os.path.join(os.path.dirname(__file__), "scripts")
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", scripts_path])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["explorer", scripts_path])
        else:  # Linux
            subprocess.run(["xdg-open", scripts_path])
    
    def open_docs_directory(self):
        """打开文档目录"""
        docs_path = os.path.join(os.path.dirname(__file__), "docs")
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", docs_path])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["explorer", docs_path])
        else:  # Linux
            subprocess.run(["xdg-open", docs_path])
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 PyQt6 用户权限管理系统",
            "PyQt6 用户权限管理系统 v1.0.0\n\n"
            "这是一个基于 PyQt6 和 Cloudflare Workers 的\n"
            "现代化用户权限管理应用程序。\n\n"
            "主要功能：\n"
            "• 用户注册和登录\n"
            "• 数据库管理工具\n"
            "• 开发测试工具\n"
            "• Fluent Design UI\n\n"
            "技术栈：\n"
            "• PyQt6 + QFluentWidgets\n"
            "• Cloudflare Workers Python\n"
            "• Cloudflare D1 数据库\n\n"
            "© 2025 开发团队"
        )


def main():
    """主函数"""
    # 设置高DPI缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("PyQt6 用户权限管理系统")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("开发团队")
    
    # 设置主题
    setTheme(Theme.LIGHT)
    
    # 创建并显示主窗口
    window = MainAppWithMenu()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
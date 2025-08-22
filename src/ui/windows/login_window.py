#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录窗口
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, CheckBox, HyperlinkButton, InfoBar,
    InfoBarPosition
)

from data.api.network_client import NetworkWorker


class LoginWindow(QWidget):
    """登录窗口"""
    
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle('用户登录')
        self.setFixedSize(400, 500)
        
        # 设置窗口居中
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = TitleLabel('用户登录')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 添加间距
        layout.addSpacing(20)
        
        # 用户名输入
        self.username_input = LineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        self.username_input.setClearButtonEnabled(True)
        layout.addWidget(self.username_input)
        
        # 密码输入
        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        layout.addWidget(self.password_input)
        
        # 记住密码复选框
        self.remember_checkbox = CheckBox('记住密码')
        layout.addWidget(self.remember_checkbox)
        
        # 登录按钮
        self.login_button = PrimaryPushButton('登录')
        self.login_button.clicked.connect(self.onLogin)
        layout.addWidget(self.login_button)
        
        # 添加间距
        layout.addSpacing(10)
        
        # 底部链接区域
        link_layout = QHBoxLayout()
        
        # 忘记密码链接
        forgot_link = HyperlinkButton(
            '忘记密码？', 
            'https://example.com/forgot-password'
        )
        link_layout.addWidget(forgot_link)
        
        link_layout.addStretch()
        
        # 注册链接
        register_link = HyperlinkButton(
            '没有账号？立即注册', 
            'https://example.com/register'
        )
        link_layout.addWidget(register_link)
        
        layout.addLayout(link_layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 设置回车键触发登录
        self.username_input.returnPressed.connect(self.onLogin)
        self.password_input.returnPressed.connect(self.onLogin)
    
    def onLogin(self):
        """处理登录"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # 验证输入
        if not username:
            self.show_error('请输入用户名')
            return
        
        if not password:
            self.show_error('请输入密码')
            return
        
        # 禁用登录按钮，防止重复提交
        self.login_button.setEnabled(False)
        self.login_button.setText('登录中...')
        
        # 创建网络请求线程
        self.worker = NetworkWorker(
            'https://pw.yangxz.top/login',
            {
                'username': username,
                'password': password
            }
        )
        
        # 连接信号
        self.worker.finished.connect(self.on_login_success)
        self.worker.error.connect(self.on_login_error)
        
        # 启动线程
        self.worker.start()
    
    def on_login_success(self, result):
        """登录成功处理"""
        self.login_button.setEnabled(True)
        self.login_button.setText('登录')
        
        # 显示成功信息
        InfoBar.success(
            title='登录成功',
            content=f'欢迎回来，{result.get("username", "用户")}！',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
        # 可以在这里添加登录成功后的逻辑
        # 比如关闭登录窗口，打开主界面等
        
    def on_login_error(self, error_msg):
        """登录失败处理"""
        self.login_button.setEnabled(True)
        self.login_button.setText('登录')
        
        self.show_error(f'登录失败：{error_msg}')
    
    def show_error(self, message):
        """显示错误信息"""
        InfoBar.error(
            title='错误',
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
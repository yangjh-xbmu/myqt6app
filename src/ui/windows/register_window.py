#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册窗口
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, InfoBar, InfoBarPosition
)

from data.api.network_client import NetworkWorker


class RegisterWindow(QWidget):
    """注册窗口"""
    
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle('用户注册')
        self.setFixedSize(400, 600)
        
        # 设置窗口居中
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = TitleLabel('用户注册')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 添加间距
        layout.addSpacing(20)
        
        # 用户名输入
        self.username_input = LineEdit()
        self.username_input.setPlaceholderText('请输入用户名（3-20个字符）')
        self.username_input.setClearButtonEnabled(True)
        layout.addWidget(self.username_input)
        
        # 邮箱输入
        self.email_input = LineEdit()
        self.email_input.setPlaceholderText('请输入邮箱地址')
        self.email_input.setClearButtonEnabled(True)
        layout.addWidget(self.email_input)
        
        # 密码输入
        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText('请输入密码（至少6位）')
        layout.addWidget(self.password_input)
        
        # 确认密码输入
        self.confirm_password_input = PasswordLineEdit()
        self.confirm_password_input.setPlaceholderText('请再次输入密码')
        layout.addWidget(self.confirm_password_input)
        
        # 注册按钮
        self.register_button = PrimaryPushButton('注册')
        self.register_button.clicked.connect(self.onRegister)
        layout.addWidget(self.register_button)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 设置回车键触发注册
        self.username_input.returnPressed.connect(self.onRegister)
        self.email_input.returnPressed.connect(self.onRegister)
        self.password_input.returnPressed.connect(self.onRegister)
        self.confirm_password_input.returnPressed.connect(self.onRegister)
    
    def onRegister(self):
        """处理注册"""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # 验证输入
        if not username:
            self.show_error('请输入用户名')
            return
        
        if len(username) < 3 or len(username) > 20:
            self.show_error('用户名长度应在3-20个字符之间')
            return
        
        if not email:
            self.show_error('请输入邮箱地址')
            return
        
        if '@' not in email or '.' not in email:
            self.show_error('请输入有效的邮箱地址')
            return
        
        if not password:
            self.show_error('请输入密码')
            return
        
        if len(password) < 6:
            self.show_error('密码长度至少6位')
            return
        
        if password != confirm_password:
            self.show_error('两次输入的密码不一致')
            return
        
        # 禁用注册按钮，防止重复提交
        self.register_button.setEnabled(False)
        self.register_button.setText('注册中...')
        
        # 创建网络请求线程
        self.worker = NetworkWorker(
            'https://pw.yangxz.top/register',
            {
                'username': username,
                'email': email,
                'password': password
            }
        )
        
        # 连接信号
        self.worker.finished.connect(self.on_register_success)
        self.worker.error.connect(self.on_register_error)
        
        # 启动线程
        self.worker.start()
    
    def on_register_success(self, result):
        """注册成功处理"""
        self.register_button.setEnabled(True)
        self.register_button.setText('注册')
        
        # 显示成功信息
        InfoBar.success(
            title='注册成功',
            content=f'欢迎加入，{result.get("username", "用户")}！',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
        # 清空表单
        self.username_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        
    def on_register_error(self, error_msg):
        """注册失败处理"""
        self.register_button.setEnabled(True)
        self.register_button.setText('注册')
        
        self.show_error(f'注册失败：{error_msg}')
    
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
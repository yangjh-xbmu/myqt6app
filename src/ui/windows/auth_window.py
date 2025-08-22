#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证窗口 - 集成登录和注册功能
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, CheckBox, HyperlinkButton,
    InfoBar, InfoBarPosition, Pivot
)

from data.api.network_client import NetworkWorker


class AuthWindow(QWidget):
    """用户认证窗口 - 包含登录和注册功能"""
    
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle('用户认证')
        self.setFixedSize(450, 650)
        
        # 设置窗口居中
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = TitleLabel('用户认证')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 创建选项卡
        self.pivot = Pivot()
        self.pivot.addItem(
            routeKey='login',
            text='登录',
            onClick=lambda: self.stackedWidget.setCurrentIndex(0)
        )
        self.pivot.addItem(
            routeKey='register', 
            text='注册',
            onClick=lambda: self.stackedWidget.setCurrentIndex(1)
        )
        layout.addWidget(self.pivot)
        
        # 创建堆叠窗口
        from qfluentwidgets import QStackedWidget
        self.stackedWidget = QStackedWidget()
        
        # 创建登录页面
        login_widget = self.create_login_widget()
        self.stackedWidget.addWidget(login_widget)
        
        # 创建注册页面
        register_widget = self.create_register_widget()
        self.stackedWidget.addWidget(register_widget)
        
        layout.addWidget(self.stackedWidget)
        
        self.setLayout(layout)
        
        # 设置默认页面
        self.pivot.setCurrentItem('login')
        self.stackedWidget.setCurrentIndex(0)
    
    def create_login_widget(self):
        """创建登录页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 用户名输入
        self.login_username_input = LineEdit()
        self.login_username_input.setPlaceholderText('请输入用户名或邮箱')
        self.login_username_input.setClearButtonEnabled(True)
        layout.addWidget(self.login_username_input)
        
        # 密码输入
        self.login_password_input = PasswordLineEdit()
        self.login_password_input.setPlaceholderText('请输入密码')
        layout.addWidget(self.login_password_input)
        
        # 记住密码选项
        self.remember_checkbox = CheckBox('记住密码')
        layout.addWidget(self.remember_checkbox)
        
        # 登录按钮
        self.login_button = PrimaryPushButton('登录')
        self.login_button.clicked.connect(self.onLogin)
        layout.addWidget(self.login_button)
        
        # 忘记密码链接
        forgot_link = HyperlinkButton(
            url='https://pw.yangxz.top/forgot-password',
            text='忘记密码？'
        )
        forgot_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(forgot_link)
        
        # 添加弹性空间
        layout.addStretch()
        
        widget.setLayout(layout)
        
        # 设置回车键触发登录
        self.login_username_input.returnPressed.connect(self.onLogin)
        self.login_password_input.returnPressed.connect(self.onLogin)
        
        return widget
    
    def create_register_widget(self):
        """创建注册页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 用户名输入
        self.register_username_input = LineEdit()
        self.register_username_input.setPlaceholderText(
            '请输入用户名（3-20个字符）'
        )
        self.register_username_input.setClearButtonEnabled(True)
        layout.addWidget(self.register_username_input)
        
        # 邮箱输入
        self.register_email_input = LineEdit()
        self.register_email_input.setPlaceholderText('请输入邮箱地址')
        self.register_email_input.setClearButtonEnabled(True)
        layout.addWidget(self.register_email_input)
        
        # 密码输入
        self.register_password_input = PasswordLineEdit()
        self.register_password_input.setPlaceholderText('请输入密码（至少6位）')
        layout.addWidget(self.register_password_input)
        
        # 确认密码输入
        self.register_confirm_password_input = PasswordLineEdit()
        self.register_confirm_password_input.setPlaceholderText(
            '请再次输入密码'
        )
        layout.addWidget(self.register_confirm_password_input)
        
        # 注册按钮
        self.register_button = PrimaryPushButton('注册')
        self.register_button.clicked.connect(self.onRegister)
        layout.addWidget(self.register_button)
        
        # 添加弹性空间
        layout.addStretch()
        
        widget.setLayout(layout)
        
        # 设置回车键触发注册
        self.register_username_input.returnPressed.connect(self.onRegister)
        self.register_email_input.returnPressed.connect(self.onRegister)
        self.register_password_input.returnPressed.connect(self.onRegister)
        self.register_confirm_password_input.returnPressed.connect(
            self.onRegister
        )
        
        return widget
    
    def onLogin(self):
        """处理登录"""
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()
        
        # 验证输入
        if not username:
            self.show_error('请输入用户名或邮箱')
            return
        
        if not password:
            self.show_error('请输入密码')
            return
        
        # 禁用登录按钮，防止重复提交
        self.login_button.setEnabled(False)
        self.login_button.setText('登录中...')
        
        # 创建网络请求线程
        self.login_worker = NetworkWorker(
            'https://pw.yangxz.top/login',
            {
                'username': username,
                'password': password
            }
        )
        
        # 连接信号
        self.login_worker.finished.connect(self.on_login_success)
        self.login_worker.error.connect(self.on_login_error)
        
        # 启动线程
        self.login_worker.start()
    
    def onRegister(self):
        """处理注册"""
        username = self.register_username_input.text().strip()
        email = self.register_email_input.text().strip()
        password = self.register_password_input.text().strip()
        confirm_password = self.register_confirm_password_input.text().strip()
        
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
        self.register_worker = NetworkWorker(
            'https://pw.yangxz.top/register',
            {
                'username': username,
                'email': email,
                'password': password
            }
        )
        
        # 连接信号
        self.register_worker.finished.connect(self.on_register_success)
        self.register_worker.error.connect(self.on_register_error)
        
        # 启动线程
        self.register_worker.start()
    
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
        
        # 清空密码（根据记住密码选项决定是否清空用户名）
        if not self.remember_checkbox.isChecked():
            self.login_username_input.clear()
        self.login_password_input.clear()
    
    def on_login_error(self, error_msg):
        """登录失败处理"""
        self.login_button.setEnabled(True)
        self.login_button.setText('登录')
        
        self.show_error(f'登录失败：{error_msg}')
    
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
        self.register_username_input.clear()
        self.register_email_input.clear()
        self.register_password_input.clear()
        self.register_confirm_password_input.clear()
        
        # 切换到登录页面
        self.pivot.setCurrentItem('login')
        self.stackedWidget.setCurrentIndex(0)
    
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
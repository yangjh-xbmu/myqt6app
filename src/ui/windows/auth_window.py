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
        loginWidget = self.createLoginWidget()
        self.stackedWidget.addWidget(loginWidget)

        # 创建注册页面
        registerWidget = self.createRegisterWidget()
        self.stackedWidget.addWidget(registerWidget)

        layout.addWidget(self.stackedWidget)

        self.setLayout(layout)

        # 设置默认页面
        self.pivot.setCurrentItem('login')
        self.stackedWidget.setCurrentIndex(0)

    def createLoginWidget(self):
        """创建登录页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # 用户名输入
        self.loginUsernameInput = LineEdit()
        self.loginUsernameInput.setPlaceholderText('请输入用户名或邮箱')
        self.loginUsernameInput.setClearButtonEnabled(True)
        layout.addWidget(self.loginUsernameInput)

        # 密码输入
        self.loginPasswordInput = PasswordLineEdit()
        self.loginPasswordInput.setPlaceholderText('请输入密码')
        layout.addWidget(self.loginPasswordInput)

        # 记住密码选项
        self.rememberCheckbox = CheckBox('记住密码')
        layout.addWidget(self.rememberCheckbox)

        # 登录按钮
        self.loginButton = PrimaryPushButton('登录')
        self.loginButton.clicked.connect(self.onLogin)
        layout.addWidget(self.loginButton)

        # 忘记密码链接
        forgotLink = HyperlinkButton('忘记密码？')
        forgotLink.setUrl('https://pw.yangxz.top/forgot-password')
        forgotLink.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(forgotLink)

        # 添加弹性空间
        layout.addStretch()

        widget.setLayout(layout)

        # 设置回车键触发登录
        self.loginUsernameInput.returnPressed.connect(self.onLogin)
        self.loginPasswordInput.returnPressed.connect(self.onLogin)

        return widget

    def createRegisterWidget(self):
        """创建注册页面"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # 用户名输入
        self.registerUsernameInput = LineEdit()
        self.registerUsernameInput.setPlaceholderText(
            '请输入用户名（3-20个字符）'
        )
        self.registerUsernameInput.setClearButtonEnabled(True)
        layout.addWidget(self.registerUsernameInput)

        # 邮箱输入
        self.registerEmailInput = LineEdit()
        self.registerEmailInput.setPlaceholderText('请输入邮箱地址')
        self.registerEmailInput.setClearButtonEnabled(True)
        layout.addWidget(self.registerEmailInput)

        # 密码输入
        self.registerPasswordInput = PasswordLineEdit()
        self.registerPasswordInput.setPlaceholderText('请输入密码（至少6位）')
        layout.addWidget(self.registerPasswordInput)

        # 确认密码输入
        self.registerConfirmPasswordInput = PasswordLineEdit()
        self.registerConfirmPasswordInput.setPlaceholderText(
            '请再次输入密码'
        )
        layout.addWidget(self.registerConfirmPasswordInput)

        # 注册按钮
        self.registerButton = PrimaryPushButton('注册')
        self.registerButton.clicked.connect(self.onRegister)
        layout.addWidget(self.registerButton)

        # 添加弹性空间
        layout.addStretch()

        widget.setLayout(layout)

        # 设置回车键触发注册
        self.registerUsernameInput.returnPressed.connect(self.onRegister)
        self.registerEmailInput.returnPressed.connect(self.onRegister)
        self.registerPasswordInput.returnPressed.connect(self.onRegister)
        self.registerConfirmPasswordInput.returnPressed.connect(
            self.onRegister
        )

        return widget

    def onLogin(self):
        """处理登录"""
        username = self.loginUsernameInput.text().strip()
        password = self.loginPasswordInput.text().strip()

        # 验证输入
        if not username:
            self.showError('请输入用户名或邮箱')
            return

        if not password:
            self.showError('请输入密码')
            return

        # 禁用登录按钮，防止重复提交
        self.loginButton.setEnabled(False)
        self.loginButton.setText('登录中...')

        # 创建网络请求线程
        self.loginWorker = NetworkWorker(
            'https://pw.yangxz.top/login',
            {
                'username': username,
                'password': password
            }
        )

        # 连接信号
        self.loginWorker.finished.connect(self.onLoginSuccess)
        self.loginWorker.error.connect(self.onLoginError)

        # 启动线程
        self.loginWorker.start()

    def onRegister(self):
        """处理注册"""
        username = self.registerUsernameInput.text().strip()
        email = self.registerEmailInput.text().strip()
        password = self.registerPasswordInput.text().strip()
        confirmPassword = self.registerConfirmPasswordInput.text().strip()

        # 验证输入
        if not username:
            self.showError('请输入用户名')
            return

        if len(username) < 3 or len(username) > 20:
            self.showError('用户名长度应在3-20个字符之间')
            return

        if not email:
            self.showError('请输入邮箱地址')
            return

        if '@' not in email or '.' not in email:
            self.showError('请输入有效的邮箱地址')
            return

        if not password:
            self.showError('请输入密码')
            return

        if len(password) < 6:
            self.showError('密码长度至少6位')
            return

        if password != confirmPassword:
            self.showError('两次输入的密码不一致')
            return

        # 禁用注册按钮，防止重复提交
        self.registerButton.setEnabled(False)
        self.registerButton.setText('注册中...')

        # 创建网络请求线程
        self.registerWorker = NetworkWorker(
            'https://pw.yangxz.top/register',
            {
                'username': username,
                'email': email,
                'password': password
            }
        )

        # 连接信号
        self.registerWorker.finished.connect(self.onRegisterSuccess)
        self.registerWorker.error.connect(self.onRegisterError)

        # 启动线程
        self.registerWorker.start()

    def onLoginSuccess(self, result):
        """登录成功处理"""
        self.loginButton.setEnabled(True)
        self.loginButton.setText('登录')

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
        if not self.rememberCheckbox.isChecked():
            self.loginUsernameInput.clear()
        self.loginPasswordInput.clear()

    def onLoginError(self, errorMsg):
        """登录失败处理"""
        self.loginButton.setEnabled(True)
        self.loginButton.setText('登录')

        self.showError(f'登录失败：{errorMsg}')

    def onRegisterSuccess(self, result):
        """注册成功处理"""
        self.registerButton.setEnabled(True)
        self.registerButton.setText('注册')

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
        self.registerUsernameInput.clear()
        self.registerEmailInput.clear()
        self.registerPasswordInput.clear()
        self.registerConfirmPasswordInput.clear()

        # 切换到登录页面
        self.pivot.setCurrentItem('login')
        self.stackedWidget.setCurrentIndex(0)

    def onRegisterError(self, errorMsg):
        """注册失败处理"""
        self.registerButton.setEnabled(True)
        self.registerButton.setText('注册')

        self.showError(f'注册失败：{errorMsg}')

    def showError(self, message):
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

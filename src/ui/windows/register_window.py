#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册窗口
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, InfoBar, InfoBarPosition,
    HyperlinkButton
)

from business.services.auth_service import AuthService
from infrastructure.config.app_config import AppConfig
from infrastructure.logging.logger import getLogger
from business.models.user import RegisterRequest


class RegisterWindow(QWidget):
    """注册窗口"""

    # 信号定义
    registerSuccess = pyqtSignal(dict)  # 注册成功信号
    switchToLogin = pyqtSignal()  # 切换到登录窗口信号

    def __init__(self):
        super().__init__()

        # 初始化服务
        self.authService = AuthService()
        self.config = AppConfig()
        self.logger = getLogger(__name__)

        # 连接认证服务信号
        self._connectAuthSignals()

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
        self.usernameInput = LineEdit()
        self.usernameInput.setPlaceholderText('请输入用户名（3-20个字符）')
        self.usernameInput.setClearButtonEnabled(True)
        layout.addWidget(self.usernameInput)

        # 邮箱输入
        self.emailInput = LineEdit()
        self.emailInput.setPlaceholderText('请输入邮箱地址')
        self.emailInput.setClearButtonEnabled(True)
        layout.addWidget(self.emailInput)

        # 密码输入
        self.passwordInput = PasswordLineEdit()
        self.passwordInput.setPlaceholderText('请输入密码（至少6位）')
        layout.addWidget(self.passwordInput)

        # 确认密码输入
        self.confirmPasswordInput = PasswordLineEdit()
        self.confirmPasswordInput.setPlaceholderText('请再次输入密码')
        layout.addWidget(self.confirmPasswordInput)

        # 注册按钮
        self.registerButton = PrimaryPushButton('注册')
        self.registerButton.clicked.connect(self.onRegister)
        layout.addWidget(self.registerButton)

        # 登录链接
        loginLayout = QHBoxLayout()
        loginLayout.addStretch()
        loginLink = HyperlinkButton('已有账号？立即登录')
        loginLink.setUrl('')
        loginLink.clicked.connect(self.switchToLogin.emit)
        loginLayout.addWidget(loginLink)
        loginLayout.addStretch()
        layout.addLayout(loginLayout)

        # 添加弹性空间
        layout.addStretch()

        self.setLayout(layout)

        # 设置回车键触发注册
        self.usernameInput.returnPressed.connect(self.onRegister)
        self.emailInput.returnPressed.connect(self.onRegister)
        self.passwordInput.returnPressed.connect(self.onRegister)
        self.confirmPasswordInput.returnPressed.connect(self.onRegister)

    def _connectAuthSignals(self):
        """连接认证服务信号"""
        self.authService.registerSuccess.connect(self._onAuthSuccess)
        self.authService.registerFailed.connect(self._onAuthFailed)

    def onRegister(self):
        """处理注册"""
        username = self.usernameInput.text().strip()
        email = self.emailInput.text().strip()
        password = self.passwordInput.text().strip()
        confirmPassword = self.confirmPasswordInput.text().strip()

        # 基本验证
        if not username or not email or not password:
            self.showError('请填写所有必填字段')
            return

        if password != confirmPassword:
            self.showError('两次输入的密码不一致')
            return

        try:
            # 创建注册请求对象
            registerRequest = RegisterRequest(
                username=username,
                email=email,
                password=password
            )

            # 设置加载状态
            self._setLoading(True)

            # 异步注册
            self.authService.register(registerRequest)

        except Exception as e:
            self.logger.error(f"注册请求创建失败: {str(e)}")
            self.showError(f'注册失败: {str(e)}')
            self._setLoading(False)

    def _onAuthSuccess(self, userData):
        """认证成功处理"""
        self._setLoading(False)

        # 显示成功信息
        InfoBar.success(
            title='注册成功',
            content=f'欢迎加入，{userData.get("username", "用户")}！',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

        # 清空表单
        self._clearForm()

        # 发射注册成功信号
        self.registerSuccess.emit(userData)

    def _onAuthFailed(self, errorMsg):
        """认证失败处理"""
        self._setLoading(False)
        self.showError(f'注册失败：{errorMsg}')

    def _setLoading(self, loading):
        """设置加载状态"""
        if loading:
            self.registerButton.setEnabled(False)
            self.registerButton.setText('注册中...')
        else:
            self.registerButton.setEnabled(True)
            self.registerButton.setText('注册')

    def _clearForm(self):
        """清空表单"""
        self.usernameInput.clear()
        self.emailInput.clear()
        self.passwordInput.clear()
        self.confirmPasswordInput.clear()

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

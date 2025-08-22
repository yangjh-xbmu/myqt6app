#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录窗口
"""

import asyncio
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    TitleLabel, LineEdit, PasswordLineEdit,
    PrimaryPushButton, CheckBox, HyperlinkButton, InfoBar,
    InfoBarPosition
)

from business.services.auth_service import AuthService
from infrastructure.config.app_config import AppConfig
from infrastructure.logging.logger import getLogger


class AsyncWorker(QThread):
    """异步工作线程"""
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, coro):
        super().__init__()
        self.coro = coro

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.coro)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()


class LoginWindow(QWidget):
    """登录窗口"""

    # 信号定义
    loginSuccess = pyqtSignal(dict)
    switchToRegister = pyqtSignal()
    switchToMain = pyqtSignal()

    def __init__(self, config_manager: Optional[AppConfig] = None):
        super().__init__()
        self.config = config_manager or AppConfig()
        self.logger = getLogger(__name__)
        self.authService = AuthService(self.config)

        # 工作线程
        self.worker: Optional[AsyncWorker] = None

        self.initUi()
        self.connectAuthSignals()
        self.loadSavedCredentials()

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
        self.usernameInput = LineEdit()
        self.usernameInput.setPlaceholderText('请输入用户名')
        self.usernameInput.setClearButtonEnabled(True)
        layout.addWidget(self.usernameInput)

        # 密码输入
        self.passwordInput = PasswordLineEdit()
        self.passwordInput.setPlaceholderText('请输入密码')
        layout.addWidget(self.passwordInput)

        # 记住密码复选框
        self.rememberCheckbox = CheckBox('记住密码')
        layout.addWidget(self.rememberCheckbox)

        # 登录按钮
        self.loginButton = PrimaryPushButton('登录')
        self.loginButton.clicked.connect(self.onLogin)
        layout.addWidget(self.loginButton)

        # 添加间距
        layout.addSpacing(10)

        # 底部链接区域
        linkLayout = QHBoxLayout()

        # 忘记密码链接
        forgotLink = HyperlinkButton(
            '忘记密码？',
            ''
        )
        forgotLink.clicked.connect(self.onForgotPasswordClicked)
        linkLayout.addWidget(forgotLink)

        linkLayout.addStretch()

        # 注册链接
        self.registerLink = HyperlinkButton(
            '没有账号？立即注册',
            ''
        )
        self.registerLink.clicked.connect(self.switchToRegister.emit)
        linkLayout.addWidget(self.registerLink)

        layout.addLayout(linkLayout)

        # 添加弹性空间
        layout.addStretch()

        self.setLayout(layout)

        # 设置回车键触发登录
        self.usernameInput.returnPressed.connect(self.onLogin)
        self.passwordInput.returnPressed.connect(self.onLogin)

    def connectAuthSignals(self):
        """连接认证服务信号"""
        self.authService.loginSuccess.connect(self.onAuthSuccess)
        self.authService.loginFailed.connect(self.onAuthFailed)
        self.authService.forgotPasswordSuccess.connect(
            self.onForgotPasswordSuccess)
        self.authService.forgotPasswordFailed.connect(
            self.onForgotPasswordFailed)

    def loadSavedCredentials(self):
        """加载保存的凭据"""
        try:
            savedUsername = self.config.get('auth.saved_username', '')
            if savedUsername:
                self.usernameInput.setText(savedUsername)
                self.rememberCheckbox.setChecked(True)
        except Exception as e:
            self.logger.warning(f"加载保存的凭据失败: {str(e)}")

    def saveCredentials(self):
        """保存凭据"""
        try:
            if self.rememberCheckbox.isChecked():
                self.config.set('auth.saved_username',
                                self.usernameInput.text())
            else:
                self.config.remove('auth.saved_username')
        except Exception as e:
            self.logger.warning(f"保存凭据失败: {str(e)}")

    def onLogin(self):
        """处理登录"""
        username = self.usernameInput.text().strip()
        password = self.passwordInput.text().strip()
        remember = self.rememberCheckbox.isChecked()

        # 验证输入
        if not username:
            self.showError('请输入用户名或邮箱')
            self.usernameInput.setFocus()
            return

        if not password:
            self.showError('请输入密码')
            self.passwordInput.setFocus()
            return

        # 设置加载状态
        self.setLoading(True)

        # 直接调用登录方法
        try:
            success = self.authService.login(username, password, remember)
            self.onWorkerFinished(success)
        except Exception as e:
            self.onWorkerError(str(e))

    @pyqtSlot(bool)
    def onWorkerFinished(self, success: bool):
        """工作线程完成"""
        self.setLoading(False)
        if success:
            self.saveCredentials()

    @pyqtSlot(str)
    def onWorkerError(self, error: str):
        """工作线程错误"""
        self.setLoading(False)
        self.showError(f"登录失败: {error}")

    @pyqtSlot(dict)
    def onAuthSuccess(self, result: dict):
        """认证成功处理"""
        user = result.get('user', {})
        username = user.get('username', '用户')

        self.logger.info("登录成功")

        # 显示成功信息
        InfoBar.success(
            title='登录成功',
            content=f'欢迎回来，{username}！',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

        # 发射登录成功信号
        self.loginSuccess.emit(result)

    @pyqtSlot(str)
    def onAuthFailed(self, error: str):
        """认证失败处理"""
        self.logger.warning(f"登录失败: {error}")
        self.showError(error)

    def setLoading(self, loading: bool):
        """设置加载状态"""
        self.loginButton.setEnabled(not loading)
        self.usernameInput.setEnabled(not loading)
        self.passwordInput.setEnabled(not loading)
        self.rememberCheckbox.setEnabled(not loading)

        if loading:
            self.loginButton.setText('登录中...')
        else:
            self.loginButton.setText('登录')

    def clearForm(self):
        """清空表单"""
        self.passwordInput.clear()
        if not self.rememberCheckbox.isChecked():
            self.usernameInput.clear()
        self.usernameInput.setFocus()

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

    def onForgotPasswordClicked(self):
        """忘记密码点击处理"""
        from qfluentwidgets import MessageBox

        # 创建输入对话框
        dialog = MessageBox(
            title='忘记密码',
            content='请输入您的邮箱地址，我们将发送重置密码的链接到您的邮箱。',
            parent=self
        )

        # 添加邮箱输入框
        emailInput = LineEdit()
        emailInput.setPlaceholderText('请输入邮箱地址')
        dialog.textLayout.addWidget(emailInput)

        # 连接确认按钮
        def onConfirm():
            email = emailInput.text().strip()
            if not email:
                InfoBar.warning(
                    title='提示',
                    content='请输入邮箱地址',
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return

            # 调用忘记密码服务
            self.authService.forgot_password(email)
            dialog.close()

        dialog.yesButton.clicked.connect(onConfirm)
        dialog.show()

    @pyqtSlot(str)
    def onForgotPasswordSuccess(self, message: str):
        """忘记密码成功处理"""
        InfoBar.success(
            title='发送成功',
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

    @pyqtSlot(str)
    def onForgotPasswordFailed(self, error: str):
        """忘记密码失败处理"""
        InfoBar.error(
            title='发送失败',
            content=error,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

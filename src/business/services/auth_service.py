#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证服务 - 处理登录、注册等认证相关业务逻辑
"""

from typing import Optional
from business.models.user import User, LoginRequest, RegisterRequest
from business.validators.user_validator import UserValidator
from data.api.auth_client import AuthClient
# 移除JWTManager导入，改为使用云端验证
from infrastructure.config.app_config import AppConfig
from infrastructure.logging.logger import getLogger
from business.services.session_manager import SessionManager
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class AuthService(QObject):
    """用户认证服务"""

    # 信号定义
    loginSuccess = pyqtSignal(dict)
    loginFailed = pyqtSignal(str)
    registerSuccess = pyqtSignal(dict)
    registerFailed = pyqtSignal(str)
    logoutSuccess = pyqtSignal()
    tokenRefreshed = pyqtSignal(str)
    sessionExpired = pyqtSignal()
    forgotPasswordSuccess = pyqtSignal(str)
    forgotPasswordFailed = pyqtSignal(str)
    resetPasswordSuccess = pyqtSignal(str)
    resetPasswordFailed = pyqtSignal(str)

    def __init__(self, configManager: Optional[AppConfig] = None):
        super().__init__()
        self.config = configManager or AppConfig()
        self.logger = getLogger('auth_service')
        self.validator = UserValidator()
        self.authClient = AuthClient()
        # 移除本地JWT管理器，改为使用云端验证

        # 会话管理器
        self.sessionManager = SessionManager()
        self._connectSessionSignals()

        # 自动刷新定时器
        self.autoRefreshTimer = QTimer()
        self.autoRefreshTimer.timeout.connect(self._autoRefreshToken)

        # 尝试恢复保存的会话
        self.tryAutoLogin()

    def _connectSessionSignals(self):
        """连接会话管理器信号"""
        self.sessionManager.sessionRestored.connect(
            self._onSessionRestored)
        self.sessionManager.sessionExpired.connect(
            self._onSessionExpired)
        self.sessionManager.autoLoginSuccess.connect(
            self._onAutoLoginSuccess)
        self.sessionManager.autoLoginFailed.connect(
            self._onAutoLoginFailed)

    def tryAutoLogin(self):
        """尝试自动登录"""
        try:
            if self.sessionManager.restoreSession():
                self.logger.info("自动登录成功")
                return True
            else:
                self.logger.debug("没有可恢复的会话")
                return False
        except Exception as e:
            self.logger.error(f"自动登录失败: {str(e)}")
            return False

    def _onSessionRestored(self, sessionData):
        """会话恢复处理"""
        try:
            userData = sessionData.get('user', {})
            self.logger.info(f"会话已恢复: {userData.get('username', 'Unknown')}")
            self.loginSuccess.emit(userData)
        except Exception as e:
            self.logger.error(f"处理会话恢复失败: {str(e)}")

    def _onSessionExpired(self):
        """会话过期处理"""
        self.logger.info("会话已过期")
        self.sessionExpired.emit()

    def _onAutoLoginSuccess(self, userData):
        """自动登录成功处理"""
        self.logger.info("自动登录成功")
        self.loginSuccess.emit(userData)

    def _onAutoLoginFailed(self, errorMsg):
        """自动登录失败处理"""
        self.logger.warning(f"自动登录失败: {errorMsg}")

    def login(self, username: str, password: str,
              remember: bool = False) -> bool:
        """用户登录

        Args:
            username: 用户名或邮箱
            password: 密码
            remember: 是否记住密码

        Returns:
            bool: 登录是否成功
        """
        try:
            # 创建登录请求
            loginRequest = LoginRequest(
                username=username,
                password=password,
                rememberMe=remember
            )

            # 验证输入
            validationErrors = self.validator.validateLoginRequest(
                loginRequest
            )
            if validationErrors:
                errorMsg = '; '.join(validationErrors)
                self.logger.warning(f"登录验证失败: {errorMsg}")
                self.loginFailed.emit(errorMsg)
                return False

            # 调用API
            authResponse = self.authClient.login(loginRequest)

            # 检查登录是否成功
            if authResponse.success:
                # 使用会话管理器开始会话
                self.sessionManager.startSession(
                    user=authResponse.user,
                    accessToken=authResponse.accessToken,
                    refreshToken=authResponse.refreshToken,
                    rememberMe=remember
                )

                # 启动自动刷新
                self._startAutoRefresh()

                self.logger.info(f"用户 {username} 登录成功")
                self.loginSuccess.emit(authResponse.toDict())
                return True
            else:
                # 登录失败
                errorMsg = authResponse.message or "登录失败"
                self.logger.warning(f"用户 {username} 登录失败: {errorMsg}")
                self.loginFailed.emit(errorMsg)
                return False

        except Exception as e:
            errorMsg = f"登录失败: {str(e)}"
            self.logger.error(errorMsg)
            self.loginFailed.emit(errorMsg)
            return False

    def register(self, registerRequest: RegisterRequest) -> bool:
        """用户注册

        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            confirm_password: 确认密码

        Returns:
            bool: 注册是否成功
        """
        try:
            # 验证输入
            validationErrors = self.validator.validateRegisterRequest(
                registerRequest
            )
            if validationErrors:
                errorMsg = '; '.join(validationErrors)
                self.logger.warning(f"注册验证失败: {errorMsg}")
                self.registerFailed.emit(errorMsg)
                return False

            # 调用API
            authResponse = self.authClient.register(registerRequest)

            self.logger.info(f"用户 {registerRequest.username} 注册成功")
            self.registerSuccess.emit(authResponse.toDict())
            return True

        except Exception as e:
            errorMsg = f"注册失败: {str(e)}"
            self.logger.error(errorMsg)
            self.registerFailed.emit(errorMsg)
            return False

    def logout(self) -> bool:
        """用户登出"""
        try:
            accessToken = self.sessionManager.getAccessToken()
            if accessToken:
                # 调用API登出
                self.authClient.logout(accessToken)

            # 结束会话
            self.sessionManager.endSession()

            # 停止自动刷新
            self.autoRefreshTimer.stop()

            self.logger.info("用户登出成功")
            self.logoutSuccess.emit()
            return True

        except Exception as e:
            self.logger.error(f"登出失败: {str(e)}")
            # 即使API调用失败，也清除本地状态
            self.sessionManager.endSession()
            self.autoRefreshTimer.stop()
            self.logoutSuccess.emit()
            return False

    def isLoggedIn(self) -> bool:
        """检查是否已登录"""
        return self.sessionManager.isActive()

    def getCurrentUser(self) -> Optional[User]:
        """获取当前用户"""
        return self.sessionManager.getCurrentUser()

    def getAccessToken(self) -> Optional[str]:
        """获取访问令牌"""
        return self.sessionManager.getAccessToken()

    def _startAutoRefresh(self):
        """启动自动刷新令牌"""
        accessToken = self.sessionManager.getAccessToken()
        if accessToken:
            # 使用固定间隔刷新令牌（每25分钟刷新一次）
            try:
                # 启动定时器，25分钟后刷新
                refreshInterval = 25 * 60 * 1000  # 25分钟转换为毫秒
                self.autoRefreshTimer.start(refreshInterval)
                self.logger.info("自动刷新定时器已启动")
            except Exception as e:
                self.logger.warning(f"设置自动刷新失败: {str(e)}")

    def _autoRefreshToken(self):
        """自动刷新令牌"""
        try:
            refreshToken = self.sessionManager.getRefreshToken()
            if refreshToken:
                # 使用会话管理器的刷新方法
                if self.sessionManager._refreshToken(refreshToken):
                    newToken = self.sessionManager.getAccessToken()
                    self.tokenRefreshed.emit(newToken)
                    self._startAutoRefresh()
                else:
                    self.logger.warning("令牌刷新失败")
                    self.sessionExpired.emit()
        except Exception as e:
            self.logger.error(f"自动刷新令牌失败: {str(e)}")
            self.sessionExpired.emit()

    def changePassword(self, oldPassword: str, newPassword: str,
                       confirmPassword: str) -> bool:
        """修改密码

        Args:
            oldPassword: 旧密码
            newPassword: 新密码
            confirmPassword: 确认新密码

        Returns:
            bool: 验证是否通过
        """
        if not self.isLoggedIn():
            return False

        # 验证新密码
        isValid, errorMsg = self.validator.validatePasswordChange(
            oldPassword, newPassword, confirmPassword
        )
        if not isValid:
            return False

        # TODO: 实现密码修改的网络请求
        return True

    def forgotPassword(self, email: str) -> bool:
        """忘记密码

        Args:
            email: 邮箱地址

        Returns:
            bool: 请求是否成功
        """
        try:
            # 验证邮箱格式
            if not self.validator.validateEmail(email):
                self.logger.warning(f"邮箱格式不正确: {email}")
                self.forgotPasswordFailed.emit("邮箱格式不正确")
                return False

            # 调用API
            authResponse = self.authClient.forgotPassword(email)

            if authResponse.success:
                self.logger.info(f"忘记密码请求成功: {email}")
                self.forgotPasswordSuccess.emit(authResponse.message)
                return True
            else:
                self.logger.warning(f"忘记密码请求失败: {authResponse.message}")
                self.forgotPasswordFailed.emit(authResponse.message)
                return False

        except Exception as e:
            errorMsg = f"忘记密码请求失败: {str(e)}"
            self.logger.error(errorMsg)
            self.forgotPasswordFailed.emit(errorMsg)
            return False

    def resetPassword(self, token: str, newPassword: str) -> bool:
        """重置密码

        Args:
            token: 重置令牌
            newPassword: 新密码

        Returns:
            bool: 重置是否成功
        """
        try:
            # 验证新密码
            if len(newPassword) < 6:
                self.logger.warning("新密码长度不足")
                self.resetPasswordFailed.emit("密码长度至少6位")
                return False

            # 调用API
            authResponse = self.authClient.resetPassword(
                token, newPassword)

            if authResponse.success:
                self.logger.info("密码重置成功")
                self.resetPasswordSuccess.emit(authResponse.message)
                return True
            else:
                self.logger.warning(f"密码重置失败: {authResponse.message}")
                self.resetPasswordFailed.emit(authResponse.message)
                return False

        except Exception as e:
            errorMsg = f"密码重置失败: {str(e)}"
            self.logger.error(errorMsg)
            self.resetPasswordFailed.emit(errorMsg)
            return False

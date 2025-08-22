#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话状态管理器
负责用户会话的持久化、自动登录和会话过期管理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from business.models.user import User
from infrastructure.config.app_config import AppConfig
from infrastructure.logging.logger import getLogger
from data.api.auth_client import AuthClient


class SessionManager(QObject):
    """会话状态管理器"""

    # 信号定义
    sessionRestored = pyqtSignal(dict)  # 会话恢复信号
    sessionExpired = pyqtSignal()  # 会话过期信号
    autoLoginSuccess = pyqtSignal(dict)  # 自动登录成功信号
    autoLoginFailed = pyqtSignal(str)  # 自动登录失败信号

    def __init__(self):
        super().__init__()

        # 初始化依赖
        self.config = AppConfig()
        self.logger = getLogger('session_manager')
        self.authClient = AuthClient()

        # 会话数据
        self.currentUser: Optional[User] = None
        self.accessToken: Optional[str] = None
        self.refreshToken: Optional[str] = None
        self.sessionData: Dict[str, Any] = {}

        # 会话文件路径
        self.sessionFile = os.path.join(
            self.config.get('app.data_dir', 'data'),
            'session.json'
        )

        # 自动刷新定时器
        self.refreshTimer = QTimer()
        self.refreshTimer.timeout.connect(self._checkTokenExpiry)

        # 会话检查定时器
        self.sessionTimer = QTimer()
        self.sessionTimer.timeout.connect(self._validateSession)

        self.logger.info("会话管理器初始化完成")

    def startSession(self, user: User, accessToken: str, refreshToken: str, rememberMe: bool = False):
        """开始新会话"""
        try:
            self.currentUser = user
            self.accessToken = accessToken
            self.refreshToken = refreshToken

            # 构建会话数据
            self.sessionData = {
                'user': user.toDict(),
                'accessToken': accessToken,
                'refreshToken': refreshToken,
                'loginTime': datetime.now().isoformat(),
                'rememberMe': rememberMe,
                'lastActivity': datetime.now().isoformat()
            }

            # 如果选择记住登录状态，保存到文件
            if rememberMe:
                self._saveSessionToFile()

            # 启动定时器
            self._startTimers()

            self.logger.info(f"用户 {user.username} 会话已开始")

        except Exception as e:
            self.logger.error(f"开始会话失败: {str(e)}")
            raise

    def endSession(self):
        """结束当前会话"""
        try:
            # 停止定时器
            self.refreshTimer.stop()
            self.sessionTimer.stop()

            # 清除会话数据
            self.currentUser = None
            self.accessToken = None
            self.refreshToken = None
            self.sessionData.clear()

            # 删除会话文件
            self._clearSessionFile()

            self.logger.info("会话已结束")

        except Exception as e:
            self.logger.error(f"结束会话失败: {str(e)}")

    def restoreSession(self) -> bool:
        """恢复保存的会话"""
        try:
            if not os.path.exists(self.sessionFile):
                self.logger.debug("没有找到保存的会话文件")
                return False

            with open(self.sessionFile, 'r', encoding='utf-8') as f:
                sessionData = json.load(f)

            # 验证会话数据
            if not self._validateSessionData(sessionData):
                self.logger.warning("会话数据验证失败")
                self._clearSessionFile()
                return False

            # 检查令牌是否过期（通过云端验证）
            accessToken = sessionData.get('accessToken')
            if not self._verifyTokenWithServer(accessToken):
                self.logger.info("访问令牌已过期或无效，尝试刷新")
                refreshToken = sessionData.get('refreshToken')
                if refreshToken and self._refreshToken(refreshToken):
                    # 刷新成功，重新验证
                    return self.restoreSession()
                return False

            # 恢复会话
            self.sessionData = sessionData
            self.accessToken = sessionData['accessToken']
            self.refreshToken = sessionData['refreshToken']
            self.currentUser = User.fromDict(sessionData['user'])

            # 更新最后活动时间
            self.sessionData['lastActivity'] = datetime.now().isoformat()
            self._saveSessionToFile()

            # 启动定时器
            self._startTimers()

            self.logger.info(f"会话已恢复: {self.currentUser.username}")
            self.sessionRestored.emit(self.sessionData)

            return True

        except Exception as e:
            self.logger.error(f"恢复会话失败: {str(e)}")
            self._clearSessionFile()
            return False

    def updateActivity(self):
        """更新用户活动时间"""
        if self.isActive():
            self.sessionData['lastActivity'] = datetime.now().isoformat()
            if self.sessionData.get('rememberMe', False):
                self._saveSessionToFile()

    def isActive(self) -> bool:
        """检查会话是否活跃"""
        return (self.currentUser is not None and
                self.accessToken is not None)

    def getCurrentUser(self) -> Optional[User]:
        """获取当前用户"""
        return self.currentUser

    def getAccessToken(self) -> Optional[str]:
        """获取访问令牌"""
        return self.accessToken

    def updateTokens(self, accessToken: str, refreshToken: str):
        """更新令牌"""
        self.accessToken = accessToken
        self.refreshToken = refreshToken

        if self.sessionData:
            self.sessionData['accessToken'] = accessToken
            self.sessionData['refreshToken'] = refreshToken

            if self.sessionData.get('rememberMe', False):
                self._saveSessionToFile()

    def _saveSessionToFile(self):
        """保存会话到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.sessionFile), exist_ok=True)

            with open(self.sessionFile, 'w', encoding='utf-8') as f:
                json.dump(self.sessionData, f, ensure_ascii=False, indent=2)

            self.logger.debug("会话已保存到文件")

        except Exception as e:
            self.logger.error(f"保存会话文件失败: {str(e)}")

    def _clearSessionFile(self):
        """清除会话文件"""
        try:
            if os.path.exists(self.sessionFile):
                os.remove(self.sessionFile)
                self.logger.debug("会话文件已删除")
        except Exception as e:
            self.logger.error(f"删除会话文件失败: {str(e)}")

    def _validateSessionData(self, sessionData: Dict[str, Any]) -> bool:
        """验证会话数据"""
        requiredFields = ['user', 'accessToken', 'refreshToken',
                          'loginTime']

        for field in requiredFields:
            if field not in sessionData:
                return False

        # 检查会话是否过期（默认30天）
        try:
            loginTime = datetime.fromisoformat(sessionData['loginTime'])
            maxAge = timedelta(days=self.config.get('auth.session_max_age', 30))

            if datetime.now() - loginTime > maxAge:
                self.logger.info("会话已过期")
                return False

        except (ValueError, KeyError):
            return False

        return True

    def _startTimers(self):
        """启动定时器"""
        # 每5分钟检查一次令牌过期
        self.refreshTimer.start(5 * 60 * 1000)

        # 每小时验证一次会话
        self.sessionTimer.start(60 * 60 * 1000)

    def _checkTokenExpiry(self):
        """检查令牌过期"""
        if not self.accessToken:
            return

        try:
            if not self._verifyTokenWithServer(self.accessToken):
                self.logger.info("访问令牌即将过期或已过期")
                # 尝试刷新令牌
                if (self.refreshToken and
                        self._refreshToken(self.refreshToken)):
                    self.logger.info("令牌刷新成功")
                else:
                    self.logger.warning("令牌刷新失败，会话将过期")
                    self.sessionExpired.emit()

        except Exception as e:
            self.logger.error(f"检查令牌过期失败: {str(e)}")

    def _validateSession(self):
        """验证当前会话"""
        if not self.isActive():
            return

        try:
            # 检查最后活动时间
            lastActivity = datetime.fromisoformat(self.sessionData.get('lastActivity', datetime.now().isoformat()))

            # 如果超过2小时无活动，标记会话为不活跃
            inactiveThreshold = timedelta(hours=2)
            if datetime.now() - lastActivity > inactiveThreshold:
                self.logger.info("会话因长时间无活动而过期")
                self.sessionExpired.emit()
                self.endSession()

        except Exception as e:
            self.logger.error(f"验证会话失败: {str(e)}")

    def _verifyTokenWithServer(self, token: str) -> bool:
        """通过服务器验证令牌

        Args:
            token: 要验证的令牌

        Returns:
            验证结果
        """
        try:
            if not token:
                return False

            # 使用AuthClient验证令牌
            authResponse = self.authClient.verifyToken(token)
            return authResponse.success

        except Exception as e:
            self.logger.error(f"服务器令牌验证失败: {str(e)}")
            return False

    def _refreshToken(self, refreshToken: str) -> bool:
        """刷新访问令牌

        Args:
            refreshToken: 刷新令牌

        Returns:
            刷新是否成功
        """
        try:
            # 设置刷新令牌并调用刷新API
            self.authClient.refreshToken = refreshToken
            authResponse = self.authClient.refreshAccessToken()

            if authResponse.success and authResponse.accessToken:
                # 更新令牌
                self.updateTokens(
                    authResponse.accessToken,
                    authResponse.refreshToken or refreshToken
                )
                return True
            else:
                self.logger.warning(f"令牌刷新失败: {authResponse.message}")
                return False

        except Exception as e:
            self.logger.error(f"刷新令牌失败: {str(e)}")
            return False

    def getRefreshToken(self) -> Optional[str]:
        """获取刷新令牌"""
        return self.refreshToken

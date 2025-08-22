#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证API客户端 - 数据访问层
提供与认证服务的HTTP通信接口
"""

import json
import time
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from infrastructure.config.app_config import AppConfig
from infrastructure.logging.logger import getLogger
from business.models.user import (
    User, LoginRequest, RegisterRequest, AuthResponse
)


class AuthAPIError(Exception):
    """认证API错误异常"""

    def __init__(self, message: str, statusCode: Optional[int] = None,
                 responseData: Optional[Dict[str, Any]] = None):
        self.message = message
        self.statusCode = statusCode
        self.responseData = responseData or {}
        super().__init__(message)


class AuthClient:
    """用户认证API客户端

    提供用户认证相关的API调用功能
    """

    def __init__(self, baseUrl: Optional[str] = None, timeout: int = 30,
                 maxRetries: int = 3, retryDelay: float = 1.0):
        """初始化认证客户端

        Args:
            baseUrl: API基础URL，如果为None则从配置获取
            timeout: 请求超时时间（秒）
            maxRetries: 最大重试次数
            retryDelay: 重试延迟时间（秒）
        """
        self.config = AppConfig()
        self.logger = getLogger(__name__)

        # 设置API基础URL
        if baseUrl:
            self.baseUrl = baseUrl
        else:
            defaultUrl = 'http://localhost:8000'
            self.baseUrl = self.config.get('api.baseUrl', defaultUrl)

        self.timeout = timeout
        self.maxRetries = maxRetries
        self.retryDelay = retryDelay
        self.sessionToken: Optional[str] = None
        self.refreshToken: Optional[str] = None

    def _makeRequest(
        self, method: str, endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        authRequired: bool = False
    ) -> Tuple[int, Dict[str, Any]]:
        """发送HTTP请求（带重试机制）

        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            headers: 请求头
            authRequired: 是否需要认证

        Returns:
            状态码和响应数据的元组

        Raises:
            AuthAPIError: API请求失败时抛出
        """
        url = urljoin(self.baseUrl, endpoint)

        # 准备请求头
        requestHeaders = {
            'Content-Type': 'application/json',
            'User-Agent': 'MyQt6App/1.0'
        }

        if headers:
            requestHeaders.update(headers)

        # 添加认证头
        if authRequired and self.sessionToken:
            authHeader = f'Bearer {self.sessionToken}'
            requestHeaders['Authorization'] = authHeader

        # 准备请求数据
        requestData = None
        if data:
            requestData = json.dumps(data).encode('utf-8')

        # 重试机制
        lastException = None
        for attempt in range(self.maxRetries + 1):
            try:
                # 创建请求
                request = Request(
                    url=url,
                    data=requestData,
                    headers=requestHeaders,
                    method=method
                )

                # 发送请求
                with urlopen(request, timeout=self.timeout) as response:
                    statusCode = response.getcode()
                    responseData = json.loads(response.read().decode('utf-8'))

                    self.logger.debug(
                        f"API请求成功: {method} {url} -> {statusCode}"
                    )

                    return statusCode, responseData

            except HTTPError as httpError:
                # HTTP错误不重试，直接处理
                try:
                    errorData = json.loads(httpError.read().decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    errorData = {'message': str(httpError)}

                self.logger.error(
                    f"API请求HTTP错误: {method} {url} -> {httpError.code}: {errorData}"
                )

                errorMsg = errorData.get('message', str(httpError))
                raise AuthAPIError(
                    f"HTTP {httpError.code}: {errorMsg}",
                    statusCode=httpError.code,
                    responseData=errorData
                )

            except (URLError, ConnectionError, TimeoutError) as networkError:
                lastException = networkError
                if attempt < self.maxRetries:
                    self.logger.warning(
                        f"API请求失败，第{attempt + 1}次重试: {method} {url} -> {networkError}"
                    )
                    time.sleep(self.retryDelay * (attempt + 1))  # 指数退避
                    continue
                else:
                    self.logger.error(
                        f"API请求重试{self.maxRetries}次后仍失败: "
                        f"{method} {url} -> {networkError}"
                    )
                    raise AuthAPIError(
                        f"网络连接错误（重试{self.maxRetries}次后失败）: {networkError}"
                    )

            except json.JSONDecodeError as jsonError:
                # JSON解析错误
                self.logger.error(f"API响应JSON解析错误: {jsonError}")
                raise AuthAPIError(f"响应数据格式错误: {jsonError}")

            except Exception as generalError:
                lastException = generalError
                if attempt < self.maxRetries:
                    self.logger.warning(
                        f"API请求异常，第{attempt + 1}次重试: {method} {url} -> {generalError}"
                    )
                    time.sleep(self.retryDelay)
                    continue
                else:
                    self.logger.error(
                        f"API请求重试{self.maxRetries}次后仍失败: "
                        f"{method} {url} -> {generalError}"
                    )
                    raise AuthAPIError(
                        f"请求失败（重试{self.maxRetries}次后失败）: {generalError}"
                    )

        # 如果所有重试都失败了
        if lastException:
            raise AuthAPIError(f"请求失败: {lastException}")

    def login(self, request: LoginRequest) -> AuthResponse:
        """用户登录

        Args:
            request: 登录请求数据

        Returns:
            认证响应

        Raises:
            AuthAPIError: 登录失败时抛出
        """
        try:
            self.logger.info(f"尝试登录用户: {request.username}")

            # 准备请求数据
            loginData = {
                'username': request.username,
                'password': request.password,
                'rememberMe': request.rememberMe
            }

            # 发送登录请求
            statusCode, responseData = self._makeRequest(
                'POST', '/login', data=loginData
            )

            if statusCode == 200 and 'user' in responseData:
                # 登录成功
                userData = responseData.get('user', {})
                user = User.fromDict(userData) if userData else None

                # 保存令牌
                self.sessionToken = responseData.get('sessionToken')
                self.refreshToken = responseData.get('refreshToken')

                self.logger.info(f"用户登录成功: {request.username}")

                return AuthResponse(
                    success=True,
                    message=responseData.get('message', '登录成功'),
                    user=user,
                    accessToken=self.sessionToken,
                    refreshToken=self.refreshToken,
                    expiresIn=responseData.get('expiresIn')
                )
            else:
                # 登录失败
                errorMessage = (responseData.get('error') or
                                responseData.get('message', '登录失败'))
                self.logger.warning(
                    f"用户登录失败: {request.username} - {errorMessage}"
                )

                return AuthResponse(
                    success=False,
                    message=errorMessage
                )

        except AuthAPIError:
            raise
        except Exception as loginError:
            self.logger.error(f"登录过程发生错误: {loginError}")
            return AuthResponse(
                success=False,
                message=f"登录过程发生错误: {loginError}"
            )

    def register(self, request: RegisterRequest) -> AuthResponse:
        """用户注册

        Args:
            request: 注册请求数据

        Returns:
            认证响应

        Raises:
            AuthAPIError: 注册失败时抛出
        """
        try:
            self.logger.info(f"尝试注册用户: {request.username}")

            # 准备请求数据
            registerData = {
                'username': request.username,
                'email': request.email,
                'password': request.password
            }

            # 发送注册请求
            statusCode, responseData = self._makeRequest(
                'POST', '/register', data=registerData
            )

            if statusCode in [200, 201] and responseData.get('success'):
                # 注册成功
                userData = responseData.get('user', {})
                user = User.fromDict(userData) if userData else None

                # 保存令牌（如果返回）
                self.sessionToken = responseData.get('accessToken')
                self.refreshToken = responseData.get('refreshToken')

                self.logger.info(f"用户注册成功: {request.username}")

                return AuthResponse(
                    success=True,
                    message=responseData.get('message', '注册成功'),
                    user=user,
                    accessToken=self.sessionToken,
                    refreshToken=self.refreshToken,
                    expiresIn=responseData.get('expiresIn')
                )
            else:
                # 注册失败
                errorMessage = responseData.get('message', '注册失败')
                self.logger.warning(
                    f"用户注册失败: {request.username} - {errorMessage}"
                )

                return AuthResponse(
                    success=False,
                    message=errorMessage
                )

        except AuthAPIError:
            raise
        except Exception as registerError:
            self.logger.error(f"注册过程发生错误: {registerError}")
            return AuthResponse(
                success=False,
                message=f"注册过程发生错误: {registerError}"
            )

    def verifyToken(self, token: Optional[str] = None) -> AuthResponse:
        """验证令牌

        Args:
            token: 要验证的令牌，如果为None则使用当前会话令牌

        Returns:
            验证结果
        """
        try:
            verifyToken = token or self.sessionToken
            if not verifyToken:
                return AuthResponse(
                    success=False,
                    message="没有可验证的令牌"
                )

            self.logger.debug("验证令牌")

            # 发送验证请求
            headers = {'Authorization': f'Bearer {verifyToken}'}
            statusCode, responseData = self._makeRequest(
                'GET', '/api/auth/verify', headers=headers
            )

            if statusCode == 200 and responseData.get('success'):
                # 验证成功
                userData = responseData.get('user', {})
                user = User.fromDict(userData) if userData else None

                self.logger.debug("令牌验证成功")

                return AuthResponse(
                    success=True,
                    message=responseData.get('message', '令牌有效'),
                    user=user
                )
            else:
                # 验证失败
                self.logger.debug("令牌验证失败")
                return AuthResponse(
                    success=False,
                    message=responseData.get('message', '令牌无效')
                )

        except AuthAPIError:
            return AuthResponse(
                success=False,
                message="令牌验证失败"
            )
        except Exception as verifyError:
            self.logger.error(f"令牌验证过程发生错误: {verifyError}")
            return AuthResponse(
                success=False,
                message=f"令牌验证过程发生错误: {verifyError}"
            )

    def refreshAccessToken(self) -> AuthResponse:
        """刷新访问令牌

        Returns:
            刷新结果
        """
        try:
            if not self.refreshToken:
                return AuthResponse(
                    success=False,
                    message="没有刷新令牌"
                )

            self.logger.debug("刷新访问令牌")

            # 准备请求数据
            refreshData = {
                'refreshToken': self.refreshToken
            }

            # 发送刷新请求
            statusCode, responseData = self._makeRequest(
                'POST', '/api/auth/refresh', data=refreshData
            )

            if statusCode == 200 and responseData.get('success'):
                # 刷新成功
                self.sessionToken = responseData.get('accessToken')
                newRefreshToken = responseData.get('refreshToken')
                if newRefreshToken:
                    self.refreshToken = newRefreshToken

                self.logger.debug("访问令牌刷新成功")

                return AuthResponse(
                    success=True,
                    message=responseData.get('message', '令牌刷新成功'),
                    accessToken=self.sessionToken,
                    refreshToken=self.refreshToken,
                    expiresIn=responseData.get('expiresIn')
                )
            else:
                # 刷新失败
                self.logger.warning("访问令牌刷新失败")
                return AuthResponse(
                    success=False,
                    message=responseData.get('message', '令牌刷新失败')
                )

        except AuthAPIError:
            return AuthResponse(
                success=False,
                message="令牌刷新失败"
            )
        except Exception as refreshError:
            self.logger.error(f"令牌刷新过程发生错误: {refreshError}")
            return AuthResponse(
                success=False,
                message=f"令牌刷新过程发生错误: {refreshError}"
            )

    def logout(self) -> AuthResponse:
        """用户登出

        Returns:
            登出结果
        """
        try:
            if not self.sessionToken:
                return AuthResponse(
                    success=True,
                    message="已经处于登出状态"
                )

            self.logger.info("用户登出")

            # 发送登出请求
            try:
                statusCode, responseData = self._makeRequest(
                    'POST', '/api/auth/logout', authRequired=True
                )

                message = responseData.get('message', '登出成功')
            except AuthAPIError:
                # 即使登出请求失败，也清除本地令牌
                message = "登出成功（本地清除）"

            # 清除令牌
            self.sessionToken = None
            self.refreshToken = None

            self.logger.info("用户登出成功")

            return AuthResponse(
                success=True,
                message=message
            )

        except Exception as logoutError:
            self.logger.error(f"登出过程发生错误: {logoutError}")
            # 即使出错也清除本地令牌
            self.sessionToken = None
            self.refreshToken = None

            return AuthResponse(
                success=True,
                message="登出成功（本地清除）"
            )

    def isAuthenticated(self) -> bool:
        """检查是否已认证

        Returns:
            是否已认证
        """
        return bool(self.sessionToken)

    def getCurrentUser(self) -> Optional[User]:
        """获取当前用户信息

        Returns:
            当前用户信息，如果未认证则返回None
        """
        if not self.isAuthenticated():
            return None

        try:
            response = self.verifyToken()
            return response.user if response.success else None
        except Exception as getUserError:
            self.logger.error(f"获取当前用户信息失败: {getUserError}")
            return None

    def setTokens(self, accessToken: str,
                  refreshToken: Optional[str] = None):
        """设置令牌

        Args:
            accessToken: 访问令牌
            refreshToken: 刷新令牌
        """
        self.sessionToken = accessToken
        if refreshToken:
            self.refreshToken = refreshToken

    def clearTokens(self):
        """清除所有令牌"""
        self.sessionToken = None
        self.refreshToken = None

    def forgotPassword(self, email: str) -> AuthResponse:
        """忘记密码

        Args:
            email: 邮箱地址

        Returns:
            认证响应

        Raises:
            AuthAPIError: 请求失败时抛出
        """
        try:
            self.logger.info(f"发送忘记密码请求: {email}")

            # 准备请求数据
            forgotData = {
                'email': email
            }

            # 发送忘记密码请求
            statusCode, responseData = self._makeRequest(
                'POST', '/forgot-password', data=forgotData
            )

            if statusCode == 200:
                self.logger.info(f"忘记密码请求成功: {email}")
                return AuthResponse(
                    success=True,
                    message=responseData.get('message', '重置邮件已发送')
                )
            else:
                errorMessage = (responseData.get('error') or
                                responseData.get('message', '忘记密码请求失败'))
                self.logger.warning(
                    f"忘记密码请求失败: {email} - {errorMessage}"
                )
                return AuthResponse(
                    success=False,
                    message=errorMessage
                )

        except AuthAPIError:
            raise
        except Exception as forgotPasswordError:
            self.logger.error(f"忘记密码请求过程发生错误: {forgotPasswordError}")
            return AuthResponse(
                success=False,
                message=f"忘记密码请求过程发生错误: {forgotPasswordError}"
            )

    def resetPassword(self, token: str, newPassword: str) -> AuthResponse:
        """重置密码

        Args:
            token: 重置令牌
            newPassword: 新密码

        Returns:
            认证响应

        Raises:
            AuthAPIError: 请求失败时抛出
        """
        try:
            self.logger.info("发送重置密码请求")

            # 准备请求数据
            resetData = {
                'token': token,
                'newPassword': newPassword
            }

            # 发送重置密码请求
            statusCode, responseData = self._makeRequest(
                'POST', '/reset-password', data=resetData
            )

            if statusCode == 200:
                self.logger.info("密码重置成功")
                return AuthResponse(
                    success=True,
                    message=responseData.get('message', '密码重置成功')
                )
            else:
                errorMessage = (responseData.get('error') or
                                responseData.get('message', '密码重置失败'))
                self.logger.warning(f"密码重置失败: {errorMessage}")
                return AuthResponse(
                    success=False,
                    message=errorMessage
                )

        except AuthAPIError:
            raise
        except Exception as resetPasswordError:
            self.logger.error(f"密码重置过程发生错误: {resetPasswordError}")
            return AuthResponse(
                success=False,
                message=f"密码重置过程发生错误: {resetPasswordError}"
            )

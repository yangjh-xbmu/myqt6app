#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT令牌管理器 - 基础设施层
提供JWT令牌的生成、验证、解析和刷新功能
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

from infrastructure.config.app_config import config
from infrastructure.logging.logger import getLogger


class JWTManager:
    """JWT令牌管理器

    负责JWT令牌的生成、验证、解析和管理
    """

    def __init__(self):
        self.logger = getLogger('jwt_manager')
        self._secretKey = self._getSecretKey()
        self._algorithm = config.get('jwt.algorithm', 'HS256')
        self._accessTokenExpire = config.get(
            'jwt.accessTokenExpireMinutes', 30
        )
        self._refreshTokenExpire = config.get(
            'jwt.refreshTokenExpireDays', 7
        )

    def _getSecretKey(self) -> str:
        """获取JWT密钥

        Returns:
            JWT密钥字符串
        """
        # 从配置文件获取密钥
        secretKey = config.get('jwt.secretKey')

        if not secretKey:
            # 如果配置中没有密钥，生成一个默认密钥（仅用于开发环境）
            import secrets
            secretKey = secrets.token_urlsafe(32)
            self.logger.warning(
                "使用自动生成的JWT密钥，生产环境请配置固定密钥"
            )

        return secretKey

    def generateAccessToken(self, userData: Dict[str, Any]) -> str:
        """生成访问令牌

        Args:
            userData: 用户数据字典，包含用户ID、用户名等信息

        Returns:
            JWT访问令牌字符串
        """
        try:
            now = datetime.now(timezone.utc)
            expireTime = now + timedelta(minutes=self._accessTokenExpire)

            payload = {
                'userId': userData.get('id'),
                'username': userData.get('username'),
                'email': userData.get('email'),
                'iat': now,
                'exp': expireTime,
                'type': 'access'
            }

            token = jwt.encode(
                payload, self._secretKey, algorithm=self._algorithm
            )

            self.logger.info(f"生成访问令牌成功 - 用户: {userData.get('username')}")
            return token

        except Exception as e:
            self.logger.error(f"生成访问令牌失败: {e}")
            raise

    def generateRefreshToken(self, userData: Dict[str, Any]) -> str:
        """生成刷新令牌

        Args:
            userData: 用户数据字典

        Returns:
            JWT刷新令牌字符串
        """
        try:
            now = datetime.now(timezone.utc)
            expireTime = now + timedelta(days=self._refreshTokenExpire)

            payload = {
                'userId': userData.get('id'),
                'username': userData.get('username'),
                'iat': now,
                'exp': expireTime,
                'type': 'refresh'
            }

            token = jwt.encode(
                payload, self._secretKey, algorithm=self._algorithm
            )

            self.logger.info(f"生成刷新令牌成功 - 用户: {userData.get('username')}")
            return token

        except Exception as e:
            self.logger.error(f"生成刷新令牌失败: {e}")
            raise

    def verifyToken(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌

        Args:
            token: JWT令牌字符串

        Returns:
            解析后的令牌数据，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                self._secretKey,
                algorithms=[self._algorithm]
            )

            # 检查令牌类型
            tokenType = payload.get('type')
            if tokenType not in ['access', 'refresh']:
                self.logger.warning(f"无效的令牌类型: {tokenType}")
                return None

            self.logger.debug(f"令牌验证成功 - 用户: {payload.get('username')}")
            return payload

        except jwt.ExpiredSignatureError:
            self.logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"无效的令牌: {e}")
            return None
        except Exception as e:
            self.logger.error(f"令牌验证失败: {e}")
            return None

    def decodeToken(self, token: str) -> Optional[Dict[str, Any]]:
        """解析JWT令牌（不验证签名）

        Args:
            token: JWT令牌字符串

        Returns:
            解析后的令牌数据，解析失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            return payload
        except Exception as e:
            self.logger.error(f"令牌解析失败: {e}")
            return None

    def isTokenExpired(self, token: str) -> bool:
        """检查令牌是否过期

        Args:
            token: JWT令牌字符串

        Returns:
            True表示已过期，False表示未过期
        """
        payload = self.decodeToken(token)
        if not payload:
            return True

        expTimestamp = payload.get('exp')
        if not expTimestamp:
            return True

        expTime = datetime.fromtimestamp(expTimestamp, timezone.utc)
        currentTime = datetime.now(timezone.utc)

        return currentTime >= expTime

    def refreshAccessToken(self, refreshToken: str) -> Optional[str]:
        """使用刷新令牌生成新的访问令牌

        Args:
            refreshToken: 刷新令牌字符串

        Returns:
            新的访问令牌，失败返回None
        """
        try:
            # 验证刷新令牌
            payload = self.verifyToken(refreshToken)
            if not payload:
                self.logger.warning("刷新令牌验证失败")
                return None

            # 检查令牌类型
            if payload.get('type') != 'refresh':
                self.logger.warning("令牌类型不是刷新令牌")
                return None

            # 生成新的访问令牌
            userData = {
                'id': payload.get('userId'),
                'username': payload.get('username'),
                'email': payload.get('email')
            }

            newAccessToken = self.generateAccessToken(userData)

            self.logger.info(f"刷新访问令牌成功 - 用户: {userData.get('username')}")
            return newAccessToken

        except Exception as e:
            self.logger.error(f"刷新访问令牌失败: {e}")
            return None

    def getUserFromToken(self, token: str) -> Optional[Dict[str, Any]]:
        """从令牌中提取用户信息

        Args:
            token: JWT令牌字符串

        Returns:
            用户信息字典，失败返回None
        """
        payload = self.verifyToken(token)
        if not payload:
            return None

        return {
            'id': payload.get('userId'),
            'username': payload.get('username'),
            'email': payload.get('email')
        }


# 全局JWT管理器实例
jwtManager = JWTManager()

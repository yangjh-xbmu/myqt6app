#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模型
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """用户数据模型"""

    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    token: Optional[str] = None
    passwordHash: Optional[str] = None
    salt: Optional[str] = None
    isVerified: bool = False
    lastLogin: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    isActive: bool = True

    def __post_init__(self):
        """初始化后处理"""
        if self.createdAt is None:
            self.createdAt = datetime.now()
        if self.updatedAt is None:
            self.updatedAt = datetime.now()

    def isValid(self) -> bool:
        """检查用户数据是否有效"""
        return (
            self.username is not None and
            len(self.username.strip()) > 0 and
            self.email is not None and
            '@' in self.email
        )

    def toDict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'token': self.token,
            'createdAt': (
                self.createdAt.isoformat() if self.createdAt else None
            ),
            'updatedAt': (
                self.updatedAt.isoformat() if self.updatedAt else None
            ),
            'isActive': self.isActive
        }

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户对象

        Args:
            data: 用户数据字典

        Returns:
            用户对象
        """
        # 处理时间戳
        createdAt = None
        if data.get('createdAt'):
            createdAt = datetime.fromisoformat(data['createdAt'])

        updatedAt = None
        if data.get('updatedAt'):
            updatedAt = datetime.fromisoformat(data['updatedAt'])

        lastLogin = None
        if data.get('lastLogin'):
            lastLogin = datetime.fromisoformat(data['lastLogin'])

        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            email=data.get('email', ''),
            passwordHash=data.get('passwordHash', ''),
            salt=data.get('salt', ''),
            isActive=data.get('isActive', True),
            isVerified=data.get('isVerified', False),
            createdAt=createdAt,
            updatedAt=updatedAt,
            lastLogin=lastLogin,
            metadata=data.get('metadata', {})
        )

    def updateLoginTime(self) -> None:
        """更新最后登录时间"""
        self.lastLogin = datetime.now()
        self.updatedAt = datetime.now()

    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"User(id={self.id}, username='{self.username}', "
            f"email='{self.email}')"
        )

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (
            f"User(id={self.id}, username='{self.username}', "
            f"email='{self.email}', isActive={self.isActive})"
        )


@dataclass
class LoginRequest:
    """登录请求数据模型"""
    username: str
    password: str
    rememberMe: bool = False

    def isValid(self) -> bool:
        """验证登录请求数据"""
        return bool(self.username) and bool(self.password)


@dataclass
class RegisterRequest:
    """注册请求数据模型"""
    username: str
    email: str
    password: str
    confirmPassword: str

    def isValid(self) -> bool:
        """验证注册请求数据"""
        return (
            bool(self.username) and
            bool(self.email) and
            bool(self.password) and
            self.password == self.confirmPassword
        )


@dataclass
class AuthResponse:
    """认证响应数据模型"""
    success: bool
    message: str = ""
    user: Optional[User] = None
    accessToken: Optional[str] = None
    refreshToken: Optional[str] = None
    expiresIn: Optional[int] = None

    def toDict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'message': self.message,
            'user': self.user.toDict() if self.user else None,
            'accessToken': self.accessToken,
            'refreshToken': self.refreshToken,
            'expiresIn': self.expiresIn
        }

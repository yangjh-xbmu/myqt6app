#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户模型
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """用户数据模型"""
    
    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    token: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def is_valid(self) -> bool:
        """检查用户数据是否有效"""
        return (
            self.username is not None and 
            len(self.username.strip()) > 0 and
            self.email is not None and 
            '@' in self.email
        )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'token': self.token,
            'created_at': (
                self.created_at.isoformat() if self.created_at else None
            ),
            'updated_at': (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """从字典创建用户对象"""
        user = cls(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            token=data.get('token'),
            is_active=data.get('is_active', True)
        )
        
        # 处理时间字段
        if data.get('created_at'):
            try:
                user.created_at = datetime.fromisoformat(
                    data['created_at'].replace('Z', '+00:00')
                )
            except (ValueError, AttributeError):
                pass
        
        if data.get('updated_at'):
            try:
                user.updated_at = datetime.fromisoformat(
                    data['updated_at'].replace('Z', '+00:00')
                )
            except (ValueError, AttributeError):
                pass
        
        return user
    
    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"User(id={self.id}, username='{self.username}', "
            f"email='{self.email}')"
        )
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()
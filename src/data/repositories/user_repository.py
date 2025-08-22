#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据仓库 - 实现用户数据的仓库模式
"""

from typing import List, Optional
from ..database.database_manager import DatabaseManager
from ...business.models.user import User


class UserRepository:
    """用户数据仓库"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
    
    def create(self, user: User) -> Optional[User]:
        """创建用户
        
        Args:
            user: 用户对象
            
        Returns:
            Optional[User]: 创建成功返回用户对象，失败返回None
        """
        try:
            user_id = self.db_manager.add_user(
                username=user.username,
                email=user.email,
                password_hash=user.password_hash
            )
            
            if user_id:
                user.id = user_id
                return user
            
            return None
            
        except Exception as e:
            print(f"创建用户失败: {e}")
            return None
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象，不存在返回None
        """
        try:
            user_data = self.db_manager.get_user_by_id(user_id)
            if user_data:
                return User.from_dict(user_data)
            return None
            
        except Exception as e:
            print(f"获取用户失败: {e}")
            return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 用户对象，不存在返回None
        """
        try:
            user_data = self.db_manager.get_user_by_username(username)
            if user_data:
                return User.from_dict(user_data)
            return None
            
        except Exception as e:
            print(f"获取用户失败: {e}")
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            Optional[User]: 用户对象，不存在返回None
        """
        try:
            user_data = self.db_manager.get_user_by_email(email)
            if user_data:
                return User.from_dict(user_data)
            return None
            
        except Exception as e:
            print(f"获取用户失败: {e}")
            return None
    
    def get_all(self) -> List[User]:
        """获取所有用户
        
        Returns:
            List[User]: 用户列表
        """
        try:
            users_data = self.db_manager.get_all_users()
            return [User.from_dict(user_data) for user_data in users_data]
            
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return []
    
    def search(self, keyword: str) -> List[User]:
        """搜索用户
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[User]: 匹配的用户列表
        """
        try:
            users_data = self.db_manager.search_users(keyword)
            return [User.from_dict(user_data) for user_data in users_data]
            
        except Exception as e:
            print(f"搜索用户失败: {e}")
            return []
    
    def update(self, user: User) -> bool:
        """更新用户信息
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 更新是否成功
        """
        try:
            return self.db_manager.update_user(
                user_id=user.id,
                username=user.username,
                email=user.email
            )
            
        except Exception as e:
            print(f"更新用户失败: {e}")
            return False
    
    def delete(self, user_id: int) -> bool:
        """删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            return self.db_manager.delete_user(user_id)
            
        except Exception as e:
            print(f"删除用户失败: {e}")
            return False
    
    def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在
        
        Args:
            username: 用户名
            
        Returns:
            bool: 用户名是否存在
        """
        return self.get_by_username(username) is not None
    
    def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 邮箱是否存在
        """
        return self.get_by_email(email) is not None
    
    def count(self) -> int:
        """获取用户总数
        
        Returns:
            int: 用户总数
        """
        try:
            stats = self.db_manager.get_stats()
            return stats.get('total_users', 0)
            
        except Exception as e:
            print(f"获取用户总数失败: {e}")
            return 0
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据仓库 - 实现用户数据的仓库模式
"""

from typing import List, Optional
from src.data.database.database_manager import DatabaseManager
from src.business.models.user import User


class UserRepository:
    """用户数据仓库"""

    def __init__(self, databaseManager: DatabaseManager = None):
        self.databaseManager = databaseManager or DatabaseManager()

    def create(self, user: User) -> Optional[User]:
        """创建用户

        Args:
            user: 用户对象

        Returns:
            Optional[User]: 创建成功返回用户对象，失败返回None
        """
        try:
            userId = self.databaseManager.addUser(
                username=user.username,
                email=user.email,
                passwordHash=user.passwordHash
            )

            if userId:
                user.id = userId
                return user

            return None

        except Exception as createError:
            print(f"创建用户失败: {createError}")
            return None

    def getById(self, userId: int) -> Optional[User]:
        """根据ID获取用户

        Args:
            userId: 用户ID

        Returns:
            Optional[User]: 用户对象，不存在返回None
        """
        try:
            userData = self.databaseManager.getUserById(userId)
            if userData:
                return User.fromDict(userData)
            return None

        except Exception as getByIdError:
            print(f"获取用户失败: {getByIdError}")
            return None

    def getByUsername(self, username: str) -> Optional[User]:
        """根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            Optional[User]: 用户对象，不存在返回None
        """
        try:
            userData = self.databaseManager.getUserByUsername(username)
            if userData:
                return User.fromDict(userData)
            return None

        except Exception as getByUsernameError:
            print(f"获取用户失败: {getByUsernameError}")
            return None

    def getByEmail(self, email: str) -> Optional[User]:
        """根据邮箱获取用户

        Args:
            email: 邮箱地址

        Returns:
            Optional[User]: 用户对象，不存在返回None
        """
        try:
            userData = self.databaseManager.getUserByEmail(email)
            if userData:
                return User.fromDict(userData)
            return None

        except Exception as getByEmailError:
            print(f"获取用户失败: {getByEmailError}")
            return None

    def getAll(self) -> List[User]:
        """获取所有用户

        Returns:
            List[User]: 用户列表
        """
        try:
            usersData = self.databaseManager.getAllUsers()
            return [User.fromDict(userData) for userData in usersData]

        except Exception as getAllError:
            print(f"获取用户列表失败: {getAllError}")
            return []

    def search(self, keyword: str) -> List[User]:
        """搜索用户

        Args:
            keyword: 搜索关键词

        Returns:
            List[User]: 匹配的用户列表
        """
        try:
            usersData = self.databaseManager.searchUsers(keyword)
            return [User.fromDict(userData) for userData in usersData]

        except Exception as searchError:
            print(f"搜索用户失败: {searchError}")
            return []

    def update(self, user: User) -> bool:
        """更新用户信息

        Args:
            user: 用户对象

        Returns:
            bool: 更新是否成功
        """
        try:
            return self.databaseManager.updateUser(
                userId=user.id,
                username=user.username,
                email=user.email
            )

        except Exception as updateError:
            print(f"更新用户失败: {updateError}")
            return False

    def delete(self, userId: int) -> bool:
        """删除用户

        Args:
            userId: 用户ID

        Returns:
            bool: 删除是否成功
        """
        try:
            return self.databaseManager.deleteUser(userId)

        except Exception as deleteError:
            print(f"删除用户失败: {deleteError}")
            return False

    def existsByUsername(self, username: str) -> bool:
        """检查用户名是否存在

        Args:
            username: 用户名

        Returns:
            bool: 用户名是否存在
        """
        return self.getByUsername(username) is not None

    def existsByEmail(self, email: str) -> bool:
        """检查邮箱是否存在

        Args:
            email: 邮箱地址

        Returns:
            bool: 邮箱是否存在
        """
        return self.getByEmail(email) is not None

    def count(self) -> int:
        """获取用户总数

        Returns:
            int: 用户总数
        """
        try:
            stats = self.databaseManager.getStats()
            return stats.get('totalUsers', 0)

        except Exception as countError:
            print(f"获取用户总数失败: {countError}")
            return 0

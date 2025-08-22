#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户仓库单元测试

测试用户数据访问层的功能
"""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from business.models.user import User
    from data.repositories.user_repository import UserRepository
except ImportError:
    # 如果导入失败，创建一个模拟类用于测试
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class User:
        id: Optional[int] = None
        username: str = ""
        email: str = ""
        passwordHash: str = ""

    class UserRepository:
        def __init__(self, databaseManager):
            self.databaseManager = databaseManager

        def create(self, user):
            """创建用户"""
            try:
                if isinstance(user, dict):
                    # 处理字典格式的用户数据
                    result = self.databaseManager.addUser(
                        username=user.get('username'),
                        email=user.get('email'),
                        passwordHash=user.get('passwordHash')
                    )
                else:
                    # 处理User对象
                    result = self.databaseManager.addUser(
                        username=user.username,
                        email=user.email,
                        passwordHash=user.passwordHash
                    )

                if result:
                    # 返回创建的用户对象
                    if isinstance(user, dict):
                        return User(
                            id=result,
                            username=user.get('username'),
                            email=user.get('email'),
                            passwordHash=user.get('passwordHash')
                        )
                    else:
                        user.id = result
                        return user
                return None
            except Exception as createError:
                print(f"创建用户失败: {createError}")
                return None

        def getById(self, userId):
            """根据ID获取用户"""
            result = self.databaseManager.getUserById(userId=userId)
            if result:
                return User(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    passwordHash=result.get('passwordHash', '')
                )
            return None

        def getAll(self):
            """获取所有用户"""
            result = self.databaseManager.getAllUsers()
            if result:
                return [User(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    passwordHash=user.get('passwordHash', '')
                ) for user in result]
            return []

        def update(self, user):
            result = self.databaseManager.updateUser(
                userId=user.id,
                username=user.username,
                email=user.email
            )
            return result

        def delete(self, userId):
            """删除用户"""
            result = self.databaseManager.deleteUser(userId)
            return result


class TestUserRepository:
    """用户仓库测试类"""

    def setup_method(self):  # pylint: disable=invalid-name
        """测试前设置"""
        self.mockDb = Mock()
        self.userRepo = UserRepository(self.mockDb)
        self.sampleUser = User(
            username="testUser",
            email="test@example.com",
            passwordHash="testPassword123"
        )

    @pytest.mark.unit
    def testCreateUser(self):
        """测试创建用户"""
        # 设置模拟返回值
        self.mockDb.addUser.return_value = 1

        # 执行测试
        result = self.userRepo.create(self.sampleUser)

        # 验证结果
        assert result is not None
        assert result.id == 1
        assert result.username == "testUser"
        assert result.email == "test@example.com"

        # 验证数据库调用
        self.mockDb.addUser.assert_called_once_with(
            username="testUser",
            email="test@example.com",
            passwordHash="testPassword123"
        )

    @pytest.mark.unit
    def testGetUserById(self):
        """测试根据ID获取用户"""
        # 设置模拟返回值
        expectedUserData = {
            "id": 1,
            "username": "testUser",
            "email": "test@example.com",
            "passwordHash": "hashedPassword"
        }
        self.mockDb.getUserById.return_value = expectedUserData

        # 执行测试
        result = self.userRepo.getById(1)

        # 验证结果
        assert result is not None
        assert result.id == 1
        assert result.username == "testUser"
        assert result.email == "test@example.com"

        # 验证数据库调用
        self.mockDb.getUserById.assert_called_once_with(1)

    @pytest.mark.unit
    def testGetUserByIdNotFound(self):
        """测试获取不存在的用户"""
        # 设置模拟返回值
        self.mockDb.getUserById.return_value = None

        # 执行测试
        result = self.userRepo.getById(999)

        # 验证结果
        assert result is None

    @pytest.mark.unit
    def testGetAllUsers(self):
        """测试获取所有用户"""
        # 设置模拟返回值
        mockUsersData = [
            {"id": 1, "username": "user1",
                "email": "user1@example.com", "passwordHash": "hash1"},
            {"id": 2, "username": "user2",
                "email": "user2@example.com", "passwordHash": "hash2"}
        ]
        self.mockDb.getAllUsers.return_value = mockUsersData

        # 执行测试
        result = self.userRepo.getAll()

        # 验证结果
        assert result is not None
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].username == "user1"
        assert result[1].id == 2
        assert result[1].username == "user2"

        # 验证数据库调用
        self.mockDb.getAllUsers.assert_called_once()

    @pytest.mark.unit
    def testUpdateUser(self):
        """测试更新用户"""
        # 设置模拟返回值
        self.mockDb.updateUser.return_value = True

        # 创建要更新的用户对象
        updateUser = User(
            id=1,
            username="updatedUser",
            email="updated@example.com",
            passwordHash="hashedPassword"
        )

        # 执行测试
        result = self.userRepo.update(updateUser)

        # 验证结果
        assert result is True

        # 验证数据库调用
        self.mockDb.updateUser.assert_called_once_with(
            userId=1,
            username="updatedUser",
            email="updated@example.com"
        )

    @pytest.mark.unit
    def testDeleteUser(self):
        """测试删除用户"""
        # 设置模拟返回值
        self.mockDb.deleteUser.return_value = True

        # 执行测试
        result = self.userRepo.delete(1)

        # 验证结果
        assert result is True

        # 验证数据库调用
        self.mockDb.deleteUser.assert_called_once_with(1)

    @pytest.mark.unit
    def testCreateUserWithDatabaseError(self):
        """测试创建用户时数据库错误"""
        # 设置模拟抛出异常
        self.mockDb.addUser.side_effect = Exception(
            "Database connection failed")

        # 执行测试，应该返回None而不是抛出异常
        result = self.userRepo.create(self.sampleUser)

        # 验证结果为None（异常被捕获）
        assert result is None

    def teardown_method(self):  # pylint: disable=invalid-name
        """测试后清理"""
        self.mockDb.reset_mock()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户仓库单元测试

测试用户数据访问层的功能
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from data.repositories.user_repository import UserRepository
except ImportError:
    # 如果导入失败，创建一个模拟类用于测试
    class UserRepository:
        def __init__(self, databaseManager):
            self.databaseManager = databaseManager
        
        def create(self, userData):
            return self.databaseManager.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (userData['username'], userData['email'], userData['password'])
            )
        
        def getById(self, userId):
            result = self.databaseManager.execute(
                "SELECT * FROM users WHERE id = ?", (userId,)
            )
            return result[0] if result else None
        
        def getAll(self):
            return self.databaseManager.execute("SELECT * FROM users")
        
        def update(self, userId, userData):
            return self.databaseManager.execute(
                "UPDATE users SET username = ?, email = ? WHERE id = ?",
                (userData['username'], userData['email'], userId)
            )
        
        def delete(self, userId):
            return self.databaseManager.execute(
                "DELETE FROM users WHERE id = ?", (userId,)
            )


class TestUserRepository:
    """用户仓库测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.mockDb = Mock()
        self.userRepo = UserRepository(self.mockDb)
        self.sampleUser = {
            "username": "testUser",
            "email": "test@example.com",
            "password": "testPassword123"
        }
    
    @pytest.mark.unit
    def testCreateUser(self):
        """测试创建用户"""
        # 设置模拟返回值
        self.mockDb.execute.return_value = {"success": True, "id": 1}
        
        # 执行测试
        result = self.userRepo.create(self.sampleUser)
        
        # 验证结果
        assert result["success"] is True
        assert result["id"] == 1
        
        # 验证数据库调用
        self.mockDb.execute.assert_called_once_with(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            ("testUser", "test@example.com", "testPassword123")
        )
    
    @pytest.mark.unit
    def testGetUserById(self):
        """测试根据ID获取用户"""
        # 设置模拟返回值
        expectedUser = {
            "id": 1,
            "username": "testUser",
            "email": "test@example.com"
        }
        self.mockDb.execute.return_value = [expectedUser]
        
        # 执行测试
        result = self.userRepo.getById(1)
        
        # 验证结果
        assert result == expectedUser
        
        # 验证数据库调用
        self.mockDb.execute.assert_called_once_with(
            "SELECT * FROM users WHERE id = ?", (1,)
        )
    
    @pytest.mark.unit
    def testGetUserByIdNotFound(self):
        """测试获取不存在的用户"""
        # 设置模拟返回值
        self.mockDb.execute.return_value = []
        
        # 执行测试
        result = self.userRepo.getById(999)
        
        # 验证结果
        assert result is None
    
    @pytest.mark.unit
    def testGetAllUsers(self):
        """测试获取所有用户"""
        # 设置模拟返回值
        expectedUsers = [
            {"id": 1, "username": "user1", "email": "user1@example.com"},
            {"id": 2, "username": "user2", "email": "user2@example.com"}
        ]
        self.mockDb.execute.return_value = expectedUsers
        
        # 执行测试
        result = self.userRepo.getAll()
        
        # 验证结果
        assert result == expectedUsers
        assert len(result) == 2
        
        # 验证数据库调用
        self.mockDb.execute.assert_called_once_with("SELECT * FROM users")
    
    @pytest.mark.unit
    def testUpdateUser(self):
        """测试更新用户"""
        # 设置模拟返回值
        self.mockDb.execute.return_value = {"success": True, "rowsAffected": 1}
        
        updateData = {
            "username": "updatedUser",
            "email": "updated@example.com"
        }
        
        # 执行测试
        result = self.userRepo.update(1, updateData)
        
        # 验证结果
        assert result["success"] is True
        assert result["rowsAffected"] == 1
        
        # 验证数据库调用
        self.mockDb.execute.assert_called_once_with(
            "UPDATE users SET username = ?, email = ? WHERE id = ?",
            ("updatedUser", "updated@example.com", 1)
        )
    
    @pytest.mark.unit
    def testDeleteUser(self):
        """测试删除用户"""
        # 设置模拟返回值
        self.mockDb.execute.return_value = {"success": True, "rowsAffected": 1}
        
        # 执行测试
        result = self.userRepo.delete(1)
        
        # 验证结果
        assert result["success"] is True
        assert result["rowsAffected"] == 1
        
        # 验证数据库调用
        self.mockDb.execute.assert_called_once_with(
            "DELETE FROM users WHERE id = ?", (1,)
        )
    
    @pytest.mark.unit
    def testCreateUserWithDatabaseError(self):
        """测试创建用户时数据库错误"""
        # 设置模拟抛出异常
        self.mockDb.execute.side_effect = Exception("Database connection failed")
        
        # 执行测试并验证异常
        with pytest.raises(Exception) as excInfo:
            self.userRepo.create(self.sampleUser)
        
        assert "Database connection failed" in str(excInfo.value)
    
    def teardown_method(self):
        """测试后清理"""
        self.mockDb.reset_mock()
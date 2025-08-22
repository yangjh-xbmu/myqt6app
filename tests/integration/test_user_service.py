#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户服务集成测试

测试用户服务的完整业务流程
"""

import sys
from pathlib import Path

import pytest


# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


class MockUserRepository:
    """模拟用户仓库"""

    def __init__(self):
        self.users = {
            1: {"id": 1, "username": "admin", "email": "admin@example.com", "isActive": True},
            2: {"id": 2, "username": "user1", "email": "user1@example.com", "isActive": True},
            3: {"id": 3, "username": "user2", "email": "user2@example.com", "isActive": False}
        }
        self.nextId = 4

    def create(self, userData):
        """创建用户"""
        newUser = {
            "id": self.nextId,
            "username": userData["username"],
            "email": userData["email"],
            "isActive": True
        }
        self.users[self.nextId] = newUser
        self.nextId += 1
        return {"success": True, "id": newUser["id"]}

    def getById(self, userId):
        """根据ID获取用户"""
        return self.users.get(userId)

    def getAll(self):
        """获取所有用户"""
        return list(self.users.values())

    def update(self, userId, userData):
        """更新用户"""
        if userId in self.users:
            self.users[userId].update(userData)
            return {"success": True, "rowsAffected": 1}
        return {"success": False, "rowsAffected": 0}

    def delete(self, userId):
        """删除用户"""
        if userId in self.users:
            del self.users[userId]
            return {"success": True, "rowsAffected": 1}
        return {"success": False, "rowsAffected": 0}

    def searchByUsername(self, username):
        """根据用户名搜索"""
        return [user for user in self.users.values() if username.lower() in user["username"].lower()]


class UserService:
    """用户服务类"""

    def __init__(self, userRepository):
        self.userRepository = userRepository

    def createUser(self, username, email, password):
        """创建用户"""
        # 验证输入
        if not username or not email or not password:
            raise ValueError("用户名、邮箱和密码不能为空")

        if len(password) < 6:
            raise ValueError("密码长度不能少于6位")

        if "@" not in email:
            raise ValueError("邮箱格式不正确")

        # 检查用户名是否已存在
        existingUsers = self.userRepository.searchByUsername(username)
        if existingUsers:
            raise ValueError("用户名已存在")

        # 创建用户
        userData = {
            "username": username,
            "email": email,
            "password": password  # 实际应用中应该加密
        }

        return self.userRepository.create(userData)

    def getUserById(self, userId):
        """获取用户信息"""
        if not userId or userId <= 0:
            raise ValueError("用户ID无效")

        user = self.userRepository.getById(userId)
        if not user:
            raise ValueError("用户不存在")

        return user

    def getAllActiveUsers(self):
        """获取所有活跃用户"""
        allUsers = self.userRepository.getAll()
        return [user for user in allUsers if user.get("isActive", True)]

    def updateUser(self, userId, username=None, email=None):
        """更新用户信息"""
        # 验证用户存在
        self.getUserById(userId)

        updateData = {}
        if username:
            updateData["username"] = username
        if email:
            if "@" not in email:
                raise ValueError("邮箱格式不正确")
            updateData["email"] = email

        if not updateData:
            raise ValueError("没有提供要更新的数据")

        return self.userRepository.update(userId, updateData)

    def deactivateUser(self, userId):
        """停用用户"""
        return self.userRepository.update(userId, {"isActive": False})

    def deleteUser(self, userId):
        """删除用户"""
        # 验证用户存在
        self.getUserById(userId)

        return self.userRepository.delete(userId)

    def searchUsers(self, keyword):
        """搜索用户"""
        if not keyword:
            return []

        return self.userRepository.searchByUsername(keyword)


class TestUserServiceIntegration:
    """用户服务集成测试类"""

    def setupMethod(self):
        """测试前设置"""
        self.mockRepo = MockUserRepository()
        self.userService = UserService(self.mockRepo)

    @pytest.mark.integration
    def testCreateUserSuccess(self):
        """测试成功创建用户"""
        result = self.userService.createUser(
            "newUser", "new@example.com", "password123")

        assert result["success"] is True
        assert "id" in result

        # 验证用户已创建
        createdUser = self.userService.getUserById(result["id"])
        assert createdUser["username"] == "newUser"
        assert createdUser["email"] == "new@example.com"

    @pytest.mark.integration
    def testCreateUserValidation(self):
        """测试创建用户时的验证"""
        # 测试空用户名
        with pytest.raises(ValueError, match="用户名、邮箱和密码不能为空"):
            self.userService.createUser("", "test@example.com", "password123")

        # 测试短密码
        with pytest.raises(ValueError, match="密码长度不能少于6位"):
            self.userService.createUser("testUser", "test@example.com", "123")

        # 测试无效邮箱
        with pytest.raises(ValueError, match="邮箱格式不正确"):
            self.userService.createUser(
                "testUser", "invalid-email", "password123")

        # 测试重复用户名
        with pytest.raises(ValueError, match="用户名已存在"):
            self.userService.createUser(
                "admin", "test@example.com", "password123")

    @pytest.mark.integration
    def testGetUserById(self):
        """测试根据ID获取用户"""
        user = self.userService.getUserById(1)

        assert user["id"] == 1
        assert user["username"] == "admin"
        assert user["email"] == "admin@example.com"

    @pytest.mark.integration
    def testGetUserByIdNotFound(self):
        """测试获取不存在的用户"""
        with pytest.raises(ValueError, match="用户不存在"):
            self.userService.getUserById(999)

    @pytest.mark.integration
    def testGetAllActiveUsers(self):
        """测试获取所有活跃用户"""
        activeUsers = self.userService.getAllActiveUsers()

        assert len(activeUsers) == 2  # user2是非活跃的
        usernames = [user["username"] for user in activeUsers]
        assert "admin" in usernames
        assert "user1" in usernames
        assert "user2" not in usernames

    @pytest.mark.integration
    def testUpdateUser(self):
        """测试更新用户"""
        result = self.userService.updateUser(
            1, username="newAdmin", email="newadmin@example.com")

        assert result["success"] is True

        # 验证更新结果
        updatedUser = self.userService.getUserById(1)
        assert updatedUser["username"] == "newAdmin"
        assert updatedUser["email"] == "newadmin@example.com"

    @pytest.mark.integration
    def testUpdateUserValidation(self):
        """测试更新用户时的验证"""
        # 测试无效邮箱
        with pytest.raises(ValueError, match="邮箱格式不正确"):
            self.userService.updateUser(1, email="invalid-email")

        # 测试没有更新数据
        with pytest.raises(ValueError, match="没有提供要更新的数据"):
            self.userService.updateUser(1)

    @pytest.mark.integration
    def testDeactivateUser(self):
        """测试停用用户"""
        result = self.userService.deactivateUser(1)

        assert result["success"] is True

        # 验证用户已停用
        user = self.userService.getUserById(1)
        assert user["isActive"] is False

    @pytest.mark.integration
    def testDeleteUser(self):
        """测试删除用户"""
        result = self.userService.deleteUser(2)

        assert result["success"] is True

        # 验证用户已删除
        with pytest.raises(ValueError, match="用户不存在"):
            self.userService.getUserById(2)

    @pytest.mark.integration
    def testSearchUsers(self):
        """测试搜索用户"""
        results = self.userService.searchUsers("user")

        assert len(results) == 2
        usernames = [user["username"] for user in results]
        assert "user1" in usernames
        assert "user2" in usernames

    @pytest.mark.integration
    def testCompleteUserWorkflow(self):
        """测试完整的用户工作流程"""
        # 1. 创建用户
        createResult = self.userService.createUser(
            "workflowUser", "workflow@example.com", "password123")
        userId = createResult["id"]

        # 2. 获取用户
        user = self.userService.getUserById(userId)
        assert user["username"] == "workflowUser"

        # 3. 更新用户
        self.userService.updateUser(userId, username="updatedWorkflowUser")
        updatedUser = self.userService.getUserById(userId)
        assert updatedUser["username"] == "updatedWorkflowUser"

        # 4. 停用用户
        self.userService.deactivateUser(userId)
        deactivatedUser = self.userService.getUserById(userId)
        assert deactivatedUser["isActive"] is False

        # 5. 删除用户
        self.userService.deleteUser(userId)
        with pytest.raises(ValueError, match="用户不存在"):
            self.userService.getUserById(userId)

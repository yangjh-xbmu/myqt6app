#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
camelCase命名规范测试

测试项目中camelCase命名规范的使用
"""

import pytest


class TestCamelCaseNaming:
    """camelCase命名规范测试类"""

    # 测试用常量
    MAX_CONNECTIONS = 100
    DEFAULT_TIMEOUT = 30

    @pytest.mark.unit
    def testCamelCaseVariable(self):
        """测试camelCase变量命名"""
        camelCaseVar = 1
        assert camelCaseVar == 1

        userName = "testUser"
        assert userName == "testUser"

        itemList = [1, 2, 3]
        assert len(itemList) == 3

    @pytest.mark.unit
    def testCamelCaseFunction(self):
        """测试camelCase函数命名"""
        def getUserData(userId):
            """获取用户数据"""
            return {"id": userId, "name": "Test User"}

        userData = getUserData(1)
        assert userData["id"] == 1
        assert userData["name"] == "Test User"

    @pytest.mark.unit
    def testCamelCaseMethod(self):
        """测试camelCase方法命名"""
        class TestClass:
            def __init__(self):
                self.userName = "testUser"

            def getUserName(self):
                """获取用户名"""
                return self.userName

            def setUserName(self, newName):
                """设置用户名"""
                self.userName = newName

        testObj = TestClass()
        assert testObj.getUserName() == "testUser"

        testObj.setUserName("newUser")
        assert testObj.getUserName() == "newUser"

    @pytest.mark.unit
    def testConstantNaming(self):
        """测试常量命名"""
        assert self.MAX_CONNECTIONS == 100
        assert self.DEFAULT_TIMEOUT == 30

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据验证器 - 业务逻辑层
提供用户数据的验证规则和业务逻辑检查
"""

import re
from typing import List, Dict, Any, Optional
from business.models.user import User, LoginRequest, RegisterRequest


class ValidationError(Exception):
    """验证错误异常"""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class UserValidator:
    """用户数据验证器

    提供用户相关数据的验证功能
    """

    # 验证规则常量
    minUsernameLength = 3
    maxUsernameLength = 30
    minPasswordLength = 8
    maxPasswordLength = 128

    # 正则表达式模式
    emailPattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    usernamePattern = re.compile(r'^[a-zA-Z0-9_-]+$')

    @classmethod
    def validateEmail(cls, email: str) -> bool:
        """验证邮箱格式

        Args:
            email: 邮箱地址

        Returns:
            是否为有效邮箱格式
        """
        if not email or not isinstance(email, str):
            return False
        return bool(cls.emailPattern.match(email.strip()))

    @classmethod
    def validateUsername(cls, username: str) -> bool:
        """验证用户名格式

        Args:
            username: 用户名

        Returns:
            是否为有效用户名格式
        """
        if not username or not isinstance(username, str):
            return False

        username = username.strip()

        # 检查长度
        lengthValid = (
            cls.minUsernameLength <= len(username) <= cls.maxUsernameLength
        )
        if not lengthValid:
            return False

        # 检查字符
        return bool(cls.usernamePattern.match(username))

    @classmethod
    def validatePassword(cls, password: str) -> bool:
        """验证密码强度

        Args:
            password: 密码

        Returns:
            是否为有效密码
        """
        if not password or not isinstance(password, str):
            return False

        # 检查长度
        lengthValid = (
            cls.minPasswordLength <= len(password) <= cls.maxPasswordLength
        )
        if not lengthValid:
            return False

        # 检查密码复杂度
        hasUpper = any(c.isupper() for c in password)
        hasLower = any(c.islower() for c in password)
        hasDigit = any(c.isdigit() for c in password)
        specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        hasSpecial = any(c in specialChars for c in password)

        # 至少包含3种字符类型
        complexityCount = sum([hasUpper, hasLower, hasDigit, hasSpecial])
        return complexityCount >= 3

    @classmethod
    def validateUser(cls, user: User) -> List[str]:
        """验证用户对象

        Args:
            user: 用户对象

        Returns:
            验证错误列表
        """
        errors = []

        # 验证用户名
        if not cls.validateUsername(user.username):
            errors.append(
                f"用户名必须是{cls.minUsernameLength}-"
                f"{cls.maxUsernameLength}个字符，"
                "只能包含字母、数字、下划线和连字符"
            )

        # 验证邮箱
        if not cls.validateEmail(user.email):
            errors.append("邮箱格式不正确")

        # 验证密码哈希（如果存在）
        if user.passwordHash and not user.salt:
            errors.append("密码哈希存在但缺少盐值")

        return errors

    @classmethod
    def validateLoginRequest(cls, request: LoginRequest) -> List[str]:
        """验证登录请求

        Args:
            request: 登录请求对象

        Returns:
            验证错误列表
        """
        errors = []

        if not request.username:
            errors.append("用户名不能为空")

        if not request.password:
            errors.append("密码不能为空")

        return errors

    @classmethod
    def validateRegisterRequest(cls, request: RegisterRequest) -> List[str]:
        """验证注册请求

        Args:
            request: 注册请求对象

        Returns:
            验证错误列表
        """
        errors = []

        # 验证用户名
        if not cls.validateUsername(request.username):
            errors.append(
                f"用户名必须是{cls.minUsernameLength}-"
                f"{cls.maxUsernameLength}个字符，"
                "只能包含字母、数字、下划线和连字符"
            )

        # 验证邮箱
        if not cls.validateEmail(request.email):
            errors.append("邮箱格式不正确")

        # 验证密码
        if not cls.validatePassword(request.password):
            errors.append(
                f"密码必须是{cls.minPasswordLength}-"
                f"{cls.maxPasswordLength}个字符，"
                "至少包含大写字母、小写字母、数字、特殊字符中的3种"
            )

        # 验证密码确认
        if request.password != request.confirmPassword:
            errors.append("两次输入的密码不一致")

        return errors

    @classmethod
    def validateAndRaise(cls, data: Any, validationType: str = 'user') -> None:
        """验证数据并在失败时抛出异常

        Args:
            data: 要验证的数据
            validationType: 验证类型 ('user', 'login', 'register')

        Raises:
            ValidationError: 验证失败时抛出
        """
        errors = []

        if validationType == 'user' and isinstance(data, User):
            errors = cls.validateUser(data)
        elif validationType == 'login' and isinstance(data, LoginRequest):
            errors = cls.validateLoginRequest(data)
        elif (validationType == 'register' and
              isinstance(data, RegisterRequest)):
            errors = cls.validateRegisterRequest(data)
        else:
            raise ValidationError(f"不支持的验证类型: {validationType}")

        if errors:
            raise ValidationError('; '.join(errors))

    @classmethod
    def getPasswordStrengthScore(cls, password: str) -> Dict[str, Any]:
        """获取密码强度评分

        Args:
            password: 密码

        Returns:
            包含强度评分和建议的字典
        """
        if not password:
            return {
                'score': 0,
                'strength': 'very_weak',
                'suggestions': ['请输入密码']
            }

        score = 0
        suggestions = []

        # 长度检查
        if len(password) >= cls.minPasswordLength:
            score += 25
        else:
            suggestions.append(
                f"密码长度至少{cls.minPasswordLength}个字符"
            )

        # 字符类型检查
        hasUpper = any(c.isupper() for c in password)
        hasLower = any(c.islower() for c in password)
        hasDigit = any(c.isdigit() for c in password)
        hasSpecial = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

        if hasUpper:
            score += 20
        else:
            suggestions.append("添加大写字母")

        if hasLower:
            score += 20
        else:
            suggestions.append("添加小写字母")

        if hasDigit:
            score += 20
        else:
            suggestions.append("添加数字")

        if hasSpecial:
            score += 15
        else:
            suggestions.append("添加特殊字符")

        # 确定强度等级
        if score >= 90:
            strength = 'very_strong'
        elif score >= 70:
            strength = 'strong'
        elif score >= 50:
            strength = 'medium'
        elif score >= 30:
            strength = 'weak'
        else:
            strength = 'very_weak'

        return {
            'score': score,
            'strength': strength,
            'suggestions': suggestions
        }

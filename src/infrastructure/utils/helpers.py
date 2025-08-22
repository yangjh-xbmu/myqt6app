#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具类 - 提供常用的辅助函数
"""

import hashlib
import secrets
import string
import re
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path


class PasswordHelper:
    """密码相关工具"""

    @staticmethod
    def hashPassword(password: str, salt: Optional[str] = None) -> str:
        """生成密码哈希

        Args:
            password: 原始密码
            salt: 盐值，如果不提供则自动生成

        Returns:
            str: 密码哈希值（包含盐值）
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # 使用PBKDF2算法
        passwordHash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        )

        return f"{salt}:{passwordHash.hex()}"

    @staticmethod
    def verifyPassword(password: str, hashedPassword: str) -> bool:
        """验证密码

        Args:
            password: 原始密码
            hashedPassword: 存储的密码哈希

        Returns:
            bool: 密码是否正确
        """
        try:
            salt, storedHash = hashedPassword.split(':', 1)

            # 使用相同的盐值重新计算哈希
            passwordHash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )

            return passwordHash.hex() == storedHash

        except ValueError:
            return False

    @staticmethod
    def generatePassword(length: int = 12,
                         includeUppercase: bool = True,
                         includeLowercase: bool = True,
                         includeNumbers: bool = True,
                         includeSymbols: bool = False) -> str:
        """生成随机密码

        Args:
            length: 密码长度
            includeUppercase: 是否包含大写字母
            includeLowercase: 是否包含小写字母
            includeNumbers: 是否包含数字
            includeSymbols: 是否包含符号

        Returns:
            str: 生成的密码
        """
        characters = ''

        if includeUppercase:
            characters += string.ascii_uppercase
        if includeLowercase:
            characters += string.ascii_lowercase
        if includeNumbers:
            characters += string.digits
        if includeSymbols:
            characters += '!@#$%^&*()_+-=[]{}|;:,.<>?'

        if not characters:
            characters = string.ascii_letters + string.digits

        return ''.join(secrets.choice(characters) for _ in range(length))


class ValidationHelper:
    """数据验证工具"""

    @staticmethod
    def isValidEmail(email: str) -> bool:
        """验证邮箱格式

        Args:
            email: 邮箱地址

        Returns:
            bool: 邮箱格式是否有效
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def isValidUsername(username: str) -> bool:
        """验证用户名格式

        Args:
            username: 用户名

        Returns:
            bool: 用户名格式是否有效
        """
        # 用户名只能包含字母、数字、下划线，长度3-20
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None

    @staticmethod
    def isStrongPassword(password: str) -> Dict[str, bool]:
        """检查密码强度

        Args:
            password: 密码

        Returns:
            Dict[str, bool]: 密码强度检查结果
        """
        return {
            'lengthOk': len(password) >= 8,
            'hasUppercase': bool(re.search(r'[A-Z]', password)),
            'hasLowercase': bool(re.search(r'[a-z]', password)),
            'hasNumbers': bool(re.search(r'\d', password)),
            'hasSymbols': bool(
                re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password)
            )
        }

    @staticmethod
    def sanitizeInput(text: str) -> str:
        """清理用户输入

        Args:
            text: 输入文本

        Returns:
            str: 清理后的文本
        """
        if not text:
            return ''

        # 移除首尾空白
        text = text.strip()

        # 移除潜在的危险字符
        dangerousChars = ['<', '>', '"', "'", '&', ';']
        for char in dangerousChars:
            text = text.replace(char, '')

        return text


class DateTimeHelper:
    """日期时间工具"""

    @staticmethod
    def formatDatetime(dateTime: datetime,
                       formatStr: str = '%Y-%m-%d %H:%M:%S') -> str:
        """格式化日期时间

        Args:
            dt: 日期时间对象
            formatStr: 格式字符串

        Returns:
            str: 格式化后的日期时间字符串
        """
        return dateTime.strftime(formatStr)

    @staticmethod
    def parseDatetime(dateStr: str,
                      formatStr: str = '%Y-%m-%d %H:%M:%S'
                      ) -> Optional[datetime]:
        """解析日期时间字符串

        Args:
            dateStr: 日期时间字符串
            formatStr: 格式字符串

        Returns:
            Optional[datetime]: 解析后的日期时间对象
        """
        try:
            return datetime.strptime(dateStr, formatStr)
        except ValueError:
            return None

    @staticmethod
    def getRelativeTime(dateTime: datetime) -> str:
        """获取相对时间描述

        Args:
            dt: 日期时间对象

        Returns:
            str: 相对时间描述
        """
        now = datetime.now()
        diff = now - dateTime

        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"

    @staticmethod
    def isExpired(dateTime: datetime, durationHours: int = 24) -> bool:
        """检查是否过期

        Args:
            dt: 日期时间对象
            durationHours: 有效期（小时）

        Returns:
            bool: 是否过期
        """
        expiryTime = dateTime + timedelta(hours=durationHours)
        return datetime.now() > expiryTime


class FileHelper:
    """文件操作工具"""

    @staticmethod
    def ensureDir(path: str) -> bool:
        """确保目录存在

        Args:
            path: 目录路径

        Returns:
            bool: 操作是否成功
        """
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    @staticmethod
    def getFileSize(filePath: str) -> int:
        """获取文件大小

        Args:
            filePath: 文件路径

        Returns:
            int: 文件大小（字节）
        """
        try:
            return Path(filePath).stat().st_size
        except Exception:
            return 0

    @staticmethod
    def formatFileSize(sizeBytes: int) -> str:
        """格式化文件大小

        Args:
            sizeBytes: 文件大小（字节）

        Returns:
            str: 格式化后的文件大小
        """
        if sizeBytes == 0:
            return "0B"

        sizeNames = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while sizeBytes >= 1024 and i < len(sizeNames) - 1:
            sizeBytes /= 1024.0
            i += 1

        return f"{sizeBytes:.1f}{sizeNames[i]}"

    @staticmethod
    def isSafePath(path: str, basePath: str) -> bool:
        """检查路径是否安全（防止路径遍历攻击）

        Args:
            path: 要检查的路径
            basePath: 基础路径

        Returns:
            bool: 路径是否安全
        """
        try:
            resolvedPath = Path(path).resolve()
            resolvedBase = Path(basePath).resolve()
            return resolvedPath.is_relative_to(resolvedBase)
        except Exception:
            return False


class StringHelper:
    """字符串工具"""

    @staticmethod
    def truncate(text: str, maxLength: int, suffix: str = '...') -> str:
        """截断字符串

        Args:
            text: 原始字符串
            maxLength: 最大长度
            suffix: 后缀

        Returns:
            str: 截断后的字符串
        """
        if len(text) <= maxLength:
            return text

        return text[:maxLength - len(suffix)] + suffix

    @staticmethod
    def toSnakeCase(text: str) -> str:
        """转换为蛇形命名

        Args:
            text: 原始字符串

        Returns:
            str: 蛇形命名字符串
        """
        # 在大写字母前插入下划线
        firstStep = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        # 在小写字母和大写字母之间插入下划线
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', firstStep).lower()

    @staticmethod
    def toCamelCase(text: str) -> str:
        """转换为驼峰命名

        Args:
            text: 原始字符串

        Returns:
            str: 驼峰命名字符串
        """
        components = text.split('_')
        return (components[0] +
                ''.join(word.capitalize() for word in components[1:]))

    @staticmethod
    def generateToken(length: int = 32) -> str:
        """生成随机令牌

        Args:
            length: 令牌长度

        Returns:
            str: 随机令牌
        """
        return secrets.token_urlsafe(length)

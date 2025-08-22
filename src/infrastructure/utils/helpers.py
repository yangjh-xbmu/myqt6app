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
    def hash_password(password: str, salt: Optional[str] = None) -> str:
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
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        )
        
        return f"{salt}:{password_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码
        
        Args:
            password: 原始密码
            hashed_password: 存储的密码哈希
            
        Returns:
            bool: 密码是否正确
        """
        try:
            salt, stored_hash = hashed_password.split(':', 1)
            
            # 使用相同的盐值重新计算哈希
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            return password_hash.hex() == stored_hash
            
        except ValueError:
            return False
    
    @staticmethod
    def generate_password(length: int = 12,
                          include_uppercase: bool = True,
                          include_lowercase: bool = True,
                          include_numbers: bool = True,
                          include_symbols: bool = False) -> str:
        """生成随机密码
        
        Args:
            length: 密码长度
            include_uppercase: 是否包含大写字母
            include_lowercase: 是否包含小写字母
            include_numbers: 是否包含数字
            include_symbols: 是否包含符号
            
        Returns:
            str: 生成的密码
        """
        characters = ''
        
        if include_uppercase:
            characters += string.ascii_uppercase
        if include_lowercase:
            characters += string.ascii_lowercase
        if include_numbers:
            characters += string.digits
        if include_symbols:
            characters += '!@#$%^&*()_+-=[]{}|;:,.<>?'
        
        if not characters:
            characters = string.ascii_letters + string.digits
        
        return ''.join(secrets.choice(characters) for _ in range(length))


class ValidationHelper:
    """数据验证工具"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 邮箱格式是否有效
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
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
    def is_strong_password(password: str) -> Dict[str, bool]:
        """检查密码强度
        
        Args:
            password: 密码
            
        Returns:
            Dict[str, bool]: 密码强度检查结果
        """
        return {
            'length_ok': len(password) >= 8,
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_numbers': bool(re.search(r'\d', password)),
            'has_symbols': bool(
                re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password)
            )
        }
    
    @staticmethod
    def sanitize_input(text: str) -> str:
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
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text


class DateTimeHelper:
    """日期时间工具"""
    
    @staticmethod
    def format_datetime(dt: datetime,
                        format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """格式化日期时间
        
        Args:
            dt: 日期时间对象
            format_str: 格式字符串
            
        Returns:
            str: 格式化后的日期时间字符串
        """
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_datetime(date_str: str,
                       format_str: str = '%Y-%m-%d %H:%M:%S'
                       ) -> Optional[datetime]:
        """解析日期时间字符串
        
        Args:
            date_str: 日期时间字符串
            format_str: 格式字符串
            
        Returns:
            Optional[datetime]: 解析后的日期时间对象
        """
        try:
            return datetime.strptime(date_str, format_str)
        except ValueError:
            return None
    
    @staticmethod
    def get_relative_time(dt: datetime) -> str:
        """获取相对时间描述
        
        Args:
            dt: 日期时间对象
            
        Returns:
            str: 相对时间描述
        """
        now = datetime.now()
        diff = now - dt
        
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
    def is_expired(dt: datetime, duration_hours: int = 24) -> bool:
        """检查是否过期
        
        Args:
            dt: 日期时间对象
            duration_hours: 有效期（小时）
            
        Returns:
            bool: 是否过期
        """
        expiry_time = dt + timedelta(hours=duration_hours)
        return datetime.now() > expiry_time


class FileHelper:
    """文件操作工具"""
    
    @staticmethod
    def ensure_dir(path: str) -> bool:
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
    def get_file_size(file_path: str) -> int:
        """获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件大小（字节）
        """
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            str: 格式化后的文件大小
        """
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    @staticmethod
    def is_safe_path(path: str, base_path: str) -> bool:
        """检查路径是否安全（防止路径遍历攻击）
        
        Args:
            path: 要检查的路径
            base_path: 基础路径
            
        Returns:
            bool: 路径是否安全
        """
        try:
            resolved_path = Path(path).resolve()
            resolved_base = Path(base_path).resolve()
            return resolved_path.is_relative_to(resolved_base)
        except Exception:
            return False


class StringHelper:
    """字符串工具"""
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = '...') -> str:
        """截断字符串
        
        Args:
            text: 原始字符串
            max_length: 最大长度
            suffix: 后缀
            
        Returns:
            str: 截断后的字符串
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def to_snake_case(text: str) -> str:
        """转换为蛇形命名
        
        Args:
            text: 原始字符串
            
        Returns:
            str: 蛇形命名字符串
        """
        # 在大写字母前插入下划线
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        # 在小写字母和大写字母之间插入下划线
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def to_camel_case(text: str) -> str:
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
    def generate_token(length: int = 32) -> str:
        """生成随机令牌
        
        Args:
            length: 令牌长度
            
        Returns:
            str: 随机令牌
        """
        return secrets.token_urlsafe(length)
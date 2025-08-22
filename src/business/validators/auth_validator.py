#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证验证器 - 验证用户输入的认证相关数据
"""

import re
from typing import Tuple


class AuthValidator:
    """认证数据验证器"""
    
    def __init__(self):
        # 邮箱正则表达式
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # 用户名正则表达式（3-20个字符，字母数字下划线）
        self.username_pattern = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    
    def validate_login_input(self, username: str, 
                            password: str) -> Tuple[bool, str]:
        """验证登录输入
        
        Args:
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not username or not username.strip():
            return False, '请输入用户名或邮箱'
        
        if not password or not password.strip():
            return False, '请输入密码'
        
        username = username.strip()
        
        # 检查用户名长度
        if len(username) < 3:
            return False, '用户名或邮箱长度不能少于3个字符'
        
        if len(username) > 50:
            return False, '用户名或邮箱长度不能超过50个字符'
        
        # 检查密码长度
        if len(password) < 6:
            return False, '密码长度不能少于6位'
        
        if len(password) > 128:
            return False, '密码长度不能超过128位'
        
        return True, ''
    
    def validate_register_input(self, username: str, email: str,
                                password: str, 
                                confirm_password: str) -> Tuple[bool, str]:
        """验证注册输入
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            confirm_password: 确认密码
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        # 验证用户名
        is_valid, error_msg = self.validate_username(username)
        if not is_valid:
            return False, error_msg
        
        # 验证邮箱
        is_valid, error_msg = self.validate_email(email)
        if not is_valid:
            return False, error_msg
        
        # 验证密码
        is_valid, error_msg = self.validate_password(password)
        if not is_valid:
            return False, error_msg
        
        # 验证确认密码
        if password != confirm_password:
            return False, '两次输入的密码不一致'
        
        return True, ''
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """验证用户名
        
        Args:
            username: 用户名
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not username or not username.strip():
            return False, '请输入用户名'
        
        username = username.strip()
        
        if len(username) < 3:
            return False, '用户名长度不能少于3个字符'
        
        if len(username) > 20:
            return False, '用户名长度不能超过20个字符'
        
        if not self.username_pattern.match(username):
            return False, '用户名只能包含字母、数字和下划线'
        
        # 检查是否以数字开头
        if username[0].isdigit():
            return False, '用户名不能以数字开头'
        
        return True, ''
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """验证邮箱
        
        Args:
            email: 邮箱地址
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not email or not email.strip():
            return False, '请输入邮箱地址'
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return False, '邮箱地址长度不能超过254个字符'
        
        if not self.email_pattern.match(email):
            return False, '请输入有效的邮箱地址'
        
        return True, ''
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """验证密码
        
        Args:
            password: 密码
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not password:
            return False, '请输入密码'
        
        if len(password) < 6:
            return False, '密码长度不能少于6位'
        
        if len(password) > 128:
            return False, '密码长度不能超过128位'
        
        # 检查密码复杂度（至少包含字母和数字）
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_letter and has_digit):
            return False, '密码必须包含至少一个字母和一个数字'
        
        # 检查是否包含空格
        if ' ' in password:
            return False, '密码不能包含空格'
        
        return True, ''
    
    def validate_password_change(self, old_password: str, 
                                 new_password: str,
                                 confirm_password: str) -> Tuple[bool, str]:
        """验证密码修改
        
        Args:
            old_password: 旧密码
            new_password: 新密码
            confirm_password: 确认新密码
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not old_password:
            return False, '请输入当前密码'
        
        # 验证新密码
        is_valid, error_msg = self.validate_password(new_password)
        if not is_valid:
            return False, error_msg
        
        # 验证确认密码
        if new_password != confirm_password:
            return False, '两次输入的新密码不一致'
        
        # 检查新旧密码是否相同
        if old_password == new_password:
            return False, '新密码不能与当前密码相同'
        
        return True, ''
    
    def is_email(self, text: str) -> bool:
        """检查文本是否为邮箱格式
        
        Args:
            text: 待检查的文本
            
        Returns:
            bool: 是否为邮箱格式
        """
        if not text:
            return False
        
        return self.email_pattern.match(text.strip().lower()) is not None
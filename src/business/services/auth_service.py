#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证服务 - 处理登录、注册等认证相关业务逻辑
"""

from typing import Dict, Optional
from ..models.user import User
from ..validators.auth_validator import AuthValidator
from ...data.api.network_client import NetworkWorker
from PyQt6.QtCore import QObject, pyqtSignal


class AuthService(QObject):
    """用户认证服务"""
    
    # 信号定义
    login_success = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    register_success = pyqtSignal(dict)
    register_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.validator = AuthValidator()
        self.current_user: Optional[User] = None
        self.api_base_url = 'https://pw.yangxz.top'
    
    def login(self, username: str, password: str, 
              remember: bool = False) -> bool:
        """用户登录
        
        Args:
            username: 用户名或邮箱
            password: 密码
            remember: 是否记住密码
            
        Returns:
            bool: 验证是否通过（不代表登录成功，需要等待网络响应）
        """
        # 验证输入
        is_valid, error_msg = self.validator.validate_login_input(
            username, password
        )
        if not is_valid:
            self.login_failed.emit(error_msg)
            return False
        
        # 创建网络请求
        self.login_worker = NetworkWorker(
            f'{self.api_base_url}/login',
            {
                'username': username,
                'password': password
            }
        )
        
        # 连接信号
        self.login_worker.finished.connect(self._on_login_response)
        self.login_worker.error.connect(self._on_login_error)
        
        # 启动请求
        self.login_worker.start()
        
        return True
    
    def register(self, username: str, email: str, password: str, 
                confirm_password: str) -> bool:
        """用户注册
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            confirm_password: 确认密码
            
        Returns:
            bool: 验证是否通过（不代表注册成功，需要等待网络响应）
        """
        # 验证输入
        is_valid, error_msg = self.validator.validate_register_input(
                username, email, password, confirm_password
        )
        if not is_valid:
            self.register_failed.emit(error_msg)
            return False
        
        # 创建网络请求
        self.register_worker = NetworkWorker(
            f'{self.api_base_url}/register',
            {
                'username': username,
                'email': email,
                'password': password
            }
        )
        
        # 连接信号
        self.register_worker.finished.connect(self._on_register_response)
        self.register_worker.error.connect(self._on_register_error)
        
        # 启动请求
        self.register_worker.start()
        
        return True
    
    def logout(self):
        """用户登出"""
        self.current_user = None
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """获取当前用户"""
        return self.current_user
    
    def _on_login_response(self, result: Dict):
        """处理登录响应"""
        try:
            # 创建用户对象
            user_data = result.get('user', {})
            self.current_user = User(
                id=user_data.get('id'),
                username=user_data.get('username'),
                email=user_data.get('email'),
                token=result.get('token')
            )
            
            self.login_success.emit(result)
            
        except Exception as e:
            self.login_failed.emit(f'登录响应处理失败: {str(e)}')
    
    def _on_login_error(self, error_msg: str):
        """处理登录错误"""
        self.login_failed.emit(error_msg)
    
    def _on_register_response(self, result: Dict):
        """处理注册响应"""
        self.register_success.emit(result)
    
    def _on_register_error(self, error_msg: str):
        """处理注册错误"""
        self.register_failed.emit(error_msg)
    
    def change_password(self, old_password: str, new_password: str, 
                      confirm_password: str) -> bool:
        """修改密码
        
        Args:
            old_password: 旧密码
            new_password: 新密码
            confirm_password: 确认新密码
            
        Returns:
            bool: 验证是否通过
        """
        if not self.is_logged_in():
            return False
        
        # 验证新密码
        is_valid, error_msg = self.validator.validate_password_change(
                old_password, new_password, confirm_password
        )
        if not is_valid:
            return False
        
        # TODO: 实现密码修改的网络请求
        return True
    
    def reset_password(self, email: str) -> bool:
        """重置密码
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 验证是否通过
        """
        if not self.validator.validate_email(email):
            return False
        
        # TODO: 实现密码重置的网络请求
        return True
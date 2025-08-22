#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库服务 - 处理数据库相关业务逻辑
"""


from PyQt6.QtCore import QObject, pyqtSignal
from ...data.database.database_manager import DatabaseManager


class DatabaseService(QObject):
    """数据库服务"""
    
    # 信号定义
    operation_success = pyqtSignal(str, dict)  # 操作类型, 结果数据
    operation_failed = pyqtSignal(str, str)    # 操作类型, 错误信息
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
    
    def get_all_users(self) -> bool:
        """获取所有用户
        
        Returns:
            bool: 操作是否成功启动
        """
        try:
            users = self.db_manager.get_all_users()
            self.operation_success.emit('get_users', {'users': users})
            return True
        except Exception as e:
            self.operation_failed.emit('get_users', str(e))
            return False
    
    def search_users(self, keyword: str) -> bool:
        """搜索用户
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            bool: 操作是否成功启动
        """
        try:
            users = self.db_manager.search_users(keyword)
            self.operation_success.emit('search_users', {'users': users})
            return True
        except Exception as e:
            self.operation_failed.emit('search_users', str(e))
            return False
    
    def add_user(self, username: str, email: str, password: str) -> bool:
        """添加用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            bool: 操作是否成功启动
        """
        try:
            user_id = self.db_manager.add_user(username, email, password)
            self.operation_success.emit(
                'add_user', 
                {'user_id': user_id, 'username': username}
            )
            return True
        except Exception as e:
            self.operation_failed.emit('add_user', str(e))
            return False
    
    def update_user(self, user_id: int, username: str = None,
                    email: str = None) -> bool:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            username: 新用户名（可选）
            email: 新邮箱（可选）
            
        Returns:
            bool: 操作是否成功启动
        """
        try:
            success = self.db_manager.update_user(user_id, username, email)
            if success:
                self.operation_success.emit(
                    'update_user', 
                    {'user_id': user_id}
                )
            else:
                self.operation_failed.emit('update_user', '用户不存在')
            return success
        except Exception as e:
            self.operation_failed.emit('update_user', str(e))
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作是否成功启动
        """
        try:
            success = self.db_manager.delete_user(user_id)
            if success:
                self.operation_success.emit(
                    'delete_user', 
                    {'user_id': user_id}
                )
            else:
                self.operation_failed.emit('delete_user', '用户不存在')
            return success
        except Exception as e:
            self.operation_failed.emit('delete_user', str(e))
            return False
    
    def get_user_by_id(self, user_id: int) -> bool:
        """根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作是否成功启动
        """
        try:
            user = self.db_manager.get_user_by_id(user_id)
            if user:
                self.operation_success.emit('get_user', {'user': user})
            else:
                self.operation_failed.emit('get_user', '用户不存在')
            return user is not None
        except Exception as e:
            self.operation_failed.emit('get_user', str(e))
            return False
    
    def get_database_stats(self) -> bool:
        """获取数据库统计信息
        
        Returns:
            bool: 操作是否成功启动
        """
        try:
            stats = self.db_manager.get_stats()
            self.operation_success.emit('get_stats', stats)
            return True
        except Exception as e:
            self.operation_failed.emit('get_stats', str(e))
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """备份数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 操作是否成功启动
        """
        try:
            success = self.db_manager.backup_database(backup_path)
            if success:
                self.operation_success.emit(
                    'backup_database', 
                    {'backup_path': backup_path}
                )
            else:
                self.operation_failed.emit('backup_database', '备份失败')
            return success
        except Exception as e:
            self.operation_failed.emit('backup_database', str(e))
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """恢复数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 操作是否成功启动
        """
        try:
            success = self.db_manager.restore_database(backup_path)
            if success:
                self.operation_success.emit(
                    'restore_database', 
                    {'backup_path': backup_path}
                )
            else:
                self.operation_failed.emit('restore_database', '恢复失败')
            return success
        except Exception as e:
            self.operation_failed.emit('restore_database', str(e))
            return False
    
    def initialize_database(self) -> bool:
        """初始化数据库
        
        Returns:
            bool: 操作是否成功启动
        """
        try:
            success = self.db_manager.initialize_database()
            if success:
                self.operation_success.emit('initialize_database', {})
            else:
                self.operation_failed.emit('initialize_database', '初始化失败')
            return success
        except Exception as e:
            self.operation_failed.emit('initialize_database', str(e))
            return False
    
    def close_database(self):
        """关闭数据库连接"""
        try:
            self.db_manager.close()
        except Exception as e:
            self.operation_failed.emit('close_database', str(e))
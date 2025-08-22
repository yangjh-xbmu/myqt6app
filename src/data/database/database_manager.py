#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器 - 处理SQLite数据库操作
"""

import sqlite3
import os
from typing import List, Dict, Optional, Any
from datetime import datetime


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def initialize_database(self) -> bool:
        """初始化数据库表结构
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # 创建用户会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # 创建索引
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_username "
                "ON users(username)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_users_email "
                "ON users(email)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_token "
                "ON user_sessions(token)"
            )
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"数据库初始化失败: {e}")
            return False
    
    def add_user(self, username: str, email: str, password_hash: str) -> int:
        """添加用户
        
        Args:
            username: 用户名
            email: 邮箱
            password_hash: 密码哈希
            
        Returns:
            int: 新用户的ID
            
        Raises:
            sqlite3.Error: 数据库操作错误
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, updated_at)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, datetime.now()))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 用户信息字典，不存在则返回None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE id = ? AND is_active = 1", 
            (user_id,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[Dict]: 用户信息字典，不存在则返回None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1", 
            (username,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            Optional[Dict]: 用户信息字典，不存在则返回None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1", 
            (email,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户
        
        Returns:
            List[Dict]: 用户信息列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE is_active = 1 ORDER BY created_at DESC"
        )
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def search_users(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索用户
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[Dict]: 匹配的用户信息列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{keyword}%"
        cursor.execute("""
            SELECT * FROM users 
            WHERE (username LIKE ? OR email LIKE ?) AND is_active = 1
            ORDER BY created_at DESC
        """, (search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def update_user(self, user_id: int, username: str = None,
                    email: str = None) -> bool:
        """更新用户信息
        
        Args:
            user_id: 用户ID
            username: 新用户名（可选）
            email: 新邮箱（可选）
            
        Returns:
            bool: 更新是否成功
        """
        if not username and not email:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 构建动态更新语句
        update_fields = []
        params = []
        
        if username:
            update_fields.append("username = ?")
            params.append(username)
        
        if email:
            update_fields.append("email = ?")
            params.append(email)
        
        update_fields.append("updated_at = ?")
        params.append(datetime.now())
        params.append(user_id)
        
        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = ? AND is_active = 1
        """
        
        cursor.execute(query, params)
        conn.commit()
        
        return cursor.rowcount > 0
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户（软删除）
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET is_active = 0, updated_at = ?
            WHERE id = ? AND is_active = 1
        """, (datetime.now(), user_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息
        
        Returns:
            Dict: 统计信息
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取用户总数
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        total_users = cursor.fetchone()[0]
        
        # 获取今日新增用户数
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE is_active = 1 AND DATE(created_at) = DATE('now')
        """)
        today_users = cursor.fetchone()[0]
        
        # 获取活跃会话数
        cursor.execute("""
            SELECT COUNT(*) FROM user_sessions 
            WHERE is_active = 1 AND expires_at > datetime('now')
        """)
        active_sessions = cursor.fetchone()[0]
        
        db_size = (
            os.path.getsize(self.db_path) 
            if os.path.exists(self.db_path) else 0
        )
        
        return {
            'total_users': total_users,
            'today_users': today_users,
            'active_sessions': active_sessions,
            'database_size': db_size
        }
    
    def backup_database(self, backup_path: str) -> bool:
        """备份数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 备份是否成功
        """
        try:
            if not os.path.exists(self.db_path):
                return False
            
            # 创建备份目录
            backup_dir = os.path.dirname(backup_path)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 复制数据库文件
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            return True
            
        except Exception as e:
            print(f"数据库备份失败: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """恢复数据库
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            bool: 恢复是否成功
        """
        try:
            if not os.path.exists(backup_path):
                return False
            
            # 关闭当前连接
            if self.connection:
                self.connection.close()
                self.connection = None
            
            # 复制备份文件
            import shutil
            shutil.copy2(backup_path, self.db_path)
            
            # 重新初始化连接
            self.initialize_database()
            
            return True
            
        except Exception as e:
            print(f"数据库恢复失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close()
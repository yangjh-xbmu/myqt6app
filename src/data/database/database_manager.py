#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器 - 负责所有数据库操作
"""

import sqlite3
from typing import List, Dict, Optional, Any


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, dbPath: str = 'local_database.db'):
        """
        初始化数据库管理器

        Args:
            dbPath: 数据库文件路径
        """
        self.dbPath = dbPath
        self.conn = None

    def connect(self):
        """连接到数据库"""
        try:
            self.conn = sqlite3.connect(self.dbPath)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"数据库连接失败: {e}")

    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def executeQuery(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        执行查询操作

        Args:
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"查询执行失败: {e}")
            return []
        finally:
            self.disconnect()

    def executeUpdate(self, query: str, params: tuple = ()) -> Optional[int]:
        """
        执行更新操作 (INSERT, UPDATE, DELETE)

        Args:
            query: SQL更新语句
            params: 更新参数

        Returns:
            返回最后插入的行ID
        """
        self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"更新执行失败: {e}")
            self.conn.rollback()
            return None
        finally:
            self.disconnect()

    def addUser(self, username: str, email: str, passwordHash: str) -> Optional[int]:
        """添加新用户"""
        query = "INSERT INTO users (username, email, passwordHash) VALUES (?, ?, ?)"
        return self.executeUpdate(query, (username, email, passwordHash))

    def getUserById(self, userId: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        query = "SELECT * FROM users WHERE id = ?"
        users = self.executeQuery(query, (userId,))
        return users[0] if users else None

    def getUserByUsername(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        query = "SELECT * FROM users WHERE username = ?"
        users = self.executeQuery(query, (username,))
        return users[0] if users else None

    def getUserByEmail(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        query = "SELECT * FROM users WHERE email = ?"
        users = self.executeQuery(query, (email,))
        return users[0] if users else None

    def getAllUsers(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        query = "SELECT * FROM users"
        return self.executeQuery(query)

    def searchUsers(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索用户"""
        query = "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?"
        param = f"%{keyword}%"
        return self.executeQuery(query, (param, param))

    def updateUser(self, userId: int, username: str, email: str) -> bool:
        """更新用户信息"""
        query = "UPDATE users SET username = ?, email = ? WHERE id = ?"
        result = self.executeUpdate(query, (username, email, userId))
        return result is not None

    def deleteUser(self, userId: int) -> bool:
        """删除用户"""
        query = "DELETE FROM users WHERE id = ?"
        result = self.executeUpdate(query, (userId,))
        return result is not None

    def getStats(self) -> Dict[str, Any]:
        """获取统计信息"""
        query = "SELECT COUNT(*) as totalUsers FROM users"
        stats = self.executeQuery(query)
        return stats[0] if stats else {'totalUsers': 0}

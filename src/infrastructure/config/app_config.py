#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理 - 统一管理应用配置
"""

import os
import json
from typing import Dict, Any
from pathlib import Path


class AppConfig:
    """应用配置管理器"""
    
    _instance = None
    _config_data = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config_data is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        # 默认配置
        self._config_data = {
            'app': {
                'name': 'MyQt6App',
                'version': '1.0.0',
                'debug': False,
                'theme': 'light'
            },
            'database': {
                'path': 'users.db',
                'backup_dir': 'backups',
                'auto_backup': True,
                'backup_interval': 24  # 小时
            },
            'network': {
                'timeout': 30,
                'retry_count': 3,
                'base_url': 'https://api.example.com',
                'user_agent': 'MyQt6App/1.0.0'
            },
            'ui': {
                'window_width': 800,
                'window_height': 600,
                'remember_size': True,
                'remember_position': True,
                'language': 'zh_CN'
            },
            'security': {
                'password_min_length': 8,
                'password_require_uppercase': True,
                'password_require_lowercase': True,
                'password_require_numbers': True,
                'password_require_symbols': False,
                'session_timeout': 3600  # 秒
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'logs/app.log',
                'max_file_size': 10485760,  # 10MB
                'backup_count': 5,
                'format': (
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            }
        }
        
        # 尝试加载配置文件
        config_file = self._get_config_file_path()
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
    
    def _get_config_file_path(self) -> Path:
        """获取配置文件路径"""
        # 优先使用环境变量指定的配置文件
        config_path = os.getenv('APP_CONFIG_PATH')
        if config_path:
            return Path(config_path)
        
        # 默认配置文件路径
        return Path('config/app_config.json')
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """合并配置"""
        for section, values in file_config.items():
            if section in self._config_data:
                if isinstance(values, dict):
                    self._config_data[section].update(values)
                else:
                    self._config_data[section] = values
            else:
                self._config_data[section] = values
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'app.name'
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config_data
        
        # 导航到最后一级的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def save(self) -> bool:
        """保存配置到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            config_file = self._get_config_file_path()
            
            # 确保目录存在
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def reload(self):
        """重新加载配置"""
        self._config_data = None
        self._load_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置段
        
        Args:
            section: 配置段名称
            
        Returns:
            Dict: 配置段内容
        """
        return self._config_data.get(section, {})
    
    def has_section(self, section: str) -> bool:
        """检查配置段是否存在
        
        Args:
            section: 配置段名称
            
        Returns:
            bool: 配置段是否存在
        """
        return section in self._config_data
    
    def has_key(self, key: str) -> bool:
        """检查配置键是否存在
        
        Args:
            key: 配置键
            
        Returns:
            bool: 配置键是否存在
        """
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return True
        except (KeyError, TypeError):
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置
        
        Returns:
            Dict: 所有配置数据
        """
        return self._config_data.copy()
    
    # 便捷方法
    @property
    def app_name(self) -> str:
        """应用名称"""
        return self.get('app.name', 'MyQt6App')
    
    @property
    def app_version(self) -> str:
        """应用版本"""
        return self.get('app.version', '1.0.0')
    
    @property
    def debug_mode(self) -> bool:
        """调试模式"""
        return self.get('app.debug', False)
    
    @property
    def database_path(self) -> str:
        """数据库路径"""
        return self.get('database.path', 'users.db')
    
    @property
    def network_timeout(self) -> int:
        """网络超时时间"""
        return self.get('network.timeout', 30)
    
    @property
    def window_size(self) -> tuple:
        """窗口大小"""
        width = self.get('ui.window_width', 800)
        height = self.get('ui.window_height', 600)
        return (width, height)
    
    @property
    def theme(self) -> str:
        """主题"""
        return self.get('app.theme', 'light')


# 全局配置实例
config = AppConfig()
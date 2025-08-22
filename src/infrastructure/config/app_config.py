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
    _configData = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._configData is None:
            self._loadConfig()

    def _loadConfig(self):
        """加载配置文件"""
        # 默认配置
        self._configData = {
            'app': {
                'name': 'MyQt6App',
                'version': '1.0.0',
                'debug': False,
                'theme': 'light'
            },
            'network': {
                'timeout': 30,
                'retryCount': 3,
                'baseUrl': 'https://api.example.com',
                'userAgent': 'MyQt6App/1.0.0'
            },
            'api': {
                'baseUrl': 'https://pw.yangxz.top'
            },
            'ui': {
                'windowWidth': 800,
                'windowHeight': 600,
                'rememberSize': True,
                'rememberPosition': True,
                'language': 'zh_CN'
            },
            'security': {
                'passwordMinLength': 8,
                'passwordRequireUppercase': True,
                'passwordRequireLowercase': True,
                'passwordRequireNumbers': True,
                'passwordRequireSymbols': False,
                'sessionTimeout': 3600  # 秒
            },
            'logging': {
                'level': 'INFO',
                'filePath': 'logs/app.log',
                'maxFileSize': 10485760,  # 10MB
                'backupCount': 5,
                'format': (
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            }
        }

        # 尝试加载配置文件
        config_file = self._getConfigFilePath()
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._mergeConfig(file_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")

    def _getConfigFilePath(self) -> Path:
        """获取配置文件路径"""
        # 优先使用环境变量指定的配置文件
        config_path = os.getenv('APP_CONFIG_PATH')
        if config_path:
            return Path(config_path)

        # 默认配置文件路径
        return Path('config/app_config.json')

    def _mergeConfig(self, file_config: Dict[str, Any]):
        """合并配置"""
        for section, values in file_config.items():
            if section in self._configData:
                if isinstance(values, dict):
                    self._configData[section].update(values)
                else:
                    self._configData[section] = values
            else:
                self._configData[section] = values

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'app.name'
            default: 默认值

        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self._configData

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
        config = self._configData

        # 导航到最后一级的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 设置值
        config[keys[-1]] = value

    def remove(self, key: str) -> bool:
        """删除配置项

        Args:
            key: 配置键，支持点号分隔的嵌套键

        Returns:
            bool: 删除是否成功
        """
        keys = key.split('.')
        config = self._configData

        try:
            # 导航到最后一级的父级
            for k in keys[:-1]:
                config = config[k]

            # 删除最后一级的键
            if keys[-1] in config:
                del config[keys[-1]]
                return True
            else:
                return False
        except (KeyError, TypeError):
            return False

    def save(self) -> bool:
        """保存配置到文件

        Returns:
            bool: 保存是否成功
        """
        try:
            config_file = self._getConfigFilePath()

            # 确保目录存在
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._configData, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def reload(self):
        """重新加载配置"""
        self._configData = None
        self._loadConfig()

    def getSection(self, section: str) -> Dict[str, Any]:
        """获取配置段

        Args:
            section: 配置段名称

        Returns:
            Dict: 配置段内容
        """
        return self._configData.get(section, {})

    def hasSection(self, section: str) -> bool:
        """检查配置段是否存在

        Args:
            section: 配置段名称

        Returns:
            bool: 配置段是否存在
        """
        return section in self._configData

    def hasKey(self, key: str) -> bool:
        """检查配置键是否存在

        Args:
            key: 配置键

        Returns:
            bool: 配置键是否存在
        """
        keys = key.split('.')
        value = self._configData

        try:
            for k in keys:
                value = value[k]
            return True
        except (KeyError, TypeError):
            return False

    def getAll(self) -> Dict[str, Any]:
        """获取所有配置

        Returns:
            Dict: 所有配置数据
        """
        return self._configData.copy()

    # 便捷方法
    @property
    def appName(self) -> str:
        """应用名称"""
        return self.get('app.name', 'MyQt6App')

    @property
    def appVersion(self) -> str:
        """应用版本"""
        return self.get('app.version', '1.0.0')

    @property
    def debugMode(self) -> bool:
        """调试模式"""
        return self.get('app.debug', False)

    @property
    def networkTimeout(self) -> int:
        """网络超时时间"""
        return self.get('network.timeout', 30)

    @property
    def windowSize(self) -> tuple:
        """窗口大小"""
        width = self.get('ui.windowWidth', 800)
        height = self.get('ui.windowHeight', 600)
        return (width, height)

    @property
    def theme(self) -> str:
        """主题"""
        return self.get('app.theme', 'light')


# 全局配置实例
config = AppConfig()

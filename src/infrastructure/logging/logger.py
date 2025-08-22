#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统 - 统一管理应用日志
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from ..config.app_config import config


class Logger:
    """日志管理器"""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def get_logger(cls, name: str = 'app') -> logging.Logger:
        """获取日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        if not cls._initialized:
            cls._setup_logging()
            cls._initialized = True
        
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def _setup_logging(cls):
        """设置日志系统"""
        # 获取日志配置
        log_level = config.get('logging.level', 'INFO')
        log_file = config.get('logging.file_path', 'logs/app.log')
        max_file_size = config.get('logging.max_file_size', 10485760)
        backup_count = config.get('logging.backup_count', 5)
        log_format = config.get(
            'logging.format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 设置根日志级别
        logging.getLogger().setLevel(getattr(logging, log_level.upper()))
        
        # 创建格式化器
        formatter = logging.Formatter(log_format)
        
        # 创建文件处理器（带轮转）
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 如果是调试模式，控制台也显示DEBUG级别
        if config.debug_mode:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)
        
        # 添加处理器到根日志记录器
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """创建日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        logger = logging.getLogger(name)
        
        # 防止重复添加处理器
        if not logger.handlers:
            # 继承根日志记录器的处理器
            logger.propagate = True
        
        return logger
    
    @classmethod
    def set_level(cls, level: str, logger_name: Optional[str] = None):
        """设置日志级别
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            logger_name: 日志记录器名称，None表示设置根日志记录器
        """
        log_level = getattr(logging, level.upper())
        
        if logger_name:
            if logger_name in cls._loggers:
                cls._loggers[logger_name].setLevel(log_level)
        else:
            logging.getLogger().setLevel(log_level)
    
    @classmethod
    def add_file_handler(cls, logger_name: str, file_path: str,
                         level: str = 'INFO'):
        """为指定日志记录器添加文件处理器
        
        Args:
            logger_name: 日志记录器名称
            file_path: 日志文件路径
            level: 日志级别
        """
        if logger_name not in cls._loggers:
            cls._loggers[logger_name] = cls._create_logger(logger_name)
        
        logger = cls._loggers[logger_name]
        
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        
        # 设置格式
        formatter = logging.Formatter(
            config.get(
                'logging.format',
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
    
    @classmethod
    def remove_handlers(cls, logger_name: str):
        """移除指定日志记录器的所有处理器
        
        Args:
            logger_name: 日志记录器名称
        """
        if logger_name in cls._loggers:
            logger = cls._loggers[logger_name]
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()


class LoggerMixin:
    """日志混入类，为其他类提供日志功能"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器"""
        class_name = self.__class__.__name__.lower()
        return Logger.get_logger(class_name)


# 便捷函数
def get_logger(name: str = 'app') -> logging.Logger:
    """获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return Logger.get_logger(name)


def configure_logging(log_level: str, debug_mode: bool = False):
    """配置日志系统的便捷函数
    
    Args:
        log_level: 日志级别
        debug_mode: 是否为调试模式
    """
    # 设置日志级别
    Logger.set_level(log_level)
    
    if debug_mode:
        Logger.set_level('DEBUG')
    
    # 触发日志系统初始化
    logger = get_logger('main')
    logger.info(f"日志系统已配置 - 级别: {log_level}")
    
    if debug_mode:
        logger.debug("调试模式已启用")


# 预定义的日志记录器
app_logger = get_logger('app')
ui_logger = get_logger('ui')
business_logger = get_logger('business')
data_logger = get_logger('data')
network_logger = get_logger('network')
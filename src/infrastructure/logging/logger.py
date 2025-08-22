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
    def getLogger(cls, name: str = 'app') -> logging.Logger:
        """获取日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            logging.Logger: 日志记录器实例
        """
        if not cls._initialized:
            cls._setupLogging()
            cls._initialized = True

        if name not in cls._loggers:
            cls._loggers[name] = cls._createLogger(name)

        return cls._loggers[name]

    @classmethod
    def _setupLogging(cls):
        """设置日志系统"""
        # 获取日志配置
        logLevel = config.get('logging.level', 'INFO')
        logFile = config.get('logging.filePath', 'logs/app.log')
        maxFileSize = config.get('logging.maxFileSize', 10485760)
        backupCount = config.get('logging.backupCount', 5)
        logFormat = config.get(
            'logging.format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 确保日志目录存在
        logPath = Path(logFile)
        logPath.parent.mkdir(parents=True, exist_ok=True)

        # 设置根日志级别
        logging.getLogger().setLevel(getattr(logging, logLevel.upper()))

        # 创建格式化器
        formatter = logging.Formatter(logFormat)

        # 创建文件处理器（带轮转）
        fileHandler = logging.handlers.RotatingFileHandler(
            logFile,
            maxBytes=maxFileSize,
            backupCount=backupCount,
            encoding='utf-8'
        )
        fileHandler.setFormatter(formatter)

        # 创建控制台处理器
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)

        # 如果是调试模式，控制台也显示DEBUG级别
        if config.debugMode:
            consoleHandler.setLevel(logging.DEBUG)
        else:
            consoleHandler.setLevel(logging.INFO)

        # 添加处理器到根日志记录器
        rootLogger = logging.getLogger()
        rootLogger.addHandler(fileHandler)
        rootLogger.addHandler(consoleHandler)

    @classmethod
    def _createLogger(cls, name: str) -> logging.Logger:
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
    def setLevel(cls, level: str, loggerName: Optional[str] = None):
        """设置日志级别

        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            loggerName: 日志记录器名称，None表示设置根日志记录器
        """
        logLevel = getattr(logging, level.upper())

        if loggerName:
            if loggerName in cls._loggers:
                cls._loggers[loggerName].setLevel(logLevel)
        else:
            logging.getLogger().setLevel(logLevel)

    @classmethod
    def addFileHandler(cls, loggerName: str, filePath: str,
                       level: str = 'INFO'):
        """为指定日志记录器添加文件处理器

        Args:
            loggerName: 日志记录器名称
            filePath: 日志文件路径
            level: 日志级别
        """
        if loggerName not in cls._loggers:
            cls._loggers[loggerName] = cls._createLogger(loggerName)

        logger = cls._loggers[loggerName]

        # 确保目录存在
        Path(filePath).parent.mkdir(parents=True, exist_ok=True)

        # 创建文件处理器
        fileHandler = logging.FileHandler(filePath, encoding='utf-8')
        fileHandler.setLevel(getattr(logging, level.upper()))

        # 设置格式
        formatter = logging.Formatter(
            config.get(
                'logging.format',
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        fileHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)

    @classmethod
    def removeHandlers(cls, loggerName: str):
        """移除指定日志记录器的所有处理器

        Args:
            loggerName: 日志记录器名称
        """
        if loggerName in cls._loggers:
            logger = cls._loggers[loggerName]
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()


class LoggerMixin:
    """日志混入类，为其他类提供日志功能"""

    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器"""
        className = self.__class__.__name__.lower()
        return Logger.getLogger(className)


# 便捷函数
def getLogger(name: str = 'app') -> logging.Logger:
    """获取日志记录器的便捷函数

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    return Logger.getLogger(name)


def configureLogging(logLevel: str, debugMode: bool = False):
    """配置日志系统的便捷函数

    Args:
        logLevel: 日志级别
        debugMode: 是否为调试模式
    """
    # 设置日志级别
    Logger.setLevel(logLevel)

    if debugMode:
        Logger.setLevel('DEBUG')

    # 触发日志系统初始化
    logger = getLogger('main')
    logger.info(f"日志系统已配置 - 级别: {logLevel}")

    if debugMode:
        logger.debug("调试模式已启用")


# 预定义的日志记录器
appLogger = getLogger('app')
uiLogger = getLogger('ui')
businessLogger = getLogger('business')
dataLogger = getLogger('data')
networkLogger = getLogger('network')

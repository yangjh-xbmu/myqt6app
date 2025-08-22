#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用主入口 - 重构后的分层架构应用
"""

import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
srcPath = Path(__file__).parent
if str(srcPath) not in sys.path:
    sys.path.insert(0, str(srcPath))


# 延迟导入以避免循环依赖
def getImports():
    """获取所需的导入模块"""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTranslator, QLocale
    from infrastructure.config.app_config import config
    from infrastructure.logging.logger import getLogger, configureLogging
    from ui.launcher import AppLauncher

    return (
        QApplication, QTranslator, QLocale, config,
        getLogger, configureLogging, AppLauncher
    )


def setupApplication():
    """设置应用程序

    Returns:
        应用程序实例
    """
    qApplication, qTranslator, qLocale, config, _, _, _ = getImports()

    app = qApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName(config.appName)
    app.setApplicationVersion(config.appVersion)
    app.setOrganizationName("MyQt6App")
    app.setOrganizationDomain("myqt6app.com")

    # 设置国际化
    translator = qTranslator()
    locale = qLocale(config.get('ui.language', 'zh_CN'))

    if translator.load(locale, "app", "_", "translations"):
        app.installTranslator(translator)

    return app


def parseArguments():
    """解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='MyQt6App - 分层架构的Qt6应用程序'
    )

    parser.add_argument(
        '--mode',
        choices=['main', 'login', 'register', 'auth', 'worker-test'],
        default='main',
        help='启动模式 (默认: main)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='配置文件路径'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )

    return parser.parse_args()


# configure_logging函数已移至infrastructure.logging.logger模块


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parseArguments()

        # 获取导入的模块
        (
            _, _, _, config, getLogger,
            configureLogging, AppLauncher
        ) = getImports()

        # 如果指定了配置文件，设置环境变量
        if args.config:
            import os
            os.environ['APP_CONFIG_PATH'] = args.config
            config.reload()

        # 配置日志系统
        configureLogging(logLevel=args.log_level, debugMode=args.debug)

        # 创建应用程序
        app = setupApplication()

        # 创建启动器
        launcher = AppLauncher()

        # 根据模式启动相应的窗口
        # 启动对应模式的窗口
        success = launcher.launch(args.mode)

        if not success:
            logger = getLogger('main')
            logger.error(f"启动模式 {args.mode} 失败")
            return 1

        # 记录启动信息
        logger = getLogger('main')
        logger.info(f"应用程序已启动 - 模式: {args.mode}")

        # 运行应用程序
        exitCode = app.exec()

        logger.info(f"应用程序退出 - 退出码: {exitCode}")
        return exitCode

    except KeyboardInterrupt:
        print("\n应用程序被用户中断")
        return 0

    except Exception as exception:
        print(f"应用程序启动失败: {exception}")

        # 尝试记录错误
        try:
            _, _, _, _, getLogger, _, _ = getImports()
            logger = getLogger('main')
            logger.error(f"应用程序启动失败: {exception}", exc_info=True)
        except Exception:
            pass

        return 1


if __name__ == '__main__':
    sys.exit(main())

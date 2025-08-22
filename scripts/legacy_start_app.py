#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用程序启动器
提供多种启动选项的便捷入口
"""

import sys
import os
import argparse


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PyQt6 用户权限管理系统启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
启动选项:
  python start_app.py                    # 启动完整的菜单式应用（推荐）
  python start_app.py --login            # 仅启动登录界面
  python start_app.py --register         # 仅启动注册界面
  python start_app.py --auth             # 启动登录+注册界面
  python start_app.py --test             # 启动 Worker API 测试工具
  python start_app.py --simple           # 启动简单的示例应用

示例:
  python start_app.py                    # 启动主应用
  python start_app.py --auth             # 启动用户认证应用
  python start_app.py --test             # 启动测试工具
        """
    )
    
    # 添加启动选项
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--login', 
        action='store_true', 
        help='启动登录界面'
    )
    group.add_argument(
        '--register', 
        action='store_true', 
        help='启动注册界面'
    )
    group.add_argument(
        '--auth', 
        action='store_true', 
        help='启动用户认证应用（登录+注册）'
    )
    group.add_argument(
        '--test', 
        action='store_true', 
        help='启动 Worker API 测试工具'
    )
    group.add_argument(
        '--simple', 
        action='store_true', 
        help='启动简单示例应用'
    )
    
    args = parser.parse_args()
    
    # 根据参数启动相应的应用
    if args.login:
        print("🚀 启动登录界面...")
        os.system(f"{sys.executable} login_app.py")
    elif args.register:
        print("🚀 启动注册界面...")
        os.system(f"{sys.executable} register_app.py")
    elif args.auth:
        print("🚀 启动用户认证应用...")
        os.system(f"{sys.executable} user_auth_app.py")
    elif args.test:
        print("🚀 启动 Worker API 测试工具...")
        os.system(f"{sys.executable} worker_test_app.py")
    elif args.simple:
        print("🚀 启动简单示例应用...")
        os.system(f"{sys.executable} main.py")
    else:
        print("🚀 启动完整的菜单式应用...")
        print("💡 提示: 这是推荐的启动方式，包含所有功能")
        os.system(f"{sys.executable} main_app_with_menu.py")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户信息查看工具
使用方法: python view_users.py [local|remote]
"""

import json
import subprocess
import sys
import os


def run_wrangler_command(database_type="remote"):
    """执行 wrangler 命令查询用户数据"""
    # 切换到 worker 目录
    worker_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "worker"
    )
    
    cmd = [
        "npx", "wrangler", "d1", "execute", "qt6-user-db",
        "--command", 
        "SELECT id, username, email, created_at FROM users " +
        "ORDER BY created_at DESC;",
        "--json"
    ]
    
    if database_type == "remote":
        cmd.append("--remote")
    
    try:
        result = subprocess.run(
            cmd, cwd=worker_dir, capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行命令失败: {e}")
        print(f"错误输出: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ 解析 JSON 失败: {e}")
        return None


def format_user_info(users_data):
    """格式化用户信息显示"""
    if not users_data or not users_data[0].get("results"):
        print("📭 没有找到用户数据")
        return
    
    users = users_data[0]["results"]
    meta = users_data[0].get("meta", {})
    
    print(f"👥 用户列表 (共 {len(users)} 个用户)")
    print("=" * 80)
    
    for user in users:
        print(f"🆔 ID: {user['id']}")
        print(f"👤 用户名: {user['username']}")
        print(f"📧 邮箱: {user['email']}")
        print(f"📅 注册时间: {user['created_at']}")
        print("-" * 40)
    
    # 显示查询元信息
    if meta:
        print("\n📊 查询信息:")
        if "duration" in meta:
            print(f"   ⏱️  查询耗时: {meta['duration']} ms")
        if "served_by_region" in meta:
            print(f"   🌍 服务区域: {meta['served_by_region']}")
        if "rows_read" in meta:
            print(f"   📖 读取行数: {meta['rows_read']}")


def main():
    """主函数"""
    database_type = sys.argv[1] if len(sys.argv) > 1 else "remote"
    
    if database_type not in ["local", "remote"]:
        print("❌ 参数错误，请使用 'local' 或 'remote'")
        sys.exit(1)
    
    db_type_text = "本地" if database_type == "local" else "远程"
    print(f"📊 正在查看 {db_type_text} 数据库用户信息...\n")
    
    users_data = run_wrangler_command(database_type)
    if users_data:
        format_user_info(users_data)
    
    print("\n💡 使用提示:")
    print("   python view_users.py local   # 查看本地数据库")
    print("   python view_users.py remote  # 查看远程数据库")
    print("   python view_users.py         # 默认查看远程数据库")


if __name__ == "__main__":
    main()
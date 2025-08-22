# 用户管理工具脚本

本目录包含用于管理和查看用户数据的实用工具脚本。

## 📋 脚本列表

### 1. view_users.py - 用户信息查看工具（推荐）

**功能**: 以友好的格式显示数据库中的用户信息

**使用方法**:
```bash
# 查看远程数据库用户（默认）
python scripts/view_users.py

# 查看远程数据库用户（显式指定）
python scripts/view_users.py remote

# 查看本地数据库用户
python scripts/view_users.py local
```

**输出示例**:
```
📊 正在查看 远程 数据库用户信息...

👥 用户列表 (共 4 个用户)
================================================================================
🆔 ID: 4
👤 用户名: yangjh
📧 邮箱: yangjh@yeah.net
📅 注册时间: 2025-08-22 04:08:46
----------------------------------------
...

📊 查询信息:
   ⏱️  查询耗时: 0.4386 ms
   🌍 服务区域: WNAM
   📖 读取行数: 8
```

### 2. view_users.sh - Shell 脚本版本

**功能**: 使用 Shell 脚本直接调用 wrangler 命令

**使用方法**:
```bash
# 查看远程数据库用户（默认）
./scripts/view_users.sh

# 查看远程数据库用户（显式指定）
./scripts/view_users.sh remote

# 查看本地数据库用户
./scripts/view_users.sh local
```

## 🔧 直接使用 Wrangler 命令

如果你想直接使用 wrangler 命令，可以在 `worker` 目录下执行：

```bash
cd worker

# 查看远程数据库用户
npx wrangler d1 execute qt6-user-db --command="SELECT id, username, email, created_at FROM users ORDER BY created_at DESC;" --remote --json

# 查看本地数据库用户
npx wrangler d1 execute qt6-user-db --command="SELECT id, username, email, created_at FROM users ORDER BY created_at DESC;" --json

# 查看表结构
npx wrangler d1 execute qt6-user-db --command=".schema users" --remote

# 统计用户数量
npx wrangler d1 execute qt6-user-db --command="SELECT COUNT(*) as user_count FROM users;" --remote --json
```

## 📊 数据库信息

- **数据库名称**: `qt6-user-db`
- **表名**: `users`
- **字段**:
  - `id`: 用户ID（主键，自增）
  - `username`: 用户名（唯一）
  - `email`: 邮箱地址（唯一）
  - `password_hash`: 密码哈希值
  - `created_at`: 创建时间
  - `updated_at`: 更新时间

## 💡 使用建议

1. **推荐使用 Python 脚本** (`view_users.py`)，因为它提供了更友好的输出格式
2. **生产环境**通常使用 `--remote` 参数查看远程数据库
3. **开发测试**时可以使用本地数据库进行调试
4. 定期备份重要的用户数据

## 🚀 扩展功能

你可以基于这些脚本扩展更多功能：

- 添加用户搜索功能
- 实现用户数据导出
- 创建用户统计报告
- 添加用户权限管理

## 🔒 安全注意事项

- 这些脚本只显示用户的基本信息，不会显示密码哈希值
- 确保只有授权人员可以访问这些管理工具
- 在生产环境中谨慎使用数据库操作命令
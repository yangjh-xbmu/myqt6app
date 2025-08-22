#!/bin/bash

# 查看用户信息脚本
# 使用方法: ./view_users.sh [local|remote]

cd "$(dirname "$0")/../worker"

DATABASE_TYPE=${1:-remote}

if [ "$DATABASE_TYPE" = "local" ]; then
    echo "📊 查看本地数据库用户信息..."
    npx wrangler d1 execute qt6-user-db --command="SELECT id, username, email, created_at FROM users ORDER BY created_at DESC;" --json
else
    echo "📊 查看远程数据库用户信息..."
    npx wrangler d1 execute qt6-user-db --command="SELECT id, username, email, created_at FROM users ORDER BY created_at DESC;" --remote --json
fi

echo ""
echo "💡 提示:"
echo "  - 使用 './view_users.sh local' 查看本地数据库"
echo "  - 使用 './view_users.sh remote' 或 './view_users.sh' 查看远程数据库"
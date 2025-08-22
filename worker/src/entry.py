from js import Response
from datetime import datetime
import json
import hashlib
import secrets
import re


def generate_salt():
    """生成随机盐值"""
    return secrets.token_hex(16)


def hash_password(password, salt):
    """使用盐值哈希密码"""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """验证用户名格式"""
    if len(username) < 3 or len(username) > 20:
        return False
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, username) is not None


async def execute_db_query(db, query, params=None):
    """执行数据库查询"""
    try:
        if params:
            # 使用 D1 的 bind 方法，一次性传入所有参数
            result = await db.prepare(query).bind(*params).all()
        else:
            result = await db.prepare(query).all()

        # 处理 D1 返回的 JsProxy 对象
        try:
            # 尝试访问 results 属性
            data = result.results if hasattr(result, 'results') else []
            # 转换为 Python 列表
            if data:
                data = list(data)
            return {'success': True, 'data': data}
        except Exception:
            # 如果无法访问 results，返回空列表
            return {'success': True, 'data': []}
    except Exception as e:
        return {'success': False, 'error': str(e)}


async def on_fetch(request, env):
    # CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }

    # Handle preflight requests
    if request.method == 'OPTIONS':
        return Response.new('', {'headers': cors_headers})

    try:
        url = request.url
        method = request.method

        # Parse URL path
        path = url.split('/')[-1].split('?')[0]

        if path == 'test' and method == 'GET':
            # 返回测试数据
            test_data = {
                'message': 'Hello from Cloudflare Python Worker!',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'items': [
                        {'id': 1, 'name': 'Item 1', 'value': 100},
                        {'id': 2, 'name': 'Item 2', 'value': 200},
                        {'id': 3, 'name': 'Item 3', 'value': 300}
                    ],
                    'total': 3
                }
            }
            return Response.new(
                json.dumps(test_data),
                {'headers': cors_headers}
            )

        elif path == 'data' and method == 'POST':
            # 处理POST数据
            response_data = {
                'message': 'POST request processed successfully',
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            return Response.new(
                json.dumps(response_data),
                {'headers': cors_headers}
            )

        elif path == 'register' and method == 'POST':
            # 用户注册
            try:
                request_text = await request.text()
                request_data = json.loads(request_text) if request_text else {}

                username = request_data.get('username', '').strip()
                email = request_data.get('email', '').strip()
                password = request_data.get('password', '')
                display_name = request_data.get('display_name', '').strip()

                # 验证输入
                if not username or not validate_username(username):
                    error_msg = '用户名格式不正确（3-20个字符，只能包含字母、数字、下划线）'
                    return Response.new(
                        json.dumps({'error': error_msg}),
                        {'status': 400, 'headers': cors_headers}
                    )

                if not email or not validate_email(email):
                    return Response.new(
                        json.dumps({'error': '邮箱格式不正确'}),
                        {'status': 400, 'headers': cors_headers}
                    )

                if not password or len(password) < 6:
                    return Response.new(
                        json.dumps({'error': '密码长度至少6个字符'}),
                        {'status': 400, 'headers': cors_headers}
                    )

                # 检查用户名和邮箱是否已存在
                check_query = (
                    "SELECT id FROM users WHERE username = ? OR email = ?"
                )
                check_result = await execute_db_query(
                    env.DB, check_query, [username, email]
                )

                if not check_result['success']:
                    error_details = check_result.get('error', 'Unknown error')
                    return Response.new(
                        json.dumps({
                            'error': '数据库查询失败',
                            'details': error_details
                        }),
                        {'status': 500, 'headers': cors_headers}
                    )

                if check_result['data']:
                    return Response.new(
                        json.dumps({'error': '用户名或邮箱已存在'}),
                        {'status': 409, 'headers': cors_headers}
                    )

                # 创建新用户
                salt = generate_salt()
                password_hash = hash_password(password, salt)

                insert_query = """
                    INSERT INTO users 
                    (username, email, password_hash, salt, display_name)
                    VALUES (?, ?, ?, ?, ?)
                """

                params = [username, email, password_hash, salt,
                          display_name or username]
                insert_result = await execute_db_query(
                    env.DB, insert_query, params
                )

                if not insert_result['success']:
                    return Response.new(
                        json.dumps({'error': '用户创建失败'}),
                        {'status': 500, 'headers': cors_headers}
                    )

                # 为新用户分配默认角色（普通用户）
                role_query = "SELECT id FROM roles WHERE name = 'user'"
                role_result = await execute_db_query(env.DB, role_query)

                if role_result['success'] and role_result['data']:
                    try:
                        role_id = role_result['data'][0]['id']
                        # 尝试从不同位置获取 user_id
                        user_id = None
                        meta = insert_result.get('meta', {})
                        if hasattr(meta, 'last_row_id'):
                            user_id = insert_result['meta']['last_row_id']
                        elif ('meta' in insert_result and 
                              'last_row_id' in insert_result['meta']):
                            user_id = insert_result['meta']['last_row_id']
                    except Exception:
                        # 如果无法获取 user_id，跳过角色分配
                        user_id = None

                    if user_id:
                        assign_role_query = """
                            INSERT INTO user_roles (user_id, role_id)
                            VALUES (?, ?)
                        """
                        await execute_db_query(
                            env.DB, assign_role_query, [user_id, role_id]
                        )

                response_data = {
                    'message': '用户注册成功',
                    'user': {
                        'username': username,
                        'email': email,
                        'display_name': display_name or username
                    }
                }

                return Response.new(
                    json.dumps(response_data),
                    {'headers': cors_headers}
                )

            except Exception as e:
                return Response.new(
                    json.dumps({'error': f'注册失败: {str(e)}'}),
                    {'status': 500, 'headers': cors_headers}
                )

        elif path == 'login' and method == 'POST':
            # 用户登录
            try:
                request_text = await request.text()
                request_data = json.loads(request_text) if request_text else {}

                username_or_email = request_data.get('username', '').strip()
                password = request_data.get('password', '')

                if not username_or_email or not password:
                    error_msg = '用户名/邮箱和密码不能为空'
                    return Response.new(
                        json.dumps({'error': error_msg}),
                        {'status': 400, 'headers': cors_headers}
                    )

                # 查找用户
                user_query = """
                    SELECT id, username, email, password_hash, salt, 
                           display_name, status
                    FROM users 
                    WHERE (username = ? OR email = ?) AND status = 'active'
                """

                user_result = await execute_db_query(
                    env.DB, user_query,
                    [username_or_email, username_or_email]
                )

                if not user_result['success'] or not user_result['data']:
                    error_msg = '用户名/邮箱或密码错误'
                    return Response.new(
                        json.dumps({'error': error_msg}),
                        {'status': 401, 'headers': cors_headers}
                    )

                try:
                    user_data = user_result['data'][0]
                    # 将JsProxy对象转换为Python字典
                    user = {}
                    keys = ['id', 'username', 'email', 'password_hash', 
                            'salt', 'display_name', 'status']
                    for key in keys:
                        try:
                            user[key] = getattr(user_data, key)
                        except Exception:
                            user[key] = None

                    # 验证密码
                    if user['salt'] and user['password_hash']:
                        expected_hash = hash_password(password, user['salt'])
                        if expected_hash != user['password_hash']:
                            error_msg = '用户名/邮箱或密码错误'
                            return Response.new(
                                json.dumps({'error': error_msg}),
                                {'status': 401, 'headers': cors_headers}
                            )
                    else:
                        return Response.new(
                            json.dumps({'error': '用户数据不完整'}),
                            {'status': 500, 'headers': cors_headers}
                        )

                except Exception as e:
                    return Response.new(
                        json.dumps({'error': f'登录处理失败: {str(e)}'}),
                        {'status': 500, 'headers': cors_headers}
                    )

                # 跳过密码验证错误处理，因为已经在上面处理了
                if False:  # 这行代码永远不会执行，只是为了保持原有结构
                    return Response.new(
                        json.dumps({'error': '用户名/邮箱或密码错误'}),
                        {'status': 401, 'headers': cors_headers}
                    )

                # 更新最后登录时间
                update_login_query = """
                    UPDATE users SET last_login_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """
                await execute_db_query(
                    env.DB, update_login_query, [user['id']]
                )

                # 生成会话令牌（简化版本）
                session_token = secrets.token_urlsafe(32)

                response_data = {
                    'message': '登录成功',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'display_name': user['display_name']
                    },
                    'session_token': session_token
                }

                return Response.new(
                    json.dumps(response_data),
                    {'headers': cors_headers}
                )

            except Exception as e:
                return Response.new(
                    json.dumps({'error': f'登录失败: {str(e)}'}),
                    {'status': 500, 'headers': cors_headers}
                )

        elif path == 'forgot-password' and method == 'POST':
            # 忘记密码
            try:
                request_text = await request.text()
                request_data = json.loads(request_text) if request_text else {}

                email = request_data.get('email', '').strip().lower()

                if not email:
                    return Response.new(
                        json.dumps({'error': '邮箱地址不能为空'}),
                        {'status': 400, 'headers': cors_headers}
                    )

                if not validate_email(email):
                    return Response.new(
                        json.dumps({'error': '邮箱格式不正确'}),
                        {'status': 400, 'headers': cors_headers}
                    )

                # 查找用户
                user_query = """
                    SELECT id, username, email, display_name
                    FROM users 
                    WHERE email = ? AND status = 'active'
                """

                user_result = await execute_db_query(
                    env.DB, user_query, [email]
                )

                # 无论用户是否存在，都返回成功信息（安全考虑）
                if user_result['success'] and user_result['data']:
                    # 生成重置令牌
                    reset_token = secrets.token_urlsafe(32)
                    
                    # 保存重置令牌到数据库（有效期1小时）
                    save_token_query = """
                        INSERT OR REPLACE INTO password_reset_tokens 
                        (user_id, token, expires_at, created_at)
                        VALUES (?, ?, datetime('now', '+1 hour'), 
                                datetime('now'))
                    """
                    
                    user_data = user_result['data'][0]
                    user_id = getattr(user_data, 'id')
                    
                    await execute_db_query(
                        env.DB, save_token_query, [user_id, reset_token]
                    )
                    
                    # TODO: 发送重置密码邮件
                    # 这里应该集成邮件服务发送重置链接
                    # reset_link = (
                    #     f"https://your-app.com/reset-password"
                    #     f"?token={reset_token}"
                    # )

                response_data = {
                    'message': '如果该邮箱已注册，您将收到密码重置邮件',
                    'success': True
                }

                return Response.new(
                    json.dumps(response_data),
                    {'headers': cors_headers}
                )

            except Exception as e:
                error_msg = f'处理忘记密码请求失败: {str(e)}'
                return Response.new(
                    json.dumps({'error': error_msg}),
                    {'status': 500, 'headers': cors_headers}
                )

        elif path == 'reset-password' and method == 'POST':
            # 重置密码
            try:
                request_text = await request.text()
                request_data = json.loads(request_text) if request_text else {}

                token = request_data.get('token', '').strip()
                new_password = request_data.get('new_password', '')

                if not token or not new_password:
                    return Response.new(
                        json.dumps({'error': '重置令牌和新密码不能为空'}),
                        {'status': 400, 'headers': cors_headers}
                    )

                if len(new_password) < 6:
                    return Response.new(
                        json.dumps({'error': '密码长度至少6位'}),
                        {'status': 400, 'headers': cors_headers}
                    )

                # 验证重置令牌
                token_query = """
                    SELECT prt.user_id, u.username, u.email
                    FROM password_reset_tokens prt
                    JOIN users u ON prt.user_id = u.id
                    WHERE prt.token = ? AND prt.expires_at > datetime('now')
                    AND u.status = 'active'
                """

                token_result = await execute_db_query(
                    env.DB, token_query, [token]
                )

                if not token_result['success'] or not token_result['data']:
                    error_msg = '重置令牌无效或已过期'
                    return Response.new(
                        json.dumps({'error': error_msg}),
                        {'status': 400, 'headers': cors_headers}
                    )

                token_data = token_result['data'][0]
                user_id = getattr(token_data, 'user_id')

                # 生成新的盐值和密码哈希
                new_salt = generate_salt()
                new_password_hash = hash_password(new_password, new_salt)

                # 更新用户密码
                update_password_query = """
                    UPDATE users 
                    SET password_hash = ?, salt = ?, updated_at = datetime('now')
                    WHERE id = ?
                """

                await execute_db_query(
                    env.DB, update_password_query,
                    [new_password_hash, new_salt, user_id]
                )

                # 删除已使用的重置令牌
                delete_token_query = """
                    DELETE FROM password_reset_tokens WHERE token = ?
                """
                await execute_db_query(env.DB, delete_token_query, [token])

                response_data = {
                    'message': '密码重置成功，请使用新密码登录',
                    'success': True
                }

                return Response.new(
                    json.dumps(response_data),
                    {'headers': cors_headers}
                )

            except Exception as e:
                return Response.new(
                    json.dumps({'error': f'重置密码失败: {str(e)}'}),
                    {'status': 500, 'headers': cors_headers}
                )

        elif path == 'status' and method == 'GET':
            # 返回Worker状态信息
            status_data = {
                'status': 'healthy',
                'uptime': 'N/A (serverless)',
                'version': '1.0.0',
                'endpoints': [
                    {
                        'path': '/test',
                        'method': 'GET',
                        'description': '获取测试数据'
                    },
                    {
                        'path': '/register',
                        'method': 'POST',
                        'description': '用户注册'
                    },
                    {
                        'path': '/login',
                        'method': 'POST',
                        'description': '用户登录'
                    },
                    {
                        'path': '/forgot-password',
                        'method': 'POST',
                        'description': '忘记密码'
                    },
                    {
                        'path': '/reset-password',
                        'method': 'POST',
                        'description': '重置密码'
                    },
                    {
                        'path': '/data',
                        'method': 'POST',
                        'description': '处理POST数据'
                    },
                    {
                        'path': '/status',
                        'method': 'GET',
                        'description': '获取状态信息'
                    }
                ]
            }
            return Response.new(
                json.dumps(status_data),
                {'headers': cors_headers}
            )

        else:
            # 404 Not Found
            return Response.new(
                json.dumps({'error': 'Endpoint not found'}),
                {'status': 404, 'headers': cors_headers}
            )

    except Exception as e:
        # 500 Internal Server Error
        return Response.new(
            json.dumps({'error': f'Internal server error: {str(e)}'}),
            {'status': 500, 'headers': cors_headers}
        )

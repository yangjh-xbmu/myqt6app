from js import Response
from datetime import datetime
import json


async def on_fetch(request, env):
    # 获取请求URL和方法
    url = request.url
    method = request.method
    
    # 设置CORS头
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # 处理预检请求
    if method == 'OPTIONS':
        return Response.new('', {'headers': cors_headers})
    
    # 解析URL路径
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    stripped_path = parsed_url.path.strip('/')
    path = stripped_path.split('/')[-1] if stripped_path else ''
    
    try:
        if path == 'test' and method == 'GET':
            # 返回测试数据
            test_data = {
                'message': '来自Python Worker的问候！',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'environment': 'development',
                'worker_info': {
                    'language': 'Python',
                    'runtime': 'Pyodide on Cloudflare Workers',
                    'status': 'running'
                }
            }
            return Response.new(
                json.dumps(test_data), 
                {'headers': cors_headers}
            )
        
        elif path == 'data' and method == 'POST':
            # 处理POST请求，返回处理后的数据
            try:
                # 简化的POST处理
                response_data = {
                    'message': '已处理POST请求',
                    'processed_at': datetime.now().isoformat(),
                    'status': 'success'
                }
                return Response.new(
                    json.dumps(response_data), 
                    {'headers': cors_headers}
                )
            except Exception as e:
                error_response = {
                    'error': 'POST处理错误',
                    'details': str(e)
                }
                return Response.new(
                    json.dumps(error_response), 
                    {'status': 400, 'headers': cors_headers}
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
            # 默认响应
            welcome_data = {
                'message': 'Welcome to Qt6 Python Worker!',
                'available_endpoints': ['/test', '/data', '/status'],
                'documentation': (
                    'Send GET request to /test for test data'
                )
            }
            return Response.new(
                json.dumps(welcome_data), 
                {'headers': cors_headers}
            )
            
    except Exception as e:
        error_response = {
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return Response.new(
            json.dumps(error_response), 
            {'status': 500, 'headers': cors_headers}
        )
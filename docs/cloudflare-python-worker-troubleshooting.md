# Cloudflare Python Worker 500 错误排查指南

## 问题概述

在使用 Cloudflare Python Workers 时，可能会遇到 HTTP 500 Internal Server Error，这通常是由于 Python Workers 的实验性特性和某些 API 兼容性问题导致的。

## 常见错误原因

### 1. 环境变量访问问题

**错误代码：**

```python
version = env.API_VERSION  # 可能导致 500 错误
```

**解决方案：**

```python
# 方法1：使用 getattr 但可能仍有问题
version = getattr(env, 'API_VERSION', '1.0.0')

# 方法2：直接使用硬编码值（推荐）
version = '1.0.0'
```

### 2. 请求体解析问题

**错误代码：**

```python
request_data = await request.json()  # 可能导致 500 错误
```

**解决方案：**

```python
# 方法1：使用 text() 然后手动解析
try:
    request_text = await request.text()
    request_data = json.loads(request_text) if request_text else {}
except Exception as e:
    request_data = {}

# 方法2：简化处理，不依赖请求体内容
response_data = {
    'message': '已处理POST请求',
    'processed_at': datetime.now().isoformat(),
    'status': 'success'
}
```

### 3. Response.json() 方法问题

**错误代码：**

```python
return Response.json(data)  # 可能不可用
```

**解决方案：**

```python
import json
from js import Response

return Response.new(
    json.dumps(data), 
    {'headers': {'Content-Type': 'application/json'}}
)
```

## 排查步骤

### 1. 检查基础端点

首先测试最简单的端点是否工作：

```bash
curl -v https://your-domain.com/test
```

### 2. 逐步简化代码

如果某个端点返回 500 错误，逐步简化该端点的代码：

1. 移除复杂的数据处理逻辑
2. 移除环境变量访问
3. 使用硬编码的响应数据
4. 确保所有异常都被正确捕获

### 3. 添加全局异常处理

```python
async def on_fetch(request, env):
    try:
        # 你的主要逻辑
        pass
    except Exception as e:
        error_response = {
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }
        return Response.new(
            json.dumps(error_response), 
            {'status': 500, 'headers': {'Content-Type': 'application/json'}}
        )
```

## 最佳实践

### 1. 保持代码简单

由于 Python Workers 仍处于实验阶段，建议：

- 避免复杂的数据处理逻辑
- 减少对外部依赖的使用
- 使用基础的 Python 标准库功能

### 2. 统一响应格式

```python
def create_json_response(data, status=200, headers=None):
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    if headers:
        default_headers.update(headers)
    
    return Response.new(
        json.dumps(data),
        {'status': status, 'headers': default_headers}
    )
```

### 3. 渐进式开发

1. 先实现最基础的功能
2. 确保基础功能稳定后再添加复杂特性
3. 每次修改后立即测试

## 调试技巧

### 1. 使用 curl 进行详细测试

```bash
# 查看详细的 HTTP 响应
curl -v https://your-domain.com/endpoint

# 测试 POST 请求
curl -v -X POST -H "Content-Type: application/json" \
  -d '{"test":"data"}' https://your-domain.com/endpoint
```

### 2. 检查 Wrangler 部署日志

```bash
pnpm wrangler deploy
# 注意部署过程中的警告信息
```

### 3. 分段测试

将复杂的端点拆分成多个简单的端点进行测试，确定问题的具体位置。

## 总结

Cloudflare Python Workers 的 500 错误通常源于：

1. **API 兼容性问题** - 某些 Python 或 Web API 在 Workers 环境中可能不完全支持
2. **环境变量访问限制** - 需要使用特定的方法访问环境变量
3. **请求/响应处理差异** - 需要使用 Workers 特定的 API 方法

解决这些问题的关键是保持代码简单、添加完善的异常处理，并采用渐进式开发方法。随着 Python Workers 功能的不断完善，这些限制可能会逐步解除。

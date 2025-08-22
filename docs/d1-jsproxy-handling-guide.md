# Cloudflare D1 数据库 JsProxy 对象处理指南

## 问题概述

在使用 Cloudflare Workers Python 环境操作 D1 数据库时，会遇到 `JsProxy` 对象处理的问题。D1 数据库查询返回的结果是 JavaScript 对象，在 Python 环境中表现为 `JsProxy` 对象，无法直接使用 Python 的字典访问语法。

## 常见错误

### 错误信息

```
'pyodide.ffi.JsProxy' object is not subscriptable
```

### 错误场景

1. 尝试使用 `result['field']` 访问 JsProxy 对象的属性
2. 对查询结果进行 Python 字典操作
3. 访问 `meta` 信息如 `last_row_id`

## 解决方案

### 1. 安全的属性访问

使用 `hasattr()` 和 `getattr()` 来安全地访问 JsProxy 对象的属性：

```python
def safe_get_attribute(obj, attr_name, default=None):
    """安全地获取 JsProxy 对象的属性"""
    try:
        if hasattr(obj, attr_name):
            return getattr(obj, attr_name)
        return default
    except Exception:
        return default
```

### 2. 处理查询结果

```python
def execute_db_query(query, params=None):
    """执行数据库查询并处理 JsProxy 结果"""
    try:
        # 执行查询
        if params:
            # D1 参数绑定需要一次性传入所有参数
            result = env.DB.prepare(query).bind(*params).all()
        else:
            result = env.DB.prepare(query).all()
        
        # 处理 JsProxy 对象
        try:
            # 尝试访问 results 属性
            if hasattr(result, 'results'):
                data = list(result.results)  # 转换为 Python 列表
            else:
                data = []
        except Exception:
            data = []
        
        return {
            'success': True,
            'data': data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': []
        }
```

### 3. 获取插入操作的 ID

```python
def get_insert_id(insert_result):
    """从插入结果中安全地获取 last_row_id"""
    user_id = None
    
    try:
        # 尝试多种方式获取 user_id
        if hasattr(insert_result, 'meta'):
            meta = insert_result.meta
            if hasattr(meta, 'last_row_id'):
                user_id = meta.last_row_id
        
        # 备选方案：尝试字典访问
        if user_id is None:
            try:
                meta = insert_result.get('meta', {})
                user_id = meta.get('last_row_id')
            except Exception:
                pass
                
    except Exception:
        pass
    
    return user_id
```

### 4. 处理用户数据访问

```python
def extract_user_data(user_data):
    """从查询结果中安全地提取用户数据"""
    if not user_data:
        return None
    
    user = user_data[0] if user_data else None
    if not user:
        return None
    
    try:
        # 安全地获取用户属性
        salt = getattr(user, 'salt', None) if hasattr(user, 'salt') else None
        password_hash = getattr(user, 'password_hash', None) if hasattr(user, 'password_hash') else None
        user_id = getattr(user, 'id', None) if hasattr(user, 'id') else None
        username = getattr(user, 'username', None) if hasattr(user, 'username') else None
        email = getattr(user, 'email', None) if hasattr(user, 'email') else None
        display_name = getattr(user, 'display_name', None) if hasattr(user, 'display_name') else None
        
        return {
            'salt': salt,
            'password_hash': password_hash,
            'id': user_id,
            'username': username,
            'email': email,
            'display_name': display_name
        }
        
    except Exception as e:
        print(f"Error extracting user data: {e}")
        return None
```

## 最佳实践

### 1. 统一的错误处理

```python
try:
    # JsProxy 操作
    result = some_jsproxy_operation()
except Exception as e:
    # 记录错误并返回默认值
    print(f"JsProxy handling error: {e}")
    return default_value
```

### 2. 防御性编程

- 始终检查对象是否存在所需属性
- 提供合理的默认值
- 使用 try-except 包装所有 JsProxy 操作

### 3. 参数绑定

D1 数据库的参数绑定需要一次性传入所有参数：

```python
# 正确的方式
result = env.DB.prepare(query).bind(*params).all()

# 错误的方式（会导致参数绑定错误）
stmt = env.DB.prepare(query)
for param in params:
    stmt = stmt.bind(param)
result = stmt.all()
```

## 调试技巧

### 1. 检查对象属性

```python
def debug_jsproxy(obj, name="object"):
    """调试 JsProxy 对象的属性"""
    print(f"Debugging {name}:")
    print(f"Type: {type(obj)}")
    
    # 尝试列出属性
    try:
        attrs = dir(obj)
        print(f"Attributes: {attrs}")
    except Exception as e:
        print(f"Cannot list attributes: {e}")
```

### 2. 逐步验证

```python
# 逐步验证每个访问步骤
if hasattr(result, 'results'):
    print("Has results attribute")
    try:
        data = list(result.results)
        print(f"Successfully converted to list: {len(data)} items")
    except Exception as e:
        print(f"Failed to convert to list: {e}")
else:
    print("No results attribute found")
```

## 总结

Cloudflare D1 数据库在 Python Workers 环境中的 JsProxy 对象处理需要特别注意：

1. **不能使用字典语法**：避免 `obj['key']` 访问方式
2. **使用属性访问**：优先使用 `hasattr()` 和 `getattr()`
3. **防御性编程**：始终包装 try-except 处理
4. **参数绑定**：一次性绑定所有参数
5. **类型转换**：将 JsProxy 结果转换为 Python 原生类型

通过遵循这些最佳实践，可以有效避免 JsProxy 相关的错误，确保应用程序的稳定运行。

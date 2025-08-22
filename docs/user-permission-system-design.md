# 用户权限管理系统设计方案

## 技术方案选择

### 推荐方案：RBAC（基于角色的访问控制）

**选择理由：**

1. **学习成本低**
   - 概念简单直观：用户 → 角色 → 权限
   - 易于理解和维护
   - 大量成熟的实践案例

2. **扩展性强**
   - 支持从简单到复杂的权限需求
   - 可以平滑升级到 ABAC（基于属性的访问控制）
   - 支持层级角色和权限继承

3. **实现成本合理**
   - 数据表结构相对简单
   - 查询逻辑清晰
   - 与 Cloudflare D1 兼容性好

### 替代方案对比

| 方案 | 学习成本 | 实现复杂度 | 扩展性 | 适用场景 |
|------|----------|------------|--------|-----------|
| **RBAC** | 低 | 中 | 高 | **推荐** - 适合大多数应用 |
| ACL | 低 | 低 | 低 | 简单应用，权限需求固定 |
| ABAC | 高 | 高 | 极高 | 复杂企业应用 |
| 自定义 | 中 | 高 | 中 | 特殊业务需求 |

## 数据库设计

### 核心表结构

#### 1. 用户表 (users)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME,
    -- 扩展字段
    metadata TEXT, -- JSON格式存储额外信息
    department VARCHAR(100),
    phone VARCHAR(20)
);
```

#### 2. 角色表 (roles)

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    level INTEGER DEFAULT 0, -- 角色层级，支持角色继承
    parent_role_id INTEGER, -- 父角色ID，支持角色层次结构
    is_system BOOLEAN DEFAULT FALSE, -- 系统角色标记
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_role_id) REFERENCES roles(id)
);
```

#### 3. 权限表 (permissions)

```sql
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL, -- 如：user.create, post.edit
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    resource VARCHAR(50) NOT NULL, -- 资源类型：user, post, system
    action VARCHAR(50) NOT NULL, -- 操作类型：create, read, update, delete
    category VARCHAR(50), -- 权限分类
    is_system BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. 用户角色关联表 (user_roles)

```sql
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    granted_by INTEGER, -- 授权人ID
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME, -- 角色过期时间（可选）
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE(user_id, role_id)
);
```

#### 5. 角色权限关联表 (role_permissions)

```sql
CREATE TABLE role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    granted_by INTEGER,
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE(role_id, permission_id)
);
```

#### 6. 用户会话表 (user_sessions) - 可选

```sql
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 索引优化

```sql
-- 用户表索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);

-- 角色表索引
CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_parent ON roles(parent_role_id);

-- 权限表索引
CREATE INDEX idx_permissions_name ON permissions(name);
CREATE INDEX idx_permissions_resource_action ON permissions(resource, action);

-- 关联表索引
CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_user_roles_role ON user_roles(role_id);
CREATE INDEX idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission ON role_permissions(permission_id);

-- 会话表索引
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
```

## 升级路径设计

### 阶段1：基础RBAC（当前实现）

- 用户、角色、权限三层结构
- 基本的增删改查操作
- 简单的权限检查

### 阶段2：增强RBAC

- 角色层次结构（父子角色）
- 权限继承
- 临时权限授权
- 权限过期机制

### 阶段3：混合模型

- 引入用户直接权限（绕过角色）
- 条件权限（基于时间、IP等）
- 动态权限计算

### 阶段4：ABAC扩展

- 基于属性的访问控制
- 策略引擎
- 复杂的业务规则

## 实现优势

### 1. 渐进式复杂度

- 从简单的用户-角色开始
- 逐步添加高级特性
- 每个阶段都是完整可用的

### 2. 数据一致性

- 外键约束保证数据完整性
- 软删除支持（通过状态字段）
- 审计跟踪（创建时间、更新时间）

### 3. 性能考虑

- 合理的索引设计
- 支持缓存策略
- 查询优化友好

### 4. 安全性

- 密码哈希 + 盐值
- 会话管理
- 权限最小化原则

## 初始数据

### 默认角色

```sql
INSERT INTO roles (name, display_name, description, level, is_system) VALUES
('super_admin', '超级管理员', '系统最高权限', 100, TRUE),
('admin', '管理员', '系统管理权限', 80, TRUE),
('moderator', '版主', '内容管理权限', 60, FALSE),
('user', '普通用户', '基础用户权限', 20, TRUE),
('guest', '访客', '只读权限', 10, TRUE);
```

### 基础权限

```sql
INSERT INTO permissions (name, display_name, resource, action, category, is_system) VALUES
-- 用户管理
('user.create', '创建用户', 'user', 'create', 'user_management', TRUE),
('user.read', '查看用户', 'user', 'read', 'user_management', TRUE),
('user.update', '更新用户', 'user', 'update', 'user_management', TRUE),
('user.delete', '删除用户', 'user', 'delete', 'user_management', TRUE),
-- 角色管理
('role.create', '创建角色', 'role', 'create', 'role_management', TRUE),
('role.read', '查看角色', 'role', 'read', 'role_management', TRUE),
('role.update', '更新角色', 'role', 'update', 'role_management', TRUE),
('role.delete', '删除角色', 'role', 'delete', 'role_management', TRUE),
-- 系统管理
('system.config', '系统配置', 'system', 'config', 'system_management', TRUE),
('system.monitor', '系统监控', 'system', 'monitor', 'system_management', TRUE);
```

这个设计方案既满足了当前的简单需求，又为未来的复杂权限系统预留了充分的扩展空间。

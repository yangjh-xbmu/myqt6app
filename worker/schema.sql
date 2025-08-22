-- 用户权限管理系统数据表结构
-- 基于 RBAC 模型设计

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    status TEXT CHECK(status IN ('active', 'inactive', 'suspended')) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME,
    -- 扩展字段
    metadata TEXT, -- JSON格式存储额外信息
    department VARCHAR(100),
    phone VARCHAR(20)
);

-- 2. 角色表
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    level INTEGER DEFAULT 0, -- 角色层级，支持角色继承
    parent_role_id INTEGER, -- 父角色ID，支持角色层次结构
    is_system BOOLEAN DEFAULT FALSE, -- 系统角色标记
    status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_role_id) REFERENCES roles(id)
);

-- 3. 权限表
CREATE TABLE IF NOT EXISTS permissions (
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

-- 4. 用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
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

-- 5. 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
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

-- 6. 用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
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

-- 7. 密码重置令牌表
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    used_at DATETIME,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引
-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- 角色表索引
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_roles_parent ON roles(parent_role_id);

-- 权限表索引
CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name);
CREATE INDEX IF NOT EXISTS idx_permissions_resource_action ON permissions(resource, action);

-- 关联表索引
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission ON role_permissions(permission_id);

-- 会话表索引
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);

-- 密码重置令牌表索引
CREATE INDEX IF NOT EXISTS idx_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_user ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_expires ON password_reset_tokens(expires_at);

-- 插入默认角色
INSERT OR IGNORE INTO roles (name, display_name, description, level, is_system) VALUES
('super_admin', '超级管理员', '系统最高权限', 100, TRUE),
('admin', '管理员', '系统管理权限', 80, TRUE),
('moderator', '版主', '内容管理权限', 60, FALSE),
('user', '普通用户', '基础用户权限', 20, TRUE),
('guest', '访客', '只读权限', 10, TRUE);

-- 插入基础权限
INSERT OR IGNORE INTO permissions (name, display_name, resource, action, category, is_system) VALUES
-- 用户管理
('user.create', '创建用户', 'user', 'create', 'user_management', TRUE),
('user.read', '查看用户', 'user', 'read', 'user_management', TRUE),
('user.update', '更新用户', 'user', 'update', 'user_management', TRUE),
('user.delete', '删除用户', 'user', 'delete', 'user_management', TRUE),
('user.list', '用户列表', 'user', 'list', 'user_management', TRUE),
-- 角色管理
('role.create', '创建角色', 'role', 'create', 'role_management', TRUE),
('role.read', '查看角色', 'role', 'read', 'role_management', TRUE),
('role.update', '更新角色', 'role', 'update', 'role_management', TRUE),
('role.delete', '删除角色', 'role', 'delete', 'role_management', TRUE),
('role.assign', '分配角色', 'role', 'assign', 'role_management', TRUE),
-- 权限管理
('permission.read', '查看权限', 'permission', 'read', 'permission_management', TRUE),
('permission.assign', '分配权限', 'permission', 'assign', 'permission_management', TRUE),
-- 系统管理
('system.config', '系统配置', 'system', 'config', 'system_management', TRUE),
('system.monitor', '系统监控', 'system', 'monitor', 'system_management', TRUE),
-- 基础权限
('auth.login', '登录系统', 'auth', 'login', 'basic', TRUE),
('auth.logout', '退出系统', 'auth', 'logout', 'basic', TRUE),
('profile.read', '查看个人资料', 'profile', 'read', 'basic', TRUE),
('profile.update', '更新个人资料', 'profile', 'update', 'basic', TRUE);

-- 为默认角色分配权限
-- 超级管理员：所有权限
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'super_admin';

-- 管理员：用户和角色管理权限
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'admin' 
AND p.category IN ('user_management', 'role_management', 'basic');

-- 普通用户：基础权限
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'user' 
AND p.category = 'basic';

-- 访客：只有登录权限
INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name = 'guest' 
AND p.name IN ('auth.login', 'profile.read');
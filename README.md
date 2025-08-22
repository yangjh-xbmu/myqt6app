# PyQt6 用户权限管理系统

一个基于 PyQt6 和 Cloudflare Workers Python 的现代化用户权限管理系统。

## 🚀 快速开始

### 启动应用程序

**统一启动方式：**

```bash
cd src
python main.py --mode main      # 启动主应用程序（推荐）
python main.py --mode login     # 启动登录界面
python main.py --mode auth      # 启动用户认证应用
python main.py --mode register  # 启动注册界面
python main.py --mode test      # 启动 API 测试工具
```

**直接启动（兼容旧版本）：**

```bash
python main_app_with_menu.py    # 主应用程序
python login_app.py             # 登录界面
python user_auth_app.py         # 用户认证应用
```

## 📋 功能特性

### 🎯 主要功能

- **用户管理**
  - 用户注册和登录
  - 基于 Cloudflare D1 数据库的用户存储
  - 安全的密码哈希处理

- **数据库管理**
  - 远程和本地数据库查看
  - 用户数据管理工具
  - 数据库管理面板

- **开发工具**
  - Worker API 测试界面
  - 脚本管理工具
  - 开发调试功能

### 🎨 界面特性

- **现代化 UI**：基于 QFluentWidgets 的 Fluent Design
- **传统菜单栏**：类似 Word 软件的标准菜单栏
- **主题支持**：浅色、深色、自动主题切换
- **快捷键支持**：常用功能的键盘快捷键

### 🧪 自动化测试

- **文件监控**：代码修改时自动运行相关测试
- **Git钩子**：提交和推送时自动质量检查
- **CI/CD流水线**：GitHub Actions自动化测试和部署
- **多层测试**：单元测试、集成测试、UI测试
- **测试覆盖率**：自动生成覆盖率报告

## 🏗️ 项目结构

### 分层架构设计

项目采用现代化的分层架构，将代码按职责分离到不同层次：

```txt
myqt6app/
├── src/                       # 源代码目录（分层架构）
│   ├── main.py                # 统一应用入口
│   ├── ui/                    # 表示层 (Presentation Layer)
│   │   ├── launcher.py        # 应用启动器
│   │   ├── components/        # 可复用UI组件
│   │   │   ├── database_management.py  # 数据库管理组件
│   │   │   └── settings.py    # 设置组件
│   │   ├── windows/           # 窗口类
│   │   │   ├── main_window.py # 主窗口
│   │   │   ├── login_window.py # 登录窗口
│   │   │   ├── auth_window.py  # 认证窗口
│   │   │   └── register_window.py # 注册窗口
│   │   └── dialogs/           # 对话框
│   ├── business/              # 业务逻辑层 (Business Logic Layer)
│   │   ├── services/          # 业务服务
│   │   ├── models/            # 数据模型
│   │   └── validators/        # 数据验证
│   ├── data/                  # 数据访问层 (Data Access Layer)
│   │   ├── repositories/      # 数据仓库
│   │   ├── api/               # API客户端
│   │   │   └── network_client.py # 网络客户端
│   │   └── database/          # 数据库操作
│   └── infrastructure/        # 基础设施层 (Infrastructure Layer)
│       ├── config/            # 配置管理
│       ├── logging/           # 日志系统
│       ├── security/          # 安全相关
│       └── utils/             # 工具类
├── main_app_with_menu.py      # 主应用程序（兼容旧版本）
├── login_app.py               # 登录界面（兼容旧版本）
├── user_auth_app.py           # 用户认证应用（兼容旧版本）
├── register_app.py            # 注册界面（兼容旧版本）
├── worker_test_app.py         # API 测试工具（兼容旧版本）
├── styles.qss                 # 样式文件
├── scripts/                   # 管理脚本
│   ├── view_users.py          # 用户查看工具（Python）
│   ├── view_users.sh          # 用户查看工具（Shell）
│   └── README.md              # 脚本使用说明
├── worker/                    # Cloudflare Worker 后端
│   ├── src/entry.py           # Worker 入口文件
│   ├── wrangler.toml          # Worker 配置
│   └── schema.sql             # 数据库架构
└── docs/                      # 文档目录
    ├── menu-design-guide.md   # 菜单设计指南
    ├── d1-jsproxy-handling-guide.md  # D1 数据库问题解决指南
    └── user-permission-system-design.md  # 系统设计文档
```

### 架构优势

- **分层清晰**：UI、业务逻辑、数据访问、基础设施各司其职
- **低耦合**：层间通过接口通信，便于测试和维护
- **可扩展**：新功能可以轻松添加到对应层次
- **可复用**：组件化设计，代码复用率高
- **易维护**：职责单一，修改影响范围小

## 🛠️ 技术栈

### 前端架构

- **PyQt6**：现代化的 Python GUI 框架
- **QFluentWidgets**：Fluent Design 风格的 UI 组件库
- **Python 3.8+**：主要编程语言
- **分层架构**：MVC/MVP 模式，职责分离
- **组件化设计**：可复用的 UI 组件

### 后端架构

- **Cloudflare Workers**：无服务器计算平台
- **Python Runtime**：Workers 的 Python 运行时
- **Cloudflare D1**：分布式 SQLite 数据库
- **RESTful API**：标准化的接口设计

### 设计模式

- **单例模式**：全局配置和会话管理
- **工厂模式**：组件创建和依赖注入
- **观察者模式**：事件处理和状态通知
- **策略模式**：算法和业务规则的可替换实现

## 📖 使用指南

### 菜单栏功能

**用户管理**

- `用户登录 (Ctrl+L)`：打开登录界面
- `用户注册 (Ctrl+R)`：打开注册界面

**数据库管理**

- `查看远程数据库`：查看生产环境用户数据
- `查看本地数据库`：查看开发环境数据
- `数据库管理面板`：完整的数据库管理界面

**开发工具**

- `Worker API 测试 (Ctrl+T)`：测试后端 API 接口
- `打开脚本目录`：快速访问管理脚本

**设置**

- `应用设置`：完整的设置面板
- `浅色主题`：切换到浅色主题
- `深色主题`：切换到深色主题
- `自动主题`：根据系统设置自动切换

**帮助**

- `关于 (F1)`：显示应用程序信息
- `查看文档`：打开文档目录

### 数据库查看工具

**Python 脚本（推荐）：**

```bash
cd scripts
python view_users.py          # 查看远程数据库
python view_users.py local    # 查看本地数据库
```

**Shell 脚本：**

```bash
cd scripts
./view_users.sh               # 查看远程数据库
./view_users.sh local         # 查看本地数据库
```

## 🔧 开发环境设置

### 前端依赖安装

```bash
# 安装核心依赖
pip install PyQt6 qfluentwidgets requests

# 开发依赖（可选）
pip install pytest pytest-qt black flake8
```

### 项目结构初始化

```bash
# 克隆项目后，确保目录结构完整
cd myqt6app
ls src/  # 确认分层架构目录存在
```

### 后端部署

```bash
cd worker
pnpm install
npx wrangler deploy
```

### 数据库初始化

```bash
cd worker
npx wrangler d1 execute qt6-user-db --file=schema.sql
```

### 开发规范

**代码组织原则：**

- UI 相关代码放在 `src/ui/` 层
- 业务逻辑放在 `src/business/` 层
- 数据访问放在 `src/data/` 层
- 工具类放在 `src/infrastructure/` 层

**导入规范：**

- 使用绝对导入路径
- 避免循环依赖
- 按层次组织导入语句

## 🧪 测试与自动化

### 快速开始

```bash
# 一键设置自动化测试环境
make setup-auto-test

# 启动文件监控自动测试
make watch

# 运行所有测试
make test
```

### 测试类型

- **单元测试**: 测试独立的函数和类
- **集成测试**: 测试组件间的交互
- **UI测试**: 测试用户界面功能
- **快速测试**: 运行最重要的测试子集

### 自动化功能

1. **文件监控**: 修改代码时自动运行相关测试
2. **Git钩子**: 提交前自动运行测试，确保代码质量
3. **CI/CD**: GitHub Actions自动化测试和部署

### 测试命令

```bash
# 基础测试命令
make test-unit          # 单元测试
make test-integration   # 集成测试
make test-ui           # UI测试
make test-coverage     # 覆盖率测试

# Git钩子管理
make hooks-status      # 查看钩子状态
make hooks-enable      # 启用钩子
make hooks-disable     # 禁用钩子
```

详细使用说明请参考 [自动测试指南](docs/auto-testing-guide.md)。

## 📚 文档

- [菜单设计指南](docs/menu-design-guide.md) - 详细的菜单结构设计说明
- [D1 数据库问题解决指南](docs/d1-jsproxy-handling-guide.md) - JsProxy 对象处理方案
- [系统设计文档](docs/user-permission-system-design.md) - 完整的系统架构设计
- [自动测试指南](docs/auto-testing-guide.md) - 自动化测试系统使用说明
- [脚本使用说明](scripts/README.md) - 管理脚本的详细使用方法

## 🐛 故障排除

### 常见问题

1. **应用启动失败**
   - 检查 Python 版本（需要 3.8+）
   - 确认已安装所有依赖包
   - 确保在 `src/` 目录下运行 `python main.py`
   - 检查分层架构目录是否完整

2. **导入错误 (ImportError/ModuleNotFoundError)**
   - 确认使用绝对导入路径
   - 检查 `PYTHONPATH` 环境变量
   - 验证目标模块文件是否存在
   - 避免相对导入超出顶级包

3. **数据库连接问题**
   - 检查 Worker 是否正常部署
   - 确认 D1 数据库绑定配置
   - 验证网络客户端配置

4. **UI 显示异常**
   - 更新 QFluentWidgets 到最新版本
   - 检查系统字体设置
   - 确认 UI 组件正确导入

5. **分层架构相关问题**
   - 检查各层目录结构是否正确
   - 确认组件间依赖关系
   - 验证接口定义和实现

### 获取帮助

- 查看 [文档目录](docs/) 中的详细指南
- 使用应用内的帮助菜单
- 检查控制台输出的错误信息

## 🎯 未来计划

### 功能扩展

- [ ] 用户权限分级管理
- [ ] 数据导入/导出功能
- [ ] 多语言支持
- [ ] 插件系统
- [ ] 移动端适配

### 架构优化

- [ ] 依赖注入容器实现
- [ ] 事件总线系统
- [ ] 缓存层设计
- [ ] 异步处理优化
- [x] 单元测试覆盖

### 开发体验

- [ ] 代码生成工具
- [x] 自动化测试系统
- [ ] 自动化部署流程
- [ ] 性能监控面板
- [ ] 开发文档完善
- [ ] API 文档自动生成

---

**开发者**: 基于 PyQt6 和 Cloudflare Workers 构建  
**许可证**: MIT License  
**版本**: 1.0.0

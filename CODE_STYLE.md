# 代码风格配置说明

本项目已配置多种代码检查工具来忽略行长度限制，让开发者专注于代码逻辑而不是格式问题。

## 配置文件说明

### 1. `.flake8` - Flake8 配置
- **作用**: 配置 flake8 代码检查工具
- **行长度设置**: 忽略 E501 错误（行长度超限）
- **使用方法**: 
  ```bash
  flake8 src/  # 检查代码，会忽略行长度问题
  ```

### 2. `pyproject.toml` - 现代 Python 项目配置
- **作用**: 配置 black、pylint、isort 等工具
- **行长度设置**: 设置为 120 字符（可根据需要调整）
- **使用方法**:
  ```bash
  black src/          # 格式化代码
  pylint src/         # 检查代码质量
  isort src/          # 排序导入语句
  ```

### 3. `.pylintrc` - Pylint 详细配置
- **作用**: 详细配置 pylint 检查规则
- **行长度设置**: 禁用 `line-too-long` 检查
- **使用方法**:
  ```bash
  pylint src/         # 使用配置文件检查代码
  ```

## 如何完全忽略行长度检查

### 方法 1: 使用现有配置（推荐）
项目已经配置好了，直接使用即可：
```bash
# 这些命令都会忽略行长度问题
flake8 src/
pylint src/
black src/
```

### 方法 2: IDE 配置
在你的 IDE 中配置使用项目的配置文件：
- **VS Code**: 安装 Python 扩展，会自动读取配置文件
- **PyCharm**: 在设置中启用 flake8/pylint，指向项目配置文件
- **Vim/Neovim**: 配置相应的插件使用项目配置

### 方法 3: 临时忽略
如果只想临时忽略某些文件的行长度检查：
```bash
# 忽略特定文件
flake8 --ignore=E501 src/specific_file.py

# 忽略特定目录
pylint --disable=line-too-long src/specific_dir/
```

### 方法 4: 行内忽略
在代码中添加注释来忽略特定行：
```python
# 忽略 flake8 行长度检查
very_long_line_of_code_that_exceeds_limit = "some very long string"  # noqa: E501

# 忽略 pylint 行长度检查
very_long_line_of_code_that_exceeds_limit = "some very long string"  # pylint: disable=line-too-long
```

## 推荐的开发流程

1. **编写代码**: 不用担心行长度，专注于逻辑实现
2. **运行检查**: 使用配置好的工具检查代码质量
   ```bash
   flake8 src/     # 检查语法和风格（忽略行长度）
   pylint src/     # 检查代码质量（忽略行长度）
   ```
3. **格式化代码**: 使用 black 自动格式化
   ```bash
   black src/      # 自动格式化，使用 120 字符行长度
   ```
4. **提交代码**: 代码已经符合项目规范

## 注意事项

- 虽然忽略了行长度检查，但建议保持代码的可读性
- 过长的行可能影响代码审查和维护
- 可以根据团队需求调整 `pyproject.toml` 中的 `line-length` 设置
- 配置文件已排除 `legacy/` 和 `worker/` 目录，这些目录有自己的代码风格

## 自定义配置

如果需要修改配置，编辑相应的配置文件：
- 修改 `.flake8` 来调整 flake8 规则
- 修改 `pyproject.toml` 来调整 black、pylint 等工具
- 修改 `.pylintrc` 来详细配置 pylint 规则

配置修改后，重新运行检查工具即可生效。
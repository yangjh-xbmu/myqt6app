# 自动 Import 排序配置指南

## 概述

本项目已配置自动 import 排序功能，可以在保存文件时自动修复 Python 文件的 import 顺序，解决 Pylint 的 `wrong-import-order` 错误。

## 配置文件

### 1. VS Code 设置 (`.vscode/settings.json`)

```json
{
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    },
    "python.formatting.provider": "black",
    "python.sortImports.args": [
        "--profile=black"
    ]
}
```

### 2. isort 配置 (`.isort.cfg`)

```ini
[settings]
# 与 black 兼容的配置
profile = black
line_length = 88

# import 顺序配置
known_first_party = myqt6app,src,business,data,infrastructure,ui
known_third_party = PyQt6,qfluentwidgets,pytest,watchdog,colorama,click

# 分组顺序：标准库 -> 第三方库 -> 本地库
sections = FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER

# 每个分组之间添加空行
lines_after_imports = 2
```

## Import 排序规则

### 标准顺序

1. **Future imports** (`from __future__ import ...`)
2. **标准库导入** (`import sys`, `from pathlib import Path`)
3. **第三方库导入** (`import pytest`, `from PyQt6 import QtWidgets`)
4. **本地项目导入** (`from src.business import UserService`)
5. **相对导入** (`from .models import User`)

### 示例

**修复前：**

```python
import pytest
import sys
from pathlib import Path
```

**修复后：**

```python
import sys
from pathlib import Path

import pytest
```

## 使用方法

### 自动修复（推荐）

1. **保存时自动修复**：在 Trae IDE 中保存 Python 文件时，import 顺序会自动修复
2. **VS Code**：同样支持保存时自动修复

### 手动修复

```bash
# 修复单个文件
isort filename.py

# 修复整个目录
isort src/ tests/

# 检查但不修改
isort --check-only filename.py
```

## 验证配置

运行以下命令验证配置是否正确：

```bash
# 检查 import 顺序
isort --check-only --diff tests/integration/test_user_service.py

# 运行 Pylint 检查
pylint tests/integration/test_user_service.py
```

## 常见问题

### Q: 为什么有些文件没有自动修复？

A: 确保：

1. 文件扩展名是 `.py`
2. VS Code 已安装 Python 扩展
3. 项目已安装 `isort` 和 `black`

### Q: 如何自定义 import 分组？

A: 编辑 `.isort.cfg` 文件中的 `known_first_party` 和 `known_third_party` 配置。

### Q: 与其他格式化工具冲突怎么办？

A: 使用 `profile = black` 确保与 Black 格式化工具兼容。

## 相关工具

- **isort**: Python import 排序工具
- **black**: Python 代码格式化工具
- **pylint**: Python 代码质量检查工具
- **VS Code Python 扩展**: 提供 IDE 集成支持

#!/usr/bin/env python3
import sys
import traceback

sys.path.insert(0, 'src')

try:
    from ui.launcher import AppLauncher
    print("导入成功")
except Exception as e:
    print(f"导入失败: {e}")
    traceback.print_exc()

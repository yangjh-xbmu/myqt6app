#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 import 顺序自动修复
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# 故意打乱的 import 顺序
import pytest


def testFunction():
    """测试函数"""
    print("Testing import order auto-fix")
    return True


if __name__ == "__main__":
    testFunction()

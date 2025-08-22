#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试主窗口 - 用于调试段错误问题
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class TestMainWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        """初始化用户界面"""
        self.setWindowTitle("测试主窗口")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央窗口部件
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        # 创建布局
        layout = QVBoxLayout(centralWidget)
        
        # 添加简单标签
        label = QLabel("测试主窗口 - 如果看到这个说明基本UI正常")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    print("测试窗口已显示")
    sys.exit(app.exec())
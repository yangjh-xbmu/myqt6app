#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试qfluentwidgets组件 - 用于调试段错误问题
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

try:
    from qfluentwidgets import TitleLabel, PrimaryPushButton, PushButton
    print("qfluentwidgets导入成功")
except ImportError as e:
    print(f"qfluentwidgets导入失败: {e}")
    sys.exit(1)


class TestQFluentWindow(QMainWindow):
    """测试qfluentwidgets窗口"""
    
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        """初始化用户界面"""
        self.setWindowTitle("测试qfluentwidgets组件")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央窗口部件
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        # 创建布局
        layout = QVBoxLayout(centralWidget)
        
        print("开始创建TitleLabel...")
        # 添加TitleLabel
        titleLabel = TitleLabel("测试标题")
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titleLabel)
        print("TitleLabel创建成功")
        
        print("开始创建PrimaryPushButton...")
        # 添加按钮
        primaryBtn = PrimaryPushButton("主要按钮")
        layout.addWidget(primaryBtn)
        print("PrimaryPushButton创建成功")
        
        print("开始创建PushButton...")
        normalBtn = PushButton("普通按钮")
        layout.addWidget(normalBtn)
        print("PushButton创建成功")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print("QApplication创建成功")
    
    window = TestQFluentWindow()
    print("测试窗口创建成功")
    
    window.show()
    print("测试窗口已显示")
    
    sys.exit(app.exec())
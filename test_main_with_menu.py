#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试带菜单的主窗口 - 用于调试段错误问题
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from qfluentwidgets import TitleLabel, PrimaryPushButton, PushButton


class TestMainWithMenu(QMainWindow):
    """测试带菜单的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        """初始化用户界面"""
        print("开始初始化UI...")
        
        # 设置窗口属性
        self.setWindowTitle("测试带菜单的主窗口")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口字体
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        print("字体设置完成")
        
        # 创建菜单栏
        print("开始创建菜单...")
        self.createMenu()
        print("菜单创建完成")
        
        # 创建中央窗口部件
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        # 创建主布局
        layout = QVBoxLayout(centralWidget)
        
        # 添加欢迎标题
        print("创建标题标签...")
        welcomeLabel = TitleLabel("测试主窗口")
        welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcomeLabel)
        print("标题标签创建完成")
        
        # 添加按钮
        print("创建按钮...")
        testBtn = PrimaryPushButton("测试按钮")
        testBtn.clicked.connect(self.testAction)
        layout.addWidget(testBtn)
        print("按钮创建完成")
        
        print("UI初始化完成")
    
    def createMenu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 测试菜单
        testMenu = menubar.addMenu('测试(&T)')
        
        testAction = QAction('测试动作(&A)', self)
        testAction.setShortcut('Ctrl+T')
        testAction.setStatusTip('执行测试动作')
        testAction.triggered.connect(self.testAction)
        testMenu.addAction(testAction)
    
    def testAction(self):
        """测试动作"""
        QMessageBox.information(self, "测试", "测试动作执行成功！")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print("QApplication创建成功")
    
    window = TestMainWithMenu()
    print("测试窗口创建成功")
    
    window.show()
    print("测试窗口已显示")
    
    sys.exit(app.exec())
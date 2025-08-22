#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置组件
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import TitleLabel


class SettingsWidget(QWidget):
    """设置组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()

    def initUi(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 标题
        title = TitleLabel("应用设置")
        layout.addWidget(title)

        # 占位内容
        content = QLabel("设置功能正在开发中...")
        layout.addWidget(content)

        self.setLayout(layout)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worker测试窗口 - 用于测试Cloudflare Worker API
"""

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    TitleLabel, LineEdit, TextEdit, PrimaryPushButton,
    ComboBox, InfoBar, InfoBarPosition, CardWidget
)

import json
import requests


class WorkerRequestThread(QThread):
    """Worker请求线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url, method='GET', data=None):
        super().__init__()
        self.url = url
        self.method = method
        self.data = data

    def run(self):
        try:
            headers = {'Content-Type': 'application/json'}

            if self.method == 'GET':
                response = requests.get(self.url, headers=headers, timeout=10)
            elif self.method == 'POST':
                response = requests.post(
                    self.url,
                    data=json.dumps(self.data) if self.data else None,
                    headers=headers,
                    timeout=10
                )
            elif self.method == 'PUT':
                response = requests.put(
                    self.url,
                    data=json.dumps(self.data) if self.data else None,
                    headers=headers,
                    timeout=10
                )
            elif self.method == 'DELETE':
                response = requests.delete(
                    self.url,
                    headers=headers,
                    timeout=10
                )
            else:
                self.error.emit(f'不支持的HTTP方法: {self.method}')
                return

            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text
            }

            # 尝试解析JSON响应
            try:
                result['json'] = response.json()
            except json.JSONDecodeError:
                result['json'] = None

            self.finished.emit(result)

        except requests.exceptions.RequestException as e:
            self.error.emit(f'请求失败: {str(e)}')
        except Exception as e:
            self.error.emit(f'未知错误: {str(e)}')


class WorkerTestWindow(QWidget):
    """Worker测试窗口"""

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle('Cloudflare Worker API 测试工具')
        self.setFixedSize(800, 700)

        # 设置窗口居中
        self.setWindowFlags(Qt.WindowType.Window)

        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        title = TitleLabel('Cloudflare Worker API 测试工具')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 请求配置卡片
        requestCard = CardWidget()
        requestLayout = QVBoxLayout()
        requestLayout.setSpacing(15)

        # URL输入
        self.urlInput = LineEdit()
        self.urlInput.setPlaceholderText(
            '请输入API URL '
            '(例如: https://your-worker.your-subdomain.workers.dev/api/test)'
        )
        self.urlInput.setText('https://pw.yangxz.top/api/test')
        self.urlInput.setClearButtonEnabled(True)
        requestLayout.addWidget(self.urlInput)

        # HTTP方法选择
        methodLayout = QHBoxLayout()
        methodLayout.addWidget(TitleLabel('HTTP方法:'))

        self.methodCombo = ComboBox()
        self.methodCombo.addItems(['GET', 'POST', 'PUT', 'DELETE'])
        self.methodCombo.setCurrentText('GET')
        methodLayout.addWidget(self.methodCombo)
        methodLayout.addStretch()

        requestLayout.addLayout(methodLayout)

        # 请求数据输入
        requestLayout.addWidget(TitleLabel('请求数据 (JSON格式):'))
        self.requestDataInput = TextEdit()
        self.requestDataInput.setPlaceholderText(
            '请输入JSON格式的请求数据\n例如: {"key": "value"}'
        )
        self.requestDataInput.setFixedHeight(120)
        requestLayout.addWidget(self.requestDataInput)

        # 发送请求按钮
        self.sendButton = PrimaryPushButton('发送请求')
        self.sendButton.clicked.connect(self.sendRequest)
        requestLayout.addWidget(self.sendButton)

        requestCard.setLayout(requestLayout)
        layout.addWidget(requestCard)

        # 响应显示卡片
        responseCard = CardWidget()
        responseLayout = QVBoxLayout()
        responseLayout.setSpacing(15)

        responseLayout.addWidget(TitleLabel('响应结果:'))

        self.responseDisplay = TextEdit()
        self.responseDisplay.setPlaceholderText('响应结果将在这里显示...')
        self.responseDisplay.setReadOnly(True)
        responseLayout.addWidget(self.responseDisplay)

        responseCard.setLayout(responseLayout)
        layout.addWidget(responseCard)

        self.setLayout(layout)

        # 设置回车键触发发送请求
        self.urlInput.returnPressed.connect(self.sendRequest)

    def sendRequest(self):
        """发送请求"""
        url = self.urlInput.text().strip()
        method = self.methodCombo.currentText()

        # 验证URL
        if not url:
            self.showError('请输入API URL')
            return

        if not url.startswith(('http://', 'https://')):
            self.showError('请输入有效的URL（以http://或https://开头）')
            return

        # 解析请求数据
        requestData = None
        if method in ['POST', 'PUT']:
            dataText = self.requestDataInput.toPlainText().strip()
            if dataText:
                try:
                    requestData = json.loads(dataText)
                except json.JSONDecodeError as e:
                    self.showError(f'请求数据JSON格式错误: {str(e)}')
                    return

        # 禁用发送按钮，防止重复请求
        self.sendButton.setEnabled(False)
        self.sendButton.setText('发送中...')

        # 清空响应显示
        self.responseDisplay.clear()

        # 创建请求线程
        self.worker = WorkerRequestThread(url, method, requestData)

        # 连接信号
        self.worker.finished.connect(self.onRequestFinished)
        self.worker.error.connect(self.onRequestError)

        # 启动线程
        self.worker.start()

    def onRequestFinished(self, result):
        """请求完成处理"""
        self.sendButton.setEnabled(True)
        self.sendButton.setText('发送请求')

        # 格式化响应结果
        responseText = f"状态码: {result['status_code']}\n\n"

        # 显示响应头
        responseText += "响应头:\n"
        for key, value in result['headers'].items():
            responseText += f"  {key}: {value}\n"
        responseText += "\n"

        # 显示响应内容
        responseText += "响应内容:\n"
        if result['json']:
            # 格式化JSON响应
            responseText += json.dumps(
                result['json'],
                indent=2,
                ensure_ascii=False
            )
        else:
            responseText += result['content']

        self.responseDisplay.setPlainText(responseText)

        # 显示成功信息
        InfoBar.success(
            title='请求成功',
            content=f'状态码: {result["status_code"]}',
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def onRequestError(self, errorMsg):
        """请求错误处理"""
        self.sendButton.setEnabled(True)
        self.sendButton.setText('发送请求')

        self.responseDisplay.setPlainText(f'请求失败: {errorMsg}')

        self.showError(f'请求失败: {errorMsg}')

    def showError(self, message):
        """显示错误信息"""
        InfoBar.error(
            title='错误',
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
